"""Traceable evidence ledger for BALL 001 materials-health claims.

A PASS means that required evidence artifacts, checksums, QC, and review
metadata exist. It is not a claim of safety, clinical causation, or external
laboratory accreditation. Files can be tampered with before registration;
independent scientific review remains necessary.
"""

from __future__ import annotations

import csv
import hashlib
import math
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path


class ReviewOutcome(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ClaimStatus(StrEnum):
    PENDING = "PENDING"
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"


GATE_KINDS = {
    "G0_MATERIAL_IDENTITY": "MATERIAL_ID",
    "G1_TOTAL_CONTENT": "CONTENT_ASSAY",
    "G2_SWEAT_MIGRATION": "MIGRATION_ASSAY",
    "G3_REALISTIC_TRANSFER": "CONTACT_STUDY",
    "G4_DERMAL_UPTAKE": "DERMAL_STUDY",
    "G5_DOSE_CONTEXT": "TOXICOLOGY_REVIEW",
    "G6_ENGINEERING_EQUIVALENCE": "MECHANICAL_TEST",
}
GATES = tuple(GATE_KINDS)
RAW_REQUIRED = frozenset(
    {
        "G1_TOTAL_CONTENT",
        "G2_SWEAT_MIGRATION",
        "G3_REALISTIC_TRANSFER",
        "G4_DERMAL_UPTAKE",
        "G6_ENGINEERING_EQUIVALENCE",
    }
)
LAB_REQUIRED = frozenset({"G1_TOTAL_CONTENT", "G2_SWEAT_MIGRATION"})


@dataclass(frozen=True)
class EvidenceRecord:
    record_id: str
    gate: str
    kind: str
    sample_id: str
    lot_id: str
    method_id: str
    artifact_path: str
    artifact_sha256: str
    raw_path: str = ""
    raw_sha256: str = ""
    calibration_path: str = ""
    calibration_sha256: str = ""
    qc_path: str = ""
    qc_sha256: str = ""
    reviewer: str = ""
    reviewed_on: str = ""
    review_outcome: ReviewOutcome = ReviewOutcome.PENDING


@dataclass(frozen=True)
class ClaimRecord:
    claim_id: str
    claim_type: str
    claim_text: str
    status: ClaimStatus
    gate: str
    sample_id: str
    lot_id: str
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuditResult:
    valid: bool
    errors: tuple[str, ...]


@dataclass(frozen=True)
class SpecimenGate:
    gate: str
    status: str
    evidence_ids: tuple[str, ...]
    reason: str


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _checked_path(root: Path, relative_path: str, expected: str) -> Path:
    if not relative_path or not expected:
        raise ValueError("Missing path or SHA-256 digest.")
    if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise ValueError("SHA-256 must be a lowercase 64-character hex digest.")
    resolved_root = root.resolve()
    path = (resolved_root / relative_path).resolve()
    if not path.is_relative_to(resolved_root):
        raise ValueError("Artifact path escapes the evidence root.")
    if not path.is_file():
        raise ValueError(f"Evidence artifact missing: {relative_path}")
    if file_sha256(path) != expected:
        raise ValueError(f"SHA-256 mismatch: {relative_path}")
    return path


def _qc_check(path: Path) -> None:
    """Check recorded numerical QC against explicit method-specific limits."""

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError("QC CSV must contain exactly one data row.")
    row = rows[0]
    keys = (
        "blank_ug",
        "max_blank_ug",
        "spike_recovery_percent",
        "min_spike_recovery_percent",
        "max_spike_recovery_percent",
        "duplicate_rpd_percent",
        "max_duplicate_rpd_percent",
    )
    try:
        values = {key: float(row[key]) for key in keys}
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("QC CSV missing or invalid numeric fields.") from exc
    if not all(math.isfinite(v) and v >= 0 for v in values.values()):
        raise ValueError("QC contains non-finite or negative values.")
    if values["min_spike_recovery_percent"] > values["max_spike_recovery_percent"]:
        raise ValueError("Invalid QC recovery range.")
    if values["blank_ug"] > values["max_blank_ug"]:
        raise ValueError("QC blank exceeds limit.")
    if not (
        values["min_spike_recovery_percent"]
        <= values["spike_recovery_percent"]
        <= values["max_spike_recovery_percent"]
    ):
        raise ValueError("QC spike recovery outside limits.")
    if values["duplicate_rpd_percent"] > values["max_duplicate_rpd_percent"]:
        raise ValueError("QC duplicate RPD exceeds limit.")


def audit_evidence(record: EvidenceRecord, root: Path) -> AuditResult:
    errors: list[str] = []
    if record.gate not in GATE_KINDS:
        errors.append("unknown_gate")
    elif record.kind != GATE_KINDS[record.gate]:
        errors.append("evidence_kind_does_not_match_gate")
    if not all(
        (record.record_id, record.sample_id, record.lot_id, record.method_id)
    ):
        errors.append("missing_specimen_or_method_provenance")
    if record.review_outcome is not ReviewOutcome.ACCEPTED:
        errors.append("independent_review_not_accepted")
    if not record.reviewer or not record.reviewed_on:
        errors.append("missing_reviewer_or_review_date")
    else:
        try:
            reviewed = date.fromisoformat(record.reviewed_on)
            if reviewed > datetime.now(UTC).date():
                errors.append("review_date_in_future")
        except ValueError:
            errors.append("invalid_review_date")

    for label, relative, sha in (
        ("artifact", record.artifact_path, record.artifact_sha256),
        ("raw", record.raw_path, record.raw_sha256),
        ("calibration", record.calibration_path, record.calibration_sha256),
        ("qc", record.qc_path, record.qc_sha256),
    ):
        required = label == "artifact" or (
            label == "raw" and record.gate in RAW_REQUIRED
        ) or (label in ("calibration", "qc") and record.gate in LAB_REQUIRED)
        if not required and not relative and not sha:
            continue
        try:
            path = _checked_path(root, relative, sha)
            if label == "qc" and record.gate in LAB_REQUIRED:
                _qc_check(path)
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
    return AuditResult(not errors, tuple(errors))


def evaluate_specimen_gates(
    records: tuple[EvidenceRecord, ...],
    root: Path,
    *,
    sample_id: str,
    lot_id: str,
) -> tuple[SpecimenGate, ...]:
    """Do not mix evidence from different specimens or production lots."""

    reached = True
    output: list[SpecimenGate] = []
    for gate in GATES:
        if not reached:
            output.append(SpecimenGate(gate, "NOT_REACHED", (), "Earlier gate open."))
            continue
        accepted = tuple(
            record.record_id
            for record in records
            if record.gate == gate
            and record.sample_id == sample_id
            and record.lot_id == lot_id
            and audit_evidence(record, root).valid
        )
        if accepted:
            output.append(
                SpecimenGate(gate, "PASS", accepted, "Evidence accepted for audit.")
            )
        else:
            output.append(
                SpecimenGate(
                    gate,
                    "INDETERMINATE",
                    (),
                    "No verified evidence for this specimen and lot.",
                )
            )
            reached = False
    return tuple(output)


def audit_claim(
    claim: ClaimRecord,
    records: tuple[EvidenceRecord, ...],
    root: Path,
) -> AuditResult:
    """Prevent a literature or analogue claim from masquerading as product data."""

    if claim.status is ClaimStatus.PENDING:
        return AuditResult(True, ())
    errors: list[str] = []
    if claim.claim_type == "HEALTH_CAUSATION":
        errors.append("health_causation_requires_separate_human_study")
    if claim.gate not in GATE_KINDS:
        errors.append("unsupported_claim_requires_product_evidence_gate")
    if not claim.evidence_ids:
        errors.append("supported_claim_has_no_evidence_ids")
    indexed = {record.record_id: record for record in records}
    for record_id in claim.evidence_ids:
        record = indexed.get(record_id)
        if record is None:
            errors.append(f"unknown_evidence_id:{record_id}")
            continue
        if (
            record.gate != claim.gate
            or record.sample_id != claim.sample_id
            or record.lot_id != claim.lot_id
        ):
            errors.append(f"evidence_scope_mismatch:{record_id}")
        result = audit_evidence(record, root)
        if not result.valid:
            errors.append(f"unverified_evidence:{record_id}")
    if claim.gate in GATE_KINDS:
        decisions = evaluate_specimen_gates(
            records, root, sample_id=claim.sample_id, lot_id=claim.lot_id
        )
        matching = next(x for x in decisions if x.gate == claim.gate)
        if matching.status != "PASS":
            errors.append("prior_evidence_gates_not_satisfied")
    return AuditResult(not errors, tuple(errors))


def verified_migration_row(
    record: EvidenceRecord,
    root: Path,
    *,
    target: str,
    migration_rate_ug_cm2_h: float,
    medium: str,
    temperature_c: float,
) -> None:
    """Bind an exposure input to a hashed, QC-accepted assay result.

    The assay artifact is a one-row CSV with the columns checked below.
    This is a provenance check, not independent validation of the laboratory.
    """

    if record.gate != "G2_SWEAT_MIGRATION":
        raise ValueError("Migration input requires G2 evidence.")
    result = audit_evidence(record, root)
    if not result.valid:
        raise ValueError("Unverified migration evidence: " + "; ".join(result.errors))
    path = _checked_path(root, record.artifact_path, record.artifact_sha256)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError("Migration assay artifact must contain one data row.")
    row = rows[0]
    try:
        assay_rate = float(row["migration_rate_ug_cm2_h"])
        assay_temperature = float(row["temperature_c"])
        identity = (
            row["sample_id"] == record.sample_id
            and row["lot_id"] == record.lot_id
            and row["target"] == target
            and row["medium"] == medium
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Migration assay missing required fields.") from exc
    if not identity or not (
        math.isfinite(assay_rate)
        and assay_rate >= 0
        and math.isclose(assay_rate, migration_rate_ug_cm2_h, rel_tol=1e-9)
        and math.isclose(assay_temperature, temperature_c, abs_tol=1e-6)
    ):
        raise ValueError("Migration input differs from audited assay artifact.")


EVIDENCE_FIELDS = tuple(EvidenceRecord.__dataclass_fields__)
CLAIM_FIELDS = (
    "claim_id", "claim_type", "claim_text", "status", "gate",
    "sample_id", "lot_id", "evidence_ids"
)


def load_evidence_csv(path: Path) -> tuple[EvidenceRecord, ...]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not set(EVIDENCE_FIELDS).issubset(
            reader.fieldnames
        ):
            raise ValueError("Evidence ledger CSV has missing columns.")
        records = tuple(
            EvidenceRecord(
                **{field: row[field] for field in EVIDENCE_FIELDS
                   if field != "review_outcome"},
                review_outcome=ReviewOutcome(row["review_outcome"]),
            )
            for row in reader
        )
    ids = [record.record_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate evidence record IDs.")
    return records


def load_claims_csv(path: Path) -> tuple[ClaimRecord, ...]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not set(CLAIM_FIELDS).issubset(
            reader.fieldnames
        ):
            raise ValueError("Claim ledger CSV has missing columns.")
        claims = tuple(
            ClaimRecord(
                claim_id=row["claim_id"],
                claim_type=row["claim_type"],
                claim_text=row["claim_text"],
                status=ClaimStatus(row["status"]),
                gate=row["gate"],
                sample_id=row["sample_id"],
                lot_id=row["lot_id"],
                evidence_ids=tuple(
                    x.strip() for x in row["evidence_ids"].split(";") if x.strip()
                ),
            )
            for row in reader
        )
    ids = [claim.claim_id for claim in claims]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate claim IDs.")
    return claims
