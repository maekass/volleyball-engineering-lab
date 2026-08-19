import pytest

from ball001.design import (
    BALL_001,
    EvidenceClass,
)
from ball001.pressure_baseline import (
    calculate_pressure_baseline,
    nominal_fivb_pressure_pa,
    total_wall_thickness_m,
)
from ball001.volleyball_benchmark import (
    FIVB_INDOOR_BALL,
)


def test_total_wall_thickness_is_positive() -> None:
    thickness_m = total_wall_thickness_m(
        BALL_001
    )

    assert thickness_m > 0.0


def test_nominal_pressure_is_midpoint_of_fivb_range() -> None:
    expected_pressure_pa = 0.5 * (
        FIVB_INDOOR_BALL.internal_pressure_min_pa
        + FIVB_INDOOR_BALL.internal_pressure_max_pa
    )

    assert nominal_fivb_pressure_pa() == pytest.approx(
        expected_pressure_pa
    )


def test_pressure_baseline_uses_positive_geometry() -> None:
    result = calculate_pressure_baseline(
        BALL_001
    )

    assert result.radius_m > 0.0
    assert result.wall_thickness_m > 0.0
    assert result.thickness_to_radius_ratio > 0.0


def test_membrane_force_matches_spherical_relation() -> None:
    result = calculate_pressure_baseline(
        BALL_001
    )

    expected_force = (
        result.pressure_pa
        * result.radius_m
        / 2.0
    )

    assert (
        result.membrane_force_per_length_n_m
        == pytest.approx(expected_force)
    )


def test_homogenized_stress_matches_force_over_thickness() -> None:
    result = calculate_pressure_baseline(
        BALL_001
    )

    expected_stress = (
        result.membrane_force_per_length_n_m
        / result.wall_thickness_m
    )

    assert (
        result.homogenized_membrane_stress_pa
        == pytest.approx(expected_stress)
    )


def test_pressure_and_thickness_evidence_are_distinguished() -> None:
    result = calculate_pressure_baseline(
        BALL_001
    )

    assert (
        result.pressure_evidence
        == EvidenceClass.BENCHMARK
    )

    assert (
        result.wall_thickness_evidence
        == EvidenceClass.PENDING
    )


def test_nonpositive_pressure_is_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_pressure_baseline(
            BALL_001,
            pressure_pa=0.0,
        )