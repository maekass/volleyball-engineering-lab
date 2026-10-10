"""Synthetic fixtures only; not actual BALL 001 experimental measurements."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ball001.research_integrity import (
    EvidenceRecord,
    ReviewOutcome,
    file_sha256,
)


def _write_csv(path: Path, header: tuple[str, ...], values: tuple[object, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerow(values)


@pytest.fixture
def audited_migration_case(tmp_path: Path) -> tuple[EvidenceRecord, Path]:
    """Hash-checked synthetic laboratory evidence for unit tests only."""

    assay = tmp_path / "assay.csv"
    _write_csv(
        assay,
        (
            "sample_id", "lot_id", "target", "medium",
            "temperature_c", "migration_rate_ug_cm2_h",
        ),
        (
            "SYNTHETIC-TEST", "SYNTHETIC-LOT", "example",
            "synthetic sweat", 37.0, 0.2,
        ),
    )
    raw = tmp_path / "raw.csv"
    _write_csv(raw, ("instrument_response",), (12.5,))
    calibration = tmp_path / "calibration.csv"
    _write_csv(calibration, ("standard_ug", "response"), (1.0, 12.5))
    qc = tmp_path / "qc.csv"
    _write_csv(
        qc,
        (
            "blank_ug", "max_blank_ug", "spike_recovery_percent",
            "min_spike_recovery_percent", "max_spike_recovery_percent",
            "duplicate_rpd_percent", "max_duplicate_rpd_percent",
        ),
        (0.02, 0.1, 95.0, 70.0, 130.0, 8.0, 30.0),
    )
    record = EvidenceRecord(
        record_id="EVID-SYNTHETIC-001",
        gate="G2_SWEAT_MIGRATION",
        kind="MIGRATION_ASSAY",
        sample_id="SYNTHETIC-TEST",
        lot_id="SYNTHETIC-LOT",
        method_id="SYNTHETIC-METHOD",
        artifact_path="assay.csv",
        artifact_sha256=file_sha256(assay),
        raw_path="raw.csv",
        raw_sha256=file_sha256(raw),
        calibration_path="calibration.csv",
        calibration_sha256=file_sha256(calibration),
        qc_path="qc.csv",
        qc_sha256=file_sha256(qc),
        reviewer="Unit-test reviewer",
        reviewed_on=datetime.now(UTC).date().isoformat(),
        review_outcome=ReviewOutcome.ACCEPTED,
    )
    return record, tmp_path
