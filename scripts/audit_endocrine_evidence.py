"""Audit evidence artifacts and claims without promoting pending work to PASS."""

from __future__ import annotations

import argparse
from pathlib import Path

from ball001.research_integrity import (
    GATES,
    audit_claim,
    audit_evidence,
    evaluate_specimen_gates,
    load_claims_csv,
    load_evidence_csv,
)

ROOT = Path(__file__).resolve().parents[1]


def run_audit(
    root: Path,
    evidence_path: Path,
    claims_path: Path,
    *,
    strict: bool = False,
) -> tuple[str, bool]:
    records = load_evidence_csv(evidence_path)
    claims = load_claims_csv(claims_path)
    lines = [
        "# BALL 001 research integrity audit",
        "",
        f"Evidence records: {len(records)}",
        f"Claim records: {len(claims)}",
        "PASS is a provenance/QC completeness result, not a safety claim.",
        "",
    ]
    errors = 0
    for record in records:
        result = audit_evidence(record, root)
        lines.append(
            f"- {record.record_id}: "
            f"{'AUDIT_PASS' if result.valid else 'AUDIT_FAIL'}"
            + (f" ({'; '.join(result.errors)})" if result.errors else "")
        )
        errors += not result.valid
    for claim in claims:
        result = audit_claim(claim, records, root)
        lines.append(
            f"- {claim.claim_id}: {claim.status} "
            f"{'CLAIM_CHECK_PASS' if result.valid else 'CLAIM_CHECK_FAIL'}"
            + (f" ({'; '.join(result.errors)})" if result.errors else "")
        )
        errors += not result.valid

    specimens = sorted({(r.sample_id, r.lot_id) for r in records})
    if not specimens:
        lines.append("- Evidence gates: NO_PRODUCT_MEASUREMENTS_REGISTERED")
        if strict:
            errors += 1
    for sample_id, lot_id in specimens:
        lines.append(f"## Specimen {sample_id} / lot {lot_id}")
        decisions = evaluate_specimen_gates(
            records, root, sample_id=sample_id, lot_id=lot_id
        )
        for decision in decisions:
            lines.append(
                f"- {decision.gate}: {decision.status} "
                f"({', '.join(decision.evidence_ids) or 'none'})"
            )
        if strict and len([x for x in decisions if x.status == "PASS"]) != len(GATES):
            errors += 1
    lines.append("")
    lines.append(
        "Audit result: " + ("FAIL" if errors else "PASS_WITH_PENDING_EVIDENCE")
    )
    return "\n".join(lines) + "\n", errors == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--evidence", type=Path, default=ROOT / "data" / "research_evidence.csv"
    )
    parser.add_argument(
        "--claims", type=Path, default=ROOT / "data" / "research_claims.csv"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Require all specimen gates; expected to fail before lab studies.",
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report, passed = run_audit(
        args.root, args.evidence, args.claims, strict=args.strict
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
