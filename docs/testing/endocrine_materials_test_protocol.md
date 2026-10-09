# BALL 001 Endocrine-Active Materials Testing Protocol

**Protocol type:** materials characterization and exposure-screening protocol  
**Human subjects:** none in Phases 0–6  
**Primary question:** Do volleyball materials release measurable quantities of
targeted endocrine-active or reproductive-hazard chemicals under realistic
hand-contact conditions, and can materials engineering reduce migration
without degrading ball performance?

## 1. Scope and non-claims

This protocol is not a medical diagnostic protocol and does not assume that a
benchmark volleyball contains any target chemical. It intentionally separates
**hazard identification**, **product presence**, **migration**, **dermal
uptake**, and **risk characterization**.

No statement that a product is “endocrine disrupting,” “unsafe,” or “safer”
may be made solely from a watchlist or supplier material name.

## 2. Study arms

Use a tiered design so expensive chemistry is performed only after material
identity is known.

### Arm A — benchmark balls

At minimum, include two elite indoor competition models from separate
manufacturers. If resources allow, use three production lots per model and
three balls per lot. Record SKU, lot/date code, country of purchase, purchase
date, storage history, inflation history, and whether the sample is new or
field-aged.

### Arm B — BALL 001 candidate coupons

Prepare coupons for each candidate outer-skin, coating, adhesive,
reinforcement, and bladder formulation. Assign immutable material-batch IDs.

### Arm C — aged/worn materials

Repeat selected assays after controlled abrasion, flexure/impact cycling,
sweat exposure, cleaning, elevated temperature/humidity, and UV aging. The
objective is to determine whether aging changes migration or exposes buried
layers.

## 3. Evidence gates

| Gate | Required evidence | Decision rule |
| --- | --- | --- |
| G0 Material identity | Supplier documentation + analytical material ID where needed | Do not target chemistry solely from a marketing name |
| G1 Total content | Validated quantitative assay with blanks, calibration and recovery | Presence above LOQ triggers migration evaluation; non-detect is reported with LOQ |
| G2 Sweat migration | Measured release under skin-relevant conditions | Measurable migration triggers realistic-transfer modeling |
| G3 Realistic transfer | Volleyball-specific contact time, area, moisture and pressure | Replace practice duration with cumulative contact duration |
| G4 Dermal uptake | Valid literature analogue or OECD 428-style study | Do not infer absorbed dose from external load without an uptake factor |
| G5 Dose context | Chemical-specific toxicological reference and uncertainty analysis | Health-risk language prohibited before this gate |
| G6 Engineering equivalence | Mechanical, durability and user-performance criteria | A chemistry change is not accepted if it breaks required sport performance |

## 4. Phase 0 — documentation and supplier screen

For every material or commercial benchmark, collect:

- technical data sheet and SDS where available;
- polymer family and grade;
- plasticizer/additive disclosure where available;
- adhesive/coating system;
- pigment/ink system;
- recycled-content source and contamination-control documentation;
- REACH SVHC and Annex XVII statements where relevant;
- California Proposition 65 disclosure if marketed in California;
- supplier change-control policy.

Create an `UNKNOWN` field rather than inferring missing chemistry.

## 5. Phase 1 — layer map and material identification

### 5.1 Non-destructive / minimally destructive methods

1. Photograph and weigh intact ball.
2. Record circumference, inflation pressure, and surface condition.
3. Map panel and seam construction.
4. Use ATR-FTIR on accessible surface and dissected layers.
5. Use Raman spectroscopy where pigments/fillers obscure FTIR.
6. Use optical microscopy or micro-CT for layer thickness and interfaces.
7. Use DSC/TGA selectively to distinguish polymer families, filler fraction,
   and thermal transitions.
8. Use XRF as a screening method for elemental constituents; XRF is not a
   substitute for organic-chemical analysis.

### 5.2 Output

For every physical layer, produce:

