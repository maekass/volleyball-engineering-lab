import pytest

from ball001.cad import (
    build_half_section_layers,
    build_layer_solids,
    outer_radius_mm,
)
from ball001.design import BALL_001
from ball001.geometry import (
    radius_from_circumference,
    spherical_shell_volume,
)

MM3_PER_M3 = 1_000_000_000.0


def test_cad_outer_radius_matches_geometry_model() -> None:
    expected_radius_mm = (
        radius_from_circumference(BALL_001.circumference_m) * 1000.0
    )

    assert outer_radius_mm(BALL_001) == pytest.approx(expected_radius_mm)


def test_cad_layer_count_matches_design() -> None:
    cad_layers = build_layer_solids(BALL_001)

    assert len(cad_layers) == len(BALL_001.layers)


def test_cad_layer_volumes_match_analytical_model() -> None:
    cad_layers = build_layer_solids(BALL_001)

    for design_layer, cad_layer in zip(
        BALL_001.layers,
        cad_layers,
        strict=True,
    ):
        analytical_volume_m3 = spherical_shell_volume(
            outer_radius_m=cad_layer.outer_radius_mm / 1000.0,
            thickness_m=design_layer.thickness_m,
        )

        analytical_volume_mm3 = analytical_volume_m3 * MM3_PER_M3
        cad_volume_mm3 = cad_layer.solid.val().Volume()

        assert cad_volume_mm3 == pytest.approx(
            analytical_volume_mm3,
            rel=1e-8,
        )


def test_half_section_layer_count_matches_design() -> None:
    section_layers = build_half_section_layers(BALL_001)

    assert len(section_layers) == len(BALL_001.layers)


def test_half_section_volumes_are_half_of_full_layers() -> None:
    full_layers = build_layer_solids(BALL_001)
    section_layers = build_half_section_layers(BALL_001)

    for full_layer, section_layer in zip(
        full_layers,
        section_layers,
        strict=True,
    ):
        full_volume_mm3 = full_layer.solid.val().Volume()
        section_volume_mm3 = section_layer.solid.val().Volume()

        assert section_volume_mm3 == pytest.approx(
            full_volume_mm3 / 2.0,
            rel=1e-8,
        )