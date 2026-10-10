"""Evidence-gated screening tools for chemical exposure from volleyball materials.

This module is deliberately conservative. It does not diagnose disease, infer
that a commercial volleyball contains a chemical, or convert a hazard into a
health-risk claim without measured product and exposure data.

The intended workflow is:
material identity -> total content -> migration -> transfer/uptake -> dose context
-> engineering equivalence.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from statistics import fmean

from ball001.research_integrity import EvidenceRecord, verified_migration_row


class GateStatus(StrEnum):
    """State of a sequential evidence gate."""

    PASS = "PASS"
    ESCALATE = "ESCALATE"
    INDETERMINATE = "INDETERMINATE"
    NOT_REACHED = "NOT_REACHED"


class EvidenceBasis(StrEnum):
    """Provenance class for a material-health input."""

    REGULATORY = "REGULATORY"
    LITERATURE = "LITERATURE"
    MATERIAL_ANALOGUE = "MATERIAL_ANALOGUE"
    PRODUCT_MEASURED = "PRODUCT_MEASURED"
    SUPPLIER_DISCLOSURE = "SUPPLIER_DISCLOSURE"
    HYPOTHESIS = "HYPOTHESIS"


@dataclass(frozen=True)
class ChemicalTarget:
    target: str
    cas: str
    chemical_class: str
    health_domain: str
    material_relevance: str
    preferred_screen: str
    product_presence: str
    evidence_basis: EvidenceBasis
    source: str


@dataclass(frozen=True)
class ContactScenario:
    """Observed or deliberately conservative hand/ball contact scenario."""

    cumulative_contact_seconds_per_session: float
    sessions_per_week: float
    contact_area_cm2: float
    body_mass_kg: float
    transfer_efficiency_fraction: float = 1.0

    def __post_init__(self) -> None:
        values = (
            self.cumulative_contact_seconds_per_session,
            self.sessions_per_week,
            self.contact_area_cm2,
            self.body_mass_kg,
            self.transfer_efficiency_fraction,
        )
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Contact scenario must contain finite values.")
        if self.cumulative_contact_seconds_per_session < 0:
            raise ValueError("Cumulative contact time must be non-negative.")
        if self.sessions_per_week < 0:
            raise ValueError("Sessions per week must be non-negative.")
        if self.contact_area_cm2 <= 0:
            raise ValueError("Contact area must be positive.")
        if self.body_mass_kg <= 0:
            raise ValueError("Body mass must be positive.")
        if not 0 <= self.transfer_efficiency_fraction <= 1:
            raise ValueError("Transfer efficiency must be between 0 and 1.")

    @property
    def mean_daily_contact_hours(self) -> float:
        weekly_seconds = (
            self.cumulative_contact_seconds_per_session * self.sessions_per_week
        )
        return weekly_seconds / 7.0 / 3600.0


@dataclass(frozen=True)
class MigrationReplicate:
    migrated_mass_ug: float
    exposed_area_cm2: float
    duration_h: float

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(v)
            for v in (self.migrated_mass_ug, self.exposed_area_cm2, self.duration_h)
        ):
            raise ValueError("Migration replicate must contain finite values.")
        if self.migrated_mass_ug < 0:
            raise ValueError("Migrated mass must be non-negative.")
        if self.exposed_area_cm2 <= 0:
            raise ValueError("Exposed area must be positive.")
        if self.duration_h <= 0:
            raise ValueError("Migration duration must be positive.")

    @property
    def migration_rate_ug_cm2_h(self) -> float:
        return self.migrated_mass_ug / self.exposed_area_cm2 / self.duration_h


@dataclass(frozen=True)
class QCCriteria:
    max_blank_ug: float
    min_spike_recovery_percent: float
    max_spike_recovery_percent: float
    max_duplicate_rpd_percent: float

    def __post_init__(self) -> None:
        values = (
            self.max_blank_ug, self.min_spike_recovery_percent,
            self.max_spike_recovery_percent, self.max_duplicate_rpd_percent,
        )
        if not all(math.isfinite(v) and v >= 0 for v in values):
            raise ValueError("QC criteria must be finite and non-negative.")
        if self.min_spike_recovery_percent > self.max_spike_recovery_percent:
            raise ValueError("Invalid spike recovery acceptance range.")


@dataclass(frozen=True)
class LabQualityControl:
    blank_ug: float
    spike_recovery_percent: float
    duplicate_rpd_percent: float

    def __post_init__(self) -> None:
        values = (
            self.blank_ug, self.spike_recovery_percent,
            self.duplicate_rpd_percent,
        )
        if not all(math.isfinite(v) and v >= 0 for v in values):
            raise ValueError("QC measurements must be finite and non-negative.")


@dataclass(frozen=True)
class QCDecision:
    accepted: bool
    failures: tuple[str, ...]


def evaluate_lab_qc(
    record: LabQualityControl,
    criteria: QCCriteria,
) -> QCDecision:
    """Apply explicit lab SOP limits rather than hidden universal thresholds."""

    failures: list[str] = []
    if record.blank_ug > criteria.max_blank_ug:
        failures.append("blank_above_acceptance_limit")
    if not (
        criteria.min_spike_recovery_percent
        <= record.spike_recovery_percent
        <= criteria.max_spike_recovery_percent
    ):
        failures.append("spike_recovery_outside_acceptance_range")
    if record.duplicate_rpd_percent > criteria.max_duplicate_rpd_percent:
        failures.append("duplicate_rpd_above_acceptance_limit")
    return QCDecision(accepted=not failures, failures=tuple(failures))


@dataclass(frozen=True)
class MigrationMeasurement:
    target: str
    migration_rate_ug_cm2_h: float
    medium: str
    temperature_c: float
    evidence_basis: EvidenceBasis = EvidenceBasis.HYPOTHESIS
    evidence_record_id: str = ""

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(v)
            for v in (self.migration_rate_ug_cm2_h, self.temperature_c)
        ):
            raise ValueError("Migration measurement must be finite.")
        if self.migration_rate_ug_cm2_h < 0:
            raise ValueError("Migration rate must be non-negative.")


def migration_measurement_from_replicates(
    target: str,
    replicates: tuple[MigrationReplicate, ...],
    *,
    medium: str,
    temperature_c: float,
) -> MigrationMeasurement:
    if len(replicates) < 3:
        raise ValueError("At least three migration replicates are required.")
    rate = fmean(r.migration_rate_ug_cm2_h for r in replicates)
    return MigrationMeasurement(
        target=target,
        migration_rate_ug_cm2_h=rate,
        medium=medium,
        temperature_c=temperature_c,
    )


@dataclass(frozen=True)
class ExternalDermalEstimate:
    target: str
    external_ug_per_day: float
    external_ug_per_kg_day: float
    absorbed_ug_per_kg_day: float | None


def estimate_external_dermal_exposure(
    measurement: MigrationMeasurement,
    scenario: ContactScenario,
    *,
    dermal_absorption_fraction: float | None = None,
    evidence_record: EvidenceRecord | None = None,
    evidence_root: Path | None = None,
) -> ExternalDermalEstimate:
    """Screen external exposure only from a hash-audited product assay."""

    if measurement.evidence_basis is not EvidenceBasis.PRODUCT_MEASURED:
        raise ValueError(
            "Dose estimation requires a product-measured migration rate, not an "
            "analogue or hypothesis."
        )
    if evidence_record is None or evidence_root is None:
        raise ValueError("Exposure calculation requires audited G2 evidence.")
    if (
        not measurement.evidence_record_id
        or measurement.evidence_record_id != evidence_record.record_id
    ):
        raise ValueError("Migration evidence record ID mismatch.")
    verified_migration_row(
        evidence_record,
        evidence_root,
        target=measurement.target,
        migration_rate_ug_cm2_h=measurement.migration_rate_ug_cm2_h,
        medium=measurement.medium,
        temperature_c=measurement.temperature_c,
    )
    if dermal_absorption_fraction is not None and not (
        math.isfinite(dermal_absorption_fraction)
        and 0 <= dermal_absorption_fraction <= 1
    ):
        raise ValueError("Dermal absorption fraction must be between 0 and 1.")

    external_ug_per_day = (
        measurement.migration_rate_ug_cm2_h
        * scenario.contact_area_cm2
        * scenario.mean_daily_contact_hours
        * scenario.transfer_efficiency_fraction
    )
    external_ug_per_kg_day = external_ug_per_day / scenario.body_mass_kg
    absorbed = None
    if dermal_absorption_fraction is not None:
        absorbed = external_ug_per_kg_day * dermal_absorption_fraction

    return ExternalDermalEstimate(
        target=measurement.target,
        external_ug_per_day=external_ug_per_day,
        external_ug_per_kg_day=external_ug_per_kg_day,
        absorbed_ug_per_kg_day=absorbed,
    )


@dataclass(frozen=True)
class DoseContext:
    absorbed_ug_per_kg_day: float
    reference_ug_per_kg_day: float

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(v)
            for v in (self.absorbed_ug_per_kg_day, self.reference_ug_per_kg_day)
        ):
            raise ValueError("Dose context must be finite.")
        if self.absorbed_ug_per_kg_day < 0:
            raise ValueError("Absorbed dose must be non-negative.")
        if self.reference_ug_per_kg_day <= 0:
            raise ValueError("Reference value must be positive.")

    @property
    def screening_ratio(self) -> float:
        return self.absorbed_ug_per_kg_day / self.reference_ug_per_kg_day


@dataclass(frozen=True)
class EngineeringConstraint:
    name: str
    baseline_value: float
    candidate_value: float
    relative_tolerance: float

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(v)
            for v in (self.baseline_value, self.candidate_value, self.relative_tolerance)
        ):
            raise ValueError("Engineering constraint must be finite.")
        if self.baseline_value == 0:
            raise ValueError("Baseline value cannot be zero.")
        if self.relative_tolerance < 0:
            raise ValueError("Relative tolerance must be non-negative.")

    @property
    def relative_difference(self) -> float:
        return abs(self.candidate_value - self.baseline_value) / abs(
            self.baseline_value
        )

    @property
    def passes(self) -> bool:
        return self.relative_difference <= self.relative_tolerance


def performance_equivalence(
    constraints: tuple[EngineeringConstraint, ...],
) -> bool:
    if not constraints:
        raise ValueError("At least one engineering constraint is required.")
    return all(constraint.passes for constraint in constraints)


@dataclass(frozen=True)
class EvidenceGateInputs:
    material_identity_confirmed: bool = False
    total_content_measured: bool = False
    migration_measured: bool = False
    realistic_transfer_characterized: bool = False
    dermal_uptake_characterized: bool = False
    toxicological_reference_identified: bool = False
    performance_equivalence_verified: bool = False


@dataclass(frozen=True)
class GateDecision:
    gate: str
    status: GateStatus
    reason: str


def evaluate_evidence_gates(
    inputs: EvidenceGateInputs,
) -> tuple[GateDecision, ...]:
    """Illustrative checklist ONLY; use audited specimen gates for claims.

    These Boolean inputs are not evidence records. PASS here never authorizes
    a product measurement, exposure, safety or health conclusion.
    """

    checks = (
        ("G0_MATERIAL_IDENTITY", inputs.material_identity_confirmed,
         "Layer chemistry / material family is identified."),
        ("G1_TOTAL_CONTENT", inputs.total_content_measured,
         "Targeted total-content chemistry has been measured with QA/QC."),
        ("G2_SWEAT_MIGRATION", inputs.migration_measured,
         "Migration into a skin-relevant medium has been measured."),
        ("G3_REALISTIC_TRANSFER", inputs.realistic_transfer_characterized,
         "Realistic ball-handling transfer conditions are characterized."),
        ("G4_DERMAL_UPTAKE", inputs.dermal_uptake_characterized,
         "Dermal uptake is characterized or defensibly bounded."),
        ("G5_DOSE_CONTEXT", inputs.toxicological_reference_identified,
         "A chemical-specific reference point exists for dose context."),
        ("G6_ENGINEERING_EQUIVALENCE", inputs.performance_equivalence_verified,
         "Material substitution preserves required ball performance."),
    )

    reached = True
    decisions: list[GateDecision] = []
    for gate, complete, reason in checks:
        if not reached:
            decisions.append(
                GateDecision(
                    gate=gate,
                    status=GateStatus.NOT_REACHED,
                    reason="Prior evidence gate is incomplete.",
                )
            )
            continue
        if complete:
            decisions.append(GateDecision(gate, GateStatus.PASS, reason))
        else:
            decisions.append(
                GateDecision(
                    gate,
                    GateStatus.INDETERMINATE,
                    f"Missing evidence: {reason}",
                )
            )
            reached = False
    return tuple(decisions)


def load_watchlist(path: str | Path) -> tuple[ChemicalTarget, ...]:
    records: list[ChemicalTarget] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            records.append(
                ChemicalTarget(
                    target=row["target"],
                    cas=row["cas"],
                    chemical_class=row["chemical_class"],
                    health_domain=row["health_domain"],
                    material_relevance=row["material_relevance"],
                    preferred_screen=row["preferred_screen"],
                    product_presence=row["product_presence"],
                    evidence_basis=EvidenceBasis(row["evidence_basis"]),
                    source=row["source"],
                )
            )
    return tuple(records)
