from ball001.design import BALL_001
from ball001.panel_candidate_metrics import (
    calculate_all_candidate_metrics,
)


def main() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    print(
        "BALL 001 — PANEL ARCHITECTURE METRICS"
    )
    print("=" * 104)

    print(
        f"{'Candidate':<34}"
        f"{'Regions':>9}"
        f"{'Guides':>9}"
        f"{'Boundary':>13}"
        f"{'L / Area':>14}"
        f"{'Mean Shared':>14}"
        f"{'Mean Area':>11}"
    )

    print("-" * 104)

    for result in results:
        print(
            f"{result.name:<34}"
            f"{result.region_count:>9}"
            f"{result.guide_count:>9}"
            f"{result.schematic_boundary_length_m:>10.3f} m"
            f"{result.boundary_length_per_area_m_m2:>11.2f} 1/m"
            f"{result.mean_shared_boundary_per_region_m:>11.3f} m"
            f"{result.mean_region_area_m2 * 1_000_000:>12.0f} mm²"
        )

    print()
    print(
        "Boundary lengths are schematic geometry metrics, "
        "not measured seam lengths."
    )

    print(
        "Guide-display offset is removed before length "
        "metrics are calculated."
    )

    print(
        "All candidate geometries remain PENDING "
        "computational design concepts."
    )


if __name__ == "__main__":
    main()