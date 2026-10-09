"""Generate an evidence-gated BALL 001 materials-health screening report."""

from __future__ import annotations

import argparse
from pathlib import Path

from ball001.endocrine_materials import (
    EvidenceGateInputs,
    evaluate_evidence_gates,
    load_watchlist,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WATCHLIST = ROOT / "data" / "endocrine_materials_watchlist.csv"


def build_report(watchlist_path: Path) -> str:
    targets = load_watchlist(watchlist_path)
    lines = [
        "# BALL 001 materials-health screening",
        "",
        "This report is a research-prioritization tool. It does not assert that ",
        "BALL 001 or any benchmark ball contains the listed chemicals.",
        "",
        f"Watchlist targets: {len(targets)}",
    ]
    for target in targets:
        lines.append(
            f"- {target.target} ({target.cas}) — {target.preferred_screen}; "
            f"presence={target.product_presence}"
        )

    lines.extend(["", "## Evidence gates"])
    for decision in evaluate_evidence_gates(EvidenceGateInputs()):
        lines.append(
            f"- {decision.gate}: {decision.status} — {decision.reason}"
        )
    lines.extend(
        [
            "",
            "No dose or health-risk estimate is generated until product-specific ",
            "migration and contact evidence satisfy the required gates.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--watchlist",
        type=Path,
        default=DEFAULT_WATCHLIST,
        help="CSV chemical-target watchlist.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional Markdown output path. Prints to stdout when omitted.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(args.watchlist)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
