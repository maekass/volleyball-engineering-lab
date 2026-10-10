import pytest

from ball001.research_statistics import (
    AnalyticalObservation,
    EquivalenceInterval,
    QuantificationState,
    all_critical_metrics_equivalent,
)


def test_nondetect_is_interval_not_zero() -> None:
    observation = AnalyticalObservation(
        QuantificationState.NOT_DETECTED, lod=0.01, loq=0.04
    )
    assert observation.quantified_value is None
    assert observation.censoring_interval == (0.0, 0.01)


def test_detected_below_loq_cannot_be_given_exact_value() -> None:
    with pytest.raises(ValueError, match="exact concentration"):
        AnalyticalObservation(
            QuantificationState.DETECTED_BELOW_LOQ,
            lod=0.01, loq=0.04, quantified_value=0.025
        )


def test_quantified_result_must_exceed_loq() -> None:
    with pytest.raises(ValueError, match="at least LOQ"):
        AnalyticalObservation(
            QuantificationState.QUANTIFIED,
            lod=0.01, loq=0.04, quantified_value=0.025
        )


def test_equivalence_requires_whole_ci_inside_preregistered_margin() -> None:
    good = EquivalenceInterval(
        "compression", -0.8, 0.8, -2.0, 2.0, 0.90,
        12, "mixed-effects CI", "PREREG-001"
    )
    bad = EquivalenceInterval(
        "wet grip", -1.0, 3.0, -2.0, 2.0, 0.90,
        12, "mixed-effects CI", "PREREG-001"
    )
    assert good.equivalent_by_interval
    assert not bad.equivalent_by_interval
    assert not all_critical_metrics_equivalent((good, bad))


def test_ci_touching_equivalence_boundary_does_not_pass() -> None:
    touching = EquivalenceInterval(
        "mass", -2.0, 1.0, -2.0, 2.0, 0.90,
        12, "hierarchical CI", "PREREG-001"
    )
    assert not touching.equivalent_by_interval


def test_equivalence_rejects_unregistered_analysis() -> None:
    with pytest.raises(ValueError, match="preregistration"):
        EquivalenceInterval(
            "mass", -1.0, 1.0, -2.0, 2.0, 0.90,
            12, "hierarchical CI", ""
        )
