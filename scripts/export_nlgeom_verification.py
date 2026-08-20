from pathlib import Path

from ball001.geometric_nonlinearity import (
    export_nlgeom_deck,
)

LINEAR_DECK_PATH = Path(
    "exports/fea/ball001_shell_verify.inp"
)

NONLINEAR_DECK_PATH = Path(
    "exports/fea/nonlinear/"
    "ball001_shell_verify_nlgeom.inp"
)


def main() -> None:
    result = export_nlgeom_deck(
        linear_deck_path=LINEAR_DECK_PATH,
        nonlinear_deck_path=NONLINEAR_DECK_PATH,
    )

    print(
        "BALL 001 — GEOMETRIC NONLINEARITY "
        "VERIFICATION DECK"
    )
    print("=" * 72)

    print(
        f"Linear source deck:     "
        f"{result.source_path}"
    )

    print(
        f"Nonlinear output deck:  "
        f"{result.output_path}"
    )

    print(
        f"NLGEOM step count:      "
        f"{result.nonlinear_step_count}"
    )

    print()
    print(
        "Controlled change:"
    )

    print(
        "  *STEP  →  *STEP,NLGEOM"
    )

    print()
    print(
        "Geometry, mesh, material, thickness, "
        "pressure, constraints, and output "
        "requests are otherwise preserved."
    )

    print()
    print(
        "Evidence status:"
    )

    print(
        "  Artificial verification material: "
        "PENDING"
    )

    print(
        "  Solver result: SIMULATED"
    )


if __name__ == "__main__":
    main()