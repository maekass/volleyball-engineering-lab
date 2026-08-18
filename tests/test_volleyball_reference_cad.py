from ball001.design import BALL_001
from ball001.panel_reference import V200W_PANEL_REFERENCE
from ball001.volleyball_reference_cad import (
    MERIDIAN_COUNT,
    SCHEMATIC_REGION_COUNT,
    TRANSVERSE_BOUNDARY_POLAR_DEG,
    build_schematic_panel_guides,
)


def test_schematic_region_count_matches_reference_count() -> None:
    assert SCHEMATIC_REGION_COUNT == 18
    assert (
        SCHEMATIC_REGION_COUNT
        == V200W_PANEL_REFERENCE.panel_count
    )


def test_schematic_guide_count() -> None:
    guides = build_schematic_panel_guides(
        BALL_001
    )

    expected_guide_count = (
        MERIDIAN_COUNT
        + len(TRANSVERSE_BOUNDARY_POLAR_DEG)
    )

    assert len(guides) == expected_guide_count


def test_all_reference_guides_have_positive_length() -> None:
    guides = build_schematic_panel_guides(
        BALL_001
    )

    assert all(
        guide.Length() > 0
        for guide in guides
    )


def test_reference_uses_multiple_curved_divisions() -> None:
    assert MERIDIAN_COUNT > 3
    assert len(TRANSVERSE_BOUNDARY_POLAR_DEG) == 2