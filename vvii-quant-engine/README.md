# VVII Quantitative Diligence Engine

Point-in-time market intelligence and technical diligence for the U.S. and global volleyball market. The engine covers collegiate workflows, match telemetry, scouting software, automated vision, and musculoskeletal load validation.

Principal frame: Mae Kass, MPH, MS. Healthcare and diagnostics, private markets, quantitative systems.

## Zero-conflict mandate

VVII is an unfunded research and deal-by-deal co-investment readiness platform.

- Blind-pool assets under management: **$0**
- Management fee: **0%**
- Carry on a closed single-deal vehicle: **15%–20%**, as a planning parameter
- Transfer: **100% ROFR transferability upon full-time employment**

This repository does not contain a CRM, a sequencing tool, or a binding general-partner or advisor contract. Nothing in `src/artifacts/` is an offer to sell securities or a solicitation of an offer to buy securities.

## What the engine scores

Allocation per deal is modeled at **$100,000–$350,000**. Limited-partner checks are modeled at **$10,000–$50,000**. A Sydecar-style pass-through setup of **$4,500–$14,500** is a planning range deducted from wires, not a vendor quote. On a $100,000 net target the gross floor is therefore $104,500–$114,500.

The mandate's first-close soft circle is **$150,000–$175,000**, which is **6–7** limited partners at a **$25,000** illustrative check. That check is the size that reconciles the partner count with the soft-circle band. It sits inside the $10,000–$50,000 range. The calculation lives in `engines/spv_economics.py`.

Market coverage, separate from the score weights:

1. Volleyball-native software and NCAA contractor enablement, including hardware-agnostic single-camera optical ingestion at 60 frames per second or faster with a live Data Volley (`.dvw`) export.
2. Match telemetry and automated vision.
3. Scouting software and collegiate workflows.
4. Musculoskeletal load systems with a clinical validation record.

Diligence score, 0–5, weights sum to 1:

| Pillar | Weight | Full-score evidence |
| --- | --- | --- |
| Technical ingestion | 30% | Hardware-agnostic, one camera, at least 60 fps, live `.dvw` export. Each flag is 1.25. |
| Workflow and `.dvw` lock-in | 25% | Native `.dvw` plus Hudl or Otto Sport / SportWrench = 5. `.dvw` alone = 4. Hudl or Otto without `.dvw` = 3. Standalone dashboard = 1. |
| Rule-cycle or clinical catalyst | 25% | 2026–27 NCAA center line (Rule 15.2.4.3), court logos (Rule 1.2.2.4), or challenge review (Rule 18.1.4.7), and/or a peer-reviewed Pearson r of at least 0.85 against a force plate. |
| M&A / exit path | 20% | Named fit with Hudl, Otto Sport, Catapult, SeatGeek, Paciolan, or an orthopedic health system. |

The 25/25/20 weights are the workflow, catalyst, and exit weights in the mandate. The remaining 30% is technical ingestion. A one-page tear-sheet is rendered only when the composite is **at least 3.75**. The same evidence always yields the same composite and the same SHA-256 input hash. Acquirer order does not change the hash.

## Provenance

Every stored signal carries a non-null `http` or `https` source URL, a timezone-aware retrieval timestamp, and a SHA-256 of the canonical JSON payload. Naive timestamps and empty URLs are rejected in `db/provenance.py` and by the SQLite schema. Retrieval time for the seeded database is fixed at 2026-11-27 15:00 UTC so the file can be rebuilt.

## Precedent ledger

`data/precedent_transactions.json` is a 2016–2026 ledger in three tiers: pro-league capital, volleyball-native software, and adjacent performance or venue infrastructure.

`summarize_ledger` adds a row only when `sum_eligible` is true. As compiled on 27 November 2026, that audited point sum is **$331,750,000**:

- Volleyball-exclusive: LOVB Series A $16.75 million (September 2022), Series B $35 million (September 2023), and the 21 November 2024 Atwater-led round of $100 million. Subtotal **$151,750,000**.
- Adjacent: Catapult's XOS acquisition, US$60 million (announced 13 July 2016), and Hudl's May 2020 Bain financing of $120 million. Subtotal **$180,000,000**.

LOVB's stated cumulative of $160 million is stored on the November 2024 row and is not added again. The PVF "more than $150 million" commitment, the secondary MLV funding reports, the Athletes Unlimited multi-sport round, undisclosed Hudl acquisitions (VolleyMetrics, 13 December 2017; Balltime, 6 February 2025), the Learfield/Paciolan terms, and the SeatGeek–Paciolan partnership are in the file and out of the sum. A $750 million ecosystem total is not the audited sum of this ledger.

