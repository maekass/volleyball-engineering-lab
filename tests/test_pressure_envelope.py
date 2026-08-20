import pytest

from ball001.nonlinear_stiffness_sweep import (
    GeometryMode,
)
from ball001.pressure_envelope import (
    PRESSURE_LEVELS,
    PressureEnvelopeCase,
    PressureLevel,
    build_pressure_envelope_cases,
    build_pressure_envelope_deck,
)

SOURCE_DECK = (
    "*HEADING\n"
    "*MATERIAL,NAME=SHELL\n"
    "*ELASTIC\n"
    "1000.000000000, 0.300000000\n"
    "*STEP\n"
    "*STATIC\n"
    "*DLOAD\n"
    "EALL,P,0.030656000\n"
    "*END STEP\n"
)


def test_pressure_envelope_contains_six_cases() -> None:
    cases = (
        build_pressure_envelope_cases()
    )

    assert len(cases) == 6


def test_pressure_levels_match_project_benchmarks() -> None:
    pressures = [
        level.pressure_kpa
        for level in PRESSURE_LEVELS
    ]

    assert pressures == pytest.approx(
        [
            29.430,
            30.656,
            31.882,
        ]
    )


def test_each_pressure_has_both_geometry_modes() -> None:
    cases = (
        build_pressure_envelope_cases()
    )

    for pressure_level in PRESSURE_LEVELS:
        modes = {
            case.geometry_mode
            for case in cases
            if (
                case.pressure_level
                == pressure_level
            )
        }

        assert modes == {
            GeometryMode.LINEAR,
            GeometryMode.NLGEOM,
        }


def test_kpa_converts_to_n_mm2() -> None:
    level = PressureLevel(
        label="test",
        pressure_kpa=30.656,
    )

    assert (
        level.pressure_n_mm2
        == pytest.approx(
            0.030656
        )
    )


def test_pressure_envelope_uses_20_mpa_anchor() -> None:
    case = PressureEnvelopeCase(
        pressure_level=PRESSURE_LEVELS[1],
        geometry_mode=(
            GeometryMode.LINEAR
        ),
    )

    assert (
        case.youngs_modulus_mpa
        == pytest.approx(20.0)
    )

    assert (
        case.poisson_ratio
        == pytest.approx(0.35)
    )


def test_deck_replaces_pressure() -> None:
    case = PressureEnvelopeCase(
        pressure_level=PRESSURE_LEVELS[2],
        geometry_mode=(
            GeometryMode.NLGEOM
        ),
    )

    deck = (
        build_pressure_envelope_deck(
            SOURCE_DECK,
            case,
        )
    )

    assert (
        "EALL,P,0.031882000"
        in deck
    )

    assert (
        "EALL,P,0.030656000"
        not in deck
    )


def test_deck_updates_material_and_geometry_mode() -> None:
    case = PressureEnvelopeCase(
        pressure_level=PRESSURE_LEVELS[0],
        geometry_mode=(
            GeometryMode.NLGEOM
        ),
    )

    deck = (
        build_pressure_envelope_deck(
            SOURCE_DECK,
            case,
        )
    )

    assert (
        "20.000000000, 0.350000000"
        in deck
    )

    assert "*STEP,NLGEOM" in deck