"""Positional jump-load benchmarks and a comparison against supplied claims.

Published means are stored as printed. A share printed in the source is stored
beside the ratio of those means and is not replaced by it. No force-plate
correlation is inferred from a percent-agreement figure.

Sources:
- Sanders et al., Translational Sports Medicine, PMC11669427.
  Daily means, NCAA Division I women, 16-week season, n=12.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11669427/
- Skazalski, Whiteley, and Bahr, Scand J Med Sci Sports, 2018;28:2293-2298.
  doi:10.1111/sms.13255. Professional club, Vert Classic IMU.
- Rabello et al., patellar-tendon UTC, elite men, 7-week preseason.
  Weekly jump frequency 269 (SD 90). PMC6850050.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6850050/
"""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

_FORCE_PLATE_R = Decimal("0.85")

SANDERS_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11669427/"
SANDERS_CITATION = (
    "Sanders GJ, Skodinski S, Cabarkapa DV, Howard M, Cabarkapa D, Peacock CA. "
    "Positional Differences in Jump Loads and Force and Velocity Metrics "
    "Throughout a 16-Week Division I Volleyball Season. "
    "Translational Sports Medicine. PMC11669427."
)
SKAZALSKI_URL = "https://doi.org/10.1111/sms.13255"
SKAZALSKI_CITATION = (
    "Skazalski C, Whiteley R, Bahr R. High jump demands in professional "
    "volleyball—large variability exists between players and player positions. "
    "Scandinavian Journal of Medicine & Science in Sports. 2018;28(11):2293-2298. "
    "doi:10.1111/sms.13255."
)
RABELLO_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6850050/"
RABELLO_CITATION = (
    "Rabello LM, Zwerver J, Stewart RE, van den Akker-Scheek I, Brink MS. "
    "Patellar tendon structure responds to load over a 7-week preseason in "
    "elite male volleyball players. PMC6850050."
)


class Benchmark(BaseModel):
    model_config = ConfigDict(frozen=True)

    benchmark_id: str
    cohort_id: str
    position: str
    metric: str
    mean: Decimal
    sd: Decimal | None
    unit: str
    reported_share: Decimal | None = None
    instrument: str
    citation: str
    source_url: str
    force_plate_r: Decimal | None = None
    population_note: str


class CommercialClaim(BaseModel):
    model_config = ConfigDict(frozen=True)

    claim_id: str
    vendor: str
    record_status: str
    cohort_id: str
    position: str
    metric: str
    unit: str
    value: Decimal
    force_plate_r: Decimal | None
    peer_reviewed: bool
    source_url: str


