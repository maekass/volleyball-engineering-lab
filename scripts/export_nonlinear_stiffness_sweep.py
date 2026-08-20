from pathlib import Path

from ball001.nonlinear_stiffness_sweep import (
    build_stiffness_sweep_cases,
    build_stiffness_sweep_deck,
)

SOURCE_DECK_PATH = Path(
    "exports/fea/ball001_shell_verify.inp"
)

OUTPUT_DIRECTORY = Path(
    "exports/fea/nonlinear_stiffness"
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
        build_stiffness_sweep_cases()
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "BALL 001 — NONLINEAR "
        "STIFFNESS SWEEP"
    )
    print("=" * 88)

    print(
        f"Source deck:     "
        f"{SOURCE_DECK_PATH}"
    )

    print(
        f"Output directory:"
        f" {OUTPUT_DIRECTORY}"
    )

    print(
        f"Cases:           "
        f"{len(cases)}"
    )

    print()

    print(
        f"{'Case':<38}"
        f"{'E [MPa]':>12}"
        f"{'ν':>10}"
        f"{'Geometry':>14}"
    )

    print("-" * 88)

    for case in cases:
        deck_text = (
            build_stiffness_sweep_deck(
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
            f"{case.solver_name:<38}"
            f"{case.youngs_modulus_mpa:>12.1f}"
            f"{case.poisson_ratio:>10.3f}"
            f"{case.geometry_mode.value:>14}"
        )

    print()
    print(
        "Controlled quantities:"
    )

    print(
        "  geometry / mesh / thickness / "
        "pressure / constraints"
    )

    print()
    print(
        "Sweep variables:"
    )

    print(
        "  effective Young's modulus"
    )

    print(
        "  linear geometry vs NLGEOM"
    )

    print()
    print(
        "NLGEOM increment controls:"
    )

    print(
        "  initial: 0.05"
    )

    print(
        "  minimum: 1.0e-5"
    )

    print(
        "  maximum: 0.10"
    )

    print()
    print(
        "Material stiffness values are "
        "PENDING sensitivity anchors, "
        "not measured volleyball properties."
    )


if __name__ == "__main__":
    main()