from pathlib import Path

from ball001.pressure_envelope import (
    build_pressure_envelope_cases,
    build_pressure_envelope_deck,
)

SOURCE_DECK_PATH = Path(
    "exports/fea/ball001_shell_verify.inp"
)

OUTPUT_DIRECTORY = Path(
    "exports/fea/pressure_envelope"
)


def main() -> None:
    if not SOURCE_DECK_PATH.exists():
        raise FileNotFoundError(
            "Verified S3 source deck does not exist: "
            f"{SOURCE_DECK_PATH}"
        )

    source_deck_text = (
        SOURCE_DECK_PATH.read_text()
    )

    cases = (
        build_pressure_envelope_cases()
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "BALL 001 — PRESSURE ENVELOPE "
        "DECK EXPORT"
    )
    print("=" * 92)

    print(
        f"Source deck:      "
        f"{SOURCE_DECK_PATH}"
    )

    print(
        f"Output directory: "
        f"{OUTPUT_DIRECTORY}"
    )

    print(
        f"Cases:            "
        f"{len(cases)}"
    )

    print()

    print(
        f"{'Case':<42}"
        f"{'Pressure [kPa]':>18}"
        f"{'E [MPa]':>12}"
        f"{'Geometry':>14}"
    )

    print("-" * 92)

    for case in cases:
        deck_text = (
            build_pressure_envelope_deck(
                source_deck_text,
                case,
            )
        )

        output_path = (
            OUTPUT_DIRECTORY
            / f"{case.solver_name}.inp"
        )

        output_path.write_text(
            deck_text
        )

        print(
            f"{case.solver_name:<42}"
            f"{case.pressure_level.pressure_kpa:>18.3f}"
            f"{case.youngs_modulus_mpa:>12.1f}"
            f"{case.geometry_mode.value:>14}"
        )

    print()
    print(
        "Controlled quantities:"
    )

    print(
        "  mesh / thickness / constraints / "
        "effective modulus / Poisson ratio"
    )

    print()
    print(
        "Sweep variable:"
    )

    print(
        "  pressure across the BALL 001 "
        "benchmark envelope"
    )

    print()
    print(
        "Geometry formulations:"
    )

    print(
        "  LINEAR and NLGEOM at each pressure"
    )

    print()
    print(
        "Effective modulus remains a PENDING "
        "sensitivity anchor."
    )

    print(
        "Generated decks are numerical "
        "verification artifacts."
    )


if __name__ == "__main__":
    main()