from dataclasses import dataclass
from math import sqrt
from pathlib import Path

import gmsh
import numpy as np
import pyvista as pv

from ball001.calculix_results import (
    FrdStress,
    parse_frd_results,
)


@dataclass(frozen=True)
class SurfaceMeshData:
    node_tags: tuple[int, ...]
    points_mm: tuple[
        tuple[float, float, float],
        ...,
    ]
    triangles: tuple[
        tuple[int, int, int],
        ...,
    ]


def load_gmsh_surface_mesh(
    mesh_path: Path,
) -> SurfaceMeshData:
    if not mesh_path.exists():
        raise FileNotFoundError(
            f"Gmsh mesh does not exist: {mesh_path}"
        )

    gmsh.initialize()

    try:
        gmsh.open(str(mesh_path))

        node_tags_raw, coordinates_raw, _ = (
            gmsh.model.mesh.getNodes()
        )

        node_tags = tuple(
            int(tag)
            for tag in node_tags_raw
        )

        if not node_tags:
            raise ValueError(
                "Gmsh mesh contains no nodes."
            )

        coordinates = np.asarray(
            coordinates_raw,
            dtype=float,
        ).reshape((-1, 3))

        points_mm = tuple(
            (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )
            for point in coordinates
        )

        (
            element_types,
            _element_tags,
            element_node_tags,
        ) = gmsh.model.mesh.getElements(
            dim=2
        )

        triangles = []

        for (
            element_type,
            flat_node_tags,
        ) in zip(
            element_types,
            element_node_tags,
            strict=True,
        ):
            (
                element_name,
                element_dimension,
                _element_order,
                node_count,
                _local_coordinates,
                _primary_node_count,
            ) = gmsh.model.mesh.getElementProperties(
                element_type
            )

            if (
                element_dimension != 2
                or not element_name.startswith(
                    "Triangle"
                )
            ):
                continue

            if node_count < 3:
                continue

            flat_tags = [
                int(tag)
                for tag in flat_node_tags
            ]

            for start in range(
                0,
                len(flat_tags),
                node_count,
            ):
                element_nodes = flat_tags[
                    start : start + node_count
                ]

                triangles.append(
                    (
                        element_nodes[0],
                        element_nodes[1],
                        element_nodes[2],
                    )
                )

        if not triangles:
            raise ValueError(
                "Gmsh mesh contains no "
                "triangular surface elements."
            )

        return SurfaceMeshData(
            node_tags=node_tags,
            points_mm=points_mm,
            triangles=tuple(
                triangles
            ),
        )

    finally:
        gmsh.finalize()


def _unit_radial_vector(
    point_mm: tuple[
        float,
        float,
        float,
    ],
) -> tuple[
    float,
    float,
    float,
]:
    x_mm, y_mm, z_mm = point_mm

    radius_mm = sqrt(
        x_mm**2
        + y_mm**2
        + z_mm**2
    )

    if radius_mm <= 0.0:
        raise ValueError(
            "Surface point radius must be positive."
        )

    return (
        x_mm / radius_mm,
        y_mm / radius_mm,
        z_mm / radius_mm,
    )


def _radial_displacement_mm(
    point_mm: tuple[
        float,
        float,
        float,
    ],
    displacement_mm: tuple[
        float,
        float,
        float,
    ],
) -> float:
    nx, ny, nz = (
        _unit_radial_vector(
            point_mm
        )
    )

    ux, uy, uz = displacement_mm

    return (
        ux * nx
        + uy * ny
        + uz * nz
    )


def _tangential_displacement_mm(
    point_mm: tuple[
        float,
        float,
        float,
    ],
    displacement_mm: tuple[
        float,
        float,
        float,
    ],
) -> float:
    nx, ny, nz = (
        _unit_radial_vector(
            point_mm
        )
    )

    radial_mm = (
        _radial_displacement_mm(
            point_mm,
            displacement_mm,
        )
    )

    ux, uy, uz = displacement_mm

    tx = ux - radial_mm * nx
    ty = uy - radial_mm * ny
    tz = uz - radial_mm * nz

    return sqrt(
        tx**2
        + ty**2
        + tz**2
    )


