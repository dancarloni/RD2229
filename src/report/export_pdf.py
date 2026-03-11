"""Export PDF opzionale via WeasyPrint."""

from __future__ import annotations

from pathlib import Path


class PDFExporter:
    """Esporta HTML in PDF quando WeasyPrint e' disponibile."""

    def export(self, html_content: str, path: str | Path) -> Path:
        output_path = Path(path)
        try:
            from weasyprint import HTML
        except ImportError as exc:  # pragma: no cover - dipendenza opzionale
            raise RuntimeError(
                "WeasyPrint non disponibile. Installare con 'pip install weasyprint'."
            ) from exc

        HTML(string=html_content).write_pdf(str(output_path))
        return output_path
