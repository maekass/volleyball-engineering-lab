# Adobe MCP Integration — Volley Lab / BALL 001

This directory is the contributor starter kit for using Adobe tooling from AI
coding assistants via the Model Context Protocol (MCP). It turns Volley Lab
engineering artifacts — structural renders, mesh views, plots, and CAD
exports — into publication-quality figures, diagrams, and communication
graphics without hand-carrying files between tools.

**Scope boundary:** Adobe MCP is a *communication* toolchain for this
project. Nothing it produces is engineering evidence. See
[Evidence policy](#evidence-policy) below.

---

## Which "Adobe MCP"?

"Adobe MCP" is a fragmented label. As of mid-2026 the relevant options are:

| Option | What it is | Status | Used here |
| --- | --- | --- | --- |
| **Adobe for creativity** (`https://adobe-creativity.adobe.io/mcp`) | Adobe-hosted remote MCP server with 50+ tools across Firefly generation and Express-tier editing of Photoshop, Lightroom, Illustrator, InDesign, Premiere, and Adobe Stock ([Adobe Developer](https://developer.adobe.com/adobe-for-creativity/)) | Official, GA since April 2026 | ✅ Primary |
| **Illustrator (Beta) built-in MCP** (`http://localhost:18412/v1/mcp`) | Local MCP server inside the Illustrator Beta desktop app; ~40 tools for direct document manipulation ([Adobe Help](https://helpx.adobe.com/ie/illustrator/desktop/connect-with-other-apps-and-tools/connect-illustrator-to-ai-tools.html)) | Official, beta | Optional |
| **Adobe Express Developer MCP** (`@adobe/express-developer-mcp`) | Docs/TypeScript-definition server for building Express *add-ons* ([Adobe Developer](https://developer.adobe.com/express/add-ons/docs/guides/getting-started/local-development/mcp-server)) | Official, stable | ❌ Not relevant (we do not build Express add-ons) |
| Community servers (`mikechambers/adb-mcp`, `matrayu/adobe-mcp`, etc.) | UXP-plugin + proxy stacks that drive full desktop Photoshop/Premiere/InDesign | Unofficial, unsupported by Adobe | ❌ Avoided (unaudited plugin + proxy surface) |

**Why "Adobe for creativity" is the primary choice**

1. **Officially supported and hosted** — no local proxy, UXP plugin, or
   Node/Python sidecar for contributors to install and trust.
2. **Standard transport** — Streamable HTTP, supported by every major MCP
   client (Claude, Claude Code, Cursor, VS Code, Codex).
3. **OAuth, zero secrets in the repo** — the client opens a browser sign-in
   on first use; no API keys, tokens, or client secrets are committed. Guest
   mode works without an Adobe account (~40 free tools); signing in unlocks
   the full toolset, Creative Cloud storage, and higher limits.
4. **Right capability shape** — figure annotation, vector cleanup, layout,
   image editing, and asset generation are exactly the communication tasks
   this project needs; we do not need deep desktop-app scripting.

---

## Architecture

```
┌────────────────────────────── engineering side ─────────────────────────────┐
│                                                                             │
│  src/ball001/*  ──►  scripts/export_*.py / view_*.py / *_report.py          │
│                        │                                                    │
│                        ▼                                                    │
│                  exports/  (VTK/VTP, PNG renders, CAD, plots — untracked)   │
│                        │                                                    │
│                        ▼                                                    │
│      scripts/export_adobe_handoff.py  (src/ball001/adobe_handoff.py)       │
│                        │   copies files + writes manifest.json              │
│                        ▼   with evidence labels (provenance gate)           │
│              exports/adobe_handoff/  ◄── the only sanctioned handoff        │
│                                                                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │  files uploaded / referenced in chat
                                       ▼
┌────────────────────────────── design side ──────────────────────────────────┐
│                                                                             │
│  MCP client (Claude / Claude Code / Cursor / VS Code)                       │
│      │  Streamable HTTP + OAuth                                             │
│      ▼                                                                      │
│  https://adobe-creativity.adobe.io/mcp   (Adobe-hosted MCP server)          │
│      │  Firefly · Photoshop · Illustrator · InDesign · Express tools        │
│      ▼                                                                      │
│  Communication artifacts (figures, diagrams, one-pagers)                    │
│      — labeled COMMUNICATION, never SIMULATED / MEASURED —                  │
│                                                                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

Key properties:

- **One-way flow.** Engineering artifacts flow *into* design sessions
  through the manifest-gated handoff directory. Designed outputs never flow
  back into `exports/fea/`, `exports/visualization/`, or any evidence path.
- **Provenance travels with the pixels.** `manifest.json` records source
  path, artifact kind, evidence label, and a human description for every
  staged file, so any figure can be traced to the solver output or CAD
  export behind it.
- **No credentials at rest.** OAuth tokens live in the MCP client's own
  store, never in this repository.

---

## Setup

### Prerequisites

- An MCP-compatible client: Claude (web/Desktop), Claude Code, Cursor, or
  VS Code (agent mode).
- Optional but recommended: a free or paid Adobe account (guest mode works
  with reduced capability).
- No Node, Python packages, or plugins are required for the hosted server.

### Claude Code

The repo ships a project-scoped config in [`.mcp.json`](../../.mcp.json), so
inside the repo the server is available automatically. Approve it when
prompted, then authenticate:

```bash
claude          # start a session inside the repo
/mcp            # select adobe-creativity → Authenticate (browser OAuth)
claude mcp list # verify: adobe-creativity … ✓ connected
```

To register it user-wide instead:

```bash
claude mcp add --transport http --scope user \
  adobe-creativity https://adobe-creativity.adobe.io/mcp
```

### Cursor

The repo ships [`.cursor/mcp.json`](../../.cursor/mcp.json). Open the repo,
then **Settings → MCP** → enable `adobe-creativity` and complete the browser
OAuth prompt on first tool use.

### VS Code

The repo ships [`.vscode/mcp.json`](../../.vscode/mcp.json). Open the repo,
run **MCP: List Servers** (or click **Start** on the server in the MCP view),
and complete the OAuth flow.

### Claude web / Claude Desktop

Install the connector from the directory: search **Adobe for creativity**
under *Customize → Connectors*, click **Install**, and optionally sign in
with your Adobe ID ([setup guide](https://developer.adobe.com/adobe-for-creativity/getting-started/)).

### Verify the connection

In any connected client, ask:

> List the Adobe MCP tools you have available.

You should see Firefly generation plus Photoshop/Illustrator/Express-style
editing tools. Then try a dry run:

> Create a 1920×1080 dark-background title card that says "Volley Lab —
> BALL 001 Structural Baseline".

### Optional: local Illustrator (Beta) MCP

For precision vector work (seam-topology diagrams, panel flat patterns) you
can additionally connect the Illustrator Beta desktop app's built-in MCP
server: in Illustrator (Beta), open **MCP & Tools**, choose your client, and
follow the generated command — it points at `http://localhost:18412/v1/mcp`
with a per-machine bearer key ([Adobe Help](https://helpx.adobe.com/ie/illustrator/desktop/connect-with-other-apps-and-tools/connect-illustrator-to-ai-tools.html)).
That key is machine-local: **never commit it**. Register the server at user
scope (`--scope user`), not in this repo's checked-in configs.

---

## Usage

### 1. Produce engineering artifacts as usual

```bash
python scripts/export_structural_vtk.py
python scripts/render_structural_results.py
python scripts/view_panel_candidates.py
```

### 2. Stage a handoff with evidence labels

```bash
python scripts/export_adobe_handoff.py \
  --kind render \
  --label SIMULATED \
  --description "Radial displacement field, medium mesh, CalculiX baseline" \
  exports/visualization/ball001_structural_verification.png
```

This copies files into `exports/adobe_handoff/` (git-ignored) and writes
`manifest.json` with provenance. Run it once per kind/label group.

### 3. Run the design session

Open your MCP client, attach or reference the staged files, and use the
recipes in [`prompts/`](prompts/):

- [`prompts/structural-figure.md`](prompts/structural-figure.md) — annotate
  solver renders into publication figures.
- [`prompts/panel-flat-pattern.md`](prompts/panel-flat-pattern.md) — vector
  seam-topology and panel-layout diagrams.
- [`prompts/project-one-pager.md`](prompts/project-one-pager.md) — project
  brief / summary graphics.

Always paste the relevant `manifest.json` entries into the session so the
assistant knows each image's evidence label and must render the caption
accordingly.

### 4. File the outputs

Save designed outputs outside the evidence tree (e.g.
`exports/adobe_handoff/out/`, git-ignored) or attach them to documents,
decks, or posts. Do not place them in `exports/fea/` or
`exports/visualization/`.

---

## Evidence policy

Volley Lab's evidence standard (README §7) separates STANDARD, BENCHMARK,
LITERATURE, TARGET, SIMULATED, MEASURED, PENDING, and UNKNOWN. Adobe MCP
adds one hard rule at the design boundary:

1. Every artifact entering a design session carries its evidence label via
   the handoff manifest (`src/ball001/adobe_handoff.py` enforces the label
   vocabulary).
2. Every designed output is a **communication artifact**. It may *depict*
   SIMULATED or MEASURED data, but it is itself neither. Captions in
   designed figures must preserve the underlying label (e.g. "SIMULATED —
   CalculiX, not a physical measurement").
3. Generative fills, style transfers, and AI-composited imagery must never
   be presented as renders of actual BALL 001 geometry or results.

---

## Security notes

- The hosted server uses OAuth; tokens are held by your MCP client. Nothing
  in this repo stores or needs credentials.
- The checked-in configs point only at Adobe's official endpoint. Review any
  PR that changes `.mcp.json`, `.cursor/mcp.json`, or `.vscode/mcp.json` as
  carefully as dependency changes (MCP servers are a supply-chain surface).
- Community desktop-control servers are intentionally not configured here;
  if you experiment with them, do so at user scope on your own machine.
- Treat uploaded artifacts as leaving your machine: stage only files you are
  comfortable sending to Adobe's hosted service. Do not stage licensed
  third-party material (e.g. patent figures, purchased references).

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Server listed but no tools | Complete OAuth (`/mcp` in Claude Code; first tool call in Cursor/VS Code triggers it). |
| OAuth window never opens | Check corporate SSO/pop-up blockers; retry from the client's MCP settings. |
| Tools present but limited | You are in guest mode — sign in with an Adobe ID for the full toolset and higher limits. |
| `exports/adobe_handoff/` missing | It is generated on demand and git-ignored; run `scripts/export_adobe_handoff.py`. |
| Enterprise Claude cannot see the connector | An org admin must enable third-party connectors (Organization settings → Skills). |

## Contributor checklist

- [ ] Connected `adobe-creativity` in at least one MCP client and verified
      tools list.
- [ ] Staged artifacts only through `scripts/export_adobe_handoff.py`.
- [ ] Kept evidence labels in figure captions.
- [ ] No designed output committed into evidence paths.
- [ ] No tokens, bearer keys, or machine-local MCP endpoints committed.
