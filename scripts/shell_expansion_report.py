from ball001.design import BALL_001
from ball001.shell_expansion import (
    calculate_stiffness_sensitivity,
)


def main() -> None:
    results = calculate_stiffness_sensitivity(
        BALL_001
    )

    print(
        "BALL 001 — EFFECTIVE SHELL "
        "STIFFNESS SENSITIVITY"
    )
    print("=" * 86)

    print(
        f"{'Case':<18}"
        f"{'E':>12}"
        f"{'nu':>8}"
        f"{'Strain':>12}"
        f"{'Radial u':>14}"
        f"{'Delta C':>14}"
    )

    print("-" * 86)

    for result in results:
        print(
            f"{result.material_name:<18}"
            f"{result.youngs_modulus_pa / 1_000_000:>9.1f} MPa"
            f"{result.poisson_ratio:>8.2f}"
            f"{result.biaxial_strain * 100:>10.3f} %"
            f"{result.radial_displacement_m * 1000:>11.3f} mm"
            f"{result.circumference_change_m * 1000:>11.3f} mm"
        )

    print()
    print(
        "Moduli are PENDING computational sensitivity "
        "anchors, not measured volleyball properties."
    )
    print(
        "Results use a linear thin-spherical-membrane "
        "analytical model."
    )
    print(
        "Large predicted strains indicate where a later "
        "geometrically/materially nonlinear model may be needed."
    )


if __name__ == "__main__":
    main()