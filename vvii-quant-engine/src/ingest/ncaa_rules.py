"""Extract cited NCAA rule numbers from a local rules PDF.

The parser normalizes the spaced numbering used in NCAA PDF text extraction
(`15 .2 .4 .3`). pypdf also emits U+FFFD between the digits of some rule
numbers in the official book (`1.2.2.4`), so those separators are treated as
dots before the number is read. The parser returns only the rule identifiers
this engine models.
It does not download the rules book.
"""

from __future__ import annotations

import re
from datetime import datetime
from io import BytesIO

from db.provenance import stamp
from pydantic import BaseModel, ConfigDict
from pypdf import PdfReader

_RULE_TOPICS = {
    "15.2.4.3": "center_line",
    "1.2.2.4": "commercial_logos",
    "18.1.4.7": "challenge_review",
}
_NUMBER = re.compile(r"\d(?:\s*\.\s*\d)+")
_DOT_LIKE = str.maketrans(
    {
        "\ufffd": ".",
        "\u00b7": ".",
        "\u2024": ".",
        "\u2219": ".",
        "\u2022": ".",
        "\uf0b7": ".",
    }
)


class RuleExcerpt(BaseModel):
    model_config = ConfigDict(frozen=True)

    rule_id: str
    topic: str
    source_url: str
    retrieved_at: datetime
    content_sha256: str


def normalize_rule_text(text: str) -> str:
    cleaned = text.replace("\u00a0", " ").translate(_DOT_LIKE)
    cleaned = _NUMBER.sub(lambda match: re.sub(r"\s+", "", match.group(0)), cleaned)
    return re.sub(r"[ \t]+", " ", cleaned)


def extract_rule_excerpts(
    pdf_bytes: bytes,
    source_url: str,
    retrieved_at: datetime,
) -> list[RuleExcerpt]:
    reader = PdfReader(BytesIO(pdf_bytes))
    raw = "\n".join(page.extract_text() or "" for page in reader.pages)
    text = normalize_rule_text(raw)
    excerpts: list[RuleExcerpt] = []
    for rule_id, topic in _RULE_TOPICS.items():
        if rule_id not in text:
            continue
        payload = {"rule_id": rule_id, "topic": topic, "excerpt_source": "pdf_text"}
        provenance = stamp(source_url, retrieved_at, payload)
        excerpts.append(
            RuleExcerpt(
                rule_id=rule_id,
                topic=topic,
                source_url=provenance.source_url,
                retrieved_at=provenance.retrieved_at,
                content_sha256=provenance.content_sha256,
            )
        )
    return excerpts
