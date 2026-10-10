# Reproducible Literature Review Protocol — Volleyball Materials and Women's Health

**Status:** Search strategy and extraction template only. This document is
not a completed systematic review, and no PRISMA counts are claimed.

## Review questions

**A — Athlete physiology:** Which physiological and clinical factors are
associated with health, training availability and measured/perceived
performance in female volleyball athletes?

**B — Materials exposure:** What is known about endocrine/reproductive
hazards of chemicals relevant to ball polymers, coatings, adhesives and
rubber; and what product-specific evidence exists for migration and dermal
exposure during sports-equipment handling?

**C — Engineering intervention:** Which material substitutions, barriers,
surface treatments and aging protocols reduce migration while preserving
mechanical/tribological properties?

These reviews must not be pooled into a single causal claim.

## Databases and source hierarchy

Search PubMed/MEDLINE, OpenAlex and Crossref for bibliographic discovery.
Use Web of Science or Scopus where institutional access is available. For
standards/regulation search official OECD, ECHA, FIVB and relevant ISO/CPSC
sources. Record which sources were accessible and the exact search date.

Prefer primary experimental studies, systematic reviews and authoritative
consensus statements. Mark preprints, abstracts without full text,
manufacturer marketing and regulatory notices distinctly.

## Search strings to execute and log verbatim

PubMed syntax (adapt per database and preserve the adapted query):

**Athlete track**

```text
(volleyball[Title/Abstract]) AND
(female[Title/Abstract] OR women[Title/Abstract]) AND
(menstrual OR "relative energy deficiency" OR iron OR "pelvic floor"
 OR "performance" OR "hormonal contraception")
```

**Materials track**

```text
(volleyball OR "sports ball" OR "sports equipment" OR polyurethane
 OR elastomer OR rubber) AND
(phthalate OR bisphenol OR alkylphenol OR "endocrine disrupt*"
 OR "chemical migration") AND
(sweat OR dermal OR skin OR contact OR exposure OR leaching)
```

**Transport/engineering track**

```text
(polymer OR polyurethane OR elastomer) AND
("Fickian diffusion" OR "mass transfer" OR "migration testing"
 OR "synthetic sweat" OR "diffusion barrier") AND
(aging OR abrasion OR contact OR coating OR plasticizer)
```

Also run exact-title and citation-chaining searches for foundational papers.
Store each query's database, exact string, date, returned count and export
file checksum. Search strings are starting points; amendments are versioned.

## Eligibility and exclusion

Include studies with explicit material/chemical identity and analytical
methods for the materials track; include female-athlete or volleyball
performance studies with clear population and outcomes for the athlete track.
Distinguish in-vivo human exposure, in-vitro skin, product migration,
animal toxicology, epidemiology, and numerical modeling.

Exclude records without relevant endpoints, duplicate reports of the same
dataset (retain canonical report), and untraceable marketing claims.
Retain an exclusion log. Do not exclude null results because they are null.

## Screening and quality appraisal

1. Deduplicate by DOI/PMID/title and document the rule.
2. Two independent reviewers screen title/abstract where feasible.
3. Resolve disagreements with a documented third review/adjudication.
4. Record full-text exclusions with reasons.
5. Extract study design, material, population, sample size, assay, dose
   route, uncertainty, measured endpoint and limitations.
6. Evaluate bias appropriate to design; distinguish hazard from exposure.
7. Rate directness: volleyball-specific / other sports article / general
   polymer / general human exposure.
8. Report study counts only after executing the search and preserving logs.

Use `data/literature_screening_template.csv`. Link each accepted study to
an explicit claim ID. If only one reviewer is available, disclose the
limitation rather than claiming dual screening.

## Current interpretation

The existing research paper and evidence map are **narrative, proposal-stage
reviews**. They should not be labeled PRISMA-compliant or exhaustive until
the procedure above is executed and its search log and screening counts are
deposited.
