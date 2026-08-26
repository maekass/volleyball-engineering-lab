# Recipe: Structural Results → Publication Figure

**Inputs:** PNG renders staged via `scripts/export_adobe_handoff.py`
(kind `render`, label `SIMULATED`), plus their `manifest.json` entries.

**Goal:** A clean, annotated figure suitable for the README, a technical
post, or a slide — with the evidence label preserved in the caption.

## Prompt template

> I'm attaching structural renders from a CalculiX shell verification of
> BALL 001, an indoor volleyball concept (660 mm nominal circumference).
> Manifest entries:
>
> ```
> <paste the relevant manifest.json entries here>
> ```
>
> Using the Adobe tools:
> 1. Compose the renders side by side on a neutral light background,
>    1600×900, with consistent margins.
> 2. Add callout labels for peak radial displacement and mean tangential
>    stress regions (I'll give exact values below).
> 3. Add a title: "BALL 001 — Structural Verification (CalculiX baseline)".
> 4. Add a caption bar at the bottom that reads exactly:
>    "SIMULATED — computational output, not a physical measurement."
> 5. Keep all text in a single sans-serif family; no decorative effects.
>
> Values: <paste values from the relevant *_report.py output>

## Rules

- The caption's evidence label is not optional.
- Do not let generative tools redraw, "enhance", or inpaint the render
  content itself — layout, annotation, and typography only.