`sample_id -> layer_id -> polymer_family -> thickness -> mass_fraction ->
analytical_confidence -> evidence_class`

## 6. Phase 2 — targeted total-content chemistry

Use accredited or validated laboratory methods. Target selection is based on
Phase 1 material identity and the project watchlist.

### Primary endocrine/reproductive screen

**Ortho-phthalates:** DEHP, DBP, BBP, DIBP, and a broader plasticizer panel
where justified. Use GC-MS or GC-MS/MS after validated solvent extraction.
CPSC-CH-C1001-09.4 can inform phthalate analytical practice even when the ball
itself is not a children’s product.

**Bisphenols:** BPA, BPS, BPF where resin or coating chemistry justifies
testing. Use LC-MS/MS with isotope-labelled internal standards where feasible.

**Alkylphenols:** Include 4-tert-octylphenol if rubber/coating chemistry or
supplier information makes it plausible.

### Co-hazard screen

**PAHs:** For rubber/plastic components with repeated skin contact, quantify
the EU REACH priority PAHs by GC-MS. PAHs are included because materials-health
engineering should not ignore a non-endocrine hazard arising from the same
material decision.

**Residual isocyanates:** If polyurethane chemistry is confirmed, evaluate
residual MDI/TDI only with a validated method appropriate to free-isocyanate
migration. This is principally a sensitization/chemical-safety question, not
an endocrine endpoint.

### Exploratory only

PFAS, organotins, antioxidants, benzothiazoles, or other targets should be
added only when formulation information, non-target screening, or literature
gives a defensible reason. Do not create an unlimited target list merely
because a compound has been reported somewhere in plastics.

## 7. Phase 3 — sweat-mediated migration

### 7.1 Principle

Total content is not exposure. Measure chemical release from the article under
simulated skin contact.

Use EPA consumer-product migration guidance as a framework for selecting
article size, surrogate sweat volume, pressure, contact duration, and
temperature. ISO 105-E04 perspiration chemistry may be used as a standardized
starting medium, with any modification documented.

### 7.2 Conditions

For each material/sample:

- acidic and near-neutral synthetic sweat where analytically appropriate;
- 32–37 °C contact temperature;
- dry-control extraction;
- representative contact pressure;
- at least three migration durations spanning short contact to conservative
  extended contact;
- new and aged/worn surface conditions;
- triplicate samples minimum per condition;
- procedural blank, solvent blank, matrix spike and duplicate;
- surface-area-normalized reporting in `µg/cm²` and, when time-resolved,
  `µg/cm²/h`.

The exact durations must be justified from observed volleyball contact rather
than copied from unrelated consumer products.

## 8. Phase 4 — volleyball contact characterization

Instrument real use before estimating exposure.

### 8.1 Tasks

Characterize at least:

- setting drills;
- serve-receive/pass drills;
- serving;
- ball retrieval/carrying;
- warm-up handling;
- match play.

### 8.2 Variables

Measure or estimate:

- number of ball contacts per session;
- contact duration per touch from high-speed video where feasible;
- cumulative hand-ball contact time;
- effective contact area;
- palm/finger distribution;
- dry versus sweaty-hand condition;
- ball surface temperature;
- contact pressure proxy or force where instrumented data are available;
- session frequency per week.

Do **not** substitute total practice duration for dermal contact duration.

## 9. Phase 5 — dermal uptake escalation

Only proceed if migration is measurable and potentially decision-relevant.

Preferred hierarchy:

1. Chemical-specific, matrix-relevant published dermal absorption data.
2. Validated in-vitro human-skin testing consistent with OECD TG 428.
3. Conservative bounding assumption clearly labeled as such.

The model must preserve separate values for:

- mass released from article;
- mass transferred to skin/surface film;
- mass crossing the skin;
- systemic dose estimate.

Never equate these quantities.

## 10. Phase 6 — risk-context calculation

For each target with sufficient evidence:

