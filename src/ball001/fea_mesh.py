from dataclasses import dataclass
from pathlib import Path

import gmsh

from ball001.cad import outer_radius_mm
from ball001.design import BallDesign


@dataclass(frozen=True)
class SurfaceMeshSpec:
    label: str
    characteristic_length_mm: float


@dataclass(frozen=True)
class SurfaceMeshResult:
    label: str
    radius_mm: float
    characteristic_length_mm: float
    node_count: int
    triangle_count: int


COARSE_MESH = SurfaceMeshSpec(
    label="coarse",
    characteristic_length_mm=15.0,
)

MEDIUM_MESH = SurfaceMeshSpec(
    label="medium",
    characteristic_length_mm=10.0,
)

FINE_MESH = SurfaceMeshSpec(
    label="fine",
    characteristic_length_mm=7.5,
)

SURFACE_MESH_SPECS = (
    COARSE_MESH,
    MEDIUM_MESH,
    FINE_MESH,
)


def generate_surface_mesh(
    design: BallDesign,
    spec: SurfaceMeshSpec,
    output_path: Path | None = None,
    terminal_output: bool = False,
) -> SurfaceMeshResult:
    if spec.characteristic_length_mm <= 0.0:
        raise ValueError(
            "Characteristic mesh length must be positive."
        )

    radius_mm = outer_radius_mm(design)

    gmsh.initialize()

    try:
        gmsh.option.setNumber(
            "General.Terminal",
            1 if terminal_output else 0,
        )

        gmsh.model.add(
            f"BALL_001_{spec.label}_surface_mesh"
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
            spec.characteristic_length_mm,
        )

        gmsh.option.setNumber(
            "Mesh.MeshSizeMax",
            spec.characteristic_length_mm,
        )

        gmsh.model.mesh.generate(2)

        node_tags, _, _ = (
            gmsh.model.mesh.getNodes()
        )

        element_types, element_tags, _ = (
            gmsh.model.mesh.getElements(2)
        )

        triangle_count = 0

        for element_type, tags in zip(
            element_types,
            element_tags,
            strict=True,
        ):
            element_name = (
                gmsh.model.mesh.getElementProperties(
                    element_type
                )[0]
            )

            if "Triangle" in element_name:
                triangle_count += len(tags)

        if output_path is not None:
            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            gmsh.write(
                str(output_path)
            )

        return SurfaceMeshResult(
            label=spec.label,
            radius_mm=radius_mm,
            characteristic_length_mm=(
                spec.characteristic_length_mm
            ),
            node_count=len(node_tags),
            triangle_count=triangle_count,
        )

    finally:
        gmsh.finalize()