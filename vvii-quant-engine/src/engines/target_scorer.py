"""Deterministic four-pillar diligence score. Scale is 0–5. Gate is 3.75."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Decimal

from db.provenance import content_sha256, stamp
from pydantic import BaseModel, ConfigDict

_SCORE_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)

TEARSHEET_THRESHOLD = Decimal("3.75")
_WEIGHTS = {
    "technical_ingestion": Decimal("0.30"),
    "workflow_lock_in": Decimal("0.25"),
    "catalyst": Decimal("0.25"),
    "exit_path": Decimal("0.20"),
}
_STRATEGIC = {
    "hudl",
    "otto sport",
    "catapult",
    "seatgeek",
    "paciolan",
    "orthopedic health system",
    "orthopedic health systems",
}
_FORCE_PLATE_R = Decimal("0.85")


class TargetEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_id: str
    display_name: str
    record_status: str
    source_url: str
    hardware_agnostic: bool
    frame_rate_fps: Decimal
    single_camera: bool
    exports_live_dvw: bool
    integrates_dvw: bool
    integrates_hudl: bool
    integrates_otto_or_sportwrench: bool
    standalone_only: bool
    addresses_crs: bool
    addresses_centerline: bool
    addresses_logos: bool
    force_plate_r: Decimal | None
    peer_reviewed_validation: bool
    named_acquirers: tuple[str, ...]


class DiligenceResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_id: str
    display_name: str
    record_status: str
    source_url: str
    technical_ingestion: Decimal
    workflow_lock_in: Decimal
    catalyst: Decimal
    exit_path: Decimal
    composite: Decimal
    gate_pass: bool
    input_sha256: str


def _q2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def _q4(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)


def _normalize_acquirer(name: str) -> str:
    return " ".join(name.casefold().split())


def technical_ingestion_score(evidence: TargetEvidence) -> Decimal:
    step = Decimal("1.25")
    score = Decimal(0)
    if evidence.hardware_agnostic:
        score += step
    if evidence.frame_rate_fps >= Decimal(60):
        score += step
    if evidence.single_camera:
        score += step
    if evidence.exports_live_dvw:
        score += step
    return _q2(score)


def workflow_lock_in_score(evidence: TargetEvidence) -> Decimal:
    native = evidence.integrates_dvw
    platform = evidence.integrates_hudl or evidence.integrates_otto_or_sportwrench
    if native and platform:
        return Decimal("5.00")
    if native:
        return Decimal("4.00")
    if platform:
        return Decimal("3.00")
    if evidence.standalone_only:
        return Decimal("1.00")
    return Decimal("0.00")


def catalyst_score(evidence: TargetEvidence) -> Decimal:
    hits = sum(
        (
            evidence.addresses_crs,
            evidence.addresses_centerline,
            evidence.addresses_logos,
        )
    )
    correlation = evidence.force_plate_r
    validated = (
        evidence.peer_reviewed_validation
        and correlation is not None
        and correlation >= _FORCE_PLATE_R
    )
    if hits and validated:
        return Decimal("5.00")
    if validated:
        return Decimal("4.00")
    if hits >= 2:
        return Decimal("4.00")
    if hits == 1:
        return Decimal("3.00")
    if correlation is not None:
        return Decimal("1.00")
    return Decimal("0.00")


def exit_path_score(evidence: TargetEvidence) -> Decimal:
    recognized: set[str] = set()
    outside = False
    for name in evidence.named_acquirers:
        normalized = _normalize_acquirer(name)
        if normalized in _STRATEGIC:
            recognized.add(normalized)
        elif normalized:
            outside = True
    count = len(recognized)
    if count >= 3:
        return Decimal("5.00")
    if count == 2:
        return Decimal("4.00")
    if count == 1:
        return Decimal("3.00")
    if outside:
        return Decimal("1.00")
    return Decimal("0.00")


def evidence_payload(evidence: TargetEvidence) -> dict:
    payload = evidence.model_dump(mode="json")
    payload["named_acquirers"] = sorted(
        _normalize_acquirer(name) for name in evidence.named_acquirers
    )
    return payload


def score_target(evidence: TargetEvidence) -> DiligenceResult:
    payload = evidence_payload(evidence)
    provenance = stamp(evidence.source_url, _SCORE_EPOCH, payload)
    technical = technical_ingestion_score(evidence)
    workflow = workflow_lock_in_score(evidence)
    catalyst = catalyst_score(evidence)
    exit_path = exit_path_score(evidence)
    composite = _q4(
        technical * _WEIGHTS["technical_ingestion"]
        + workflow * _WEIGHTS["workflow_lock_in"]
        + catalyst * _WEIGHTS["catalyst"]
        + exit_path * _WEIGHTS["exit_path"]
    )
    return DiligenceResult(
        target_id=evidence.target_id,
        display_name=evidence.display_name,
        record_status=evidence.record_status,
        source_url=provenance.source_url,
        technical_ingestion=technical,
        workflow_lock_in=workflow,
        catalyst=catalyst,
        exit_path=exit_path,
        composite=composite,
        gate_pass=composite >= TEARSHEET_THRESHOLD,
        input_sha256=content_sha256(payload),
    )
