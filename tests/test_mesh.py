import pytest

from ball001.cad import outer_radius_mm
from ball001.design import BALL_001
from ball001.mesh import (
    BALL001_MESH_SPECS,
    SurfaceMeshSpec,
    generate_surface_mesh,
)


@pytest.fixture(scope="module")
def mesh_results():
    return tuple(
        generate_surface_mesh(
            BALL_001,
            spec,
        )
        for spec in BALL001_MESH_SPECS
    )


def test_mesh_specs_refine_in_order() -> None:
    target_sizes = [
        spec.target_size_mm
        for spec in BALL001_MESH_SPECS
    ]

    assert target_sizes == [12.0, 8.0, 5.0]


def test_all_meshes_have_nodes_and_triangles(
    mesh_results,
) -> None:
    for result in mesh_results:
        assert result.node_count > 0
        assert result.triangle_count > 0


def test_finer_meshes_have_more_triangles(
    mesh_results,
) -> None:
    triangle_counts = [
        result.triangle_count
        for result in mesh_results
    ]

    assert (
        triangle_counts[0]
        < triangle_counts[1]
        < triangle_counts[2]
    )


def test_mesh_nodes_lie_on_ball_radius(
    mesh_results,
) -> None:
    expected_radius_mm = outer_radius_mm(
        BALL_001
    )

    for result in mesh_results:
        assert (
            result.min_node_radius_mm
            == pytest.approx(
                expected_radius_mm,
                abs=1e-4,
            )
        )

        assert (
            result.max_node_radius_mm
            == pytest.approx(
                expected_radius_mm,
                abs=1e-4,
            )
        )


def test_invalid_mesh_size_is_rejected() -> None:
    invalid_spec = SurfaceMeshSpec(
        name="invalid",
        target_size_mm=0.0,
    )

    with pytest.raises(
        ValueError,
        match="positive",
    ):
        generate_surface_mesh(
            BALL_001,
            invalid_spec,
        )