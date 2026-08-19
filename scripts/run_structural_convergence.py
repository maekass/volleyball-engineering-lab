from pathlib import Path

from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
)
from ball001.mesh import (
    BALL001_MESH_SPECS,
)
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
)
from ball001.structural_convergence import (
    relative_change_percent,
    run_structural_convergence_case,
)

OUTPUT_DIRECTORY = Path(
    "exports/fea/convergence"
)


def main() -> None:
    results = []

    for mesh_spec in BALL001_MESH_SPECS:
        print(
            f"Running {mesh_spec.name} "
            f"({mesh_spec.target_size_mm:.1f} mm)..."
        )

        result = (
            run_structural_convergence_case(
                design=BALL_001,
                mesh_spec=mesh_spec,
                load_case=(
                    BALL001_NOMINAL_PRESSURE
                ),
                material=(
                    BALL001_VERIFICATION_MATERIAL
                ),
                output_directory=(
                    OUTPUT_DIRECTORY
                ),
            )
        )

        results.append(
            result
        )

    print()
    print(
        "BALL 001 — STRUCTURAL MESH "
        "CONVERGENCE"
    )
    print("=" * 122)

    print(
        f"{'Mesh':<9}"
        f"{'Size':>10}"
        f"{'Triangles':>12}"
        f"{'Radial u':>14}"
        f"{'u error':>11}"
        f"{'Δu':>10}"
        f"{'Tangential S':>16}"
        f"{'S error':>11}"
        f"{'ΔS':>10}"
        f"{'Outward':>11}"
    )

    print("-" * 122)

    previous_result = None

    for result in results:
        if previous_result is None:
            displacement_change = None
            stress_change = None

        else:
            displacement_change = (
                relative_change_percent(
                    result.mean_radial_displacement_mm,
                    previous_result.mean_radial_displacement_mm,
                )
            )

            stress_change = (
                relative_change_percent(
                    result.mean_tangential_stress_n_mm2,
                    previous_result.mean_tangential_stress_n_mm2,
                )
            )

        displacement_change_text = (
            "—"
            if displacement_change is None
            else f"{displacement_change:.3f} %"
        )

        stress_change_text = (
            "—"
            if stress_change is None
            else f"{stress_change:.3f} %"
        )

        print(
            f"{result.mesh_name:<9}"
            f"{result.target_size_mm:>7.1f} mm"
            f"{result.triangle_count:>12}"
            f"{result.mean_radial_displacement_mm:>11.6f} mm"
            f"{result.displacement_error_percent:>8.3f} %"
            f"{displacement_change_text:>10}"
            f"{result.mean_tangential_stress_n_mm2:>13.6f}"
            f"{result.stress_error_percent:>8.3f} %"
            f"{stress_change_text:>10}"
            f"{100.0 * result.outward_node_fraction:>8.2f} %"
        )

        previous_result = result

    print()
    print(
        "Δu and ΔS compare each mesh with the "
        "next-coarser mesh."
    )

    print(
        "Analytical error compares the FEA result "
        "with the spherical-shell verification target."
    )

    print(
        "This study verifies numerical convergence "
        "of the artificial shell model."
    )

    print(
        "It is not a prediction of real volleyball "
        "material behavior."
    )


if __name__ == "__main__":
    main()