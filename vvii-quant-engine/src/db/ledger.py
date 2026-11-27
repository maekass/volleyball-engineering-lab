"""Precedent-transaction ledger. Only point-disclosed amounts are summed."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class LedgerError(ValueError):
    """The ledger file violates its own summation rules."""


@dataclass(frozen=True)
class LedgerSummary:
    volleyball_exclusive_point_usd: int
    adjacent_point_usd: int
    audited_point_sum_usd: int
    excluded_ids: tuple[str, ...]


def load_ledger(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def summarize_ledger(ledger: dict) -> LedgerSummary:
    exclusive = 0
    adjacent = 0
    excluded: list[str] = []
    for row in ledger["transactions"]:
        if not row["sum_eligible"]:
            excluded.append(row["id"])
            continue
        amount = row["amount_usd"]
        if not isinstance(amount, int):
            raise LedgerError(f"{row['id']} is marked sum-eligible without a point USD amount")
        if row["volleyball_exclusive"]:
            exclusive += amount
        else:
            adjacent += amount
    return LedgerSummary(
        volleyball_exclusive_point_usd=exclusive,
        adjacent_point_usd=adjacent,
        audited_point_sum_usd=exclusive + adjacent,
        excluded_ids=tuple(excluded),
    )
