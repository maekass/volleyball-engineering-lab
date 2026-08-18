from ball001.design import BALL_001
from ball001.sensitivity import MM_PER_M, run_seam_sensitivity

WIDTHS_MM = (
    1.5,
    2.5,
    3.5,
)

DEPTHS_MM = (
    0.2,
    0.4,
    0.6,
)


def main() -> None:
    results = run_seam_sensitivity(
        BALL_001,
        widths_mm=WIDTHS_MM,
        depths_mm=DEPTHS_MM,
    )

    print("BALL 001 — SEAM SENSITIVITY STUDY")
    print("=" * 72)
    print(
        f"{'Width':>8}"
        f"{'Depth':>10}"
        f"{'Mass removed':>18}"
        f"{'Adjusted mass':>18}"
        f"{'Target delta':>16}"
    )
    print("-" * 72)

    for result in results:
        width_mm = result.width_m * MM_PER_M
        depth_mm = result.depth_m * MM_PER_M

        print(
            f"{width_mm:8.2f}"
            f"{depth_mm:10.2f}"
            f"{result.removed_mass_kg * 1000:18.3f}"
            f"{result.adjusted_mass_kg * 1000:18.2f}"
            f"{result.target_delta_kg * 1000:16.2f}"
        )

    print()
    print("Units: width/depth = mm; masses = g")
    print("Evidence class: PENDING computational design inputs.")
    print("Results are CAD-derived estimates, not measured values.")


if __name__ == "__main__":
    main()