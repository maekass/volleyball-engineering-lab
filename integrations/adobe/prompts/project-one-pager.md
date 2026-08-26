# Recipe: Project One-Pager / Summary Graphic

**Inputs:** A hero render (kind `render`), 1–2 plots (kind `plot`), and the
project framing from the top of the repository README.

**Goal:** A single-page summary graphic (A4 or 1080×1350) introducing
Volley Lab / BALL 001 to a non-specialist audience — recruiters, partners,
or the volleyball community.

## Prompt template

> Create a one-page summary graphic for Volley Lab / BALL 001, an
> independent volleyball engineering study. Attached assets and manifest:
>
> ```
> <paste the relevant manifest.json entries here>
> ```
>
> Layout:
> 1. Header: "Volley Lab / BALL 001" with the one-line framing:
>    "How much of a great volleyball is actually necessary?"
> 2. Hero: the attached structural render, uncropped, with a small
>    "SIMULATED" tag anchored to its corner.
> 3. Three-column strip: Regulation constraints (660 mm circumference,
>    270 g nominal mass) · Method (CAD → mesh → FEA → test) · Status
>    (CalculiX structural baseline; physical validation pending).
> 4. Footer: repository URL and "Simulation ≠ measurement — all physical
>    performance claims pending validation."
> 5. Restrained palette (one accent color), generous whitespace, sans-serif.

## Rules

- Status text must match the README's current "Status" line — update the
  prompt, not the truth.
- No fabricated imagery of a physical BALL 001 prototype: none exists yet.
