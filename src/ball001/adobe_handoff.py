"""Stage Volley Lab visual artifacts for Adobe MCP design workflows.

Volley Lab uses Adobe MCP (primarily the Adobe-hosted "Adobe for creativity"
Model Context Protocol server) to turn engineering artifacts — VTK renders,
matplotlib/PyVista plots, CAD exports, and report excerpts — into publication
and communication graphics.

This module enforces the project evidence standard at the boundary between
engineering outputs and design tooling:

- Every artifact handed to a design workflow carries an explicit evidence
  label (STANDARD, BENCHMARK, LITERATURE, TARGET, SIMULATED, MEASURED,
  PENDING, UNKNOWN).
- A machine-readable ``manifest.json`` records provenance for every staged
  file so a designed figure can always be traced back to the engineering
  artifact that produced it.
- Anything produced downstream by Adobe tools is a COMMUNICATION artifact.
  It is never SIMULATED or MEASURED evidence, and it must never re-enter the
  engineering record as such.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

EVIDENCE_LABELS: tuple[str, ...] = (
    "STANDARD",
    "BENCHMARK",
    "LITERATURE",
    "TARGET",
    "SIMULATED",
    "MEASURED",
    "PENDING",
    "UNKNOWN",
)

ARTIFACT_KINDS: tuple[str, ...] = (
    "render",
    "plot",
    "cad_export",
    "mesh_view",
    "report_excerpt",
    "reference_image",
)

MANIFEST_FILENAME = "manifest.json"
MANIFEST_SCHEMA_VERSION = 1

HANDOFF_POLICY = (
    "Adobe MCP outputs are communication artifacts. They are not SIMULATED "
    "or MEASURED evidence and must not re-enter the engineering record as "
    "evidence."
)


@dataclass(frozen=True)
class HandoffArtifact:
    """A single engineering artifact staged for a design workflow."""

    source_path: str
    kind: str
    evidence_label: str
    description: str


@dataclass(frozen=True)
class HandoffResult:
    """Result of staging artifacts into a handoff directory."""

    destination_dir: str
    manifest_path: str
    staged_files: tuple[str, ...]


def validate_artifact(artifact: HandoffArtifact) -> None:
    """Reject artifacts that violate the handoff contract."""

    if artifact.kind not in ARTIFACT_KINDS:
        raise ValueError(
            f"Unknown artifact kind '{artifact.kind}'. "
            f"Expected one of: {', '.join(ARTIFACT_KINDS)}"
        )

    if artifact.evidence_label not in EVIDENCE_LABELS:
        raise ValueError(
            f"Unknown evidence label '{artifact.evidence_label}'. "
            f"Expected one of: {', '.join(EVIDENCE_LABELS)}"
        )

    if not artifact.description.strip():
        raise ValueError(
            "Every handoff artifact requires a non-empty description "
            "so designed figures remain traceable."
        )

    source = Path(artifact.source_path)

    if not source.is_file():
        raise FileNotFoundError(
            f"Handoff artifact does not exist: {artifact.source_path}"
        )


def _unique_destination_name(
    source: Path,
    taken: set[str],
) -> str:
    candidate = source.name
    stem = source.stem
    suffix = source.suffix
    counter = 1

    while candidate in taken:
        counter += 1
        candidate = f"{stem}_{counter}{suffix}"

    taken.add(candidate)
    return candidate


def stage_handoff(
    artifacts: Sequence[HandoffArtifact],
    destination_dir: Path,
) -> HandoffResult:
    """Copy artifacts into a handoff directory and write a manifest.

    The destination directory is created if needed. File name collisions
    between artifacts are resolved deterministically with numeric suffixes.
    """

    if not artifacts:
        raise ValueError("At least one handoff artifact is required.")

    for artifact in artifacts:
        validate_artifact(artifact)

    destination_dir.mkdir(parents=True, exist_ok=True)

    taken: set[str] = set()
    manifest_entries = []
    staged_files = []

    for artifact in artifacts:
        source = Path(artifact.source_path)
        staged_name = _unique_destination_name(source, taken)
        staged_path = destination_dir / staged_name

        shutil.copy2(source, staged_path)
        staged_files.append(str(staged_path))

        entry = asdict(artifact)
        entry["staged_filename"] = staged_name
        manifest_entries.append(entry)

    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "project": "Volley Lab / BALL 001",
        "policy": HANDOFF_POLICY,
        "artifacts": manifest_entries,
    }

    manifest_path = destination_dir / MANIFEST_FILENAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    return HandoffResult(
        destination_dir=str(destination_dir),
        manifest_path=str(manifest_path),
        staged_files=tuple(staged_files),
    )


def load_manifest(manifest_path: Path) -> dict:
    """Load and structurally validate a handoff manifest."""

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported handoff manifest schema version: "
            f"{manifest.get('schema_version')!r}"
        )

    for entry in manifest.get("artifacts", []):
        if entry.get("evidence_label") not in EVIDENCE_LABELS:
            raise ValueError(
                "Manifest entry has an invalid evidence label: "
                f"{entry.get('evidence_label')!r}"
            )

    return manifest


def summarize_by_label(
    artifacts: Iterable[HandoffArtifact],
) -> dict[str, int]:
    """Count staged artifacts per evidence label for reporting."""

    counts: dict[str, int] = {}

    for artifact in artifacts:
        counts[artifact.evidence_label] = (
            counts.get(artifact.evidence_label, 0) + 1
        )

    return counts
