from pathlib import Path

from ball001.calculix_results import (
    analyze_calculix_verification,
)
from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
)
from ball001.geometric_nonlinearity_comparison import (
    compare_geometric_nonlinearity,
)
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
)

MESH_PATH = Path(
    "exports/fea/ball001_medium_ccx.msh"
)

LINEAR_FRD_PATH = Path(
    "exports/fea/ball001_shell_verify.frd"
)

NONLINEAR_FRD_PATH = Path(
    "exports/fea/nonlinear/"
    "ball001_shell_verify_nlgeom.frd"
)


def main() -> None:
    linear = analyze_calculix_verification(
        mesh_path=MESH_PATH,
        frd_path=LINEAR_FRD_PATH,
        design=BALL_001,
        load_case=(
            BALL001_NOMINAL_PRESSURE
        ),
        material=(
            BALL001_VERIFICATION_MATERIAL
        ),
    )

    nonlinear = analyze_calculix_verification(
        mesh_path=MESH_PATH,
        frd_path=NONLINEAR_FRD_PATH,
        design=BALL_001,
        load_case=(
            BALL001_NOMINAL_PRESSURE
        ),
        material=(
            BALL001_VERIFICATION_MATERIAL
        ),
    )

    comparison = (
        compare_geometric_nonlinearity(
            linear,
            nonlinear,
        )
    )

    print(
        "BALL 001 — LINEAR / NLGEOM "
        "SHELL COMPARISON"
    )
    print("=" * 92)

    print(
        f"{'Metric':<34}"
        f"{'Linear':>18}"
        f"{'NLGEOM':>18}"
        f"{'Change':>18}"
    )

    print("-" * 92)

    print(
        f"{'Result nodes':<34}"
        f"{linear.displacement_node_count:>18}"
        f"{nonlinear.displacement_node_count:>18}"
        f"{'—':>18}"
    )

    print(
        f"{'Mean radial u [mm]':<34}"
        f"{comparison.linear_radial_displacement_mm:>18.6f}"
        f"{comparison.nonlinear_radial_displacement_mm:>18.6f}"
        f"{comparison.displacement_change_percent:>15.3f} %"
    )

    print(
        f"{'Analytical u error':<34}"
        f"{comparison.linear_displacement_error_percent:>15.3f} %"
        f"{comparison.nonlinear_displacement_error_percent:>15.3f} %"
        f"{'—':>18}"
    )

    print(
        f"{'Mean tangential S [N/mm²]':<34}"
        f"{comparison.linear_tangential_stress_n_mm2:>18.6f}"
        f"{comparison.nonlinear_tangential_stress_n_mm2:>18.6f}"
        f"{comparison.stress_change_percent:>15.3f} %"
    )

    print(
        f"{'Analytical S error':<34}"
        f"{comparison.linear_stress_error_percent:>15.3f} %"
        f"{comparison.nonlinear_stress_error_percent:>15.3f} %"
        f"{'—':>18}"
    )

    print(
        f"{'Outward nodes':<34}"
        f"{100.0 * comparison.linear_outward_node_fraction:>15.2f} %"
        f"{100.0 * comparison.nonlinear_outward_node_fraction:>15.2f} %"
        f"{'—':>18}"
    )

    print(
        f"{'Max tangential u [mm]':<34}"
        f"{comparison.linear_max_tangential_displacement_mm:>18.6f}"
        f"{comparison.nonlinear_max_tangential_displacement_mm:>18.6f}"
        f"{'—':>18}"
    )

    print()
    print(
        "Both models use the same S3 mesh, "
        "nominal pressure, thickness, constraints, "
        "and artificial verification material."
    )

    print(
        "The controlled numerical change is "
        "small-displacement geometry versus NLGEOM."
    )

    print(
        "These results verify solver behavior; "
        "they are not measured volleyball properties."
    )


if __name__ == "__main__":
    main()