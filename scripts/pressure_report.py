from ball001.design import BALL_001
from ball001.pressure import (
    BALL001_PRESSURE_CASES,
    calculate_pressure_benchmark,
)


def main() -> None:
    print(
        "BALL 001 — INFLATION PRESSURE BENCHMARK"
    )
    print("=" * 86)

    print(
        f"{'Case':<22}"
        f"{'Pressure':>14}"
        f"{'Membrane N':>18}"
        f"{'Hemisphere F':>17}"
        f"{'Balance F':>15}"
    )

    print("-" * 86)

    for case in BALL001_PRESSURE_CASES:
        result = calculate_pressure_benchmark(
            BALL_001,
            case,
        )

        print(
            f"{result.name:<22}"
            f"{result.pressure_pa / 1000.0:>11.3f} kPa"
            f"{result.membrane_resultant_n_per_m:>14.1f} N/m"
            f"{result.hemisphere_pressure_resultant_n:>13.2f} N"
            f"{result.great_circle_membrane_balance_n:>11.2f} N"
        )

    print()
    print(
        "Membrane resultant follows the analytical spherical "
        "pressure-vessel relation N = p r / 2."
    )

    print(
        "The nominal case is a TARGET selected within the "
        "volleyball benchmark pressure range."
    )

    print(
        "These values are analytical verification targets, "
        "not measured BALL 001 results."
    )


if __name__ == "__main__":
    main()