"""Point-in-time hashing and source-URL audit stamps."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class ProvenanceError(ValueError):
    """A record cannot enter the ledger without a source and a timestamp."""


class Provenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_url: str
    retrieved_at: datetime
    content_sha256: str


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ProvenanceError("datetime values in a payload must be timezone-aware")
        return value.astimezone(UTC).isoformat()
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"Object of type {type(value).__name__} is not canonical JSON")


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_json_default,
    ).encode("utf-8")


def content_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def stamp(source_url: str | None, retrieved_at: datetime, payload: dict[str, Any]) -> Provenance:
    if not isinstance(source_url, str) or not source_url.strip():
        raise ProvenanceError("source_url is required")
    cleaned = source_url.strip()
    if not cleaned.startswith(("https://", "http://")):
        raise ProvenanceError("source_url must be an http(s) URL")
    if (
        not isinstance(retrieved_at, datetime)
        or retrieved_at.tzinfo is None
        or retrieved_at.utcoffset() is None
    ):
        raise ProvenanceError("retrieved_at must be timezone-aware")
    return Provenance(
        source_url=cleaned,
        retrieved_at=retrieved_at,
        content_sha256=content_sha256(payload),
    )
