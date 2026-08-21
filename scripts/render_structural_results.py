from pathlib import Path

import numpy as np
import pyvista as pv

INPUT_PATH = Path(
    "exports/visualization/"
    "ball001_structural_verification.vtp"
)

OUTPUT_DIRECTORY = Path(
    "exports/visualization/renders"
)

DEFORMATION_SCALE = 500.0


def save_undeformed_mesh(
    surface: pv.PolyData,
) -> None:
    plotter = pv.Plotter(
        off_screen=True
    )

    plotter.add_mesh(
        surface,
        show_edges=True,
    )

    plotter.add_text(
        "BALL 001 — Undeformed S3 shell mesh",
        font_size=12,
    )

    plotter.camera_position = "iso"

    plotter.show(
        screenshot=(
            OUTPUT_DIRECTORY
            / "01_undeformed_mesh.png"
        ),
        auto_close=True,
    )


def save_radial_displacement(
    surface: pv.PolyData,
) -> None:
    plotter = pv.Plotter(
        off_screen=True
    )

    plotter.add_mesh(
        surface,
        scalars=(
            "radial_displacement_mm"
        ),
        show_edges=False,
        scalar_bar_args={
            "title": (
                "Radial displacement [mm]"
            ),
        },
    )

    plotter.add_text(
        "BALL 001 — Radial displacement",
        font_size=12,
    )

    plotter.camera_position = "iso"

    plotter.show(
        screenshot=(
            OUTPUT_DIRECTORY
            / "02_radial_displacement.png"
        ),
        auto_close=True,
    )


def save_tangential_stress(
    surface: pv.PolyData,
) -> None:
    plotter = pv.Plotter(
        off_screen=True
    )

    plotter.add_mesh(
        surface,
        scalars=(
            "mean_tangential_stress_n_mm2"
        ),
        show_edges=False,
        scalar_bar_args={
            "title": (
                "Mean tangential stress "
                "[N/mm²]"
            ),
        },
    )

    plotter.add_text(
        "BALL 001 — Mean tangential stress",
        font_size=12,
    )

    plotter.camera_position = "iso"

    plotter.show(
        screenshot=(
            OUTPUT_DIRECTORY
            / "03_tangential_stress.png"
        ),
        auto_close=True,
    )


def save_deformed_shape(
    surface: pv.PolyData,
) -> None:
    displacement = np.asarray(
        surface.point_data[
            "displacement_mm"
        ]
    )

    deformed = surface.copy(
        deep=True
    )

    deformed.points = (
        np.asarray(
            surface.points
        )
        + displacement
        * DEFORMATION_SCALE
    )

    plotter = pv.Plotter(
        off_screen=True
    )

    plotter.add_mesh(
        surface,
        show_edges=True,
        opacity=0.20,
    )

    plotter.add_mesh(
        deformed,
        scalars=(
            "radial_displacement_mm"
        ),
        show_edges=False,
        scalar_bar_args={
            "title": (
                "Radial displacement [mm]"
            ),
        },
    )

    plotter.add_text(
        "BALL 001 — Deformed shell "
        f"({DEFORMATION_SCALE:.0f}× scale)",
        font_size=12,
    )

    plotter.camera_position = "iso"

    plotter.show(
        screenshot=(
            OUTPUT_DIRECTORY
            / "04_deformed_shape.png"
        ),
        auto_close=True,
    )


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Structural VTK dataset does not exist: "
            f"{INPUT_PATH}"
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    surface = pv.read(
        INPUT_PATH
    )

    print(
        "BALL 001 — STRUCTURAL "
        "RESULT RENDERING"
    )
    print("=" * 72)

    print(
        f"Input:        {INPUT_PATH}"
    )

    print(
        f"Points:       {surface.n_points}"
    )

    print(
        f"Triangles:    {surface.n_cells}"
    )

    print(
        f"Deformation:  "
        f"{DEFORMATION_SCALE:.0f}×"
    )

    print()

    save_undeformed_mesh(
        surface
    )

    save_radial_displacement(
        surface
    )

    save_tangential_stress(
        surface
    )

    save_deformed_shape(
        surface
    )

    print(
        "Created:"
    )

    for path in sorted(
        OUTPUT_DIRECTORY.glob(
            "*.png"
        )
    ):
        print(
            f"  {path}"
        )

    print()
    print(
        "Field values are SIMULATED."
    )

    print(
        "Deformation scale is visual "
        "magnification only."
    )


if __name__ == "__main__":
    main()
