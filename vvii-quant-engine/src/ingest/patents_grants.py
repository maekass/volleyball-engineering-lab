"""USPTO PatentsView and NSF award queries for volleyball instrumentation.

PatentsView is queried on CPC groups A63B (sport apparatus) and G06V
(image or video recognition) with the word volleyball in the abstract.
NSF results are retained only when the program name contains SBIR or STTR.
"""

from __future__ import annotations

from datetime import datetime

import httpx
from db.provenance import stamp
from pydantic import BaseModel, ConfigDict

PATENTSVIEW_URL = "https://search.patentsview.org/api/v1/patent/"
NSF_URL = "https://api.nsf.gov/services/v1/awards.json"
USER_AGENT = "vvii-quant-engine/0.1 (research; unfunded diligence)"


class PatentSignal(BaseModel):
    model_config = ConfigDict(frozen=True)

    signal_type: str
    external_id: str
    title: str
    source_url: str
    retrieved_at: datetime
    content_sha256: str


class GrantSignal(BaseModel):
    model_config = ConfigDict(frozen=True)

    signal_type: str
    external_id: str
    title: str
    awardee: str
    amount_usd: int
    source_url: str
    retrieved_at: datetime
    content_sha256: str
    program: str


def build_patentsview_query(size: int = 25) -> dict:
    return {
        "q": {
            "_and": [
                {"_text_phrase": {"patent_abstract": "volleyball"}},
                {
                    "_or": [
                        {"_begins": {"cpc_current.cpc_group": "A63B"}},
                        {"_begins": {"cpc_current.cpc_group": "G06V"}},
                    ]
                },
            ]
        },
        "f": ["patent_id", "patent_title", "patent_date"],
        "o": {"size": size},
    }


def build_nsf_params(program: str) -> dict[str, str]:
    if program not in {"SBIR", "STTR"}:
        raise ValueError("program must be SBIR or STTR")
    return {
        "keyword": "volleyball",
        "printFields": "id,title,awardeeName,fundsObligatedAmt,date,fundProgramName",
    }


def parse_patentsview(payload: dict, retrieved_at: datetime) -> list[PatentSignal]:
    rows: list[PatentSignal] = []
    for patent in payload.get("patents") or []:
        patent_id = str(patent["patent_id"])
        url = f"https://patents.google.com/patent/{patent_id}"
        title = str(patent.get("patent_title") or patent_id)
        body = {
            "patent_id": patent_id,
            "title": title,
            "patent_date": patent.get("patent_date"),
        }
        provenance = stamp(url, retrieved_at, body)
        rows.append(
            PatentSignal(
                signal_type="patent",
                external_id=patent_id,
                title=title,
                source_url=provenance.source_url,
                retrieved_at=provenance.retrieved_at,
                content_sha256=provenance.content_sha256,
            )
        )
    return rows


def parse_nsf_awards(
    payload: dict,
    retrieved_at: datetime,
) -> tuple[list[GrantSignal], list[str]]:
    awards = payload.get("response", {}).get("award") or []
    rows: list[GrantSignal] = []
    rejected: list[str] = []
    for award in awards:
        program = str(award.get("fundProgramName") or "")
        award_id = str(award.get("id") or "")
        if "SBIR" not in program and "STTR" not in program:
            rejected.append(award_id or program or "unspecified")
            continue
        url = f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={award_id}"
        amount = int(str(award.get("fundsObligatedAmt") or "0").split(".", 1)[0])
        title = str(award.get("title") or award_id)
        body = {
            "award_id": award_id,
            "title": title,
            "awardee": award.get("awardeeName"),
            "amount_usd": amount,
            "program": program,
        }
        provenance = stamp(url, retrieved_at, body)
        rows.append(
            GrantSignal(
                signal_type="grant",
                external_id=award_id,
                title=title,
                awardee=str(award.get("awardeeName") or ""),
                amount_usd=amount,
                source_url=provenance.source_url,
                retrieved_at=provenance.retrieved_at,
                content_sha256=provenance.content_sha256,
                program=program,
            )
        )
    return rows, rejected


def fetch_patents(client: httpx.Client, retrieved_at: datetime) -> list[PatentSignal]:
    response = client.post(
        PATENTSVIEW_URL,
        json=build_patentsview_query(),
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return parse_patentsview(response.json(), retrieved_at)


def fetch_nsf(
    client: httpx.Client,
    program: str,
    retrieved_at: datetime,
) -> list[GrantSignal]:
    response = client.get(
        NSF_URL,
        params=build_nsf_params(program),
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    rows, _rejected = parse_nsf_awards(response.json(), retrieved_at)
    return rows
