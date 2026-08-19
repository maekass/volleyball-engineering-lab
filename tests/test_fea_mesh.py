import pytest

from ball001.cad import outer_radius_mm
from ball001.design import BALL_001
from ball001.fea_mesh import (
    COARSE_MESH,
    FINE_MESH,
    SurfaceMeshSpec,
    generate_surface_mesh,
)


def test_mesh_radius_matches_ball001_geometry() -> None:
    result = generate_surface_mesh(
        BALL_001,
        COARSE_MESH,
    )

    assert result.radius_mm == pytest.approx(
        outer_radius_mm(BALL_001)
    )


def test_surface_mesh_has_nodes_and_triangles() -> None:
    result = generate_surface_mesh(
        BALL_001,
        COARSE_MESH,
    )

    assert result.node_count > 0
    assert result.triangle_count > 0


def test_fine_mesh_contains_more_elements_than_coarse() -> None:
    coarse = generate_surface_mesh(
        BALL_001,
        COARSE_MESH,
    )

    fine = generate_surface_mesh(
        BALL_001,
        FINE_MESH,
    )

    assert fine.node_count > coarse.node_count
    assert fine.triangle_count > coarse.triangle_count


def test_nonpositive_mesh_size_is_rejected() -> None:
    invalid_spec = SurfaceMeshSpec(
        label="invalid",
        characteristic_length_mm=0.0,
    )

    with pytest.raises(ValueError):
        generate_surface_mesh(
            BALL_001,
            invalid_spec,
        )