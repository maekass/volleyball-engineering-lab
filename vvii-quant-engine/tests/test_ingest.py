"""Parsers for OpenAlex, USPTO, NSF, and NCAA rule PDFs. No live network."""

from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO

import httpx
import pytest
from ingest.ncaa_rules import extract_rule_excerpts, normalize_rule_text
from ingest.openalex_msk import (
    build_openalex_params,
    fetch_openalex,
    parse_openalex_works,
)
from ingest.patents_grants import (
    PatentSourceError,
    build_nsf_params,
    build_patent_query,
    fetch_nsf,
    fetch_patents,
    parse_nsf_awards,
    parse_uspto_search,
)
from pypdf import PdfReader

AS_OF = datetime(2026, 11, 27, 15, 0, tzinfo=UTC)
RULES_URL = (
    "https://ncaaorg.s3.amazonaws.com/championships/sports/volleyball/"
    "rules/women/2026-27PRWVB_D1RulesChanges.pdf"
)


def minimal_pdf(text: str) -> bytes:
    if any(character in text for character in "()\\"):
        raise ValueError("fixture text must not contain PDF string delimiters")
    stream = f"BT /F1 11 Tf 48 720 Td ({text}) Tj ET\n".encode()
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        ),
        (
            b"4 0 obj\n<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"endstream\nendobj\n"
        ),
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    header = b"%PDF-1.4\n"
    offsets = []
    cursor = len(header)
    body = b""
    for obj in objects:
        offsets.append(cursor)
        body += obj
        cursor += len(obj)
    xref_lines = ["xref", "0 6", "0000000000 65535 f "]
    xref_lines.extend(f"{offset:010d} 00000 n " for offset in offsets)
    xref = ("\n".join(xref_lines) + "\n").encode()
    trailer = (
        f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{len(header) + len(body)}\n%%EOF\n"
    ).encode()
    return header + body + xref + trailer


def test_rule_normalizer_collapses_spaced_ncaa_numbering() -> None:
    raw = "15 .2 .4 .3 center line    1 .2 .2 .4 logos"
    assert "15.2.4.3" in normalize_rule_text(raw)
    assert "1.2.2.4" in normalize_rule_text(raw)


def test_replacement_character_between_rule_digits_is_a_dot() -> None:
    # Observed from pypdf text of the official rules book: the dots in
    # 1.2.2.4 arrive as U+FFFD, so the logo rule would otherwise be dropped.
    observed = "1\ufffd2\ufffd2\ufffd4 commercial logos between the attack line"
    assert "1.2.2.4" in normalize_rule_text(observed)


def test_pdf_fixture_round_trip_and_rule_parser() -> None:
    text = (
        "Rule 15.2.4.3 It is a fault to completely cross the center line "
        "and contact the opponent court with one or both feet. "
        "Rule 1.2.2.4 A maximum of two commercial logos may sit on the court, "
        "each inside a 3 meter box between the attack line and the end line, "
        "outside the front zone. "
        "Rule 18.1.4.7 A center-line foot fault is reviewable. "
        "The challenge review system is optional by institution."
    )
    payload = minimal_pdf(text)
    extracted = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(payload)).pages)
    assert "15.2.4.3" in extracted
    excerpts = extract_rule_excerpts(payload, source_url=RULES_URL, retrieved_at=AS_OF)
    by_rule = {row.rule_id: row for row in excerpts}
    assert "15.2.4.3" in by_rule
    assert "1.2.2.4" in by_rule
    assert "18.1.4.7" in by_rule
    assert by_rule["15.2.4.3"].topic == "center_line"
    assert by_rule["1.2.2.4"].topic == "commercial_logos"
    assert by_rule["18.1.4.7"].topic == "challenge_review"
    assert all(row.source_url == RULES_URL for row in excerpts)
    assert all(row.content_sha256 for row in excerpts)


def test_spaced_rule_numbers_inside_a_pdf_still_parse() -> None:
    text = (
        "15 .2 .4 .3 It is a fault to completely cross the center line "
        "and contact the opponent court. "
        "1 .2 .2 .4 Logos fit a 3 meter box between the attack line and the end line."
    )
    excerpts = extract_rule_excerpts(
        minimal_pdf(text),
        source_url=RULES_URL,
        retrieved_at=AS_OF,
    )
    assert {row.rule_id for row in excerpts} >= {"15.2.4.3", "1.2.2.4"}


