from pathlib import Path

from ball001.calculix_results import (
    analyze_calculix_verification,
)
from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
)
from ball001.formulation_comparison import (
    compare_shell_formulations,
)
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
)

S3_MESH_PATH = Path(
    "exports/fea/ball001_medium_ccx.msh"
)

S3_FRD_PATH = Path(
    "exports/fea/ball001_shell_verify.frd"
)

S6_MESH_PATH = Path(
    "exports/fea/formulation/ball001_medium_s6.msh"
)

S6_FRD_PATH = Path(
    "exports/fea/formulation/ball001_s6_verify.frd"
)


def main() -> None:
    s3 = analyze_calculix_verification(
        mesh_path=S3_MESH_PATH,
        frd_path=S3_FRD_PATH,
        design=BALL_001,
        load_case=(
            BALL001_NOMINAL_PRESSURE
        ),
        material=(
            BALL001_VERIFICATION_MATERIAL
        ),
    )

    s6 = analyze_calculix_verification(
        mesh_path=S6_MESH_PATH,
        frd_path=S6_FRD_PATH,
        design=BALL_001,
        load_case=(
            BALL001_NOMINAL_PRESSURE
        ),
        material=(
            BALL001_VERIFICATION_MATERIAL
        ),
    )

    comparison = (
        compare_shell_formulations(
            s3,
            s6,
        )
    )

    print(
        "BALL 001 — S3 / S6 "
        "SHELL FORMULATION COMPARISON"
    )
    print("=" * 92)

    print(
        f"{'Metric':<34}"
        f"{'S3':>18}"
        f"{'S6':>18}"
        f"{'S3 → S6':>18}"
    )

    print("-" * 92)

    print(
        f"{'Result nodes':<34}"
        f"{s3.displacement_node_count:>18}"
        f"{s6.displacement_node_count:>18}"
        f"{'—':>18}"
    )

    print(
        f"{'Mean radial u [mm]':<34}"
        f"{comparison.s3_radial_displacement_mm:>18.6f}"
        f"{comparison.s6_radial_displacement_mm:>18.6f}"
        f"{comparison.displacement_change_percent:>15.3f} %"
    )

    print(
        f"{'Analytical u error':<34}"
        f"{comparison.s3_displacement_error_percent:>15.3f} %"
        f"{comparison.s6_displacement_error_percent:>15.3f} %"
        f"{'—':>18}"
    )

    print(
        f"{'Mean tangential S [N/mm²]':<34}"
        f"{comparison.s3_tangential_stress_n_mm2:>18.6f}"
        f"{comparison.s6_tangential_stress_n_mm2:>18.6f}"
        f"{comparison.stress_change_percent:>15.3f} %"
    )

    print(
        f"{'Analytical S error':<34}"
        f"{comparison.s3_stress_error_percent:>15.3f} %"
        f"{comparison.s6_stress_error_percent:>15.3f} %"
        f"{'—':>18}"
    )

    print(
        f"{'Outward nodes':<34}"
        f"{100.0 * comparison.s3_outward_node_fraction:>15.2f} %"
        f"{100.0 * comparison.s6_outward_node_fraction:>15.2f} %"
        f"{'—':>18}"
    )

    print(
        f"{'Max tangential u [mm]':<34}"
        f"{comparison.s3_max_tangential_displacement_mm:>18.6f}"
        f"{comparison.s6_max_tangential_displacement_mm:>18.6f}"
        f"{'—':>18}"
    )

    print()
    print(
        "Both formulations use the same nominal "
        "BALL 001 geometry, pressure, thickness, "
        "and artificial verification material."
    )

    print(
        "The S3-to-S6 percentage columns measure "
        "formulation sensitivity, not physical "
        "volleyball performance."
    )

    print(
        "Analytical errors are measured against "
        "the thin spherical membrane benchmark."
    )


if __name__ == "__main__":
    main()