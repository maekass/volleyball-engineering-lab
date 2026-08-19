from dataclasses import dataclass
from math import sqrt
from pathlib import Path

import gmsh

from ball001.cad import outer_radius_mm
from ball001.design import BallDesign


@dataclass(frozen=True)
class SurfaceMeshSpec:
    name: str
    target_size_mm: float


@dataclass(frozen=True)
class SurfaceMeshSummary:
    name: str
    target_size_mm: float
    node_count: int
    triangle_count: int
    min_node_radius_mm: float
    max_node_radius_mm: float


COARSE_MESH = SurfaceMeshSpec(
    name="coarse",
    target_size_mm=12.0,
)

MEDIUM_MESH = SurfaceMeshSpec(
    name="medium",
    target_size_mm=8.0,
)

FINE_MESH = SurfaceMeshSpec(
    name="fine",
    target_size_mm=5.0,
)


BALL001_MESH_SPECS = (
    COARSE_MESH,
    MEDIUM_MESH,
    FINE_MESH,
)


def generate_surface_mesh(
    design: BallDesign,
    spec: SurfaceMeshSpec,
    output_path: Path | None = None,
) -> SurfaceMeshSummary:
    if spec.target_size_mm <= 0.0:
        raise ValueError(
            "Mesh target size must be positive."
        )

    radius_mm = outer_radius_mm(design)

    gmsh.initialize()

    try:
        gmsh.option.setNumber(
            "General.Terminal",
            0,
        )

        gmsh.model.add(
            f"{design.name}_{spec.name}_surface_mesh"
        )

        gmsh.model.occ.addSphere(
            0.0,
            0.0,
            0.0,
            radius_mm,
        )

        gmsh.model.occ.synchronize()

        # Use the requested target size as both the
        # minimum and maximum for this baseline study.
        gmsh.option.setNumber(
            "Mesh.MeshSizeMin",
            spec.target_size_mm,
        )

        gmsh.option.setNumber(
            "Mesh.MeshSizeMax",
            spec.target_size_mm,
        )

        # Disable competing size sources so this first
        # convergence ladder is easy to interpret.
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

        gmsh.option.setNumber(
            "Mesh.ElementOrder",
            1,
        )

        gmsh.model.mesh.generate(2)

        node_tags, node_coords, _ = (
            gmsh.model.mesh.getNodes()
        )

        triangle_type = (
            gmsh.model.mesh.getElementType(
                "triangle",
                1,
            )
        )

        triangle_tags, _ = (
            gmsh.model.mesh.getElementsByType(
                triangle_type
            )
        )

        radii_mm = []

        for index in range(
            0,
            len(node_coords),
            3,
        ):
            x_mm = node_coords[index]
            y_mm = node_coords[index + 1]
            z_mm = node_coords[index + 2]

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

        return SurfaceMeshSummary(
            name=spec.name,
            target_size_mm=spec.target_size_mm,
            node_count=len(node_tags),
            triangle_count=len(triangle_tags),
            min_node_radius_mm=min(radii_mm),
            max_node_radius_mm=max(radii_mm),
        )

    finally:
        gmsh.finalize()