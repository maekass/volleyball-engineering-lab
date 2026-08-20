from dataclasses import dataclass
from math import sqrt
from pathlib import Path

import gmsh

from ball001.cad import outer_radius_mm
from ball001.design import BallDesign
from ball001.mesh import SurfaceMeshSpec


@dataclass(frozen=True)
class QuadraticSurfaceMeshSummary:
    name: str
    target_size_mm: float
    node_count: int
    triangle_count: int
    nodes_per_triangle: int
    min_node_radius_mm: float
    max_node_radius_mm: float


def generate_quadratic_surface_mesh(
    design: BallDesign,
    spec: SurfaceMeshSpec,
    output_path: Path | None = None,
) -> QuadraticSurfaceMeshSummary:
    if spec.target_size_mm <= 0.0:
        raise ValueError(
            "Mesh target size must be positive."
        )

    radius_mm = outer_radius_mm(
        design
    )

    gmsh.initialize()

    try:
        gmsh.option.setNumber(
            "General.Terminal",
            0,
        )

        gmsh.model.add(
            f"{design.name}_{spec.name}_quadratic_surface_mesh"
        )

        gmsh.model.occ.addSphere(
            0.0,
            0.0,
            0.0,
            radius_mm,
        )

        gmsh.model.occ.synchronize()

        gmsh.option.setNumber(
            "Mesh.MeshSizeMin",
            spec.target_size_mm,
        )

        gmsh.option.setNumber(
            "Mesh.MeshSizeMax",
            spec.target_size_mm,
        )

        gmsh.option.setNumber(
            "Mesh.MeshSizeFromPoints",
            0,
        )

        gmsh.option.setNumber(
            "Mesh.MeshSizeFromCurvature",
            0,
        )

        gmsh.option.setNumber(
            "Mesh.MeshSizeExtendFromBoundary",
            0,
        )

        # Generate the same first-order surface topology
        # used by the S3 verification model.
        gmsh.model.mesh.generate(2)

        # Convert the mesh to second order.
        # Triangles now contain 3 corner nodes
        # plus 3 midside nodes.
        gmsh.model.mesh.setOrder(2)

        node_tags, node_coords, _ = (
            gmsh.model.mesh.getNodes()
        )

        triangle_type = (
            gmsh.model.mesh.getElementType(
                "triangle",
                2,
            )
        )

        (
            triangle_tags,
            triangle_node_tags,
        ) = gmsh.model.mesh.getElementsByType(
            triangle_type
        )

        if len(triangle_tags) == 0:
            raise ValueError(
                "Quadratic mesh contains no triangles."
            )

        nodes_per_triangle = (
            len(triangle_node_tags)
            // len(triangle_tags)
        )

        radii_mm = []

        for index in range(
            0,
            len(node_coords),
            3,
        ):
            x_mm = float(
                node_coords[index]
            )
            y_mm = float(
                node_coords[index + 1]
            )
            z_mm = float(
                node_coords[index + 2]
            )

            radii_mm.append(
                sqrt(
                    x_mm**2
                    + y_mm**2
                    + z_mm**2
                )
            )

        if output_path is not None:
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            gmsh.write(
                str(output_path)
            )

        return QuadraticSurfaceMeshSummary(
            name=spec.name,
            target_size_mm=(
                spec.target_size_mm
            ),
            node_count=len(
                node_tags
            ),
            triangle_count=len(
                triangle_tags
            ),
            nodes_per_triangle=(
                nodes_per_triangle
            ),
            min_node_radius_mm=min(
                radii_mm
            ),
            max_node_radius_mm=max(
                radii_mm
            ),
        )

    finally:
        gmsh.finalize()