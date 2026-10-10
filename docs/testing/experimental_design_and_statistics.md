# BALL 001 — Experimental Design, Statistics, and Verification Plan

**Status:** Pre-experimental design. Values and margins are to be fixed before
confirmatory testing; this file reports no results.

## 1. Estimands and hypotheses

**H1 / content:** For each preregistered chemical and product layer, estimate
the proportion of independent ball specimens with content above a
method-specific LOQ and the concentration distribution conditional on
quantification. Null: no quantifiable presence in tested specimens under
the stated method. A nondetect is **not** proof of chemical absence.

**H2 / migration:** Estimate cumulative released mass per contact area
(µg/cm²) at each defined time, temperature, medium, pressure and aging
condition. The primary endpoint is a prespecified migration contrast
between benchmark and candidate materials; report the absolute difference
and ratio with uncertainty. Null: no prespecified migration reduction.

**H3 / engineering equivalence:** Among candidates with evidence of reduced
migration, establish equivalence against a predefined benchmark on required
sport metrics. Null: at least one primary performance endpoint lies outside
the acceptable equivalence region. Failure to reject a difference is **not**
equivalence.

All three hypotheses are independently testable. None asserts an endocrine
health effect.

## 2. Sampling frame and units of independence

Use a two-stage design.

**Stage A — feasibility/pilot (descriptive, not confirmatory).** At least two
elite indoor competition models and BALL 001 outer-skin coupons. Record
manufacturing lot, acquisition, handling, storage, surface age, layer and
specimen IDs. Pilot chemistry establishes analyte relevance, blank
contamination, method sensitivity and variance components. No confirmatory
p-value or product-wide conclusion is justified by a tiny convenience sample.

**Stage B — confirmatory design (sample size set after pilot).** Prefer
multiple independently acquired production lots per model, multiple balls
per lot, and independent layer specimens per ball. Triplicate extraction/
migration preparations per condition are a practical minimum for QC and
variance assessment, **not** a substitute for independent product units.
Analytical injections from one extract are technical repeats.

Hierarchical structure:

```text
manufacturer/model
  └── manufacturing lot
       └── ball
            └── layer / coupon / aging arm
                 └── independent extraction or migration cell
                      └── instrument injection
```

The manifest records all levels. Never pool repeated injections as if they
were independent balls. If sample sizes cannot support population inference,
limit conclusions to the sampled articles and conditions.

## 3. Pre-registration and stopping rules

Freeze before opening confirmatory results:

- primary analytes, layers, product contrasts and time points;
- test medium pH/composition, temperature, contact area and pressure;
- baseline and candidate material identities;
- primary migration endpoint and minimum meaningful reduction;
- mechanical equivalence margins and testing standards;
- independent experimental unit and randomization/blocking;
- censoring strategy for <LOD and <LOQ observations;
- multiplicity control for primary versus exploratory analytes;
- QC thresholds from the laboratory method validation;
- analysis code commit SHA and data dictionary;
- stopping/escalation criteria.

Use `docs/research/preregistration_template.md`. Pilot modifications must
be versioned and dated; post-hoc endpoints labeled exploratory.

## 4. Chemical method validation

**G0:** ATR-FTIR/Raman identification with reference spectra, coating/
adhesive interface mapping, thickness uncertainty, and material confidence.

**G1:** Use validated GC-MS(/MS) for applicable phthalates/PAHs and
LC-MS/MS for applicable bisphenols/alkylphenols. Method selection must be
formulation-led and appropriate to the matrix; record extraction recovery,
matrix effect, calibration range, internal standards, carryover, and
identification criteria.

**G2:** Quantify migration from intact surface or layer coupon using
skin-relevant synthetic sweat with documented pH, temperature, contact
pressure, surface area and exposure duration. Distinguish total content from
migrated amount. Use time-resolved sampling to estimate transport kinetics;
blank and spike controls are mandatory.

**G3:** Measure actual cumulative ball contact using high-speed video or
validated instrumentation; separate setting, passing, serving, ball carrying,
dry/sweaty contact and practice/match context. Log uncertainties in touch
duration and contact area.

**G4:** Use route- and matrix-relevant published uptake values or OECD
TG 428-type in-vitro dermal absorption only after exposure escalation is
justified. No human biomonitoring is part of this initial study.

**G5:** Chemical-specific reference points and uncertainty reviewed by a
qualified exposure scientist/toxicologist.

**G6:** Compare new and aged candidates on mass, circumference, pressure
retention, compression, rebound, hysteresis, friction, impact and abrasion.
Use applicable FIVB requirements as constraints and predefine additional
performance margins rather than inventing standard thresholds.

## 5. QA/QC and censoring

For each analytical batch retain calibration curves, standards, procedural
blanks, field blanks where appropriate, matrix spikes, duplicate samples,
LOD, LOQ and raw chromatograms/spectra. Define laboratory-specific acceptance
ranges in the method SOP. The evidence ledger requires a hashed QC CSV
containing the actual blank, spike recovery, duplicate RPD and their limits;
a typed `PASS` label alone is insufficient.

**Nondetects:** Store the measured signal and its limit. Do not substitute
zero or LOQ/2 silently. Predefine an appropriate censored-data method (for
example interval-censored likelihood or sensitivity bounds) if the sample
size and censoring pattern permit. If most results are below LOQ, report
detection frequencies and method-limited bounds instead of fitting an
unjustified parametric distribution.

**Blank correction:** Only subtract blank contribution when the validated
method specifies how; propagate the associated uncertainty.

