from ball001.panel_candidates import (
    BALL001_PANEL_CANDIDATES,
)


def main() -> None:
    print("BALL 001 — CANDIDATE PANEL ARCHITECTURES")
    print("=" * 78)

    print(
        f"{'Candidate':<36}"
        f"{'Regions':>10}"
        f"{'Meridians':>12}"
        f"{'Zones':>8}"
        f"{'Evidence':>12}"
    )

    print("-" * 78)

    for candidate in BALL001_PANEL_CANDIDATES:
        print(
            f"{candidate.name:<36}"
            f"{candidate.region_count:>10}"
            f"{candidate.meridian_count:>12}"
            f"{candidate.zone_count:>8}"
            f"{candidate.evidence:>12}"
        )

    print()
    print(
        "These are computational BALL 001 architecture candidates, "
        "not measured commercial-ball geometries."
    )
    print(
        "The 18-region candidate does not imply reproduction of "
        "Mikasa V200W panel geometry."
    )


if __name__ == "__main__":
    main()