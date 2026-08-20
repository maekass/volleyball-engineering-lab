from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from statistics import fmean

from ball001.calculix_deck import SolverNode
from ball001.calculix_results import (
    FrdStress,
    parse_frd_results,
)
from ball001.formulation_comparison import (
    relative_change_percent,
)
from ball001.mesh_nodes import load_mesh_nodes
from ball001.nonlinear_stiffness_sweep import (
    StiffnessSweepCase,
)


@dataclass(frozen=True)
class StiffnessCaseMechanics:
    case: StiffnessSweepCase

    displacement_node_count: int
    stress_node_count: int

    mean_radial_displacement_mm: float
    max_radial_displacement_mm: float

    outward_node_fraction: float
    max_tangential_displacement_mm: float

    mean_tangential_stress_n_mm2: float

    mean_mesh_radius_mm: float
    radial_expansion_percent: float


@dataclass(frozen=True)
class NonlinearDivergenceResult:
    youngs_modulus_mpa: float

    linear_radial_displacement_mm: float
    nonlinear_radial_displacement_mm: float
    displacement_difference_percent: float

    linear_radial_expansion_percent: float
    nonlinear_radial_expansion_percent: float

    linear_tangential_stress_n_mm2: float
    nonlinear_tangential_stress_n_mm2: float
    stress_difference_percent: float

    linear_outward_node_fraction: float
    nonlinear_outward_node_fraction: float


def unit_radial_vector(
    node: SolverNode,
) -> tuple[
    float,
    float,
    float,
]:
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


def radial_displacement_mm(
    node: SolverNode,
    displacement_mm: tuple[
        float,
        float,
        float,
    ],
) -> float:
    nx, ny, nz = (
        unit_radial_vector(
            node
        )
    )

    ux, uy, uz = displacement_mm

    return (
        ux * nx
        + uy * ny
        + uz * nz
    )


def tangential_displacement_mm(
    node: SolverNode,
    displacement_mm: tuple[
        float,
        float,
        float,
    ],
) -> float:
    nx, ny, nz = (
        unit_radial_vector(
            node
        )
    )

    radial_mm = (
        radial_displacement_mm(
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


def radial_stress_n_mm2(
    node: SolverNode,
    stress: FrdStress,
) -> float:
    nx, ny, nz = (
        unit_radial_vector(
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


def mean_tangential_stress_n_mm2(
    node: SolverNode,
    stress: FrdStress,
) -> float:
    trace_n_mm2 = (
        stress.sxx_n_mm2
        + stress.syy_n_mm2
        + stress.szz_n_mm2
    )

    radial_n_mm2 = (
        radial_stress_n_mm2(
            node,
            stress,
        )
    )

    return (
        trace_n_mm2
        - radial_n_mm2
    ) / 2.0


def node_radius_mm(
    node: SolverNode,
) -> float:
    return sqrt(
        node.x_mm**2
        + node.y_mm**2
        + node.z_mm**2
    )


def analyze_stiffness_case(
    case: StiffnessSweepCase,
    mesh_path: Path,
    frd_path: Path,
) -> StiffnessCaseMechanics:
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
            radial_displacement_mm(
                node,
                displacement_mm,
            )
        )

        tangential_displacements.append(
            tangential_displacement_mm(
                node,
                displacement_mm,
            )
        )

    tangential_stresses = []

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
            mean_tangential_stress_n_mm2(
                node,
                stress,
            )
        )

    if not radial_displacements:
        raise ValueError(
            "No displacement results match "
            "the supplied mesh."
        )

    if not tangential_stresses:
        raise ValueError(
            "No stress results match "
            "the supplied mesh."
        )

    mean_radial_displacement = (
        fmean(
            radial_displacements
        )
    )

    mean_mesh_radius = (
        fmean(
            node_radius_mm(
                node
            )
            for node in mesh_nodes
        )
    )

    radial_expansion_percent = (
        mean_radial_displacement
        / mean_mesh_radius
        * 100.0
    )

    outward_node_fraction = (
        sum(
            displacement > 0.0
            for displacement
            in radial_displacements
        )
        / len(
            radial_displacements
        )
    )

    return StiffnessCaseMechanics(
        case=case,
        displacement_node_count=len(
            radial_displacements
        ),
        stress_node_count=len(
            tangential_stresses
        ),
        mean_radial_displacement_mm=(
            mean_radial_displacement
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
            fmean(
                tangential_stresses
            )
        ),
        mean_mesh_radius_mm=(
            mean_mesh_radius
        ),
        radial_expansion_percent=(
            radial_expansion_percent
        ),
    )


def compare_linear_and_nlgeom(
    linear: StiffnessCaseMechanics,
    nonlinear: StiffnessCaseMechanics,
) -> NonlinearDivergenceResult:
    if (
        linear.case.youngs_modulus_mpa
        != nonlinear.case.youngs_modulus_mpa
    ):
        raise ValueError(
            "Linear and nonlinear cases must "
            "use the same Young's modulus."
        )

    return NonlinearDivergenceResult(
        youngs_modulus_mpa=(
            linear.case.youngs_modulus_mpa
        ),
        linear_radial_displacement_mm=(
            linear.mean_radial_displacement_mm
        ),
        nonlinear_radial_displacement_mm=(
            nonlinear.mean_radial_displacement_mm
        ),
        displacement_difference_percent=(
            relative_change_percent(
                nonlinear.mean_radial_displacement_mm,
                linear.mean_radial_displacement_mm,
            )
        ),
        linear_radial_expansion_percent=(
            linear.radial_expansion_percent
        ),
        nonlinear_radial_expansion_percent=(
            nonlinear.radial_expansion_percent
        ),
        linear_tangential_stress_n_mm2=(
            linear.mean_tangential_stress_n_mm2
        ),
        nonlinear_tangential_stress_n_mm2=(
            nonlinear.mean_tangential_stress_n_mm2
        ),
        stress_difference_percent=(
            relative_change_percent(
                nonlinear.mean_tangential_stress_n_mm2,
                linear.mean_tangential_stress_n_mm2,
            )
        ),
        linear_outward_node_fraction=(
            linear.outward_node_fraction
        ),
        nonlinear_outward_node_fraction=(
            nonlinear.outward_node_fraction
        ),
    )