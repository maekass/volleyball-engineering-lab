import pytest

from ball001.design import BALL_001
from ball001.panel_candidate_cad import (
    build_candidate_panel_guides,
    equal_area_boundary_polar_degrees,
)
from ball001.panel_candidates import (
    BALL001_8_REGION,
    BALL001_12_REGION,
    BALL001_18_REGION,
    BALL001_PANEL_CANDIDATES,
)


def test_two_zone_boundary_is_equator() -> None:
    boundaries = (
        equal_area_boundary_polar_degrees(2)
    )

    assert boundaries == pytest.approx(
        (90.0,)
    )


def test_three_zone_boundaries_are_symmetric() -> None:
    boundaries = (
        equal_area_boundary_polar_degrees(3)
    )

    assert len(boundaries) == 2

    assert (
        boundaries[0]
        + boundaries[1]
    ) == pytest.approx(180.0)


def test_expected_candidate_guide_counts() -> None:
    expected_counts = {
        BALL001_8_REGION.name: 5,
        BALL001_12_REGION.name: 6,
        BALL001_18_REGION.name: 8,
    }

    for candidate in BALL001_PANEL_CANDIDATES:
        guides = build_candidate_panel_guides(
            BALL_001,
            candidate,
        )

        assert len(guides) == (
            expected_counts[
                candidate.name
            ]
        )


def test_all_candidate_guides_have_positive_length() -> None:
    for candidate in BALL001_PANEL_CANDIDATES:
        guides = build_candidate_panel_guides(
            BALL_001,
            candidate,
        )

        assert all(
            guide.Length() > 0
            for guide in guides
        )


def test_candidate_region_count_matches_grid_definition() -> None:
    for candidate in BALL001_PANEL_CANDIDATES:
        assert candidate.region_count == (
            candidate.meridian_count
            * candidate.zone_count
        )