class AuditFinding(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    reason: str | None
    z: Decimal | None
    band: str | None
    benchmark_id: str | None
    claim_id: str
    meets_force_plate_gate: bool


def _sanders(
    benchmark_id: str,
    position: str,
    metric: str,
    mean: str,
    sd: str,
    share: str | None,
) -> Benchmark:
    return Benchmark(
        benchmark_id=benchmark_id,
        cohort_id="ncaa_d1_women_16_week_daily",
        position=position,
        metric=metric,
        mean=Decimal(mean),
        sd=Decimal(sd),
        unit="jumps_per_day",
        reported_share=None if share is None else Decimal(share),
        instrument="wearable_microsensor",
        citation=SANDERS_CITATION,
        source_url=SANDERS_URL,
        population_note=(
            "Daily average across a 16-week NCAA Division I women's season, "
            "n=12. Thresholds printed in the abstract are 38.1 cm and 50.8 cm. "
            "reported_share is the percentage printed in the source table."
        ),
    )


def _skazalski(
    benchmark_id: str,
    cohort_id: str,
    position: str,
    metric: str,
    unit: str,
    mean: str,
) -> Benchmark:
    return Benchmark(
        benchmark_id=benchmark_id,
        cohort_id=cohort_id,
        position=position,
        metric=metric,
        mean=Decimal(mean),
        sd=None,
        unit=unit,
        instrument="vert_classic_imu",
        citation=SKAZALSKI_CITATION,
        source_url=SKAZALSKI_URL,
        population_note=(
            "Professional club season, 14 players, Vert Classic at the waist. "
            "The paper prints these frequencies without a standard deviation, "
            "so this row cannot support a z-score."
        ),
    )


def _build() -> dict[str, Benchmark]:
    sanders_rows = [
        ("mb", "MB", "84.1", "44.9", None, "65.4", "39.2", "0.778", "39.5", "32.7", "0.446"),
        ("oh", "OH", "59.2", "34.2", None, "39.4", "25.9", "0.666", "15.0", "15.6", "0.253"),
        ("opp", "OPP", "66.5", "26.7", None, "47.9", "24.1", "0.720", "29.7", "18.1", "0.447"),
        ("s", "S", "111.6", "61.9", None, "19.0", "16.6", "0.170", "0.4", "0.8", "0.003"),
    ]
    rows: dict[str, Benchmark] = {}
    for (
        slug,
        position,
        total,
        total_sd,
        _total_share,
        high,
        high_sd,
        high_share,
        higher,
        higher_sd,
        higher_share,
    ) in sanders_rows:
        rows[f"sanders2025-{slug}-daily-total"] = _sanders(
            f"sanders2025-{slug}-daily-total",
            position,
            "total_jumps",
            total,
            total_sd,
            None,
        )
        rows[f"sanders2025-{slug}-daily-38"] = _sanders(
            f"sanders2025-{slug}-daily-38",
            position,
            "jumps_38cm",
            high,
            high_sd,
            high_share,
        )
        rows[f"sanders2025-{slug}-daily-50"] = _sanders(
            f"sanders2025-{slug}-daily-50",
            position,
            "jumps_50cm",
            higher,
            higher_sd,
            higher_share,
        )
    match = {"S": "67", "MB": "57", "OPP": "53", "OH": "47"}
    training_session = {"S": "121", "MB": "92", "OPP": "75", "OH": "62"}
    training_hour = {"S": "92", "MB": "70", "OPP": "58", "OH": "49"}
    for position, mean in match.items():
        slug = position.casefold()
        rows[f"skazalski2018-{slug}-match-per-hour"] = _skazalski(
            f"skazalski2018-{slug}-match-per-hour",
            "professional_match_per_hour",
            position,
            "match_jump_frequency",
            "jumps_per_hour",
            mean,
        )
    rows["skazalski2018-mb-match-per-hour-on-court"] = _skazalski(
        "skazalski2018-mb-match-per-hour-on-court",
        "professional_match_per_hour_on_court",
        "MB",
        "match_jump_frequency_on_court",
        "jumps_per_hour_on_court",
        "98",
    )
    for position, mean in training_session.items():
        slug = position.casefold()
        rows[f"skazalski2018-{slug}-training-session"] = _skazalski(
            f"skazalski2018-{slug}-training-session",
            "professional_training_session",
            position,
            "training_jumps",
            "jumps_per_session",
            mean,
        )
    for position, mean in training_hour.items():
        slug = position.casefold()
        rows[f"skazalski2018-{slug}-training-per-hour"] = _skazalski(
            f"skazalski2018-{slug}-training-per-hour",
            "professional_training_per_hour",
            position,
            "training_jump_frequency",
            "jumps_per_hour",
            mean,
        )
    rows["rabello-roster-weekly-jumps"] = Benchmark(
        benchmark_id="rabello-roster-weekly-jumps",
        cohort_id="elite_male_preseason_weekly",
        position="ROSTER",
        metric="weekly_jump_frequency",
        mean=Decimal(269),
        sd=Decimal(90),
        unit="jumps_per_week",
        instrument="zephyr_bioharness_3",
        citation=RABELLO_CITATION,
        source_url=RABELLO_URL,
        population_note=(
            "Eighteen elite male players, 7-week preseason. Mean weekly jump "
            "frequency 269 (SD 90). Video agreement of 88.2% to 100% is percent "
            "agreement with manual counts, not a Pearson r against a force plate."
        ),
    )
    return rows


BENCHMARKS = _build()
_POSITION_ORDER = ("MB", "OH", "OPP", "S")


def get_benchmark(benchmark_id: str) -> Benchmark:
    return BENCHMARKS[benchmark_id]


def intensity_ratio_of_means(high: Benchmark, total: Benchmark) -> Decimal:
    if total.mean == 0:
        raise ValueError("total mean is zero")
    return high.mean / total.mean


def meets_force_plate_gate(correlation: Decimal | None, peer_reviewed: bool) -> bool:
    return bool(
        peer_reviewed and correlation is not None and correlation >= _FORCE_PLATE_R
    )


def audit_claim(claim: CommercialClaim) -> AuditFinding:
    gate = meets_force_plate_gate(claim.force_plate_r, claim.peer_reviewed)
    candidates = [
        row
        for row in BENCHMARKS.values()
        if row.cohort_id == claim.cohort_id
        and row.position == claim.position
        and row.metric == claim.metric
    ]
    if not candidates:
        return AuditFinding(
            status="not_comparable",
            reason="no_benchmark",
            z=None,
            band=None,
            benchmark_id=None,
            claim_id=claim.claim_id,
            meets_force_plate_gate=gate,
        )
    matched = [row for row in candidates if row.unit == claim.unit]
    if not matched:
        return AuditFinding(
            status="not_comparable",
            reason="unit_mismatch",
            z=None,
            band=None,
            benchmark_id=candidates[0].benchmark_id,
            claim_id=claim.claim_id,
            meets_force_plate_gate=gate,
        )
    benchmark = matched[0]
    if benchmark.sd is None or benchmark.sd == 0:
        return AuditFinding(
            status="not_comparable",
            reason="missing_dispersion",
            z=None,
            band=None,
            benchmark_id=benchmark.benchmark_id,
            claim_id=claim.claim_id,
            meets_force_plate_gate=gate,
        )
    z_value = ((claim.value - benchmark.mean) / benchmark.sd).quantize(
        Decimal("0.0001"),
        rounding=ROUND_HALF_EVEN,
    )
    magnitude = abs(z_value)
    if magnitude <= 1:
        band = "within_one_sd"
    elif magnitude <= 2:
        band = "within_two_sd"
    else:
        band = "beyond_two_sd"
    return AuditFinding(
        status="z_scored",
        reason=None,
        z=z_value,
        band=band,
        benchmark_id=benchmark.benchmark_id,
        claim_id=claim.claim_id,
        meets_force_plate_gate=gate,
    )


def benchmarks_frame() -> pd.DataFrame:
    records = []
    for row in BENCHMARKS.values():
        records.append(
            {
                "benchmark_id": row.benchmark_id,
                "cohort_id": row.cohort_id,
                "position": row.position,
                "metric": row.metric,
                "mean": float(row.mean),
                "sd": None if row.sd is None else float(row.sd),
                "unit": row.unit,
                "source_url": row.source_url,
            }
        )
    return pd.DataFrame.from_records(records)


def positional_total_jump_means() -> np.ndarray:
    values = [
        float(
            get_benchmark(f"sanders2025-{position.casefold()}-daily-total").mean
        )
        for position in _POSITION_ORDER
    ]
    return np.array(values, dtype=float)
