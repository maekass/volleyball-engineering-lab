"""Stage engineering artifacts for an Adobe MCP design session.

Usage:

    python scripts/export_adobe_handoff.py \
        --kind render \
        --label SIMULATED \
        --description "Radial displacement field, medium mesh" \
        exports/visualization/ball001_structural_verification.png

Repeat the flag group per file, or pass several files sharing one
kind/label/description. Files are copied to exports/adobe_handoff/ with a
manifest.json recording provenance and evidence labels.

The staged directory is what you upload or reference in an Adobe MCP
session (Claude, Claude Code, Cursor, or VS Code). See
integrations/adobe/README.md for the full workflow.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ball001.adobe_handoff import (
    ARTIFACT_KINDS,
    EVIDENCE_LABELS,
    HandoffArtifact,
    stage_handoff,
    summarize_by_label,
)

DEFAULT_DESTINATION = Path("exports/adobe_handoff")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Copy engineering artifacts into an evidence-labeled "
            "handoff directory for Adobe MCP design work."
        ),
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Artifact files to stage (renders, plots, CAD exports).",
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=ARTIFACT_KINDS,
        help="Artifact kind recorded in the manifest.",
    )
    parser.add_argument(
        "--label",
        required=True,
        choices=EVIDENCE_LABELS,
        help="Evidence label per the Volley Lab evidence standard.",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Short provenance note (what produced this artifact).",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help=f"Handoff directory (default: {DEFAULT_DESTINATION}).",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    artifacts = tuple(
        HandoffArtifact(
            source_path=file_path,
            kind=args.kind,
            evidence_label=args.label,
            description=args.description,
        )
        for file_path in args.files
    )

    result = stage_handoff(artifacts, args.destination)

    print("ADOBE MCP HANDOFF")
    print("=" * 50)
    print(f"Destination: {result.destination_dir}")
    print(f"Manifest:    {result.manifest_path}")
    print(f"Files:       {len(result.staged_files)}")

    for label, count in sorted(summarize_by_label(artifacts).items()):
        print(f"  {label:12s}{count:4d}")

    print()
    print(
        "NOTE: Adobe MCP outputs are communication artifacts, "
        "never SIMULATED or MEASURED evidence."
    )


if __name__ == "__main__":
    main()
