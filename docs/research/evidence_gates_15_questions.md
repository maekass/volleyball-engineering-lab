# BALL 001 — Fifteen Dissertation-Committee Questions and Evidence Gates

**Version:** 1.0 (proposal-stage architecture)  
**Status:** Scientific plan and executable controls, not a completed experimental
study. No measured volleyball chemical concentrations or health effects have
been entered into the repository.

## Primary question

**Can the chemical composition, migration behavior, and mechanical
performance of elite indoor volleyball surface materials be jointly
characterized and optimized to minimize avoidable chemical exposure while
preserving competition-level performance?**

This is a materials/exposure-engineering question. Women's-athlete physiology
motivates the selection of relevant endpoints but cannot establish a causal
effect of ball chemistry.

## Separate evidence chains

**Track A: athlete physiology and performance.** REDs, menstrual symptoms,
iron status, pelvic-floor health, sleep, contraception and injury availability
are separate health domains. The evidence map is
[`womens_athlete_health_evidence_map.md`](womens_athlete_health_evidence_map.md).
No symptom is a surrogate for volleyball-material exposure.

**Track B: polymer/materials exposure.** The sequence is formulation/layer
identity → product-specific content → migration → transfer during volleyball
contact → dermal uptake → toxicological context → safer-by-design substitution
→ mechanical equivalence. Literature about other rubber articles supports
method selection, not volleyball exposure estimates.

### Evidence classes

| Class | Source | Permitted inference |
| --- | --- | --- |
| E1 Sports medicine | Peer-reviewed clinical/sport studies | Athlete-health relevance only |
| E2 Hazard toxicology | Chemical-specific hazard studies | Plausible endpoint, not product presence |
| E3 Regulation/standards | ECHA, OECD, applicable test standards | Method/requirements, not product-specific results |
| E4 Material analogues | Other rubber/polymer migration studies | Test design and hypotheses, never numerical substitution |
| E5 Volleyball material ID | Layer-specific supplier and analytical records | Identified material on the tested specimen |
| E6 Product chemistry | Validated assay with QC, LOD/LOQ | Target concentration for the tested specimen |
| E7 Exposure physics | Migration, contact, uptake and dose records | Bounded exposure for specified conditions |
| E8 Engineering intervention | Substitution DOE and mechanical tests | Change in specified chemistry and performance endpoints |
| E9 Independent replication | Second lab / independent reanalysis | Reproducibility within declared conditions |

E1–E4 support the proposal; E5–E9 require original experiments. An
uncompleted gate remains **INDETERMINATE**, never implicitly PASS.

## The 15 questions, required evidence and present disposition

### Q01 — Is the hypothesis falsifiable?

**Required:** Preregister H1 material presence, H2 migration, and H3
migration-reduction-with-equivalence as separate hypotheses; specify primary
chemical, matrix, effect size, endpoint and null hypothesis before testing.
**Artifact:** `preregistration_template.md`. **Current:** planned; hypotheses
are registered as PENDING, not confirmed.

### Q02 — Are athlete physiology and material exposure causally separated?

**Required:** Directed causal graph including REDs, iron, menstrual symptoms,
training load, background chemical sources, ball contact, absorbed dose and
outcomes. Record confounders and alternative pathways. Do not infer clinical
effects from chemical hazard literature.
**Artifact:** evidence map and causal model section below. **Current:** conceptual
separation documented; no causal effect estimated.

### Q03 — Can another researcher reproduce the literature search?

**Required:** database, exact query, search date, inclusion/exclusion,
deduplication, screening decisions, design type, evidence grading and citation
identifiers. Prefer two independent screeners and adjudication.
**Artifact:** `literature_review_protocol.md` and
`data/literature_screening_template.csv`. **Current:** protocol/template only;
not a completed systematic review.

### Q04 — What is each layer chemically and structurally?

**Required:** sample-linked FTIR/Raman/microscopy/DSC/TGA or other appropriate
material identification; document thickness, mass fraction, confidence,
supplier provenance and coating/adhesive interfaces.
**Gate:** G0. **Current:** no specimen-specific results.

### Q05 — Why is each target chemical on the analytical panel?

**Required:** polymer/formulation relevance, chemical CAS, plausible source,
hazard endpoint, analytical method and required quantification limit; screen
replacement additives as well. Distinguish endocrine hazards from PAH and
isocyanate co-hazards.
**Artifact:** chemical watchlist and target rationale. **Current:** provisional
target list; presence UNKNOWN.

### Q06 — Are sampling and inference independent?

**Required:** separate manufacturing lots, balls, layer coupons, extracts,
instrument injections and aging groups; justify lot/sample counts from pilot
variance and intended effect size. Three injections are not three balls.
**Artifact:** `experimental_design_and_statistics.md` and sample manifest.
**Current:** design only.

### Q07 — Can the assay distinguish detection from contamination?

