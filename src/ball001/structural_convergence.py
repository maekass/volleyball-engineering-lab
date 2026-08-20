from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess

from ball001.calculix_deck import (
    export_calculix_verification_deck,
)
from ball001.calculix_results import (
    analyze_calculix_verification,
)
from ball001.design import BallDesign
from ball001.effective_shell import (
    EffectiveShellMaterial,
    total_wall_thickness_m,
)
from ball001.mesh import (
    SurfaceMeshSpec,
    generate_surface_mesh,
)
from ball001.pressure import PressureLoadCase


@dataclass(frozen=True)
class StructuralConvergenceResult:
    mesh_name: str
    target_size_mm: float
    node_count: int
    triangle_count: int
    mean_radial_displacement_mm: float
    displacement_error_percent: float
    mean_tangential_stress_n_mm2: float
    stress_error_percent: float
    outward_node_fraction: float
    max_tangential_displacement_mm: float


def relative_change_percent(
    current_value: float,
    previous_value: float,
) -> float:
    if previous_value == 0.0:
        raise ValueError(
            "Previous value must be nonzero."
        )

    return (
        abs(
            current_value
            - previous_value
        )
        / abs(previous_value)
        * 100.0
    )


def _remove_old_solver_outputs(
    directory: Path,
    job_name: str,
) -> None:
    suffixes = (
        ".12d",
        ".cvg",
        ".dat",
        ".frd",
        ".sta",
    )

    for suffix in suffixes:
        path = (
            directory
            / f"{job_name}{suffix}"
        )

        if path.exists():
            path.unlink()


def run_structural_convergence_case(
    design: BallDesign,
    mesh_spec: SurfaceMeshSpec,
    load_case: PressureLoadCase,
    material: EffectiveShellMaterial,
    output_directory: Path,
    ccx_executable: str | None = None,
) -> StructuralConvergenceResult:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    executable = (
        ccx_executable
        or shutil.which("ccx")
    )

    if executable is None:
        raise FileNotFoundError(
            "CalculiX executable 'ccx' was not found."
        )

    job_name = (
        f"ball001_{mesh_spec.name}_verify"
    )

    mesh_path = (
        output_directory
        / f"{job_name}.msh"
    )

    deck_path = (
        output_directory
        / f"{job_name}.inp"
    )

    frd_path = (
        output_directory
        / f"{job_name}.frd"
    )

    _remove_old_solver_outputs(
        output_directory,
        job_name,
    )

    mesh_summary = generate_surface_mesh(
        design,
        mesh_spec,
        output_path=mesh_path,
    )

    export_calculix_verification_deck(
        mesh_path=mesh_path,
        deck_path=deck_path,
        load_case=load_case,
        material=material,
        shell_thickness_m=(
            total_wall_thickness_m(
                design
            )
        ),
    )

    completed = subprocess.run(
        [
            executable,
            "-i",
            job_name,
        ],
        cwd=output_directory,
        check=False,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "CalculiX solve failed for "
            f"{mesh_spec.name} mesh.\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        )

    if not frd_path.exists():
        raise RuntimeError(
            "CalculiX completed without creating "
            f"the expected FRD file: {frd_path}"
        )

    verification = (
        analyze_calculix_verification(
            mesh_path=mesh_path,
            frd_path=frd_path,
            design=design,
            load_case=load_case,
            material=material,
        )
    )

    return StructuralConvergenceResult(
        mesh_name=mesh_spec.name,
        target_size_mm=(
            mesh_spec.target_size_mm
        ),
        node_count=(
            mesh_summary.node_count
        ),
        triangle_count=(
            mesh_summary.triangle_count
        ),
        mean_radial_displacement_mm=(
            verification.mean_radial_displacement_mm
        ),
        displacement_error_percent=(
            verification.displacement_error_percent
        ),
        mean_tangential_stress_n_mm2=(
            verification.mean_tangential_stress_n_mm2
        ),
        stress_error_percent=(
            verification.stress_error_percent
        ),
        outward_node_fraction=(
            verification.outward_node_fraction
        ),
        max_tangential_displacement_mm=(
            verification.max_tangential_displacement_mm
        ),
    )