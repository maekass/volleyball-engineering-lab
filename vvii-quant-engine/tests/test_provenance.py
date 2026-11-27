"""Audit rules: source URLs, timestamps, ledger sums, and deterministic scores."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from artifacts.render_deck import render_deck_html
from artifacts.render_memo import render_memo_html
from artifacts.render_tearsheet import GateError, render_tearsheet_html
from db.ledger import load_ledger, summarize_ledger
from db.provenance import ProvenanceError, content_sha256, stamp
from db.schema import DiligenceScoreRow, Signal, create_engine_for, session_factory
from db.seed import seed_database
from engines.spv_economics import first_close_math
from engines.target_scorer import (
    TEARSHEET_THRESHOLD,
    TargetEvidence,
    score_target,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

AS_OF = datetime(2026, 11, 27, 15, 0, tzinfo=UTC)
ENGINE_ROOT = Path(__file__).resolve().parents[1]


def _evidence(**overrides: object) -> TargetEvidence:
    base = {
        "target_id": "synthetic-optical-001",
        "display_name": "Synthetic Optical Example",
        "record_status": "synthetic_example",
        "source_url": "https://example.edu/vvii/synthetic-optical-001",
        "hardware_agnostic": True,
        "frame_rate_fps": Decimal(60),
        "single_camera": True,
        "exports_live_dvw": True,
        "integrates_dvw": True,
        "integrates_hudl": True,
        "integrates_otto_or_sportwrench": False,
        "standalone_only": False,
        "addresses_crs": False,
        "addresses_centerline": True,
        "addresses_logos": False,
        "force_plate_r": None,
        "peer_reviewed_validation": False,
        "named_acquirers": ("Hudl", "Catapult"),
    }
    base.update(overrides)
    return TargetEvidence(**base)  # type: ignore[arg-type]


def test_stamp_requires_https_url_and_aware_timestamp() -> None:
    payload = {"rule": "15.2.4.3", "value": Decimal("0.05")}
    stamped = stamp(
        "https://ncaaorg.s3.amazonaws.com/championships/sports/volleyball/rules/women/2026-27PRWVB_D1RulesChanges.pdf",
        AS_OF,
        payload,
    )
    assert stamped.source_url.startswith("https://")
    assert stamped.retrieved_at == AS_OF
    assert stamped.content_sha256 == content_sha256(payload)
    assert len(stamped.content_sha256) == 64


@pytest.mark.parametrize(
    "source_url",
    [None, "", "   ", "notaurl", "ftp://example.edu/rules.pdf"],
)
def test_stamp_rejects_missing_or_non_http_source(source_url: str | None) -> None:
    with pytest.raises(ProvenanceError):
        stamp(source_url, AS_OF, {"rule": "15.2.4.3"})


def test_stamp_rejects_naive_timestamp() -> None:
    with pytest.raises(ProvenanceError):
        stamp(
            "https://example.edu/rules.pdf",
            datetime(2026, 11, 27, 15, 0),  # noqa: DTZ001
            {"rule": "15.2.4.3"},
        )


def test_content_hash_is_order_independent_and_stable() -> None:
    left = content_sha256({"b": 1, "a": Decimal("3.75")})
    right = content_sha256({"a": Decimal("3.75"), "b": 1})
    assert left == right
    assert left == content_sha256({"a": Decimal("3.75"), "b": 1})
    assert left != content_sha256({"a": Decimal("3.76"), "b": 1})


def test_score_is_deterministic_and_acquirer_order_does_not_matter() -> None:
    first = score_target(_evidence(named_acquirers=("Catapult", "Hudl")))
    second = score_target(_evidence(named_acquirers=("Hudl", "Catapult")))
    assert first.composite == second.composite
    assert first.input_sha256 == second.input_sha256
    assert first.technical_ingestion == Decimal("5.00")
    assert first.workflow_lock_in == Decimal("5.00")
    assert first.catalyst == Decimal("3.00")
    assert first.exit_path == Decimal("4.00")
    assert first.composite == Decimal("4.3000")
    assert first.gate_pass is True
    assert first.composite >= TEARSHEET_THRESHOLD


def test_below_threshold_does_not_pass_the_tearsheet_gate() -> None:
    result = score_target(
        _evidence(
            hardware_agnostic=False,
            frame_rate_fps=Decimal(30),
            single_camera=False,
            exports_live_dvw=False,
            integrates_dvw=False,
            integrates_hudl=False,
            standalone_only=True,
            addresses_centerline=False,
            named_acquirers=(),
        )
    )
    assert result.composite == Decimal("0.2500")
    assert result.gate_pass is False
    with pytest.raises(GateError):
        render_tearsheet_html(result)


def test_force_plate_gate_uses_peer_reviewed_r_at_or_above_0_85() -> None:
    cleared = score_target(
        _evidence(
            addresses_centerline=False,
            force_plate_r=Decimal("0.85"),
            peer_reviewed_validation=True,
            named_acquirers=("Otto Sport",),
        )
    )
    assert cleared.catalyst == Decimal("4.00")
    short = score_target(
        _evidence(
            addresses_centerline=False,
            force_plate_r=Decimal("0.8499"),
            peer_reviewed_validation=True,
        )
    )
    assert short.catalyst == Decimal("1.00")
    unpublished = score_target(
        _evidence(
            addresses_centerline=False,
            force_plate_r=Decimal("0.95"),
            peer_reviewed_validation=False,
        )
    )
    assert unpublished.catalyst == Decimal("1.00")


def test_ledger_point_sum_excludes_floors_valuations_and_restatements() -> None:
    ledger = load_ledger(ENGINE_ROOT / "data" / "precedent_transactions.json")
    summary = summarize_ledger(ledger)
    amounts = {row["id"]: row["amount_usd"] for row in ledger["transactions"]}
    assert amounts["lovb-series-a-2022-09"] == 16_750_000
    assert amounts["lovb-series-b-2023-09"] == 35_000_000
    assert amounts["lovb-2024-11-21-atwater"] == 100_000_000
    assert amounts["catapult-xos-2016-07-13"] == 60_000_000
    assert amounts["hudl-bain-2020-05"] == 120_000_000
    assert summary.volleyball_exclusive_point_usd == 151_750_000
    assert summary.adjacent_point_usd == 180_000_000
    assert summary.audited_point_sum_usd == 331_750_000
    assert "pvf-commitment-floor" in summary.excluded_ids
    assert "mlv-2026-launch-funding-secondary" in summary.excluded_ids
    assert "au-2022-platform-round" in summary.excluded_ids
    assert "hudl-volleymetrics-2017-12-13" in summary.excluded_ids
    assert "hudl-balltime-2025-02-06" in summary.excluded_ids
    cumulative_rows = [
        row["amount_usd"]
        for row in ledger["transactions"]
        if row["amount_usd"] == 160_000_000
    ]
    assert cumulative_rows == []
    atwater = next(
        row for row in ledger["transactions"] if row["id"] == "lovb-2024-11-21-atwater"
    )
    assert atwater["issuer_reported_cumulative_usd"] == 160_000_000


def test_database_rejects_null_source_url_and_stores_score_hash(tmp_path: Path) -> None:
    path = tmp_path / "vvii_intel.db"
    seed_database(path)
    engine = create_engine_for(path)
    factory = session_factory(engine)
    with factory() as session:
        signals = session.scalars(select(Signal)).all()
        assert signals
        assert all(row.source_url.startswith("https://") for row in signals)
        assert all(row.retrieved_at.tzinfo is not None for row in signals)
        assert all(len(row.content_sha256) == 64 for row in signals)
        result = score_target(_evidence())
        session.add(
            DiligenceScoreRow.from_result(result, computed_at=AS_OF)
        )
        session.commit()
        stored = session.scalars(select(DiligenceScoreRow)).one()
        assert stored.composite == Decimal("4.3000")
        assert stored.input_sha256 == result.input_sha256
        assert stored.gate_pass is True
        session.add(
            Signal(
                signal_type="rule",
                title="missing source",
                source_url=None,
                retrieved_at=AS_OF,
                content_sha256="0" * 64,
                payload_json="{}",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.parametrize("source_url", ["", "ftp://example.edu/rules.pdf", "notaurl"])
def test_database_check_rejects_non_http_source_url(tmp_path: Path, source_url: str) -> None:
    path = tmp_path / "vvii_intel.db"
    seed_database(path)
    factory = session_factory(create_engine_for(path))
    with factory() as session:
        session.add(
            Signal(
                signal_type="rule",
                title="non-http source",
                source_url=source_url,
                retrieved_at=AS_OF,
                content_sha256="0" * 64,
                payload_json="{}",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_bundled_database_rejects_blank_source_url(tmp_path: Path) -> None:
    source = ENGINE_ROOT / "data" / "vvii_intel.db"
    copy = tmp_path / "vvii_intel.db"
    copy.write_bytes(source.read_bytes())
    connection = sqlite3.connect(copy)
    ddl = connection.execute(
        "SELECT sql FROM sqlite_master WHERE name = 'signals'"
    ).fetchone()[0]
    assert "ck_signals_source_url_http" in ddl
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO signals (signal_type, title, source_url, retrieved_at, "
            "content_sha256, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
            ("rule", "blank", "", "2026-11-27 15:00:00", "0" * 64, "{}"),
        )
    connection.close()


def test_orthopedic_alias_counts_as_one_acquirer() -> None:
    shared = {
        "exports_live_dvw": False,
        "integrates_hudl": False,
        "addresses_centerline": False,
        "force_plate_r": Decimal("0.85"),
        "peer_reviewed_validation": True,
    }
    singular = score_target(_evidence(**shared, named_acquirers=("orthopedic health system",)))
    both_spellings = score_target(
        _evidence(
            **shared,
            named_acquirers=("Orthopedic Health System", "orthopedic health systems"),
        )
    )
    assert singular.technical_ingestion == Decimal("3.75")
    assert singular.workflow_lock_in == Decimal("4.00")
    assert singular.catalyst == Decimal("4.00")
    assert singular.exit_path == Decimal("3.00")
    assert both_spellings.exit_path == Decimal("3.00")
    assert singular.composite == Decimal("3.7250")
    assert both_spellings.composite == singular.composite
    assert singular.gate_pass is False
    assert singular.input_sha256 == both_spellings.input_sha256


def test_first_close_math_reconciles_six_to_seven_lps() -> None:
    math = first_close_math()
    assert math.target_net_usd == 100_000
    assert math.management_fee == Decimal(0)
    assert math.carry_low == Decimal("0.15")
    assert math.carry_high == Decimal("0.20")
    assert math.sydecar_setup_low_usd == 4_500
    assert math.sydecar_setup_high_usd == 14_500
    assert math.minimum_gross_low_usd == 104_500
    assert math.minimum_gross_high_usd == 114_500
    assert math.illustrative_check_usd == 25_000
    assert math.soft_circle_low_usd == 150_000
    assert math.soft_circle_high_usd == 175_000
    assert math.lp_count_low == 6
    assert math.lp_count_high == 7
    assert math.lp_count_low * math.illustrative_check_usd == math.soft_circle_low_usd
    assert math.lp_count_high * math.illustrative_check_usd == math.soft_circle_high_usd


def test_memo_and_deck_carry_mandate_terms_and_audited_sum() -> None:
    memo = render_memo_html()
    deck = render_deck_html()
    assert "0% management fee" in memo
    assert "$100,000" in memo and "$350,000" in memo
    assert "$331,750,000" in memo
    assert "not an offer" in memo.lower()
    assert "transferab" in memo.lower()
    assert memo.count("<h2>") >= 4
    assert deck.count('<section class="slide">') == 6
    assert "size: 11in 8.5in" in deck
    assert "$331,750,000" in deck


def test_tearsheet_renders_only_at_or_above_threshold() -> None:
    html = render_tearsheet_html(score_target(_evidence()))
    assert "4.3000" in html
    assert "Synthetic Optical Example" in html
    assert "synthetic_example" in html
    borderline = score_target(
        _evidence(
            integrates_hudl=False,
            addresses_centerline=False,
            addresses_crs=True,
            addresses_logos=True,
            force_plate_r=Decimal("0.85"),
            peer_reviewed_validation=True,
            named_acquirers=("Hudl", "Otto Sport", "Catapult"),
        )
    )
    # 5*0.30 + 4*0.25 + 5*0.25 + 5*0.20 = 1.5 + 1 + 1.25 + 1 = 4.75
    assert borderline.composite == Decimal("4.7500")
    assert "4.7500" in render_tearsheet_html(borderline)
