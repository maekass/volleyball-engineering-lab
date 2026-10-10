"""Fail-closed tests for scientific provenance and sequential gates."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ball001.research_integrity import (
    ClaimRecord,
    ClaimStatus,
    ReviewOutcome,
    audit_claim,
    audit_evidence,
    evaluate_specimen_gates,
    load_claims_csv,
    load_evidence_csv,
    verified_migration_row,
)


def test_hashed_migration_evidence_passes_document_audit(
    audited_migration_case,
) -> None:
    record, root = audited_migration_case
    assert audit_evidence(record, root).valid


def test_tampering_invalidates_audited_evidence(audited_migration_case) -> None:
    record, root = audited_migration_case
    (root / "raw.csv").write_text("modified data\n", encoding="utf-8")
    result = audit_evidence(record, root)
    assert not result.valid
    assert any("SHA-256 mismatch" in e for e in result.errors)


def test_unreviewed_evidence_fails(audited_migration_case) -> None:
    record, root = audited_migration_case
    unreviewed = replace(record, review_outcome=ReviewOutcome.PENDING)
    assert not audit_evidence(unreviewed, root).valid


def test_rejected_qc_fails_even_with_correct_checksum(
    audited_migration_case,
) -> None:
    from ball001.research_integrity import file_sha256

    record, root = audited_migration_case
    qc = root / "qc.csv"
    qc.write_text(
        "blank_ug,max_blank_ug,spike_recovery_percent,"
        "min_spike_recovery_percent,max_spike_recovery_percent,"
        "duplicate_rpd_percent,max_duplicate_rpd_percent\n"
        "0.3,0.1,95,70,130,8,30\n",
        encoding="utf-8",
    )
    updated = replace(record, qc_sha256=file_sha256(qc))
    result = audit_evidence(updated, root)
    assert not result.valid
    assert any("blank exceeds limit" in e for e in result.errors)


def test_path_traversal_rejected(audited_migration_case) -> None:
    record, root = audited_migration_case
    escaped = replace(record, artifact_path="../outside.csv")
    assert not audit_evidence(escaped, root).valid


def test_cannot_mix_evidence_across_lots(audited_migration_case) -> None:
    record, root = audited_migration_case
    decisions = evaluate_specimen_gates(
        (record,),
        root,
        sample_id=record.sample_id,
        lot_id="DIFFERENT-LOT",
    )
    assert decisions[0].status == "INDETERMINATE"
    assert all(x.status == "NOT_REACHED" for x in decisions[1:])


def test_g2_cannot_pass_when_g0_g1_missing(audited_migration_case) -> None:
    record, root = audited_migration_case
    decisions = evaluate_specimen_gates(
        (record,), root, sample_id=record.sample_id, lot_id=record.lot_id
    )
    assert decisions[0].status == "INDETERMINATE"
    assert decisions[2].status == "NOT_REACHED"


def test_unsupported_product_claim_fails(audited_migration_case) -> None:
    record, root = audited_migration_case
    claim = ClaimRecord(
        "CLAIM-001", "MIGRATION", "Test substance migrates.",
        ClaimStatus.SUPPORTED, "G2_SWEAT_MIGRATION",
        record.sample_id, record.lot_id, (record.record_id,),
    )
    result = audit_claim(claim, (record,), root)
    assert not result.valid
    assert "prior_evidence_gates_not_satisfied" in result.errors


def test_human_health_causation_is_never_auto_approved(
    audited_migration_case,
) -> None:
    record, root = audited_migration_case
    claim = ClaimRecord(
        "CLAIM-002", "HEALTH_CAUSATION", "Hypothetical causal statement.",
        ClaimStatus.SUPPORTED, "G2_SWEAT_MIGRATION",
        record.sample_id, record.lot_id, (record.record_id,),
    )
    result = audit_claim(claim, (record,), root)
    assert "health_causation_requires_separate_human_study" in result.errors


def test_pending_hypothesis_does_not_require_fabricated_evidence(
    tmp_path: Path,
) -> None:
    claim = ClaimRecord(
        "HYP-001", "HYPOTHESIS", "Testable hypothesis.",
        ClaimStatus.PENDING, "", "", "", (),
    )
    assert audit_claim(claim, (), tmp_path).valid


def test_verified_migration_is_bound_to_exact_assay_row(
    audited_migration_case,
) -> None:
    record, root = audited_migration_case
    verified_migration_row(
        record,
        root,
        target="example",
        migration_rate_ug_cm2_h=0.2,
        medium="synthetic sweat",
        temperature_c=37.0,
    )
    with pytest.raises(ValueError, match="differs"):
        verified_migration_row(
            record,
            root,
            target="example",
            migration_rate_ug_cm2_h=0.25,
            medium="synthetic sweat",
            temperature_c=37.0,
        )


def test_evidence_csv_rejects_missing_schema(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("record_id\nE1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        load_evidence_csv(path)


def test_claims_csv_rejects_duplicate_ids(tmp_path: Path) -> None:
    path = tmp_path / "claims.csv"
    path.write_text(
        "claim_id,claim_type,claim_text,status,gate,sample_id,lot_id,evidence_ids\n"
        "H1,HYPOTHESIS,One,PENDING,,,,\n"
        "H1,HYPOTHESIS,Two,PENDING,,,,\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate"):
        load_claims_csv(path)


def test_empty_evidence_ledger_is_valid_but_has_no_passes(tmp_path: Path) -> None:
    from ball001.research_integrity import EVIDENCE_FIELDS

    path = tmp_path / "evidence.csv"
    path.write_text(",".join(EVIDENCE_FIELDS) + "\n", encoding="utf-8")
    assert load_evidence_csv(path) == ()
