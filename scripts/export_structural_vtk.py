from pathlib import Path

import numpy as np

from ball001.structural_visualization import (
    export_structural_vtp,
)

MESH_PATH = Path(
    "exports/fea/ball001_medium_ccx.msh"
)

FRD_PATH = Path(
    "exports/fea/ball001_shell_verify.frd"
)

OUTPUT_PATH = Path(
    "exports/visualization/"
    "ball001_structural_verification.vtp"
)


def main() -> None:
    surface = export_structural_vtp(
        mesh_path=MESH_PATH,
        frd_path=FRD_PATH,
        output_path=OUTPUT_PATH,
    )

    radial = surface.point_data[
        "radial_displacement_mm"
    ]

    stress = surface.point_data[
        "mean_tangential_stress_n_mm2"
    ]

    print(
        "BALL 001 — STRUCTURAL "
        "VTK EXPORT"
    )
    print("=" * 72)

    print(
        f"Points:       "
        f"{surface.n_points}"
    )

    print(
        f"Triangles:    "
        f"{surface.n_cells}"
    )

    print(
        f"Output:       "
        f"{OUTPUT_PATH}"
    )

    print()

    print(
        "Radial displacement [mm]"
    )

    print(
        f"  min:        "
        f"{np.nanmin(radial):.6f}"
    )

    print(
        f"  mean:       "
        f"{np.nanmean(radial):.6f}"
    )

    print(
        f"  max:        "
        f"{np.nanmax(radial):.6f}"
    )

    print()

    print(
        "Mean tangential stress "
        "[N/mm²]"
    )

    print(
        f"  min:        "
        f"{np.nanmin(stress):.6f}"
    )

    print(
        f"  mean:       "
        f"{np.nanmean(stress):.6f}"
    )

    print(
        f"  max:        "
        f"{np.nanmax(stress):.6f}"
    )

    print()
    print(
        "This is a SIMULATED "
        "verification dataset."
    )


if __name__ == "__main__":
    main()
