from dataclasses import dataclass
from itertools import pairwise

from ball001.design import EvidenceClass


@dataclass(frozen=True)
class StructuralConvergenceResult:
    mesh_label: str
    characteristic_length_mm: float
    node_count: int
    element_count: int
    displacement_m: float
    evidence: EvidenceClass


@dataclass(frozen=True)
class StructuralConvergenceComparison:
    coarse_label: str
    fine_label: str
    relative_displacement_change: float


def relative_change(
    previous_value: float,
    current_value: float,
) -> float:
    if previous_value == 0.0:
        raise ValueError(
            "Previous value must be nonzero "
            "for relative-change calculation."
        )

    return abs(
        current_value - previous_value
    ) / abs(previous_value)


def compare_consecutive_results(
    results: tuple[
        StructuralConvergenceResult,
        ...,
    ],
) -> tuple[
    StructuralConvergenceComparison,
    ...,
]:
    if len(results) < 2:
        raise ValueError(
            "At least two structural results are required "
            "for a convergence comparison."
        )

    comparisons = []

    for previous, current in pairwise(results):
        comparisons.append(
            StructuralConvergenceComparison(
                coarse_label=previous.mesh_label,
                fine_label=current.mesh_label,
                relative_displacement_change=(
                    relative_change(
                        previous.displacement_m,
                        current.displacement_m,
                    )
                ),
            )
        )

    return tuple(comparisons)


def is_converged(
    results: tuple[
        StructuralConvergenceResult,
        ...,
    ],
    tolerance: float,
) -> bool:
    if tolerance <= 0.0:
        raise ValueError(
            "Convergence tolerance must be positive."
        )

    comparisons = compare_consecutive_results(
        results
    )

    return (
        comparisons[-1]
        .relative_displacement_change
        <= tolerance
    )