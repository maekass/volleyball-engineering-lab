from pathlib import Path

from ball001.calculix_results import (
    analyze_calculix_verification,
)
from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
)
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
)

MESH_PATH = Path(
    "exports/fea/ball001_medium_ccx.msh"
)

FRD_PATH = Path(
    "exports/fea/ball001_shell_verify.frd"
)


def main() -> None:
    result = (
        analyze_calculix_verification(
            mesh_path=MESH_PATH,
            frd_path=FRD_PATH,
            design=BALL_001,
            load_case=(
                BALL001_NOMINAL_PRESSURE
            ),
            material=(
                BALL001_VERIFICATION_MATERIAL
            ),
        )
    )

    print(
        "BALL 001 — CALCULIX "
        "VERIFICATION RESULTS"
    )
    print("=" * 78)

    print(
        f"Displacement nodes:      "
        f"{result.displacement_node_count}"
    )

    print(
        f"Stress nodes:            "
        f"{result.stress_node_count}"
    )

    print()

    print("RADIAL DISPLACEMENT")
    print("-" * 78)

    print(
        f"Analytical target:       "
        f"{result.analytical_radial_displacement_mm:.6f} mm"
    )

    print(
        f"FEA mean:                "
        f"{result.mean_radial_displacement_mm:.6f} mm"
    )

    print(
        f"FEA standard deviation:  "
        f"{result.radial_displacement_std_mm:.6f} mm"
    )

    print(
        f"FEA minimum:             "
        f"{result.min_radial_displacement_mm:.6f} mm"
    )

    print(
        f"FEA maximum:             "
        f"{result.max_radial_displacement_mm:.6f} mm"
    )

    print(
        f"Outward nodes:           "
        f"{100.0 * result.outward_node_fraction:.2f} %"
    )

    print(
        f"Displacement error:      "
        f"{result.displacement_error_percent:.3f} %"
    )

    print(
        f"Max tangential motion:   "
        f"{result.max_tangential_displacement_mm:.6f} mm"
    )

    print()
    print("MEMBRANE STRESS")
    print("-" * 78)

    print(
        f"Analytical target:       "
        f"{result.analytical_membrane_stress_n_mm2:.6f} N/mm²"
    )

    print(
        f"FEA mean tangential:     "
        f"{result.mean_tangential_stress_n_mm2:.6f} N/mm²"
    )

    print(
        f"FEA standard deviation:  "
        f"{result.tangential_stress_std_n_mm2:.6f} N/mm²"
    )

    print(
        f"Mean radial stress:      "
        f"{result.mean_radial_stress_n_mm2:.6f} N/mm²"
    )

    print(
        f"Stress error:            "
        f"{result.stress_error_percent:.3f} %"
    )

    print()
    print(
        "Positive radial displacement means "
        "the pressure load expands outward."
    )

    print(
        "These values verify the artificial "
        "numerical shell model; they are not "
        "predictions of real volleyball behavior."
    )


if __name__ == "__main__":
    main()