def test_openalex_query_and_parser_drop_records_without_a_url() -> None:
    params = build_openalex_params()
    assert params["search"] == (
        "volleyball AND (jump OR patellar OR ACL OR IMU OR optical)"
    )
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W123",
                "display_name": "Jump load and the patellar tendon in volleyball",
                "publication_year": 2019,
                "doi": "https://doi.org/10.0000/example",
                "cited_by_count": 4,
            },
            {
                "display_name": "No identifier",
                "publication_year": 2020,
            },
        ]
    }
    rows, rejected = parse_openalex_works(payload, retrieved_at=AS_OF)
    assert len(rows) == 1
    assert rows[0].source_url == "https://openalex.org/W123"
    assert rows[0].content_sha256
    assert len(rejected) == 1


def test_openalex_client_uses_injected_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.openalex.org"
        assert "volleyball" in str(request.url)
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": "https://openalex.org/W999",
                        "display_name": "IMU jump counts in volleyball",
                        "publication_year": 2023,
                        "doi": None,
                        "cited_by_count": 1,
                    }
                ]
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = fetch_openalex(client, retrieved_at=AS_OF)
    assert rows[0].title.startswith("IMU")
    assert rows[0].source_url == "https://openalex.org/W999"


def test_uspto_query_keeps_volleyball_in_a63b_and_g06v() -> None:
    query = build_patent_query(size=5)
    assert "A63B" in query["q"]
    assert "G06V" in query["q"]
    assert "volleyball AND" in query["q"]
    assert " OR " in query["q"]
    assert query["pagination"]["limit"] == 5
    rows = parse_uspto_search(
        {
            "patentFileWrapperDataBag": [
                {
                    "applicationNumberText": "18000001",
                    "applicationMetaData": {
                        "inventionTitle": "Volleyball optical tracking",
                        "patentNumber": "1234567",
                        "cpcClassificationBag": ["A63B71/06"],
                    },
                },
                {
                    "applicationNumberText": "18000002",
                    "applicationMetaData": {
                        "inventionTitle": "Volleyball court vision",
                        "patentNumber": "7654321",
                        "cpcClassificationBag": ["G06V20/40"],
                    },
                },
                {
                    "applicationNumberText": "18000003",
                    "applicationMetaData": {
                        "inventionTitle": "Volleyball unrelated class",
                        "patentNumber": "1111111",
                        "cpcClassificationBag": ["H04N21/00"],
                    },
                },
            ]
        },
        retrieved_at=AS_OF,
    )
    assert [row.external_id for row in rows] == ["US1234567", "US7654321"]
    assert rows[0].source_url == "https://patents.google.com/patent/US1234567"
    assert rows[0].signal_type == "patent"


def test_nsf_parser_keeps_sbir_and_sttr_only() -> None:
    params = build_nsf_params("SBIR")
    assert params["keyword"] == "volleyball"
    with pytest.raises(ValueError):
        build_nsf_params("CAREER")
    rows, rejected = parse_nsf_awards(
        {
            "response": {
                "award": [
                    {
                        "id": "1234567",
                        "title": "Volleyball IMU load",
                        "awardeeName": "Example Lab",
                        "fundsObligatedAmt": "250000",
                        "date": "06/01/2021",
                        "fundProgramName": "SBIR Phase I",
                    },
                    {
                        "id": "7654321",
                        "title": "Unrelated research grant",
                        "awardeeName": "State University",
                        "fundsObligatedAmt": "90000",
                        "date": "07/01/2022",
                        "fundProgramName": "Standard Grant",
                    },
                ]
            }
        },
        retrieved_at=AS_OF,
    )
    assert [row.external_id for row in rows] == ["1234567"]
    assert rows[0].source_url == "https://www.nsf.gov/awardsearch/showAward?AWD_ID=1234567"
    assert rows[0].amount_usd == 250000
    assert len(rejected) == 1


def test_patent_and_nsf_clients_post_and_get_through_the_injected_transport() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(f"{request.method} {request.url.host} {request.url.path}")
        if request.url.host == "api.uspto.gov":
            assert request.headers["X-API-KEY"] == "fixture-key"
            return httpx.Response(200, json={"patentFileWrapperDataBag": []})
        return httpx.Response(200, json={"response": {"award": []}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    assert fetch_patents(client, retrieved_at=AS_OF, api_key="fixture-key") == []
    assert fetch_nsf(client, program="STTR", retrieved_at=AS_OF) == []
    with pytest.raises(PatentSourceError):
        fetch_patents(client, retrieved_at=AS_OF, api_key="")
    assert any("api.uspto.gov" in row and row.startswith("POST") for row in seen)
    assert any("api.nsf.gov" in row and row.startswith("GET") for row in seen)