**Recovery:** A failed matrix spike or blank invalidates the batch for
confirmatory inference until investigated and reanalyzed.

**Chain of custody:** Link each result to specimen, lot, extract, run,
method version and immutable raw-data checksum. Keep invalidated data for
audit, with explicit exclusion reason.

## 6. Statistical model and sample-size planning

Use the pilot to estimate between-lot, between-ball and within-ball
variance. For confirmatory comparisons, a mixed-effects model could be:

```text
log(migration + offset) ~ material + aging + medium + material:aging
                        + (1 | lot) + (1 | lot:ball)
```

Only use a log offset if prespecified and scientifically justified; where
non-detects dominate, use a censored-outcome model instead. Account for
repeated time points and within-specimen correlation. The actual model must
be selected from diagnostics and design constraints, not fixed blindly.

**Power:** Estimate detectable differences from pilot variance and the
independent unit count. Use simulation-based power under plausible lot
variance and censoring. Report effect sizes and confidence intervals; do
not choose a sample size based on the number of technical injections.

**Multiplicity:** Predefine a small primary analyte panel and primary
comparison. Exploratory non-target screens can use FDR control and should
not be presented as confirmatory findings.

**Blinding/randomization:** Randomize assay order and migration-cell
placement within method constraints. Blind analytical staff to candidate
labels where feasible; record batch order and drift.

## 7. Equivalence and non-inferiority

For each primary mechanical metric, choose a **physically justified**
equivalence margin from standards, benchmark variability, elite-athlete
requirements, and measurement repeatability. A generic 1% margin is not
automatically valid.

Use two one-sided tests (TOST) or an equivalent confidence-interval approach
with the correct hierarchical standard errors. For a difference `Δ` and
equivalence interval `[-δ, +δ]`, equivalence requires the confidence
interval for `Δ` to lie wholly inside the margin. For one-sided requirements
(e.g., pressure retention must not be worse by more than `δ`), specify a
non-inferiority hypothesis separately.

If **any** critical performance metric fails, the candidate does not pass
G6 even when migration decreases.

The current `EngineeringConstraint` class is a deterministic screening
check, **not** a statistical equivalence test. G6 remains open until measured
evidence and appropriate inference are supplied.

## 8. Mechanistic transport model and numerical V&V

The software implements two distinct idealizations:

1. **One-face perfect-sink slab** with an impermeable opposite face,
   constant diffusivity, uniform initial concentration and analytic
   eigenfunction solution. It estimates an idealized upper-bound release
   under its boundary assumptions, not absorbed dose.
2. **1D finite-volume slab** with a contact-dependent surface mass-transfer
   coefficient `k` and zero flux during no-contact intervals. It models
   intermittent transfer with an approximate Robin-like boundary. A
   finite external reservoir, re-partitioning, swelling, multilayer
   interfaces and skin uptake are not yet represented.

Units: cm, h, µg/cm³, cm²/h, cm/h, µg/cm². No implicit SI conversion.

**Verification:** zero-time release, bounded release, early-time analytic
limit, mass conservation, contact-off control, mesh refinement, and
parameter validation are unit-tested. Additional mesh/time refinement
against laboratory data is mandatory.

**Calibration:** Do not fit both initial concentration and diffusivity
from a sparse migration series. The current fitting routine requires a
separately measured initial concentration and at least four distinct
time points, reserving the last as a holdout. The returned grid-boundary
and profile-width flags are warnings, not confidence intervals. A model
fitted to synthetic test data is not experimentally calibrated.

**Validation:** Reserve an independent product lot or aging condition for
out-of-sample assessment. Compare predicted cumulative release against
measured values with uncertainty intervals. Revisit geometry, partition
coefficient, temperature dependence and non-Fickian transport if systematic
residuals remain.

**Sensitivity:** Vary thickness, D, initial content, k, temperature,
contact duration and surface area. The implemented deterministic parameter
envelope is **not** a statistical 95% confidence interval. Use a
probabilistic uncertainty model only after empirical parameter distributions
are established.

## 9. Independent replication and release rules

A research release requires:

1. Frozen protocol and code commit.
2. Raw-data checksums and sample/lot chain of custody.
3. QC-accepted assays and independent review.
4. Independent experimental units.
5. Reproducible analysis, with LOD/LOQ and uncertainty retained.
6. Transport model verification and external validation.
7. Independent laboratory replication of decision-relevant findings.
8. Correctly bounded conclusions: no product-wide or clinical claim from a
   narrow chemical-screening result.

`python scripts/audit_endocrine_evidence.py` audits registered evidence.
`--strict` intentionally fails while product gates are incomplete. A green
GitHub CI run demonstrates software quality checks, not that physical
evidence has been generated.

## 10. Resources and staged feasibility

The initial phase can use supplier records, a small benchmark sample,
ATR-FTIR access, high-speed-video contact analysis and a laboratory quote
for a tightly targeted assay. An independent accredited chemistry laboratory,
multiple production lots, OECD 428 uptake, and broad non-target screening
may be substantially more expensive than the existing software budget.

Do not claim that a comprehensive analytical program is feasible for
the current project budget until written laboratory quotes exist.

## 11. Human-subject boundary

No blood, urine, menstrual or patient data are needed for G0–G6. If human
contact experiments later involve recruited players, obtain an appropriate
ethics determination for that study even without biomonitoring. Clinical
biomonitoring or health outcomes would require a separately approved human
study with informed consent, privacy protections, exposure controls and
qualified clinical oversight.
