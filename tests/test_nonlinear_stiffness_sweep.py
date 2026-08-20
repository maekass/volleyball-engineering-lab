import pytest

from ball001.nonlinear_stiffness_sweep import (
    GeometryMode,
    StiffnessSweepCase,
    build_stiffness_sweep_cases,
    build_stiffness_sweep_deck,
)

SOURCE_DECK = (
    "*HEADING\n"
    "** BALL 001\n"
    "*MATERIAL,NAME=SHELL\n"
    "*ELASTIC\n"
    "1000.000000000, 0.300000000\n"
    "*STEP\n"
    "*STATIC\n"
    "*DLOAD\n"
    "EALL,P,0.030656000\n"
    "*END STEP\n"
)


def test_sweep_contains_six_cases() -> None:
    cases = build_stiffness_sweep_cases()

    assert len(cases) == 6


def test_sweep_contains_expected_stiffnesses() -> None:
    cases = build_stiffness_sweep_cases()

    moduli = {
        case.youngs_modulus_mpa
        for case in cases
    }

    assert moduli == {
        100.0,
        20.0,
        5.0,
    }


def test_each_stiffness_has_both_geometry_modes() -> None:
    cases = build_stiffness_sweep_cases()

    for modulus in (
        100.0,
        20.0,
        5.0,
    ):
        modes = {
            case.geometry_mode
            for case in cases
            if case.youngs_modulus_mpa == modulus
        }

        assert modes == {
            GeometryMode.LINEAR,
            GeometryMode.NLGEOM,
        }


def test_mpa_matches_calculix_n_mm2_units() -> None:
    case = StiffnessSweepCase(
        label="test",
        youngs_modulus_mpa=100.0,
        poisson_ratio=0.35,
        geometry_mode=GeometryMode.LINEAR,
    )

    assert (
        case.youngs_modulus_n_mm2
        == pytest.approx(100.0)
    )


def test_linear_deck_updates_material_and_step() -> None:
    case = StiffnessSweepCase(
        label="test",
        youngs_modulus_mpa=20.0,
        poisson_ratio=0.35,
        geometry_mode=GeometryMode.LINEAR,
    )

    deck = build_stiffness_sweep_deck(
        SOURCE_DECK,
        case,
    )

    assert (
        "20.000000000, 0.350000000"
        in deck
    )

    assert "*STEP,NLGEOM" not in deck
    assert "*STEP\n" in deck


def test_nlgeom_deck_enables_geometric_nonlinearity() -> None:
    case = StiffnessSweepCase(
        label="test",
        youngs_modulus_mpa=5.0,
        poisson_ratio=0.35,
        geometry_mode=GeometryMode.NLGEOM,
    )

    deck = build_stiffness_sweep_deck(
        SOURCE_DECK,
        case,
    )

    assert "*STEP,NLGEOM\n" in deck


def test_sweep_deck_adds_explicit_static_increments() -> None:
    case = StiffnessSweepCase(
        label="test",
        youngs_modulus_mpa=5.0,
        poisson_ratio=0.35,
        geometry_mode=GeometryMode.NLGEOM,
    )

    deck = build_stiffness_sweep_deck(
        SOURCE_DECK,
        case,
    )

    assert (
        "0.050000000, "
        "1.000000000, "
        "1.000000000e-05, "
        "0.100000000"
        in deck
    )


def test_pressure_load_is_preserved() -> None:
    case = StiffnessSweepCase(
        label="test",
        youngs_modulus_mpa=5.0,
        poisson_ratio=0.35,
        geometry_mode=GeometryMode.NLGEOM,
    )

    deck = build_stiffness_sweep_deck(
        SOURCE_DECK,
        case,
    )

    assert "EALL,P,0.030656000" in deck
