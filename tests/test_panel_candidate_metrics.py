import pytest

from ball001.design import BALL_001
from ball001.panel_candidate_metrics import (
    calculate_all_candidate_metrics,
)


def test_candidate_metrics_contains_three_cases() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    assert len(results) == 3


def test_expected_candidate_guide_counts() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    guide_counts = [
        result.guide_count
        for result in results
    ]

    assert guide_counts == [5, 6, 8]


def test_boundary_length_increases_with_complexity() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    lengths = [
        result.schematic_boundary_length_m
        for result in results
    ]

    assert lengths == sorted(lengths)


def test_all_candidates_use_same_ball_surface_area() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    reference_area = (
        results[0].sphere_surface_area_m2
    )

    for result in results[1:]:
        assert (
            result.sphere_surface_area_m2
            == pytest.approx(reference_area)
        )


def test_mean_region_area_decreases_with_region_count() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    mean_areas = [
        result.mean_region_area_m2
        for result in results
    ]

    assert (
        mean_areas[0]
        > mean_areas[1]
        > mean_areas[2]
    )


def test_boundary_length_per_area_increases() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    values = [
        result.boundary_length_per_area_m_m2
        for result in results
    ]

    assert values == sorted(values)


def test_mean_shared_boundary_formula() -> None:
    results = calculate_all_candidate_metrics(
        BALL_001
    )

    for result in results:
        expected = (
            2.0
            * result.schematic_boundary_length_m
            / result.region_count
        )

        assert (
            result.mean_shared_boundary_per_region_m
            == pytest.approx(expected)
        )