"""Six-slide landscape deck, 11 by 8.5 inches. Research record, not an offer."""

from __future__ import annotations

from pathlib import Path

from artifacts.formatting import ledger_summary, usd
from engines.spv_economics import first_close_math


def render_deck_html() -> str:
    _ledger, summary = ledger_summary()
    close = first_close_math()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>VVII Institutional Deck</title>
<style>
  @page {{ size: 11in 8.5in; margin: 0.55in; }}
  body {{ font-family: "Liberation Sans", "Arial", sans-serif; color: #1c1917; margin: 0; }}
  section.slide {{ page-break-after: always; min-height: 6.8in; }}
  h1 {{ font-size: 26pt; margin: 0 0 0.15in 0; }}
  h2 {{ font-size: 20pt; margin: 0 0 0.12in 0; }}
  p, li {{ font-size: 14pt; line-height: 1.35; }}
  .kicker {{ font-size: 11pt; letter-spacing: 0.06em; text-transform: uppercase; }}
</style>
</head>
<body>
<section class="slide">
  <p class="kicker">Volleyball Venture &amp; Innovation Initiative</p>
  <h1>Quantitative diligence engine</h1>
  <p>Collegiate workflows, match telemetry, scouting software, automated vision, and musculoskeletal load validation. Unfunded. Point-in-time. Auditable.</p>
  <p>This deck is not an offer to sell securities.</p>
</section>
<section class="slide">
  <h2>Zero-conflict mandate</h2>
  <ul>
    <li>$0 blind-pool assets under management.</li>
    <li>0% management fee. Carry modeled at 15%–20% on a closed deal.</li>
    <li>100% ROFR transferability upon full-time employment.</li>
    <li>No customer-relationship funnel and no advisor contract in this repository.</li>
  </ul>
</section>
<section class="slide">
  <h2>Single-deal economics</h2>
  <p>Allocation {usd(close.target_min_usd)}–{usd(close.target_max_usd)}. Checks {usd(close.lp_check_min_usd)}–{usd(close.lp_check_max_usd)}.</p>
  <p>A {usd(close.target_net_usd)} net target soft-circled at {usd(close.soft_circle_low_usd)}–{usd(close.soft_circle_high_usd)} is {close.lp_count_low}–{close.lp_count_high} partners at a {usd(close.illustrative_check_usd)} illustrative check.</p>
  <p>Setup planning range {usd(close.sydecar_setup_low_usd)}–{usd(close.sydecar_setup_high_usd)}, deducted from wires. Gross floor {usd(close.minimum_gross_low_usd)}–{usd(close.minimum_gross_high_usd)}.</p>
</section>
<section class="slide">
  <h2>Precedent ledger, 2016–2026</h2>
  <p>Audited point sum {usd(summary.audited_point_sum_usd)}.</p>
  <p>Volleyball-exclusive {usd(summary.volleyball_exclusive_point_usd)}. Adjacent infrastructure {usd(summary.adjacent_point_usd)}.</p>
  <p>Floors, valuations, undisclosed prices, and cumulative restatements stay in the file and stay out of the sum. LOVB's stated $160 million cumulative is context on the November 2024 round, not a fourth cash amount.</p>
</section>
<section class="slide">
  <h2>2026–27 rule geometry</h2>
  <ul>
    <li>Center line: 5 cm, shared by both courts. A complete foot cross plus court contact is a fault under Rule 15.2.4.3.</li>
    <li>That foot fault is reviewable under Rule 18.1.4.7. Two challenges per team; a fifth set adds one, capped at two.</li>
    <li>Commercial logos: at most two, one per half, inside a 3 m box between the attack line and the end line. Rule 1.2.2.4.</li>
  </ul>
</section>
<section class="slide">
  <h2>Score and tear-sheet gate</h2>
  <ul>
    <li>Technical ingestion, 30%. Single camera, hardware-agnostic, 60 fps or faster, live .dvw export.</li>
    <li>Workflow lock-in, 25%. Data Volley, Hudl, or Otto Sport / SportWrench.</li>
    <li>Rule-cycle or clinical catalyst, 25%. NCAA mandate, or peer-reviewed r at least 0.85 versus a force plate.</li>
    <li>Exit path, 20%. Hudl, Otto Sport, Catapult, SeatGeek / Paciolan, or an orthopedic health system.</li>
  </ul>
  <p>Composite threshold for a one-page tear-sheet: 3.75.</p>
</section>
</body>
</html>
"""


def write_deck_pdf(path: Path) -> None:
    from artifacts.render_pdf import write_pdf

    write_pdf(render_deck_html(), path)
