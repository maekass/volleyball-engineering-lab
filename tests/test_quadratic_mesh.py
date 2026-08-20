import pytest

from ball001.cad import outer_radius_mm
from ball001.design import BALL_001
from ball001.mesh import (
    MEDIUM_MESH,
    generate_surface_mesh,
)
from ball001.quadratic_mesh import (
    generate_quadratic_surface_mesh,
)


@pytest.fixture(scope="module")
def quadratic_mesh():
    return generate_quadratic_surface_mesh(
        BALL_001,
        MEDIUM_MESH,
    )


def test_quadratic_triangles_have_six_nodes(
    quadratic_mesh,
) -> None:
    assert (
        quadratic_mesh.nodes_per_triangle
        == 6
    )


def test_quadratic_mesh_has_nodes_and_triangles(
    quadratic_mesh,
) -> None:
    assert quadratic_mesh.node_count > 0
    assert quadratic_mesh.triangle_count > 0


def test_quadratic_and_linear_meshes_share_triangle_count(
    quadratic_mesh,
) -> None:
    linear_mesh = generate_surface_mesh(
        BALL_001,
        MEDIUM_MESH,
    )

    assert (
        quadratic_mesh.triangle_count
        == linear_mesh.triangle_count
    )


def test_quadratic_mesh_has_more_nodes_than_linear_mesh(
    quadratic_mesh,
) -> None:
    linear_mesh = generate_surface_mesh(
        BALL_001,
        MEDIUM_MESH,
    )

    assert (
        quadratic_mesh.node_count
        > linear_mesh.node_count
    )


def test_quadratic_nodes_lie_on_ball_radius(
    quadratic_mesh,
) -> None:
    expected_radius_mm = outer_radius_mm(
        BALL_001
    )

    assert (
        quadratic_mesh.min_node_radius_mm
        == pytest.approx(
            expected_radius_mm,
            abs=1e-4,
        )
    )

    assert (
        quadratic_mesh.max_node_radius_mm
        == pytest.approx(
            expected_radius_mm,
            abs=1e-4,
        )
    )


def test_invalid_quadratic_mesh_size_is_rejected() -> None:
    from ball001.mesh import SurfaceMeshSpec

    invalid_spec = SurfaceMeshSpec(
        name="invalid",
        target_size_mm=0.0,
    )

    with pytest.raises(
        ValueError,
        match="positive",
    ):
        generate_quadratic_surface_mesh(
            BALL_001,
            invalid_spec,
        )