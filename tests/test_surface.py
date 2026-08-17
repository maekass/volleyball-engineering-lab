from math import asin

import pytest

from ball001.cad import MM_PER_M, build_layer_solids, outer_radius_mm
from ball001.design import BALL_001, EvidenceClass
from ball001.surface import BALL_001_SEAM
from ball001.surface_cad import build_grooved_skin, seam_half_height_mm
from ball001.surface_mass import (
    calculate_groove_removed_mass,
    calculate_surface_adjusted_mass,
)


def test_seam_dimensions_are_positive() -> None:
    assert BALL_001_SEAM.width_m > 0
    assert BALL_001_SEAM.depth_m > 0


def test_seam_is_pending_evidence() -> None:
    assert BALL_001_SEAM.evidence == EvidenceClass.PENDING


def test_seam_does_not_cut_through_skin() -> None:
    skin = BALL_001.layers[0]

    assert BALL_001_SEAM.depth_m < skin.thickness_m


def test_seam_surface_width_matches_specification() -> None:
    radius_mm = outer_radius_mm(BALL_001)
    half_height_mm = seam_half_height_mm(
        BALL_001,
        BALL_001_SEAM,
    )

    half_angle_rad = asin(half_height_mm / radius_mm)
    reconstructed_width_mm = 2.0 * radius_mm * half_angle_rad

    expected_width_mm = BALL_001_SEAM.width_m * MM_PER_M

    assert reconstructed_width_mm == pytest.approx(
        expected_width_mm,
        rel=1e-12,
    )


def test_groove_removes_material_from_skin() -> None:
    original_skin = build_layer_solids(BALL_001)[0].solid
    grooved_skin = build_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
    )

    assert grooved_skin.val().Volume() < original_skin.val().Volume()

def test_grooved_skin_still_has_positive_volume() -> None:
    grooved_skin = build_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
    )

    assert grooved_skin.val().Volume() > 0


def test_groove_depth_leaves_skin_material_beneath_channel() -> None:
    skin = BALL_001.layers[0]

    remaining_skin_m = skin.thickness_m - BALL_001_SEAM.depth_m

    assert remaining_skin_m > 0
    assert remaining_skin_m == pytest.approx(0.0004)

def test_groove_removed_mass_is_positive() -> None:
    removed_mass_kg = calculate_groove_removed_mass(
        BALL_001,
        BALL_001_SEAM,
    )

    assert removed_mass_kg > 0


def test_surface_adjusted_mass_is_lower_than_baseline() -> None:
    result = calculate_surface_adjusted_mass(
        BALL_001,
        BALL_001_SEAM,
    )

    assert result.adjusted_mass_kg < result.baseline_mass_kg


def test_surface_mass_balance_is_consistent() -> None:
    result = calculate_surface_adjusted_mass(
        BALL_001,
        BALL_001_SEAM,
    )

    assert result.adjusted_mass_kg == pytest.approx(
        result.baseline_mass_kg - result.removed_skin_mass_kg
    )