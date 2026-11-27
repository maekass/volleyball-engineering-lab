"""HTML to PDF. WeasyPrint is imported only when a file is written."""

from __future__ import annotations

from pathlib import Path


class PdfBackendError(RuntimeError):
    """The PDF library or its system libraries are not available."""


def write_pdf(html: str, path: Path) -> None:
    try:
        from weasyprint import HTML
    except Exception as exc:  # ImportError or missing cairo/pango
        raise PdfBackendError(
            "WeasyPrint could not be imported. Install weasyprint and the "
            "Pango/Cairo system libraries to write a PDF."
        ) from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(path)
