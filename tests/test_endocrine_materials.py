import pytest

from ball001.endocrine_materials import (
    ContactScenario,
    DoseContext,
    EngineeringConstraint,
    EvidenceBasis,
    EvidenceGateInputs,
    GateStatus,
    LabQualityControl,
    MigrationMeasurement,
    MigrationReplicate,
    QCCriteria,
    estimate_external_dermal_exposure,
    evaluate_evidence_gates,
    evaluate_lab_qc,
    migration_measurement_from_replicates,
    performance_equivalence,
)


def test_contact_time_is_cumulative_not_session_duration() -> None:
    scenario = ContactScenario(360.0, 7.0, 200.0, 70.0)
    assert scenario.mean_daily_contact_hours == pytest.approx(0.1)


def test_migration_rate_is_area_and_time_normalized() -> None:
    replicate = MigrationReplicate(12.0, 20.0, 2.0)
    assert replicate.migration_rate_ug_cm2_h == pytest.approx(0.3)


def test_migration_requires_three_replicates() -> None:
    reps = (
        MigrationReplicate(12.0, 20.0, 2.0),
        MigrationReplicate(10.0, 20.0, 2.0),
    )
    with pytest.raises(ValueError, match="three"):
        migration_measurement_from_replicates(
            "example",
            reps,
            medium="synthetic sweat",
            temperature_c=37.0,
        )


def test_lab_qc_uses_explicit_protocol_limits() -> None:
    criteria = QCCriteria(0.1, 70.0, 130.0, 30.0)
    record = LabQualityControl(0.02, 95.0, 8.0)
    assert evaluate_lab_qc(record, criteria).accepted


def test_lab_qc_reports_each_failure() -> None:
    criteria = QCCriteria(0.1, 70.0, 130.0, 30.0)
    record = LabQualityControl(0.2, 50.0, 40.0)
    result = evaluate_lab_qc(record, criteria)
    assert not result.accepted
    assert len(result.failures) == 3


def test_external_dermal_exposure_requires_product_measurement() -> None:
    scenario = ContactScenario(60.0, 5.0, 100.0, 60.0)
    analogue = MigrationMeasurement(
        target="example",
        migration_rate_ug_cm2_h=0.1,
        medium="synthetic sweat",
        temperature_c=37.0,
        evidence_basis=EvidenceBasis.MATERIAL_ANALOGUE,
    )
    with pytest.raises(ValueError, match="product-measured"):
        estimate_external_dermal_exposure(analogue, scenario)


def test_external_exposure_is_not_absorbed_without_uptake_factor(
    audited_migration_case,
) -> None:
    record, root = audited_migration_case
    scenario = ContactScenario(360.0, 7.0, 200.0, 50.0, 0.5)
    measurement = MigrationMeasurement(
        "example", 0.2, "synthetic sweat", 37.0,
        EvidenceBasis.PRODUCT_MEASURED, record.record_id
    )
    result = estimate_external_dermal_exposure(
        measurement, scenario, evidence_record=record, evidence_root=root
    )
    assert result.external_ug_per_day == pytest.approx(2.0)
    assert result.external_ug_per_kg_day == pytest.approx(0.04)
    assert result.absorbed_ug_per_kg_day is None


def test_absorbed_estimate_requires_explicit_absorption_fraction(
    audited_migration_case,
) -> None:
    record, root = audited_migration_case
    scenario = ContactScenario(360.0, 7.0, 200.0, 50.0, 0.5)
    measurement = MigrationMeasurement(
        "example", 0.2, "synthetic sweat", 37.0,
        EvidenceBasis.PRODUCT_MEASURED, record.record_id
    )
    result = estimate_external_dermal_exposure(
        measurement,
        scenario,
        dermal_absorption_fraction=0.1,
        evidence_record=record,
        evidence_root=root,
    )
    assert result.absorbed_ug_per_kg_day == pytest.approx(0.004)


def test_dose_context_returns_ratio_not_safety_label() -> None:
    context = DoseContext(0.2, 2.0)
    assert context.screening_ratio == pytest.approx(0.1)


def test_performance_equivalence_requires_all_constraints() -> None:
    constraints = (
        EngineeringConstraint("mass", 270.0, 271.0, 0.01),
        EngineeringConstraint("compression", 100.0, 102.0, 0.03),
    )
    assert performance_equivalence(constraints)


def test_gates_stop_after_first_missing_evidence() -> None:
    decisions = evaluate_evidence_gates(
        EvidenceGateInputs(
            material_identity_confirmed=True,
            total_content_measured=True,
            migration_measured=False,
            realistic_transfer_characterized=True,
        )
    )
    assert decisions[0].status is GateStatus.PASS
    assert decisions[1].status is GateStatus.PASS
    assert decisions[2].status is GateStatus.INDETERMINATE
    assert decisions[3].status is GateStatus.NOT_REACHED


def test_complete_evidence_chain_does_not_use_safe_language() -> None:
    decisions = evaluate_evidence_gates(
        EvidenceGateInputs(
            material_identity_confirmed=True,
            total_content_measured=True,
            migration_measured=True,
            realistic_transfer_characterized=True,
            dermal_uptake_characterized=True,
            toxicological_reference_identified=True,
            performance_equivalence_verified=True,
        )
    )
    assert all(decision.status is GateStatus.PASS for decision in decisions)
    assert "safe" not in " ".join(
        decision.reason.lower() for decision in decisions
    )


def test_exposure_rejects_missing_audit_even_when_labeled_measured() -> None:
    scenario = ContactScenario(360.0, 7.0, 200.0, 50.0, 0.5)
    claimed = MigrationMeasurement(
        "example", 0.2, "synthetic sweat", 37.0,
        EvidenceBasis.PRODUCT_MEASURED, "EVID-CLAIMED"
    )
    with pytest.raises(ValueError, match="audited G2"):
        estimate_external_dermal_exposure(claimed, scenario)


def test_exposure_rejects_fabricated_rate(audited_migration_case) -> None:
    record, root = audited_migration_case
    scenario = ContactScenario(360.0, 7.0, 200.0, 50.0, 0.5)
    fabricated = MigrationMeasurement(
        "example", 20.0, "synthetic sweat", 37.0,
        EvidenceBasis.PRODUCT_MEASURED, record.record_id
    )
    with pytest.raises(ValueError, match="differs"):
        estimate_external_dermal_exposure(
            fabricated, scenario, evidence_record=record, evidence_root=root
        )