def _radial_stress_n_mm2(
    point_mm: tuple[
        float,
        float,
        float,
    ],
    stress: FrdStress,
) -> float:
    nx, ny, nz = (
        _unit_radial_vector(
            point_mm
        )
    )

    return (
        stress.sxx_n_mm2 * nx**2
        + stress.syy_n_mm2 * ny**2
        + stress.szz_n_mm2 * nz**2
        + 2.0
        * stress.sxy_n_mm2
        * nx
        * ny
        + 2.0
        * stress.syz_n_mm2
        * ny
        * nz
        + 2.0
        * stress.szx_n_mm2
        * nz
        * nx
    )


def _mean_tangential_stress_n_mm2(
    point_mm: tuple[
        float,
        float,
        float,
    ],
    stress: FrdStress,
) -> float:
    trace_n_mm2 = (
        stress.sxx_n_mm2
        + stress.syy_n_mm2
        + stress.szz_n_mm2
    )

    radial_n_mm2 = (
        _radial_stress_n_mm2(
            point_mm,
            stress,
        )
    )

    return (
        trace_n_mm2
        - radial_n_mm2
    ) / 2.0


def build_structural_polydata(
    mesh: SurfaceMeshData,
    displacements_mm: dict[
        int,
        tuple[
            float,
            float,
            float,
        ],
    ],
    stresses_n_mm2: dict[
        int,
        FrdStress,
    ],
) -> pv.PolyData:
    tag_to_index = {
        tag: index
        for index, tag in enumerate(
            mesh.node_tags
        )
    }

    points = np.asarray(
        mesh.points_mm,
        dtype=float,
    )

    triangle_indices = []

    for triangle in mesh.triangles:
        try:
            triangle_indices.append(
                [
                    tag_to_index[tag]
                    for tag in triangle
                ]
            )
        except KeyError as error:
            raise ValueError(
                "Triangle references an "
                "unknown node tag."
            ) from error

    triangle_array = np.asarray(
        triangle_indices,
        dtype=np.int64,
    )

    face_prefix = np.full(
        (
            len(triangle_array),
            1,
        ),
        3,
        dtype=np.int64,
    )

    faces = np.hstack(
        (
            face_prefix,
            triangle_array,
        )
    ).ravel()

    surface = pv.PolyData(
        points,
        faces,
    )

    surface.point_data[
        "node_tag"
    ] = np.asarray(
        mesh.node_tags,
        dtype=np.int64,
    )

    displacement_array = np.full(
        (
            len(mesh.node_tags),
            3,
        ),
        np.nan,
        dtype=float,
    )

    radial_array = np.full(
        len(mesh.node_tags),
        np.nan,
        dtype=float,
    )

    tangential_array = np.full(
        len(mesh.node_tags),
        np.nan,
        dtype=float,
    )

    tangential_stress_array = np.full(
        len(mesh.node_tags),
        np.nan,
        dtype=float,
    )

    for index, (
        node_tag,
        point_mm,
    ) in enumerate(
        zip(
            mesh.node_tags,
            mesh.points_mm,
            strict=True,
        )
    ):
        displacement = (
            displacements_mm.get(
                node_tag
            )
        )

        if displacement is not None:
            displacement_array[
                index
            ] = displacement

            radial_array[
                index
            ] = (
                _radial_displacement_mm(
                    point_mm,
                    displacement,
                )
            )

            tangential_array[
                index
            ] = (
                _tangential_displacement_mm(
                    point_mm,
                    displacement,
                )
            )

        stress = stresses_n_mm2.get(
            node_tag
        )

        if stress is not None:
            tangential_stress_array[
                index
            ] = (
                _mean_tangential_stress_n_mm2(
                    point_mm,
                    stress,
                )
            )

    surface.point_data[
        "displacement_mm"
    ] = displacement_array

    surface.point_data[
        "radial_displacement_mm"
    ] = radial_array

    surface.point_data[
        "tangential_displacement_mm"
    ] = tangential_array

    surface.point_data[
        "mean_tangential_stress_n_mm2"
    ] = tangential_stress_array

    return surface


def export_structural_vtp(
    mesh_path: Path,
    frd_path: Path,
    output_path: Path,
) -> pv.PolyData:
    if not frd_path.exists():
        raise FileNotFoundError(
            f"CalculiX FRD does not exist: {frd_path}"
        )

    mesh = load_gmsh_surface_mesh(
        mesh_path
    )

    results = parse_frd_results(
        frd_path
    )

    surface = build_structural_polydata(
        mesh=mesh,
        displacements_mm=(
            results.displacements_mm
        ),
        stresses_n_mm2=(
            results.stresses_n_mm2
        ),
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    surface.save(
        output_path
    )

    return surface
