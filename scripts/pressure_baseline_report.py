from ball001.design import BALL_001
from ball001.pressure_baseline import (
    calculate_pressure_baseline,
)
from ball001.volleyball_benchmark import (
    FIVB_INDOOR_BALL,
)


def main() -> None:
    result = calculate_pressure_baseline(
        BALL_001
    )

    print(
        "BALL 001 — PRESSURE-ONLY "
        "STRUCTURAL BASELINE"
    )
    print("=" * 72)

    print(
        f"Radius:                    "
        f"{result.radius_m * 1000:.3f} mm"
    )

    print(
        f"Wall thickness:            "
        f"{result.wall_thickness_m * 1000:.3f} mm"
    )

    print(
        f"Thickness / radius:        "
        f"{result.thickness_to_radius_ratio:.5f}"
    )

    print()

    print(
        f"FIVB pressure range:       "
        f"{FIVB_INDOOR_BALL.internal_pressure_min_pa / 1000:.3f}"
        f"–"
        f"{FIVB_INDOOR_BALL.internal_pressure_max_pa / 1000:.3f}"
        f" kPa"
    )

    print(
        f"Nominal pressure:          "
        f"{result.pressure_pa / 1000:.3f} kPa"
    )

    print(
        f"Pressure evidence:         "
        f"{result.pressure_evidence}"
    )

    print()

    print(
        f"Membrane force resultant:  "
        f"{result.membrane_force_per_length_n_m:.3f} N/m"
    )

    print(
        f"Homogenized avg. stress:   "
        f"{result.homogenized_membrane_stress_pa / 1_000_000:.4f}"
        f" MPa"
    )

    print()

    print(
        f"Wall-thickness evidence:   "
        f"{result.wall_thickness_evidence}"
    )

    print()
    print(
        "The membrane result is an analytical "
        "pressure-only sanity check."
    )

    print(
        "It is not a measured V200W property and "
        "does not represent layer-by-layer stress."
    )

    print(
        "Its purpose is to provide an independent "
        "reference for later finite-element validation."
    )


if __name__ == "__main__":
    main()