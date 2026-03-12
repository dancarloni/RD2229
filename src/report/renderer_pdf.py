"""Renderer PDF — genera report in formato PDF tramite HTML intermedio.

Strategia: genera HTML con HTMLReportRenderer, poi converte in PDF.
Supporta WeasyPrint (se disponibile), altrimenti fallback a HTML.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PDFReportRenderer:
    """Renderer PDF per report di verifica strutturale.

    Genera prima un report HTML completo, poi lo converte in PDF
    utilizzando WeasyPrint se disponibile.
    """

    def __init__(self) -> None:
        self._weasyprint_available: bool | None = None

    def _check_weasyprint(self) -> bool:
        if self._weasyprint_available is None:
            try:
                import weasyprint  # noqa: F401

                self._weasyprint_available = True
            except ImportError:
                self._weasyprint_available = False
        return self._weasyprint_available

    def render(self, data: dict[str, Any], output_path: str) -> str:
        """Genera un PDF in output_path.

        Args:
            data: dizionario con project_name, elements, results, ecc.
            output_path: percorso file PDF di output.

        Returns:
            Percorso del file generato (PDF o HTML fallback).
        """
        from .renderer_html import HTMLReportRenderer

        html_renderer = HTMLReportRenderer()
        html_content = html_renderer.render(data)

        if self._check_weasyprint():
            import weasyprint

            doc = weasyprint.HTML(string=html_content)
            doc.write_pdf(output_path)
            logger.info("Report PDF generato in '%s'.", output_path)
            return output_path

        # Fallback: salva come HTML
        fallback_path = output_path.replace(".pdf", ".html")
        if fallback_path == output_path:
            fallback_path = output_path + ".html"
        with open(fallback_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.warning(
            "WeasyPrint non disponibile. Report HTML salvato in '%s'. "
            "Installare weasyprint per generare PDF: pip install weasyprint",
            fallback_path,
        )
        return fallback_path

    def render_html_only(self, data: dict[str, Any]) -> str:
        """Genera solo il contenuto HTML (senza conversione PDF)."""
        from .renderer_html import HTMLReportRenderer

        return HTMLReportRenderer().render(data)
