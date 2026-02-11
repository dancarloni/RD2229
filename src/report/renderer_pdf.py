"""
renderer_pdf.py

Renderer PDF (STUB).

Questo modulo definisce l'interfaccia per esportare il report
in formato PDF. L'implementazione reale può essere delegata a:

- ReportLab (raccomandato)
- WeasyPrint (HTML → PDF)
- wkhtmltopdf (se disponibile)
- altre soluzioni basate su template HTML

Tuttavia:
- Questo file NON deve implementare nulla ora.
- Serve solo la struttura per future espansioni.

STUB S2:
- interfaccia render()
- docstring dettagliata
"""

from typing import Dict, Any


class PDFReportRenderer:
    """
    Interfaccia base per generare PDF.

    TODO Copilot:
    - Integrare un motore PDF
    - Riallineare stile ai template HTML/MD
    """

    def __init__(self) -> None:
        pass

    def render(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Genera un PDF in output_path.

        TODO:
        - Implementare tramite ReportLab o HTML→PDF
        """
        raise NotImplementedError("PDF rendering non implementato (stub).")



# ======================================================================
# FINE FILE renderer_pdf.py
# ======================================================================
