from pathlib import Path

from ball001.design import BALL_001
from ball001.mesh import (
    BALL001_MESH_SPECS,
    generate_surface_mesh,
)

EXPORT_DIRECTORY = Path(
    "exports/mesh"
)


def main() -> None:
    print(
        "BALL 001 — BASELINE SURFACE MESH STUDY"
    )
    print("=" * 78)

    print(
        f"{'Mesh':<12}"
        f"{'Target size':>14}"
        f"{'Nodes':>12}"
        f"{'Triangles':>14}"
        f"{'R min':>13}"
        f"{'R max':>13}"
    )

    print("-" * 78)

    for spec in BALL001_MESH_SPECS:
        output_path = (
            EXPORT_DIRECTORY
            / f"ball001_{spec.name}.msh"
        )

        result = generate_surface_mesh(
            BALL_001,
            spec,
            output_path=output_path,
        )

        print(
            f"{result.name:<12}"
            f"{result.target_size_mm:>11.1f} mm"
            f"{result.node_count:>12}"
            f"{result.triangle_count:>14}"
            f"{result.min_node_radius_mm:>10.3f} mm"
            f"{result.max_node_radius_mm:>10.3f} mm"
        )

    print()
    print(
        "Mesh sizes are computational convergence-study "
        "parameters, not physical BALL 001 dimensions."
    )

    print(
        "Meshes represent the nominal smooth spherical "
        "surface before panel-boundary effects are introduced."
    )

    print(
        f"Exports written to: {EXPORT_DIRECTORY}"
    )


if __name__ == "__main__":
    main()