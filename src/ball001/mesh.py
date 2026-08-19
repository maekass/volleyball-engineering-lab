from dataclasses import dataclass
from math import pi, sqrt
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
    faceted_surface_area_mm2: float
    analytical_surface_area_mm2: float
    surface_area_error_percent: float
    min_sicn: float
    mean_sicn: float


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


def _triangle_area_mm2(
    point_a: tuple[float, float, float],
    point_b: tuple[float, float, float],
    point_c: tuple[float, float, float],
) -> float:
    ab_x = point_b[0] - point_a[0]
    ab_y = point_b[1] - point_a[1]
    ab_z = point_b[2] - point_a[2]

    ac_x = point_c[0] - point_a[0]
    ac_y = point_c[1] - point_a[1]
    ac_z = point_c[2] - point_a[2]

    cross_x = (
        ab_y * ac_z
        - ab_z * ac_y
    )

    cross_y = (
        ab_z * ac_x
        - ab_x * ac_z
    )

    cross_z = (
        ab_x * ac_y
        - ab_y * ac_x
    )

    return 0.5 * sqrt(
        cross_x**2
        + cross_y**2
        + cross_z**2
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

        (
            triangle_tags,
            triangle_node_tags,
        ) = gmsh.model.mesh.getElementsByType(
            triangle_type
        )

        node_coordinates = {}

        radii_mm = []

        for node_index, node_tag in enumerate(
            node_tags
        ):
            coordinate_index = (
                3 * node_index
            )

            point = (
                float(
                    node_coords[
                        coordinate_index
                    ]
                ),
                float(
                    node_coords[
                        coordinate_index + 1
                    ]
                ),
                float(
                    node_coords[
                        coordinate_index + 2
                    ]
                ),
            )

            node_coordinates[
                int(node_tag)
            ] = point

            radii_mm.append(
                sqrt(
                    point[0] ** 2
                    + point[1] ** 2
                    + point[2] ** 2
                )
            )

        faceted_surface_area_mm2 = 0.0

        for index in range(
            0,
            len(triangle_node_tags),
            3,
        ):
            point_a = node_coordinates[
                int(
                    triangle_node_tags[index]
                )
            ]

            point_b = node_coordinates[
                int(
                    triangle_node_tags[
                        index + 1
                    ]
                )
            ]

            point_c = node_coordinates[
                int(
                    triangle_node_tags[
                        index + 2
                    ]
                )
            ]

            faceted_surface_area_mm2 += (
                _triangle_area_mm2(
                    point_a,
                    point_b,
                    point_c,
                )
            )

        analytical_surface_area_mm2 = (
            4.0
            * pi
            * radius_mm**2
        )

        surface_area_error_percent = (
            (
                analytical_surface_area_mm2
                - faceted_surface_area_mm2
            )
            / analytical_surface_area_mm2
            * 100.0
        )

        sicn_values = (
            gmsh.model.mesh.getElementQualities(
                triangle_tags,
                "minSICN",
            )
        )

        sicn_values_float = [
            float(value)
            for value in sicn_values
        ]

        min_sicn = min(
            sicn_values_float
        )

        mean_sicn = (
            sum(sicn_values_float)
            / len(sicn_values_float)
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
            triangle_count=len(
                triangle_tags
            ),
            min_node_radius_mm=min(
                radii_mm
            ),
            max_node_radius_mm=max(
                radii_mm
            ),
            faceted_surface_area_mm2=(
                faceted_surface_area_mm2
            ),
            analytical_surface_area_mm2=(
                analytical_surface_area_mm2
            ),
            surface_area_error_percent=(
                surface_area_error_percent
            ),
            min_sicn=min_sicn,
            mean_sicn=mean_sicn,
        )

    finally:
        gmsh.finalize()