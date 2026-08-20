from pathlib import Path

from ball001.design import BALL_001
from ball001.mesh import (
    MEDIUM_MESH,
    generate_surface_mesh,
)
from ball001.quadratic_mesh import (
    generate_quadratic_surface_mesh,
)

EXPORT_DIRECTORY = Path(
    "exports/mesh"
)

QUADRATIC_MESH_PATH = (
    EXPORT_DIRECTORY
    / "ball001_medium_quadratic.msh"
)


def main() -> None:
    linear = generate_surface_mesh(
        BALL_001,
        MEDIUM_MESH,
    )

    quadratic = (
        generate_quadratic_surface_mesh(
            BALL_001,
            MEDIUM_MESH,
            output_path=(
                QUADRATIC_MESH_PATH
            ),
        )
    )

    print(
        "BALL 001 — LINEAR / QUADRATIC "
        "SURFACE MESH CHECK"
    )
    print("=" * 78)

    print(
        f"{'Formulation':<18}"
        f"{'Nodes':>12}"
        f"{'Triangles':>14}"
        f"{'Nodes / tri':>14}"
        f"{'R min':>12}"
        f"{'R max':>12}"
    )

    print("-" * 78)

    print(
        f"{'linear':<18}"
        f"{linear.node_count:>12}"
        f"{linear.triangle_count:>14}"
        f"{3:>14}"
        f"{linear.min_node_radius_mm:>9.3f} mm"
        f"{linear.max_node_radius_mm:>9.3f} mm"
    )

    print(
        f"{'quadratic':<18}"
        f"{quadratic.node_count:>12}"
        f"{quadratic.triangle_count:>14}"
        f"{quadratic.nodes_per_triangle:>14}"
        f"{quadratic.min_node_radius_mm:>9.3f} mm"
        f"{quadratic.max_node_radius_mm:>9.3f} mm"
    )

    print()
    print(
        "The quadratic mesh preserves the same "
        "surface-element topology while adding midside nodes."
    )

    print(
        "All nodes should remain on the nominal "
        "BALL 001 spherical surface."
    )

    print(
        "This is mesh-formulation verification, "
        "not a physical volleyball result."
    )

    print(
        f"Export: {QUADRATIC_MESH_PATH}"
    )


if __name__ == "__main__":
    main()