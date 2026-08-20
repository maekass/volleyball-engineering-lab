import re
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from statistics import fmean, pstdev

from ball001.calculix_deck import SolverNode
from ball001.design import BallDesign
from ball001.effective_shell import (
    EffectiveShellMaterial,
    calculate_effective_shell_verification,
)
from ball001.mesh_nodes import load_mesh_nodes
from ball001.pressure import PressureLoadCase

_FRD_FLOAT_PATTERN = re.compile(
    r"""
    [+-]?
    (?:
        (?:\d+\.\d*)
        |
        (?:\.\d+)
        |
        (?:\d+)
    )
    (?:
        [EeDd]
        [+-]?
        \d+
    )?
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class FrdStress:
    sxx_n_mm2: float
    syy_n_mm2: float
    szz_n_mm2: float
    sxy_n_mm2: float
    syz_n_mm2: float
    szx_n_mm2: float


@dataclass(frozen=True)
class FrdResults:
    displacements_mm: dict[
        int,
        tuple[float, float, float],
    ]
    stresses_n_mm2: dict[
        int,
        FrdStress,
    ]


@dataclass(frozen=True)
class CalculixVerificationResult:
    displacement_node_count: int
    stress_node_count: int

    mean_radial_displacement_mm: float
    radial_displacement_std_mm: float
    min_radial_displacement_mm: float
    max_radial_displacement_mm: float

    outward_node_fraction: float
    max_tangential_displacement_mm: float

    mean_tangential_stress_n_mm2: float
    tangential_stress_std_n_mm2: float
    mean_radial_stress_n_mm2: float

    analytical_radial_displacement_mm: float
    analytical_membrane_stress_n_mm2: float

    displacement_error_percent: float
    stress_error_percent: float


def _parse_frd_values(
    line: str,
    count: int,
) -> tuple[float, ...]:
    if count <= 0:
        raise ValueError(
            "Requested FRD value count must be positive."
        )

    payload = line[13:]

    matches = _FRD_FLOAT_PATTERN.findall(
        payload
    )

    if len(matches) < count:
        raise ValueError(
            "FRD data line did not contain "
            f"{count} numeric values: {line!r}"
        )

    values = []

    for token in matches[:count]:
        normalized_token = (
            token.replace(
                "D",
                "E",
            ).replace(
                "d",
                "e",
            )
        )

        values.append(
            float(
                normalized_token
            )
        )

    return tuple(
        values
    )


def parse_frd_results(
    frd_path: Path,
) -> FrdResults:
    if not frd_path.exists():
        raise FileNotFoundError(
            f"FRD file does not exist: {frd_path}"
        )

    displacements = {}
    stresses = {}

    active_section = None

    with frd_path.open() as frd_file:
        for line in frd_file:
            if len(line) >= 9 and (
                line[5:9] == "DISP"
            ):
                active_section = "DISP"
                continue

            if len(line) >= 11 and (
                line[5:11] == "STRESS"
            ):
                active_section = "STRESS"
                continue

            if len(line) >= 3 and (
                line[1:3] == "-3"
            ):
                active_section = None
                continue

            if len(line) < 13:
                continue

            if line[1:3] != "-1":
                continue

            if active_section is None:
                continue

            node_tag = int(
                line[4:13]
            )

            if active_section == "DISP":
                values = _parse_frd_values(
                    line,
                    3,
                )

                displacements[node_tag] = (
                    values[0],
                    values[1],
                    values[2],
                )

            elif active_section == "STRESS":
                values = _parse_frd_values(
                    line,
                    6,
                )

                stresses[node_tag] = FrdStress(
                    sxx_n_mm2=values[0],
                    syy_n_mm2=values[1],
                    szz_n_mm2=values[2],
                    sxy_n_mm2=values[3],
                    syz_n_mm2=values[4],
                    szx_n_mm2=values[5],
                )

    if not displacements:
        raise ValueError(
            "No displacement results found in FRD file."
        )

    if not stresses:
        raise ValueError(
            "No stress results found in FRD file."
        )

    return FrdResults(
        displacements_mm=displacements,
        stresses_n_mm2=stresses,
    )


def _unit_radial_vector(
    node: SolverNode,
) -> tuple[float, float, float]:
    radius_mm = sqrt(
        node.x_mm**2
        + node.y_mm**2
        + node.z_mm**2
    )

    if radius_mm <= 0.0:
        raise ValueError(
            "Node radius must be positive."
        )

    return (
        node.x_mm / radius_mm,
        node.y_mm / radius_mm,
        node.z_mm / radius_mm,
    )


def _radial_displacement_mm(
    node: SolverNode,
    displacement_mm: tuple[
        float,
        float,
        float,
    ],
) -> float:
    nx, ny, nz = (
        _unit_radial_vector(
            node
        )
    )

    ux, uy, uz = displacement_mm

    return (
        ux * nx
        + uy * ny
        + uz * nz
    )


def _tangential_displacement_mm(
    node: SolverNode,
    displacement_mm: tuple[
        float,
        float,
        float,
    ],
) -> float:
    nx, ny, nz = (
        _unit_radial_vector(
            node
        )
    )

    radial_mm = (
        _radial_displacement_mm(
            node,
            displacement_mm,
        )
    )

    ux, uy, uz = displacement_mm

    tx = (
        ux
        - radial_mm * nx
    )

    ty = (
        uy
        - radial_mm * ny
    )

    tz = (
        uz
        - radial_mm * nz
    )

    return sqrt(
        tx**2
        + ty**2
        + tz**2
    )


def _radial_stress_n_mm2(
    node: SolverNode,
    stress: FrdStress,
) -> float:
    nx, ny, nz = (
        _unit_radial_vector(
            node
        )
    )

    return (
        stress.sxx_n_mm2 * nx**2
        + stress.syy_n_mm2 * ny**2
        + stress.szz_n_mm2 * nz**2
        + 2.0
        * stress.sxy_n_mm2
        * nx
        * ny
        + 2.0
        * stress.syz_n_mm2
        * ny
        * nz
        + 2.0
        * stress.szx_n_mm2
        * nz
        * nx
    )


def _mean_tangential_stress_n_mm2(
    node: SolverNode,
    stress: FrdStress,
) -> float:
    trace_n_mm2 = (
        stress.sxx_n_mm2
        + stress.syy_n_mm2
        + stress.szz_n_mm2
    )

    radial_n_mm2 = (
        _radial_stress_n_mm2(
            node,
            stress,
        )
    )

    return (
        trace_n_mm2
        - radial_n_mm2
    ) / 2.0


def analyze_calculix_verification(
    mesh_path: Path,
    frd_path: Path,
    design: BallDesign,
    load_case: PressureLoadCase,
    material: EffectiveShellMaterial,
) -> CalculixVerificationResult:
    mesh_nodes = load_mesh_nodes(
        mesh_path
    )

    frd_results = parse_frd_results(
        frd_path
    )

    nodes_by_tag = {
        node.tag: node
        for node in mesh_nodes
    }

    radial_displacements = []
    tangential_displacements = []

    for (
        node_tag,
        displacement_mm,
    ) in frd_results.displacements_mm.items():
        node = nodes_by_tag.get(
            node_tag
        )

        if node is None:
            continue

        radial_displacements.append(
            _radial_displacement_mm(
                node,
                displacement_mm,
            )
        )

        tangential_displacements.append(
            _tangential_displacement_mm(
                node,
                displacement_mm,
            )
        )

    tangential_stresses = []
    radial_stresses = []

    for (
        node_tag,
        stress,
    ) in frd_results.stresses_n_mm2.items():
        node = nodes_by_tag.get(
            node_tag
        )

        if node is None:
            continue

        tangential_stresses.append(
            _mean_tangential_stress_n_mm2(
                node,
                stress,
            )
        )

        radial_stresses.append(
            _radial_stress_n_mm2(
                node,
                stress,
            )
        )

    if not radial_displacements:
        raise ValueError(
            "No displacement results match mesh nodes."
        )

    if not tangential_stresses:
        raise ValueError(
            "No stress results match mesh nodes."
        )

    analytical = (
        calculate_effective_shell_verification(
            design,
            load_case,
            material,
        )
    )

    analytical_radial_displacement_mm = (
        analytical.radial_expansion_m
        * 1000.0
    )

    analytical_membrane_stress_n_mm2 = (
        analytical.membrane_stress_pa
        / 1_000_000.0
    )

    mean_radial_displacement_mm = (
        fmean(
            radial_displacements
        )
    )

    mean_tangential_stress_n_mm2 = (
        fmean(
            tangential_stresses
        )
    )

    displacement_error_percent = (
        abs(
            mean_radial_displacement_mm
            - analytical_radial_displacement_mm
        )
        / analytical_radial_displacement_mm
        * 100.0
    )

    stress_error_percent = (
        abs(
            mean_tangential_stress_n_mm2
            - analytical_membrane_stress_n_mm2
        )
        / analytical_membrane_stress_n_mm2
        * 100.0
    )

    outward_node_fraction = (
        sum(
            radial_mm > 0.0
            for radial_mm in radial_displacements
        )
        / len(
            radial_displacements
        )
    )

    return CalculixVerificationResult(
        displacement_node_count=len(
            radial_displacements
        ),
        stress_node_count=len(
            tangential_stresses
        ),
        mean_radial_displacement_mm=(
            mean_radial_displacement_mm
        ),
        radial_displacement_std_mm=(
            pstdev(
                radial_displacements
            )
        ),
        min_radial_displacement_mm=min(
            radial_displacements
        ),
        max_radial_displacement_mm=max(
            radial_displacements
        ),
        outward_node_fraction=(
            outward_node_fraction
        ),
        max_tangential_displacement_mm=max(
            tangential_displacements
        ),
        mean_tangential_stress_n_mm2=(
            mean_tangential_stress_n_mm2
        ),
        tangential_stress_std_n_mm2=(
            pstdev(
                tangential_stresses
            )
        ),
        mean_radial_stress_n_mm2=(
            fmean(
                radial_stresses
            )
        ),
        analytical_radial_displacement_mm=(
            analytical_radial_displacement_mm
        ),
        analytical_membrane_stress_n_mm2=(
            analytical_membrane_stress_n_mm2
        ),
        displacement_error_percent=(
            displacement_error_percent
        ),
        stress_error_percent=(
            stress_error_percent
        ),
    )