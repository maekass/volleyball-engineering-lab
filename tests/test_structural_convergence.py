import pytest

from ball001.design import EvidenceClass
from ball001.structural_convergence import (
    StructuralConvergenceResult,
    compare_consecutive_results,
    is_converged,
    relative_change,
)


def make_result(
    label: str,
    displacement_m: float,
) -> StructuralConvergenceResult:
    return StructuralConvergenceResult(
        mesh_label=label,
        characteristic_length_mm=5.0,
        node_count=100,
        element_count=200,
        displacement_m=displacement_m,
        evidence=EvidenceClass.SIMULATED,
    )


def test_relative_change() -> None:
    change = relative_change(
        1.0,
        0.95,
    )

    assert change == pytest.approx(0.05)


def test_relative_change_rejects_zero_reference() -> None:
    with pytest.raises(ValueError):
        relative_change(
            0.0,
            1.0,
        )


def test_consecutive_comparison_count() -> None:
    results = (
        make_result("coarse", 0.0100),
        make_result("medium", 0.0095),
        make_result("fine", 0.0094),
    )

    comparisons = compare_consecutive_results(
        results
    )

    assert len(comparisons) == 2


def test_comparison_uses_consecutive_meshes() -> None:
    results = (
        make_result("coarse", 0.0100),
        make_result("medium", 0.0095),
        make_result("fine", 0.0094),
    )

    comparisons = compare_consecutive_results(
        results
    )

    assert comparisons[0].coarse_label == "coarse"
    assert comparisons[0].fine_label == "medium"

    assert comparisons[1].coarse_label == "medium"
    assert comparisons[1].fine_label == "fine"


def test_convergence_requires_two_results() -> None:
    results = (
        make_result("coarse", 0.0100),
    )

    with pytest.raises(ValueError):
        compare_consecutive_results(
            results
        )


def test_is_converged_when_final_change_is_below_tolerance() -> None:
    results = (
        make_result("coarse", 0.0100),
        make_result("medium", 0.0095),
        make_result("fine", 0.00945),
    )

    assert is_converged(
        results,
        tolerance=0.01,
    )


def test_is_not_converged_when_final_change_is_too_large() -> None:
    results = (
        make_result("coarse", 0.0100),
        make_result("medium", 0.0095),
        make_result("fine", 0.0090),
    )

    assert not is_converged(
        results,
        tolerance=0.01,
    )


def test_result_can_be_marked_simulated() -> None:
    result = make_result(
        "coarse",
        0.0100,
    )

    assert (
        result.evidence
        == EvidenceClass.SIMULATED
    )