"""OpenAlex search for volleyball jump-load, tendon, ACL, IMU, and optical studies."""

from __future__ import annotations

from datetime import datetime

import httpx
from db.provenance import stamp
from pydantic import BaseModel, ConfigDict

OPENALEX_URL = "https://api.openalex.org/works"
USER_AGENT = "vvii-quant-engine/0.1 (research; unfunded diligence)"


class LiteratureSignal(BaseModel):
    model_config = ConfigDict(frozen=True)

    signal_type: str
    title: str
    source_url: str
    retrieved_at: datetime
    content_sha256: str
    year: int | None
    doi: str | None
    cited_by_count: int | None


def build_openalex_params() -> dict[str, str]:
    # OpenAlex treats bare words as AND. Volleyball stays mandatory; the
    # clinical and sensing terms are alternatives so a tendon paper is not
    # dropped for lacking an IMU keyword.
    return {
        "search": "volleyball AND (jump OR patellar OR ACL OR IMU OR optical)",
        "filter": "type:article",
        "per-page": "25",
    }


def parse_openalex_works(
    payload: dict,
    retrieved_at: datetime,
) -> tuple[list[LiteratureSignal], list[str]]:
    rows: list[LiteratureSignal] = []
    rejected: list[str] = []
    for work in payload.get("results", []):
        url = work.get("id")
        title = work.get("display_name") or ""
        if not isinstance(url, str) or not url.startswith("http"):
            rejected.append(title or "missing-url")
            continue
        body = {
            "openalex_id": url,
            "title": title,
            "year": work.get("publication_year"),
            "doi": work.get("doi"),
            "cited_by_count": work.get("cited_by_count"),
        }
        provenance = stamp(url, retrieved_at, body)
        rows.append(
            LiteratureSignal(
                signal_type="publication",
                title=title,
                source_url=provenance.source_url,
                retrieved_at=provenance.retrieved_at,
                content_sha256=provenance.content_sha256,
                year=work.get("publication_year"),
                doi=work.get("doi"),
                cited_by_count=work.get("cited_by_count"),
            )
        )
    return rows, rejected


def fetch_openalex(client: httpx.Client, retrieved_at: datetime) -> list[LiteratureSignal]:
    response = client.get(
        OPENALEX_URL,
        params=build_openalex_params(),
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    rows, _rejected = parse_openalex_works(response.json(), retrieved_at)
    return rows
