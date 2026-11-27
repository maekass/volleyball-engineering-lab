"""Build the point-in-time SQLite file from sourced benchmarks and rule records."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from db.provenance import canonical_bytes, stamp
from db.schema import (
    Base,
    ClinicalBenchmarkRow,
    Signal,
    create_engine_for,
    session_factory,
)
from engines.msk_validation_audit import BENCHMARKS
from sqlalchemy import select

AS_OF = datetime(2026, 11, 27, 15, 0, tzinfo=UTC)

_SOURCE_SIGNALS = (
    {
        "signal_type": "rule",
        "title": "2026 and 2027 Division I women's volleyball rules changes",
        "source_url": (
            "https://ncaaorg.s3.amazonaws.com/championships/sports/volleyball/"
            "rules/women/2026-27PRWVB_D1RulesChanges.pdf"
        ),
        "payload": {
            "rules": ["1.2.2", "15.2.4.3", "18.1.4.7"],
            "season": "2026-2027",
        },
    },
    {
        "signal_type": "rule",
        "title": "NCAA women's volleyball challenge review system manual, 2026-27",
        "source_url": (
            "https://ncaaorg.s3.amazonaws.com/championships/sports/volleyball/"
            "rules/women/2026-27PRWVB_CRSmanual.pdf"
        ),
        "payload": {"rules": ["18.1.4.7", "18.1.5.1"], "season": "2026-2027"},
    },
    {
        "signal_type": "publication",
        "title": "Sanders et al. positional jump loads, NCAA Division I women",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11669427/",
        "payload": {"pmcid": "PMC11669427", "cohort": "ncaa_d1_women_16_week_daily"},
    },
    {
        "signal_type": "publication",
        "title": "Skazalski, Whiteley, and Bahr 2018 professional jump demands",
        "source_url": "https://doi.org/10.1111/sms.13255",
        "payload": {"doi": "10.1111/sms.13255"},
    },
    {
        "signal_type": "publication",
        "title": "Rabello et al. patellar tendon structure and preseason load",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6850050/",
        "payload": {"pmcid": "PMC6850050"},
    },
    {
        "signal_type": "transaction",
        "title": "LOVB $100 million committed funding, 21 November 2024",
        "source_url": "https://www.lovb.com/news/100m-in-new-funding-for-league-one-volleyball",
        "payload": {"amount_usd": 100_000_000, "sum_note": "point amount; cumulative is separate"},
    },
)


def seed_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine_for(path)
    Base.metadata.create_all(engine)
    factory = session_factory(engine)
    with factory() as session:
        existing = session.scalars(select(Signal).limit(1)).first()
        if existing is not None:
            return
        for spec in _SOURCE_SIGNALS:
            provenance = stamp(spec["source_url"], AS_OF, spec["payload"])
            session.add(
                Signal(
                    signal_type=spec["signal_type"],
                    title=spec["title"],
                    source_url=provenance.source_url,
                    retrieved_at=provenance.retrieved_at,
                    content_sha256=provenance.content_sha256,
                    payload_json=canonical_bytes(spec["payload"]).decode("utf-8"),
                )
            )
        for benchmark in BENCHMARKS.values():
            payload = {
                "benchmark_id": benchmark.benchmark_id,
                "cohort_id": benchmark.cohort_id,
                "position": benchmark.position,
                "metric": benchmark.metric,
                "mean": benchmark.mean,
                "sd": benchmark.sd,
                "unit": benchmark.unit,
                "reported_share": benchmark.reported_share,
            }
            provenance = stamp(benchmark.source_url, AS_OF, payload)
            session.add(
                ClinicalBenchmarkRow(
                    benchmark_id=benchmark.benchmark_id,
                    cohort_id=benchmark.cohort_id,
                    position=benchmark.position,
                    metric=benchmark.metric,
                    mean_value=format(benchmark.mean, "f"),
                    sd_value=None if benchmark.sd is None else format(benchmark.sd, "f"),
                    unit=benchmark.unit,
                    citation=benchmark.citation,
                    source_url=provenance.source_url,
                    retrieved_at=provenance.retrieved_at,
                    content_sha256=provenance.content_sha256,
                )
            )
        session.commit()


def _default_database_path() -> Path:
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "data").is_dir() and (candidate / "pyproject.toml").is_file():
            return candidate / "data" / "vvii_intel.db"
    raise FileNotFoundError("engine data directory not found")


if __name__ == "__main__":
    destination = _default_database_path()
    seed_database(destination)
    print(json.dumps({"database": str(destination), "retrieved_at": AS_OF.isoformat()}))
