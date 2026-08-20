import pytest

from ball001.model_selection import (
    BALL001_MODEL_SELECTION_TARGET,
    ModelSelectionCriteria,
    RecommendedGeometryModel,
    assess_geometry_model,
)
from ball001.nonlinear_stiffness_results import (
    NonlinearDivergenceResult,
)


def _divergence(
    modulus_mpa: float,
    displacement_difference_percent: float,
    stress_difference_percent: float,
) -> NonlinearDivergenceResult:
    return NonlinearDivergenceResult(
        youngs_modulus_mpa=modulus_mpa,
        linear_radial_displacement_mm=1.0,
        nonlinear_radial_displacement_mm=1.0,
        displacement_difference_percent=(
            displacement_difference_percent
        ),
        linear_radial_expansion_percent=1.0,
        nonlinear_radial_expansion_percent=1.0,
        linear_tangential_stress_n_mm2=0.6,
        nonlinear_tangential_stress_n_mm2=0.6,
        stress_difference_percent=(
            stress_difference_percent
        ),
        linear_outward_node_fraction=1.0,
        nonlinear_outward_node_fraction=1.0,
    )


def test_default_targets_are_two_and_five_percent() -> None:
    assert (
        BALL001_MODEL_SELECTION_TARGET
        .max_displacement_difference_percent
        == pytest.approx(2.0)
    )

    assert (
        BALL001_MODEL_SELECTION_TARGET
        .max_stress_difference_percent
        == pytest.approx(5.0)
    )


def test_criteria_require_positive_targets() -> None:
    with pytest.raises(
        ValueError,
        match="Displacement",
    ):
        ModelSelectionCriteria(
            max_displacement_difference_percent=0.0,
            max_stress_difference_percent=5.0,
        )

    with pytest.raises(
        ValueError,
        match="Stress",
    ):
        ModelSelectionCriteria(
            max_displacement_difference_percent=2.0,
            max_stress_difference_percent=0.0,
        )


def test_100_mpa_case_retains_linear_model() -> None:
    result = assess_geometry_model(
        _divergence(
            modulus_mpa=100.0,
            displacement_difference_percent=0.23,
            stress_difference_percent=0.85,
        )
    )

    assert result.linear_model_accepted

    assert (
        result.recommendation
        is RecommendedGeometryModel.LINEAR
    )


def test_20_mpa_case_retains_linear_model() -> None:
    result = assess_geometry_model(
        _divergence(
            modulus_mpa=20.0,
            displacement_difference_percent=1.14,
            stress_difference_percent=4.40,
        )
    )

    assert result.linear_model_accepted

    assert result.displacement_within_target
    assert result.stress_within_target


def test_5_mpa_case_requires_nlgeom() -> None:
    result = assess_geometry_model(
        _divergence(
            modulus_mpa=5.0,
            displacement_difference_percent=4.64,
            stress_difference_percent=20.53,
        )
    )

    assert not result.linear_model_accepted

    assert (
        result.recommendation
        is RecommendedGeometryModel.NLGEOM
    )


def test_stress_can_trigger_nlgeom_when_displacement_passes() -> None:
    result = assess_geometry_model(
        _divergence(
            modulus_mpa=20.0,
            displacement_difference_percent=1.0,
            stress_difference_percent=6.0,
        )
    )

    assert result.displacement_within_target
    assert not result.stress_within_target

    assert (
        result.recommendation
        is RecommendedGeometryModel.NLGEOM
    )


def test_exact_target_boundary_is_accepted() -> None:
    result = assess_geometry_model(
        _divergence(
            modulus_mpa=20.0,
            displacement_difference_percent=2.0,
            stress_difference_percent=5.0,
        )
    )

    assert result.linear_model_accepted