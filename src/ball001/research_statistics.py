"""Scientific decision primitives that do not invent missing statistics.

A supplied confidence interval must be computed externally with the correct
independent unit, hierarchical model and prespecified endpoint. This module
checks its decision logic only; it does not claim to compute a valid CI.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class QuantificationState(StrEnum):
    NOT_DETECTED = "NOT_DETECTED"
    DETECTED_BELOW_LOQ = "DETECTED_BELOW_LOQ"
    QUANTIFIED = "QUANTIFIED"


@dataclass(frozen=True)
class AnalyticalObservation:
    """LOD and LOQ are in the same units as measured concentration."""

    state: QuantificationState
    lod: float
    loq: float
    quantified_value: float | None = None

    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in (self.lod, self.loq)):
            raise ValueError("LOD/LOQ must be finite.")
        if self.lod < 0 or self.loq < self.lod:
            raise ValueError("LOD/LOQ must be non-negative and ordered.")
        if self.state is QuantificationState.QUANTIFIED:
            if (
                self.quantified_value is None
                or not math.isfinite(self.quantified_value)
                or self.quantified_value < self.loq
            ):
                raise ValueError("Quantified value must be at least LOQ.")
        elif self.quantified_value is not None:
            raise ValueError(
                "Do not assign an exact concentration to a censored result."
            )

    @property
    def censoring_interval(self) -> tuple[float, float | None]:
        if self.state is QuantificationState.NOT_DETECTED:
            return 0.0, self.lod
        if self.state is QuantificationState.DETECTED_BELOW_LOQ:
            return self.lod, self.loq
        assert self.quantified_value is not None
        return self.quantified_value, self.quantified_value


@dataclass(frozen=True)
class EquivalenceInterval:
    """Externally computed CI and preregistered margins in matching units."""

    metric: str
    ci_lower: float
    ci_upper: float
    margin_lower: float
    margin_upper: float
    confidence_level: float
    independent_units: int
    analysis_method: str
    preregistration_id: str

    def __post_init__(self) -> None:
        values = (
            self.ci_lower, self.ci_upper,
            self.margin_lower, self.margin_upper, self.confidence_level,
        )
        if not all(math.isfinite(x) for x in values):
            raise ValueError("CI and margins must be finite.")
        if self.ci_lower > self.ci_upper:
            raise ValueError("CI bounds must be ordered.")
        if self.margin_lower >= self.margin_upper:
            raise ValueError("Equivalence margins must be ordered.")
        if not 0.9 <= self.confidence_level < 1.0:
            raise ValueError("TOST decision requires a suitable CI level.")
        if self.independent_units < 2:
            raise ValueError("At least two independent units required.")
        if not all(
            (self.metric, self.analysis_method, self.preregistration_id)
        ):
            raise ValueError("Metric, method and preregistration ID required.")

    @property
    def equivalent_by_interval(self) -> bool:
        """CI-in-margin logic only; validity of supplied CI is external."""

        return (
            self.ci_lower > self.margin_lower
            and self.ci_upper < self.margin_upper
        )


def all_critical_metrics_equivalent(
    intervals: tuple[EquivalenceInterval, ...],
) -> bool:
    if not intervals:
        raise ValueError("No prespecified mechanical metrics supplied.")
    return all(item.equivalent_by_interval for item in intervals)
