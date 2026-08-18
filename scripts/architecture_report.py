from ball001.architecture import CONTROL_TOPOLOGIES
from ball001.architecture_trade import calculate_architecture_trade_result
from ball001.design import BALL_001
from ball001.surface import BALL_001_SEAM


def main() -> None:
    print("BALL 001 — ARCHITECTURE TRADE STUDY")
    print("=" * 96)

    print(
        f"{'Architecture':<24}"
        f"{'Regions':>10}"
        f"{'Seam length':>15}"
        f"{'Mass removed':>16}"
        f"{'Adj. mass':>14}"
        f"{'Target delta':>15}"
    )

    print("-" * 96)

    for topology in CONTROL_TOPOLOGIES:
        result = calculate_architecture_trade_result(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )

        print(
            f"{result.name:<24}"
            f"{result.region_count:>10}"
            f"{result.total_seam_length_m:>14.3f} m"
            f"{result.removed_skin_mass_kg * 1000:>15.3f} g"
            f"{result.adjusted_mass_kg * 1000:>13.2f} g"
            f"{result.target_delta_kg * 1000:>14.2f} g"
        )

    print()
    print("Topology and seam dimensions are PENDING computational inputs.")
    print("Mass effects are CAD-derived estimates, not measured results.")


if __name__ == "__main__":
    main()