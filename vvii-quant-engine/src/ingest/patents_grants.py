"""USPTO Open Data Portal and NSF award queries for volleyball instrumentation.

PatentsView's search host stopped resolving when that service moved to the
USPTO Open Data Portal on 20 March 2026. The replacement search is
``api.uspto.gov`` and requires ``USPTO_ODP_API_KEY``. The query keeps
volleyball together with CPC groups A63B (sport apparatus) and G06V (image
or video recognition). The adapter then keeps a row only when the title
contains volleyball and a returned class starts with one of those groups.
NSF results are retained only when the program name contains SBIR or STTR.
"""

from __future__ import annotations

import os
from datetime import datetime

import httpx
from db.provenance import stamp
from pydantic import BaseModel, ConfigDict

USPTO_SEARCH_URL = "https://api.uspto.gov/api/v1/patent/applications/search"
USPTO_API_KEY_ENV = "USPTO_ODP_API_KEY"
NSF_URL = "https://api.nsf.gov/services/v1/awards.json"
USER_AGENT = "vvii-quant-engine/0.1 (research; unfunded diligence)"
_CPC_PREFIXES = ("A63B", "G06V")


class PatentSourceError(RuntimeError):
    """The patent search cannot run because its credential is missing."""


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


def build_patent_query(size: int = 25) -> dict:
    return {
        "q": (
            "volleyball AND ("
            "applicationMetaData.cpcClassificationBag:A63B* OR "
            "applicationMetaData.cpcClassificationBag:G06V*"
            ")"
        ),
        "fields": [
            "applicationNumberText",
            "applicationMetaData.inventionTitle",
            "applicationMetaData.patentNumber",
            "applicationMetaData.cpcClassificationBag",
        ],
        "pagination": {"offset": 0, "limit": size},
    }


def build_nsf_params(program: str) -> dict[str, str]:
    if program not in {"SBIR", "STTR"}:
        raise ValueError("program must be SBIR or STTR")
    return {
        "keyword": "volleyball",
        "printFields": "id,title,awardeeName,fundsObligatedAmt,date,fundProgramName",
    }


def _cpc_codes(metadata: dict) -> list[str]:
    return [str(code) for code in metadata.get("cpcClassificationBag") or []]


def _keeps_patent(title: str, codes: list[str]) -> bool:
    if "volleyball" not in title.casefold():
        return False
    return any(code.startswith(_CPC_PREFIXES) for code in codes)


def parse_uspto_search(payload: dict, retrieved_at: datetime) -> list[PatentSignal]:
    rows: list[PatentSignal] = []
    bag = payload.get("patentFileWrapperDataBag") or []
    for item in bag:
        metadata = item.get("applicationMetaData") or {}
        title = str(metadata.get("inventionTitle") or "")
        codes = _cpc_codes(metadata)
        if not _keeps_patent(title, codes):
            continue
        patent_number = str(metadata.get("patentNumber") or "")
        application = str(item.get("applicationNumberText") or "")
        if patent_number:
            external_id = (
                patent_number
                if patent_number.startswith("US")
                else f"US{patent_number}"
            )
            url = f"https://patents.google.com/patent/{external_id}"
        elif application:
            external_id = application
            url = f"https://api.uspto.gov/api/v1/patent/applications/{application}"
        else:
            continue
        body = {"external_id": external_id, "title": title, "cpc": codes}
        provenance = stamp(url, retrieved_at, body)
        rows.append(
            PatentSignal(
                signal_type="patent",
                external_id=external_id,
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


def fetch_patents(
    client: httpx.Client,
    retrieved_at: datetime,
    api_key: str | None = None,
) -> list[PatentSignal]:
    key = os.environ.get(USPTO_API_KEY_ENV, "") if api_key is None else api_key
    if not key.strip():
        raise PatentSourceError(
            "Set USPTO_ODP_API_KEY. PatentsView search.patentsview.org stopped "
            "resolving when PatentsView moved to the USPTO Open Data Portal on "
            "20 March 2026, and that portal requires the key."
        )
    response = client.post(
        USPTO_SEARCH_URL,
        json=build_patent_query(),
        headers={"User-Agent": USER_AGENT, "X-API-KEY": key},
    )
    response.raise_for_status()
    return parse_uspto_search(response.json(), retrieved_at)


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
