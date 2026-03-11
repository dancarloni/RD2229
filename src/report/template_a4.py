"""Template A4 per la relazione professionale di calcolo.

Fornisce layout HTML + CSS con intestazione e pie pagina.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape


@dataclass(slots=True)
class TemplateA4:
    """Renderizza pagine HTML ottimizzate per stampa A4."""

    margin_mm: int = 25
    font_family: str = "Times New Roman, Times, serif"
    font_size_pt: int = 11
    line_height: float = 1.4

    def css(self) -> str:
        """Restituisce il foglio di stile base per layout A4."""
        return f"""
@page {{
  size: A4;
  margin: {self.margin_mm}mm;
}}

@media print {{
  .a4-page {{
    break-after: page;
  }}
  .a4-page:last-child {{
    break-after: auto;
  }}
}}

body {{
  margin: 0;
  padding: 0;
  color: #1f1f1f;
  background: #f4f4f4;
  font-family: {self.font_family};
  font-size: {self.font_size_pt}pt;
  line-height: {self.line_height};
}}

.report-wrapper {{
  margin: 0 auto;
  padding: 10mm 0;
}}

.a4-page {{
  width: 210mm;
  min-height: 297mm;
  margin: 0 auto 10mm auto;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  box-sizing: border-box;
  padding: {self.margin_mm}mm;
  position: relative;
}}

.rd2229-header {{
  border-bottom: 1px solid #b8b8b8;
  padding-bottom: 4mm;
  margin-bottom: 7mm;
}}

.rd2229-header-title {{
  margin: 0;
  font-size: 14pt;
  font-weight: 700;
}}

.rd2229-header-meta {{
  margin-top: 3mm;
  font-size: 10pt;
  color: #444;
  display: flex;
  gap: 4mm;
  flex-wrap: wrap;
}}

.rd2229-content h1,
.rd2229-content h2,
.rd2229-content h3 {{
  margin-top: 0;
}}

.rd2229-content table {{
  width: 100%;
  border-collapse: collapse;
}}

.rd2229-content th,
.rd2229-content td {{
  border: 1px solid #c9c9c9;
  padding: 2mm;
}}

.rd2229-content thead th {{
  background: #efefef;
  font-weight: 700;
}}

.formula-box {{
  border: 1px solid #d4d4d4;
  background: #f6f6f6;
  padding: 2.5mm;
  margin: 2mm 0;
  font-family: "Consolas", "Courier New", monospace;
}}

.image-placeholder {{
  border: 1px dashed #a0a0a0;
  padding: 4mm;
  text-align: center;
  color: #666;
  margin: 3mm 0;
}}

.rd2229-footer {{
  position: absolute;
  left: {self.margin_mm}mm;
  right: {self.margin_mm}mm;
  bottom: {max(6, self.margin_mm - 6)}mm;
  border-top: 1px solid #c9c9c9;
  padding-top: 2mm;
  font-size: 9pt;
  color: #555;
  display: flex;
  justify-content: space-between;
}}

.rd2229-footer .page-number::after {{
  content: counter(page);
}}

.rd2229-footer .page-total::after {{
  content: counter(pages);
}}
""".strip()

    def render_header(
        self,
        *,
        progetto: str,
        professionista: str = "",
        committente: str = "",
        numero_pratica: str = "",
        data_stampa: str | None = None,
    ) -> str:
        """Renderizza intestazione con metadati progetto."""
        printed_on = data_stampa or datetime.now().strftime("%Y-%m-%d")
        return (
            '<header class="rd2229-header">'
            f'<h1 class="rd2229-header-title">{escape(progetto)}</h1>'
            '<div class="rd2229-header-meta">'
            f"<span><strong>Committente:</strong> {escape(committente)}</span>"
            f"<span><strong>Professionista:</strong> {escape(professionista)}</span>"
            f"<span><strong>Pratica:</strong> {escape(numero_pratica)}</span>"
            f"<span><strong>Data:</strong> {escape(printed_on)}</span>"
            "</div>"
            "</header>"
        )

    def render_footer(self, *, data_stampa: str | None = None) -> str:
        """Renderizza pie' pagina con data e contatore pagina."""
        printed_on = data_stampa or datetime.now().strftime("%Y-%m-%d")
        return (
            '<footer class="rd2229-footer">'
            f"<span>Stampato: {escape(printed_on)}</span>"
            '<span>Pagina <span class="page-number"></span> / '
            '<span class="page-total"></span></span>'
            "</footer>"
        )

    def render_page(
        self,
        *,
        content_html: str,
        header_html: str,
        footer_html: str,
        page_id: str | None = None,
    ) -> str:
        """Renderizza una singola pagina A4 con header, contenuto e footer."""
        page_attr = f' id="{escape(page_id)}"' if page_id else ""
        return (
            f'<section class="a4-page"{page_attr}>'
            f"{header_html}"
            f'<main class="rd2229-content">{content_html}</main>'
            f"{footer_html}"
            "</section>"
        )

    def render_document(self, *, title: str, pages_html: list[str]) -> str:
        """Renderizza il documento HTML completo contenente tutte le pagine."""
        body = "\n".join(pages_html)
        return (
            "<!DOCTYPE html>"
            '<html lang="it">'
            "<head>"
            '  <meta charset="utf-8">'
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            f"  <title>{escape(title)}</title>"
            f"  <style>{self.css()}</style>"
            "</head>"
            "<body>"
            f'<div class="report-wrapper">{body}</div>'
            "</body>"
            "</html>"
        )


A4Template = TemplateA4
