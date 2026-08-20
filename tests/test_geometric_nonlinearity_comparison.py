import pytest

from ball001.calculix_results import (
    CalculixVerificationResult,
)
from ball001.geometric_nonlinearity_comparison import (
    compare_geometric_nonlinearity,
)


def _verification_result(
    radial_displacement_mm: float,
    displacement_error_percent: float,
    tangential_stress_n_mm2: float,
    stress_error_percent: float,
    outward_node_fraction: float = 1.0,
    max_tangential_displacement_mm: float = 0.001,
) -> CalculixVerificationResult:
    return CalculixVerificationResult(
        displacement_node_count=100,
        stress_node_count=100,
        mean_radial_displacement_mm=(
            radial_displacement_mm
        ),
        radial_displacement_std_mm=0.0,
        min_radial_displacement_mm=(
            radial_displacement_mm
        ),
        max_radial_displacement_mm=(
            radial_displacement_mm
        ),
        outward_node_fraction=(
            outward_node_fraction
        ),
        max_tangential_displacement_mm=(
            max_tangential_displacement_mm
        ),
        mean_tangential_stress_n_mm2=(
            tangential_stress_n_mm2
        ),
        tangential_stress_std_n_mm2=0.0,
        mean_radial_stress_n_mm2=0.0,
        analytical_radial_displacement_mm=0.044675,
        analytical_membrane_stress_n_mm2=0.607580,
        displacement_error_percent=(
            displacement_error_percent
        ),
        stress_error_percent=(
            stress_error_percent
        ),
    )


def test_comparison_preserves_displacement_results() -> None:
    linear = _verification_result(
        radial_displacement_mm=0.0440,
        displacement_error_percent=1.5,
        tangential_stress_n_mm2=0.592,
        stress_error_percent=2.6,
    )

    nonlinear = _verification_result(
        radial_displacement_mm=0.0439,
        displacement_error_percent=1.7,
        tangential_stress_n_mm2=0.591,
        stress_error_percent=2.7,
    )

    comparison = compare_geometric_nonlinearity(
        linear,
        nonlinear,
    )

    assert (
        comparison.linear_radial_displacement_mm
        == pytest.approx(0.0440)
    )

    assert (
        comparison.nonlinear_radial_displacement_mm
        == pytest.approx(0.0439)
    )


def test_comparison_calculates_displacement_change() -> None:
    linear = _verification_result(
        radial_displacement_mm=0.0440,
        displacement_error_percent=1.5,
        tangential_stress_n_mm2=0.592,
        stress_error_percent=2.6,
    )

    nonlinear = _verification_result(
        radial_displacement_mm=0.0439,
        displacement_error_percent=1.7,
        tangential_stress_n_mm2=0.591,
        stress_error_percent=2.7,
    )

    comparison = compare_geometric_nonlinearity(
        linear,
        nonlinear,
    )

    assert (
        comparison.displacement_change_percent
        > 0.0
    )


def test_comparison_calculates_stress_change() -> None:
    linear = _verification_result(
        radial_displacement_mm=0.0440,
        displacement_error_percent=1.5,
        tangential_stress_n_mm2=0.592,
        stress_error_percent=2.6,
    )

    nonlinear = _verification_result(
        radial_displacement_mm=0.0439,
        displacement_error_percent=1.7,
        tangential_stress_n_mm2=0.591,
        stress_error_percent=2.7,
    )

    comparison = compare_geometric_nonlinearity(
        linear,
        nonlinear,
    )

    assert (
        comparison.stress_change_percent
        > 0.0
    )


def test_comparison_preserves_secondary_metrics() -> None:
    linear = _verification_result(
        radial_displacement_mm=0.0440,
        displacement_error_percent=1.5,
        tangential_stress_n_mm2=0.592,
        stress_error_percent=2.6,
        outward_node_fraction=1.0,
        max_tangential_displacement_mm=0.0017,
    )

    nonlinear = _verification_result(
        radial_displacement_mm=0.0439,
        displacement_error_percent=1.7,
        tangential_stress_n_mm2=0.591,
        stress_error_percent=2.7,
        outward_node_fraction=1.0,
        max_tangential_displacement_mm=0.0016,
    )

    comparison = compare_geometric_nonlinearity(
        linear,
        nonlinear,
    )

    assert (
        comparison.linear_outward_node_fraction
        == pytest.approx(1.0)
    )

    assert (
        comparison.nonlinear_outward_node_fraction
        == pytest.approx(1.0)
    )

    assert (
        comparison.linear_max_tangential_displacement_mm
        == pytest.approx(0.0017)
    )

    assert (
        comparison.nonlinear_max_tangential_displacement_mm
        == pytest.approx(0.0016)
    )