1. Calculate external daily dermal load from measured migration and observed
   contact.
2. Apply a defensible dermal-absorption fraction only if supported.
3. Normalize by body mass only when the comparison reference uses that unit.
4. Identify the authoritative toxicological reference point and its
   route/species assumptions.
5. Calculate a margin or screening ratio with uncertainty bounds.
6. Report source-attribution uncertainty and aggregate-exposure limitations.

A health conclusion should be reviewed by a qualified toxicologist or exposure
scientist.

## 11. Phase 7 — safer-by-design material substitution

A candidate material change enters mechanical verification only after its
chemical target is clear.

### Material design levers

- remove intentionally added high-concern plasticizer;
- switch to a polymeric or lower-migration plasticizer where justified;
- reduce extractable monomer/oligomer content;
- change coating/binder chemistry;
- add a durable diffusion barrier;
- reduce additive loading;
- improve cure conversion;
- specify low-extractables pigments and inks;
- segregate recycled feedstocks by chemistry and supplier;
- introduce supplier restricted-substance and change-control requirements.

### Coupled BALL 001 acceptance tests

Every lower-migration candidate must be re-tested for:

- mass and circumference;
- pressure retention;
- compression force-displacement curve;
- hysteresis / energy loss;
- rebound or impact response;
- dry and wet friction;
- abrasion resistance;
- seam/coating integrity;
- aging drift;
- player-contact feel when human testing is later approved.

## 12. Statistical and analytical quality plan

- Pre-register primary chemical targets before opening analytical results.
- Use lot as a random effect when multiple production lots are available.
- Report raw values, LOD and LOQ; never convert non-detects to zero without a
  stated rule.
- Use calibration checks and isotope-labelled/internal standards where
  available.
- Require spike-recovery criteria defined by the analytical laboratory.
- Retain field blanks, trip blanks where relevant, procedural blanks,
  duplicates and matrix spikes.
- Use false-discovery control only when exploratory non-target panels become
  large; targeted confirmatory analytes should be reported individually.
- Treat this as an exposure/materials study, not a clinical outcomes trial; do
  not power it around endocrine health outcomes.

## 13. Minimal viable study

If budget is constrained, the first high-information experiment is:

1. One new ball each from two elite benchmark models plus one BALL 001 surface
   coupon.
2. ATR-FTIR material identification.
3. Targeted phthalate + bisphenol + PAH screen of outer-contact layer.
4. Synthetic-sweat migration at one realistic and one conservative condition.
5. High-speed-video estimate of cumulative hand-contact time during a setter
   drill.
6. Exposure estimate using measured migration only.
7. Repeat migration after abrasion aging.

This study can produce a credible null result or identify a specific design
variable without recruiting a single human subject for biomonitoring.

## 14. Stop conditions

Stop and escalate rather than interpret if:

- sample identity or lot provenance is missing;
- blank contamination approaches sample concentration;
- spike recovery fails laboratory acceptance criteria;
- the target is below LOQ but reported as a precise concentration;
- a migration rate is borrowed from an unrelated material and presented as
  product-measured;
- a toxicological reference point is route-incompatible;
- a material substitution changes ball mechanics outside the allowed
  performance envelope;
- an endocrine-health claim is being inferred from a hazard list alone.

## 15. Deliverables

- layer/material map;
- targeted chemistry table with LOD/LOQ;
- sweat-migration dataset;
- realistic contact-exposure scenario;
- evidence-gate report;
- mechanical-equivalence report for substitutions;
- supplier restricted-substance specification;
- update to BALL 001 evidence taxonomy: `LITERATURE`, `BENCHMARK`,
  `MEASURED`, `SIMULATED`, `PENDING`, `UNKNOWN`.

The final engineering question is not “is the ball chemical-free?” It is:
**can every decision-relevant exposure pathway be bounded with evidence, and
can the design reduce avoidable chemical migration without sacrificing the
performance athletes trust?**
