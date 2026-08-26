import json
from pathlib import Path

import pytest

from ball001.adobe_handoff import (
    ARTIFACT_KINDS,
    EVIDENCE_LABELS,
    MANIFEST_FILENAME,
    MANIFEST_SCHEMA_VERSION,
    HandoffArtifact,
    load_manifest,
    stage_handoff,
    summarize_by_label,
    validate_artifact,
)


def make_artifact(tmp_path: Path, name: str = "render.png") -> HandoffArtifact:
    source = tmp_path / name
    source.write_bytes(b"fake-image-bytes")

    return HandoffArtifact(
        source_path=str(source),
        kind="render",
        evidence_label="SIMULATED",
        description="Radial displacement render, medium mesh",
    )


def test_valid_artifact_passes_validation(tmp_path: Path) -> None:
    validate_artifact(make_artifact(tmp_path))


def test_unknown_kind_is_rejected(tmp_path: Path) -> None:
    artifact = make_artifact(tmp_path)
    bad = HandoffArtifact(
        source_path=artifact.source_path,
        kind="poster",
        evidence_label="SIMULATED",
        description="x",
    )

    with pytest.raises(ValueError):
        validate_artifact(bad)


def test_unknown_evidence_label_is_rejected(tmp_path: Path) -> None:
    artifact = make_artifact(tmp_path)
    bad = HandoffArtifact(
        source_path=artifact.source_path,
        kind="render",
        evidence_label="ILLUSTRATIVE",
        description="x",
    )

    with pytest.raises(ValueError):
        validate_artifact(bad)


def test_empty_description_is_rejected(tmp_path: Path) -> None:
    artifact = make_artifact(tmp_path)
    bad = HandoffArtifact(
        source_path=artifact.source_path,
        kind="render",
        evidence_label="SIMULATED",
        description="   ",
    )

    with pytest.raises(ValueError):
        validate_artifact(bad)


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    bad = HandoffArtifact(
        source_path=str(tmp_path / "missing.png"),
        kind="render",
        evidence_label="SIMULATED",
        description="x",
    )

    with pytest.raises(FileNotFoundError):
        validate_artifact(bad)


def test_stage_handoff_copies_files_and_writes_manifest(
    tmp_path: Path,
) -> None:
    artifact = make_artifact(tmp_path)
    destination = tmp_path / "handoff"

    result = stage_handoff((artifact,), destination)

    staged = destination / "render.png"

    assert staged.is_file()
    assert staged.read_bytes() == b"fake-image-bytes"
    assert result.staged_files == (str(staged),)
    assert Path(result.manifest_path).name == MANIFEST_FILENAME


def test_manifest_records_provenance(tmp_path: Path) -> None:
    artifact = make_artifact(tmp_path)
    destination = tmp_path / "handoff"

    result = stage_handoff((artifact,), destination)
    manifest = json.loads(Path(result.manifest_path).read_text())

    assert manifest["schema_version"] == MANIFEST_SCHEMA_VERSION
    assert manifest["project"] == "Volley Lab / BALL 001"
    assert "communication artifacts" in manifest["policy"]

    (entry,) = manifest["artifacts"]

    assert entry["staged_filename"] == "render.png"
    assert entry["evidence_label"] == "SIMULATED"
    assert entry["kind"] == "render"
    assert entry["source_path"] == artifact.source_path


def test_filename_collisions_are_resolved(tmp_path: Path) -> None:
    first_dir = tmp_path / "a"
    second_dir = tmp_path / "b"
    first_dir.mkdir()
    second_dir.mkdir()

    artifacts = (
        make_artifact(first_dir),
        make_artifact(second_dir),
    )
    destination = tmp_path / "handoff"

    result = stage_handoff(artifacts, destination)

    names = sorted(Path(path).name for path in result.staged_files)

    assert names == ["render.png", "render_2.png"]


def test_stage_handoff_requires_artifacts(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        stage_handoff((), tmp_path / "handoff")


def test_load_manifest_roundtrip(tmp_path: Path) -> None:
    artifact = make_artifact(tmp_path)
    destination = tmp_path / "handoff"

    result = stage_handoff((artifact,), destination)
    manifest = load_manifest(Path(result.manifest_path))

    assert len(manifest["artifacts"]) == 1


def test_load_manifest_rejects_bad_schema(tmp_path: Path) -> None:
    manifest_path = tmp_path / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps({"schema_version": 99}))

    with pytest.raises(ValueError):
        load_manifest(manifest_path)


def test_load_manifest_rejects_bad_label(tmp_path: Path) -> None:
    manifest_path = tmp_path / MANIFEST_FILENAME
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "artifacts": [{"evidence_label": "VIBES"}],
            }
        )
    )

    with pytest.raises(ValueError):
        load_manifest(manifest_path)


def test_summarize_by_label_counts(tmp_path: Path) -> None:
    first = make_artifact(tmp_path, "a.png")

    second_source = tmp_path / "b.png"
    second_source.write_bytes(b"x")
    second = HandoffArtifact(
        source_path=str(second_source),
        kind="plot",
        evidence_label="TARGET",
        description="Target mass envelope plot",
    )

    counts = summarize_by_label((first, second, first))

    assert counts == {"SIMULATED": 2, "TARGET": 1}


def test_registry_constants_are_consistent() -> None:
    assert "SIMULATED" in EVIDENCE_LABELS
    assert "MEASURED" in EVIDENCE_LABELS
    assert "render" in ARTIFACT_KINDS
