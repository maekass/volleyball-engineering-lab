from pathlib import Path

from ball001.design import BALL_001
from ball001.fea_mesh import (
    SURFACE_MESH_SPECS,
    generate_surface_mesh,
)

EXPORT_DIRECTORY = Path(
    "exports/mesh"
)


def main() -> None:
    print(
        "BALL 001 — FEA SURFACE MESH REPORT"
    )
    print("=" * 72)

    print(
        f"{'Mesh':<12}"
        f"{'Target size':>16}"
        f"{'Nodes':>14}"
        f"{'Triangles':>16}"
    )

    print("-" * 72)

    for spec in SURFACE_MESH_SPECS:
        output_path = (
            EXPORT_DIRECTORY
            / f"ball001_surface_{spec.label}.msh"
        )

        result = generate_surface_mesh(
            BALL_001,
            spec,
            output_path=output_path,
        )

        print(
            f"{result.label:<12}"
            f"{result.characteristic_length_mm:>13.2f} mm"
            f"{result.node_count:>14}"
            f"{result.triangle_count:>16}"
        )

    print()
    print(
        "Geometry: BALL 001 nominal 660 mm circumference sphere."
    )
    print(
        "Meshes are numerical discretizations, not physical "
        "reinforcement mesh."
    )
    print(
        "No structural response has been simulated yet."
    )


if __name__ == "__main__":
    main()