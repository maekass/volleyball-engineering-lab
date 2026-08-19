import pytest

from ball001.design import BALL_001, EvidenceClass
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
    BALL001_PRESSURE_CASES,
    calculate_pressure_benchmark,
    spherical_membrane_resultant_n_per_m,
)


def test_pressure_cases_increase_in_order() -> None:
    pressures = [
        case.pressure_pa
        for case in BALL001_PRESSURE_CASES
    ]

    assert pressures == sorted(pressures)


def test_nominal_pressure_is_target_evidence() -> None:
    assert (
        BALL001_NOMINAL_PRESSURE.evidence
        == EvidenceClass.TARGET
    )


def test_membrane_resultant_increases_with_pressure() -> None:
    results = [
        calculate_pressure_benchmark(
            BALL_001,
            case,
        )
        for case in BALL001_PRESSURE_CASES
    ]

    resultants = [
        result.membrane_resultant_n_per_m
        for result in results
    ]

    assert resultants == sorted(resultants)


def test_spherical_pressure_equilibrium() -> None:
    for case in BALL001_PRESSURE_CASES:
        result = calculate_pressure_benchmark(
            BALL_001,
            case,
        )

        assert (
            result.great_circle_membrane_balance_n
            == pytest.approx(
                result.hemisphere_pressure_resultant_n
            )
        )


def test_nonpositive_pressure_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="positive",
    ):
        spherical_membrane_resultant_n_per_m(
            BALL_001,
            0.0,
        )