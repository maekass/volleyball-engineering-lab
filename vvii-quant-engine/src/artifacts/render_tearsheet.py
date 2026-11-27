"""One-page technical tear-sheet. Rendered only at a composite of 3.75 or higher."""

from __future__ import annotations

from pathlib import Path

from artifacts.formatting import text
from engines.target_scorer import TEARSHEET_THRESHOLD, DiligenceResult


class GateError(Exception):
    """The target is below the tear-sheet threshold."""

    def __init__(self, composite) -> None:
        self.composite = composite
        super().__init__(
            f"Tear-sheet gate is {TEARSHEET_THRESHOLD}; composite is {composite}."
        )


def render_tearsheet_html(result: DiligenceResult) -> str:
    if result.composite < TEARSHEET_THRESHOLD or not result.gate_pass:
        raise GateError(result.composite)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>VVII Tear-sheet {text(result.target_id)}</title>
<style>
  @page {{ size: letter; margin: 0.7in; }}
  body {{ font-family: "Liberation Sans", "Arial", sans-serif; color: #1c1917; font-size: 11pt; }}
  h1 {{ font-size: 18pt; margin-bottom: 0.05in; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border-bottom: 0.4pt solid #d6d3d1; text-align: left; padding: 4px 8px 4px 0; }}
  .status {{ font-size: 9pt; letter-spacing: 0.04em; text-transform: uppercase; }}
</style>
</head>
<body>
<p class="status">VVII technical diligence tear-sheet · {text(result.record_status)}</p>
<h1>{text(result.display_name)}</h1>
<p>Target {text(result.target_id)}. Source {text(result.source_url)}. Input hash {text(result.input_sha256)}.</p>
<table>
<tr><th>Pillar</th><th>Weight</th><th>Score</th></tr>
<tr><td>Technical ingestion</td><td>30%</td><td>{result.technical_ingestion}</td></tr>
<tr><td>Workflow and .dvw lock-in</td><td>25%</td><td>{result.workflow_lock_in}</td></tr>
<tr><td>Rule-cycle or clinical catalyst</td><td>25%</td><td>{result.catalyst}</td></tr>
<tr><td>M&amp;A / exit path</td><td>20%</td><td>{result.exit_path}</td></tr>
<tr><td>Composite</td><td>100%</td><td>{result.composite}</td></tr>
</table>
<p>Gate: composite at least {TEARSHEET_THRESHOLD}. This record clears that gate at {result.composite}. The score is a deterministic function of the evidence flags. It is not a recommendation to invest, and it is not an offer to sell securities.</p>
</body>
</html>
"""


def write_tearsheet_pdf(result: DiligenceResult, path: Path) -> None:
    from artifacts.render_pdf import write_pdf

    write_pdf(render_tearsheet_html(result), path)
