import pytest

from ball001.design import BALL_001
from ball001.mesh import (
    BALL001_MESH_SPECS,
    generate_surface_mesh,
)


@pytest.fixture(scope="module")
def quality_results():
    return tuple(
        generate_surface_mesh(
            BALL_001,
            spec,
        )
        for spec in BALL001_MESH_SPECS
    )


def test_faceted_area_is_below_analytical_sphere_area(
    quality_results,
) -> None:
    for result in quality_results:
        assert (
            result.faceted_surface_area_mm2
            < result.analytical_surface_area_mm2
        )


def test_surface_area_error_decreases_with_refinement(
    quality_results,
) -> None:
    errors = [
        result.surface_area_error_percent
        for result in quality_results
    ]

    assert (
        errors[0]
        > errors[1]
        > errors[2]
    )


def test_sicn_values_are_valid(
    quality_results,
) -> None:
    for result in quality_results:
        assert (
            0.0
            < result.min_sicn
            <= 1.0
        )

        assert (
            result.min_sicn
            <= result.mean_sicn
            <= 1.0
        )


def test_analytical_area_is_same_for_all_meshes(
    quality_results,
) -> None:
    reference_area = (
        quality_results[
            0
        ].analytical_surface_area_mm2
    )

    for result in quality_results[1:]:
        assert (
            result.analytical_surface_area_mm2
            == pytest.approx(
                reference_area
            )
        )