# Research Integrity Architecture — BALL 001 Materials Health

**Scope:** traceability and automated completeness controls. Software
validation is not independent laboratory accreditation, toxicological
validation or clinical evidence.

## Reproducible traceability chain

```text
CLAIM -> reviewed EVIDENCE RECORD -> SHA-256 artifact
      -> sample + production lot -> specimen/extract/injection
      -> analytical method + calibration -> raw data -> numeric QC
      -> gate decision -> reproducible analysis commit
```

The two ledgers live in `data/research_claims.csv` and
`data/research_evidence.csv`. Both begin without verified product data.
Pending hypotheses are recorded as PENDING, never SUPPORTED.

### Evidence record fields

- `record_id`: unique immutable evidence identifier.
- `gate`: one of G0–G6, with expected evidence kind.
- `kind`: MATERIAL_ID, CONTENT_ASSAY, MIGRATION_ASSAY, CONTACT_STUDY,
  DERMAL_STUDY, TOXICOLOGY_REVIEW or MECHANICAL_TEST.
- `sample_id`, `lot_id`, `method_id`: nonempty product provenance.
- `artifact_path` / `artifact_sha256`: actual result file, hash checked.
- `raw_path` / `raw_sha256`: instrument or primary observation data;
  mandatory for G1, G2, G3, G4 and G6.
- `calibration_path` / `calibration_sha256`: mandatory for G1 and G2.
- `qc_path` / `qc_sha256`: mandatory for G1 and G2; CSV must include
  blank, spike recovery and duplicate RPD with laboratory-specific limits.
- `reviewer`, `reviewed_on`, `review_outcome`: independent review
  metadata. ACCEPTED is required for audit PASS.

All paths are relative to the evidence root and may not escape it. Every
referenced artifact must exist and match its recorded SHA-256. The reviewer
field is **metadata**, not proof of external reviewer identity. For actual
publication, maintain separately signed review and chain-of-custody records.

### Claim fields

`claim_id, claim_type, claim_text, status, gate, sample_id, lot_id, evidence_ids`

A SUPPORTED product claim must reference existing, reviewed, hash-matching
evidence of the correct gate and specimen/lot. The required earlier gates
must also pass. A PENDING hypothesis does not need fabricated measurements.

**HEALTH_CAUSATION is never automatically approved** by G0–G6. It requires
a separate human-subject causal design, ethics review and specialist analysis.

## Scientific limitations of automated audit

The audit detects absent evidence, tampered bytes, malformed QC, wrong
specimen/lot, mismatched assay values and unsupported claim promotion.
It cannot establish that a laboratory is honest, that the chosen chemical
method is appropriate, that a reviewer is qualified, or that a health
conclusion is valid. It does not automatically verify analytical method
validation or independent replication. Those require external records.

The exposure calculator now rejects a manually typed
`PRODUCT_MEASURED` flag unless an accepted G2 evidence record and its
hashed assay row match the target, rate, medium and temperature.

**Current `evaluate_evidence_gates(EvidenceGateInputs)` is an illustrative
Boolean checklist retained for compatibility. Its PASS values are not
authoritative.** The evidence-backed function is
`evaluate_specimen_gates(records, root, sample_id=..., lot_id=...)`.

## How to run

From an installed repository environment:

```bash
python scripts/audit_endocrine_evidence.py
python scripts/audit_endocrine_evidence.py --strict
python scripts/endocrine_materials_report.py
pytest -q tests/test_research_integrity.py tests/test_diffusion_transport.py
```

The first audit should report no registered product measurements and
PENDING claims. It returns zero when the ledger is structurally honest,
even though no science gates pass. The `--strict` option returns nonzero
until every G0–G6 gate is accepted for each registered specimen.

The transport code lives in `src/ball001/diffusion_transport.py` and has
analytic, mass-balance, mesh-refinement and synthetic-calibration tests.
**Synthetic unit tests are not laboratory data or experimental validation.**

## Before accepting actual laboratory records

1. Assign immutable sample/lot IDs and preserve the physical chain of
   custody. Use `data/sample_manifest_template.csv`.
2. Freeze protocol and primary outcomes before confirmatory data review.
3. Register method SOP, validation, calibration and QC thresholds.
4. Deposit immutable raw files and hashes; preserve failed QC too.
5. Require independent analytical review and dated approval.
6. Audit the evidence ledger; link product claims only to accepted records.
7. Hold back clinical risk conclusions until appropriate uptake and
   toxicological review.
8. Publish analysis code, uncertainty and independent replication status.

For large instrument files, store in a versioned secure research archive
and register immutable artifact checksums; the current CLI requires files
to be accessible under the chosen evidence root for re-verification.

## Software release versus scientific release

GitHub CI validates imports, lint and Python tests. Scientific release
additionally requires original measurements, method validation, uncertainty,
out-of-sample transport validation, statistical equivalence and independent
replication. Do not conflate these two levels of readiness.
