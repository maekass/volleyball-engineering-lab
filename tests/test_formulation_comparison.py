import pytest

from ball001.calculix_results import (
    CalculixVerificationResult,
)
from ball001.formulation_comparison import (
    compare_shell_formulations,
    relative_change_percent,
)


def _verification_result(
    radial_displacement_mm: float,
    displacement_error_percent: float,
    tangential_stress_n_mm2: float,
    stress_error_percent: float,
) -> CalculixVerificationResult:
    return CalculixVerificationResult(
        displacement_node_count=100,
        stress_node_count=100,
        mean_radial_displacement_mm=radial_displacement_mm,
        radial_displacement_std_mm=0.0,
        min_radial_displacement_mm=radial_displacement_mm,
        max_radial_displacement_mm=radial_displacement_mm,
        outward_node_fraction=1.0,
        max_tangential_displacement_mm=0.001,
        mean_tangential_stress_n_mm2=tangential_stress_n_mm2,
        tangential_stress_std_n_mm2=0.0,
        mean_radial_stress_n_mm2=0.0,
        analytical_radial_displacement_mm=0.044675,
        analytical_membrane_stress_n_mm2=0.607580,
        displacement_error_percent=displacement_error_percent,
        stress_error_percent=stress_error_percent,
    )


def test_relative_change_percent() -> None:
    result = relative_change_percent(
        new_value=1.01,
        reference_value=1.00,
    )

    assert result == pytest.approx(1.0)


def test_relative_change_uses_absolute_difference() -> None:
    result = relative_change_percent(
        new_value=0.99,
        reference_value=1.00,
    )

    assert result == pytest.approx(1.0)


def test_zero_reference_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="nonzero",
    ):
        relative_change_percent(
            new_value=1.0,
            reference_value=0.0,
        )


def test_formulation_comparison_preserves_results() -> None:
    s3 = _verification_result(
        radial_displacement_mm=0.0440,
        displacement_error_percent=1.5,
        tangential_stress_n_mm2=0.592,
        stress_error_percent=2.6,
    )

    s6 = _verification_result(
        radial_displacement_mm=0.0445,
        displacement_error_percent=0.4,
        tangential_stress_n_mm2=0.605,
        stress_error_percent=0.4,
    )

    comparison = compare_shell_formulations(
        s3,
        s6,
    )

    assert comparison.s3_radial_displacement_mm == pytest.approx(
        0.0440
    )

    assert comparison.s6_radial_displacement_mm == pytest.approx(
        0.0445
    )

    assert comparison.s3_tangential_stress_n_mm2 == pytest.approx(
        0.592
    )

    assert comparison.s6_tangential_stress_n_mm2 == pytest.approx(
        0.605
    )


def test_comparison_calculates_positive_changes() -> None:
    s3 = _verification_result(
        radial_displacement_mm=0.0440,
        displacement_error_percent=1.5,
        tangential_stress_n_mm2=0.592,
        stress_error_percent=2.6,
    )

    s6 = _verification_result(
        radial_displacement_mm=0.0445,
        displacement_error_percent=0.4,
        tangential_stress_n_mm2=0.605,
        stress_error_percent=0.4,
    )

    comparison = compare_shell_formulations(
        s3,
        s6,
    )

    assert comparison.displacement_change_percent > 0.0
    assert comparison.stress_change_percent > 0.0