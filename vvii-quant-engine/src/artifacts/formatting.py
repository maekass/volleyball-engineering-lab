"""Shared paths and number formatting for institutional artifacts."""

from __future__ import annotations

from html import escape
from pathlib import Path

from db.ledger import LedgerSummary, load_ledger, summarize_ledger


def usd(amount: int) -> str:
    return f"${amount:,}"


def engine_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "data" / "precedent_transactions.json").is_file():
            return candidate
    raise FileNotFoundError("vvii-quant-engine data directory not found")


def ledger_summary() -> tuple[dict, LedgerSummary]:
    ledger = load_ledger(engine_root() / "data" / "precedent_transactions.json")
    return ledger, summarize_ledger(ledger)


def text(value: object) -> str:
    return escape(str(value))