Sourced franchise counts, dated to the 6 August 2025 Front Office Sports report and not updated past that source: LOVB Pro 6, MLV 8 named clubs for the 2026 season, Athletes Unlimited volleyball 4. A program-level NCAA census is not in this database.

## Rule geometry and jump load

`engines/dvw_rule_simulator.py` implements the 2026–27 center-line test: the line is 5 cm wide and belongs to both courts, so a foot still touching the line has not completely crossed. A complete cross that contacts the opponent's court is a fault under Rule 15.2.4.3 and is reviewable under Rule 18.1.4.7. Each team starts with two challenges; a fifth set adds one, capped at two. Logo boxes must be at most 3 m and must sit strictly between the attack line and the end line, one commercial logo per half. Match-log output counts status changes. It does not forecast official or coach behavior. The 720-pixel sampling bound is geometry across an 18 m court, not a calibrated camera model.

`engines/msk_validation_audit.py` stores published positional means:

- Sanders et al., Translational Sports Medicine, PMC11669427. Daily jumps for 12 NCAA Division I women over 16 weeks. Middle blockers 84.1 (SD 44.9); outside hitters 59.2 (SD 34.2); opposites 66.5 (SD 26.7); setters 111.6 (SD 61.9). High-intensity cuts printed in the abstract are 38.1 cm and 50.8 cm. Printed shares are kept as printed. The middle-blocker share at the higher cut (0.446) is not the ratio of the printed means.
- Skazalski, Whiteley, and Bahr, Scand J Med Sci Sports, 2018, doi:10.1111/sms.13255. Professional match frequencies in jumps per hour: setters 67, middles 57, opposites 53, outsides 47; middles 98 per on-court hour after the 7/12 rotation adjustment. No standard deviation is printed, so these rows do not support a z-score. Instrument: Vert Classic.
- Rabello et al., PMC6850050. Elite men, 7-week preseason, weekly jump frequency 269 (SD 90). Video agreement of 88.2%–100% is percent agreement with manual counts. It is not recorded as a force-plate correlation.

A claim is z-scored only when cohort, position, metric, and unit match and the benchmark has a non-zero standard deviation. The force-plate gate is a supplied, peer-reviewed r of at least 0.85. The engine does not invent one.

## Ingestion

Clients take an `httpx.Client`, so tests run on a mock transport and a live pull is a deliberate call.

- `ingest/openalex_msk.py` — OpenAlex works search: volleyball with jump, patellar, ACL, IMU, and optical terms. Records without an HTTP identifier are rejected.
- `ingest/patents_grants.py` — PatentsView query on CPC A63B and G06V with volleyball in the abstract. NSF award search filtered to SBIR and STTR program names.
- `ingest/ncaa_rules.py` — local PDF text. Spaced NCAA numbering (`15 .2 .4 .3`) is normalized before rule 15.2.4.3, 1.2.2.4, and 18.1.4.7 are extracted. The rules books are not vendored.

## Artifacts

- `artifacts/render_memo.py` — letter memorandum.
- `artifacts/render_deck.py` — six slides, page size 11 in by 8.5 in.
- `artifacts/render_tearsheet.py` — one page, refused below 3.75.
- `artifacts/render_pdf.py` — WeasyPrint HTML-to-PDF. Import of WeasyPrint is deferred to the write call so the test suite does not require Pango and Cairo.

## Peer-to-peer exchange

Once a benchmark or the rule-geometry note is public, outbound notes stay under 85 words. The first note carries no attachment and no fundraising ask.

- Academic and clinical counterparts (Wu Tsai Human Performance Alliance, Kathryn Ackerman, Jennifer Hicks, Kang Women's Institute, Division I labs): send the jump-load or court-geometry link and one validation question.
- Volleyball software teams (including optical, wearable, and `.dvw` pipelines): send the center-line geometry note and one question on floor-plane edge cases.
- Hiring partners (Project Level, Monarch Collective, Kynisca, Trailblazer, Courtside): the memorandum PDF, the deck PDF, and the repository link, describing an unfunded sourcing and diligence engine. That package is still not a securities offer.

## Run

```bash
cd vvii-quant-engine
python -m pip install -e ".[dev]"
pytest -q
PYTHONPATH=src python -m db.seed
```

PDF output also needs the system libraries WeasyPrint documents (Pango, Cairo, GDK-PixBuf). The HTML renderers do not.

Seeded SQLite: `data/vvii_intel.db`. Rebuild with `python -m db.seed` after deleting the file. The seed does not contain scored commercial targets. Scores are computed from evidence supplied to `engines/target_scorer.py`.
