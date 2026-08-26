# Recipe: Seam Topology / Panel Layout → Vector Diagram

**Inputs:** Topology or panel-candidate views (kind `mesh_view` or
`cad_export`, typically label `TARGET` or `SIMULATED`), plus geometry
numbers from `scripts/topology_report.py` or
`scripts/panel_candidate_report.py`.

**Goal:** A crisp vector diagram comparing seam topologies (one-, two-,
three-great-circle) or panel candidates, for documentation and discussion.

## Prompt template

> I'm designing comparison diagrams for volleyball seam topologies.
> Reference images and manifest entries attached:
>
> ```
> <paste the relevant manifest.json entries here>
> ```
>
> Using the Adobe vector tools:
> 1. Draw three spheres in a row, each showing one seam topology:
>    one, two, and three orthogonal great circles.
> 2. Use a single accent color for seam curves over a neutral sphere fill;
>    consistent stroke weight; no gradients or 3D effects.
> 3. Label each variant beneath with its seam-length total:
>    <paste totals from topology_report.py>.
> 4. Footer caption, exactly: "TARGET / SIMULATED geometry — schematic,
>    not a manufactured panel layout."
> 5. Export as SVG and a 2x PNG.

## Rules

- Diagrams are schematics; never present them as manufacturable flat
  patterns unless a real unwrap has been computed and staged.
- If using the local Illustrator (Beta) MCP for finer control, keep its
  machine-local bearer key out of the repo (user-scope config only).
