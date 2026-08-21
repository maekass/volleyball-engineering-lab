from pathlib import Path

import numpy as np
import pytest

from ball001.calculix_results import (
    FrdStress,
)
from ball001.structural_visualization import (
    SurfaceMeshData,
    build_structural_polydata,
    load_gmsh_surface_mesh,
)


def _mesh() -> SurfaceMeshData:
    return SurfaceMeshData(
        node_tags=(
            1,
            2,
            3,
        ),
        points_mm=(
            (
                100.0,
                0.0,
                0.0,
            ),
            (
                0.0,
                100.0,
                0.0,
            ),
            (
                0.0,
                0.0,
                100.0,
            ),
        ),
        triangles=(
            (
                1,
                2,
                3,
            ),
        ),
    )


def test_polydata_contains_one_triangle() -> None:
    surface = build_structural_polydata(
        mesh=_mesh(),
        displacements_mm={},
        stresses_n_mm2={},
    )

    assert surface.n_points == 3
    assert surface.n_cells == 1


def test_node_tags_are_preserved() -> None:
    surface = build_structural_polydata(
        mesh=_mesh(),
        displacements_mm={},
        stresses_n_mm2={},
    )

    assert np.array_equal(
        surface.point_data[
            "node_tag"
        ],
        np.array(
            [
                1,
                2,
                3,
            ]
        ),
    )


def test_radial_displacement_field() -> None:
    surface = build_structural_polydata(
        mesh=_mesh(),
        displacements_mm={
            1: (
                2.0,
                0.0,
                0.0,
            ),
            2: (
                0.0,
                3.0,
                0.0,
            ),
            3: (
                0.0,
                0.0,
                4.0,
            ),
        },
        stresses_n_mm2={},
    )

    assert surface.point_data[
        "radial_displacement_mm"
    ] == pytest.approx(
        [
            2.0,
            3.0,
            4.0,
        ]
    )


def test_tangential_displacement_field() -> None:
    surface = build_structural_polydata(
        mesh=_mesh(),
        displacements_mm={
            1: (
                2.0,
                3.0,
                4.0,
            ),
        },
        stresses_n_mm2={},
    )

    assert (
        surface.point_data[
            "tangential_displacement_mm"
        ][0]
        == pytest.approx(
            5.0
        )
    )


def test_tangential_stress_field() -> None:
    surface = build_structural_polydata(
        mesh=_mesh(),
        displacements_mm={},
        stresses_n_mm2={
            1: FrdStress(
                sxx_n_mm2=0.0,
                syy_n_mm2=2.0,
                szz_n_mm2=2.0,
                sxy_n_mm2=0.0,
                syz_n_mm2=0.0,
                szx_n_mm2=0.0,
            )
        },
    )

    assert (
        surface.point_data[
            "mean_tangential_stress_n_mm2"
        ][0]
        == pytest.approx(
            2.0
        )
    )


def test_missing_mesh_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Gmsh mesh",
    ):
        load_gmsh_surface_mesh(
            tmp_path
            / "missing.msh"
        )
