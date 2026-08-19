from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
    calculate_effective_shell_verification,
)
from ball001.pressure import (
    BALL001_PRESSURE_CASES,
)


def main() -> None:
    material = (
        BALL001_VERIFICATION_MATERIAL
    )

    print(
        "BALL 001 — EFFECTIVE SHELL "
        "VERIFICATION TARGETS"
    )
    print("=" * 100)

    print(
        f"Verification material E: "
        f"{material.youngs_modulus_pa / 1_000_000_000:.3f} GPa"
    )

    print(
        f"Verification material ν: "
        f"{material.poisson_ratio:.3f}"
    )

    print(
        f"Evidence: {material.evidence}"
    )

    print()

    print(
        f"{'Case':<22}"
        f"{'Pressure':>13}"
        f"{'Thickness':>13}"
        f"{'Membrane N':>15}"
        f"{'Stress':>14}"
        f"{'Radial u':>14}"
    )

    print("-" * 100)

    for load_case in BALL001_PRESSURE_CASES:
        result = (
            calculate_effective_shell_verification(
                BALL_001,
                load_case,
                material,
            )
        )

        print(
            f"{result.load_case_name:<22}"
            f"{result.pressure_pa / 1000.0:>10.3f} kPa"
            f"{result.wall_thickness_m * 1000.0:>10.3f} mm"
            f"{result.membrane_resultant_n_per_m:>11.1f} N/m"
            f"{result.membrane_stress_pa / 1000.0:>11.1f} kPa"
            f"{result.radial_expansion_m * 1000.0:>11.4f} mm"
        )

    print()

    print(
        "The elastic properties above are artificial "
        "solver-verification values."
    )

    print(
        "They are not measured or benchmark properties "
        "of Mikasa V200W or BALL 001."
    )

    print(
        "Pressure equilibrium and displacement provide "
        "analytical targets for the first FEA solve."
    )


if __name__ == "__main__":
    main()