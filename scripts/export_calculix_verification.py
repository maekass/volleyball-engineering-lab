from pathlib import Path

from ball001.calculix_deck import (
    export_calculix_verification_deck,
)
from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
    total_wall_thickness_m,
)
from ball001.mesh import (
    MEDIUM_MESH,
    generate_surface_mesh,
)
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
)

EXPORT_DIRECTORY = Path(
    "exports/fea"
)

MESH_PATH = (
    EXPORT_DIRECTORY
    / "ball001_medium_ccx.msh"
)

DECK_PATH = (
    EXPORT_DIRECTORY
    / "ball001_shell_verify.inp"
)


def main() -> None:
    mesh_summary = generate_surface_mesh(
        BALL_001,
        MEDIUM_MESH,
        output_path=MESH_PATH,
    )

    deck_summary = (
        export_calculix_verification_deck(
            mesh_path=MESH_PATH,
            deck_path=DECK_PATH,
            load_case=(
                BALL001_NOMINAL_PRESSURE
            ),
            material=(
                BALL001_VERIFICATION_MATERIAL
            ),
            shell_thickness_m=(
                total_wall_thickness_m(
                    BALL_001
                )
            ),
        )
    )

    print(
        "BALL 001 — CALCULIX VERIFICATION DECK"
    )
    print("=" * 72)

    print(
        f"Mesh target size:      "
        f"{mesh_summary.target_size_mm:.1f} mm"
    )

    print(
        f"Nodes:                 "
        f"{deck_summary.node_count}"
    )

    print(
        f"S3 triangles:          "
        f"{deck_summary.triangle_count}"
    )

    print(
        f"Triangles reoriented:  "
        f"{deck_summary.flipped_triangle_count}"
    )

    print(
        f"PIN_X node:            "
        f"{deck_summary.pin_x_tag}"
    )

    print(
        f"PIN_Y node:            "
        f"{deck_summary.pin_y_tag}"
    )

    print(
        f"PIN_Z node:            "
        f"{deck_summary.pin_z_tag}"
    )

    print(
        f"Applied pressure:      "
        f"{deck_summary.applied_pressure_n_mm2:.6f} "
        "N/mm²"
    )

    print(
        f"Deck:                  "
        f"{deck_summary.deck_path}"
    )

    print()

    print(
        "Pressure sign remains a solver-verification "
        "check: accepted results must expand radially outward."
    )


if __name__ == "__main__":
    main()