**Required:** calibrated method, blanks, matrix spike, duplicates, internal
standards where appropriate, LOD, LOQ, raw chromatograms, recovery limits,
uncertainty and QC decision. Independent review of QC.
**Gate:** G1 (content) and G2 (migration). **Current:** QC code and empty
schemas; no accepted assay.

### Q08 — Is migration described by validated physics?

**Required:** specify geometry, diffusivity, partition coefficient, surface
boundary conditions, temperature, reservoir and aging; compare mechanistic
predictions against held-out measured migration, not only synthetic data.
**Artifact:** `src/ball001/diffusion_transport.py`.
**Current:** idealized analytic and finite-volume models; uncalibrated.

### Q09 — Does the contact experiment represent volleyball use?

**Required:** high-speed contact-time measurement, touch count, contact
area, pressure, moisture and ball condition across setters, passers, servers
and retrieval. Distinguish practice duration from cumulative touch duration.
**Gate:** G3. **Current:** protocol only.

### Q10 — How much migrated material crosses skin?

**Required:** separate polymer release, skin-surface transfer, dermal
absorption and systemic dose. Use compound- and matrix-relevant published
absorption or validated in-vitro skin testing if escalation is justified.
**Gate:** G4. **Current:** no uptake data.

### Q11 — Is any dose biologically meaningful?

**Required:** qualified chemical-specific toxicology review, route-appropriate
reference, relevant sensitive windows, aggregate/background exposure, mixture
and uncertainty discussion. No safety or causal claim from a screening ratio.
**Gate:** G5. **Current:** no dose characterization.

### Q12 — Does aging alter migration?

**Required:** new, flexed/abraded, cleaned, heat/humidity/UV-aged and
field-used specimens, with pre-specified aging doses and post-aging chemical
and mechanical assays.
**Artifact:** testing protocol and experimental design. **Current:** planned.

### Q13 — Does a substitution reduce migration without regrettable effects?

**Required:** DOE comparing polymer grade, plasticizer family, barrier
coating, cure and recycled feedstock; test replacement chemicals and
wear-induced cracking. Predefine primary migration contrast.
**Gate:** G6 after G2–G5 as appropriate. **Current:** no substitution data.

### Q14 — Is sport performance statistically equivalent?

**Required:** pressure retention, mass/circumference, compression, rebound,
hysteresis, friction wet/dry, impact/contact and durability. Pre-register
equivalence margins and perform equivalence analysis; a nonsignificant
difference is not evidence of equivalence.
**Artifact:** experimental design and existing BALL 001 FEA baseline.
**Current:** computational structural baseline only; no substitution
equivalence study.

### Q15 — Can an independent lab reconstruct every claim?

**Required:** raw data hashes, sample/lot/replicate lineage, method version,
QC, reviewed evidence record, source-linked claim, model version,
environment lock, analysis scripts, independent repeat and negative-result
retention.
**Artifact:** `research_integrity_architecture.md`, evidence/claim ledgers,
audit CLI and tests. **Current:** software audit implemented; no lab replication.

## Causal separation (DAG specification)

The following arrows are **hypotheses** where ball chemistry is involved:

```text
polymer formulation -> surface content -> migration -> skin transfer
                                          -> uptake -> systemic dose
background products/diet/dust ---------------------> systemic dose

training load -> low energy availability -> athlete physiology -> performance
iron status ----------------------------------------> performance
menstrual symptoms / sleep ------------------------> performance
injury history / conditioning ----------------------> performance

systemic dose - - [unestablished causal pathway] - -> endocrine endpoint
endocrine endpoint - - [unestablished pathway] - -> sport performance
```

No arrow from volleyball chemistry to clinical endocrine or performance
outcomes is presently established.

## Four validation systems

1. **Evidence validation:** hash-bound source artifacts, specimen/lot/method
   IDs, review state, numerical QC, and claim-to-evidence links.
2. **Experimental validation:** preregistration, method validation,
   independent specimens, blinding, QC, LOD/LOQ, and measured uncertainty.
3. **Computational validation:** dimensional checks, analytical benchmarks,
   conservation, mesh/time convergence, sensitivity, calibration, holdout
   validation and parameter identifiability.
4. **Claim validation:** product claims cannot use hazard literature as a
   substitute for G0–G6; human-health causation is blocked pending a separate
   ethically reviewed human study.

## Research-readiness levels

- **Level 1: proposal ready.** Falsifiable question, critical literature
  search plan, protocol, statistical design, code, explicit unknowns.
- **Level 2: engineering evidence.** Verified specimen chemistry, migration,
  contact model, uptake bounds and mechanical measurements.
- **Level 3: publication ready.** Independent replication, uncertainty,
  peer/specialist review, full raw-data and code reproducibility.

**Current level:** proposal-stage implementation in progress; neither
Level 2 nor Level 3 is claimed.
