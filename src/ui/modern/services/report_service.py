from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .action_report import ActionReport


@dataclass
class ReportService:
    """Servizio leggero per esportazione/gestione report dalla GUI.

    Questo stub fornisce metodi utili alla GUI per esportare un artefatto
    report già costruito dal motore di calcolo o dalla pipeline.
    """

    def export_artifact(
        self, artifact: Any, stem: str, output_dir: str | None = None
    ) -> ActionReport:
        """Esporta `artifact` come markdown e HTML in `output_dir`.

        `artifact` deve essere un oggetto compatibile con le funzioni
        `src.reporting.export.export_report_md` e `export_report_html`.
        """
        from src.reporting.export import export_report_html, export_report_md

        target_dir = Path(output_dir) if output_dir else Path(".")
        target_dir.mkdir(parents=True, exist_ok=True)
        md_path = target_dir / f"{stem}_report.md"
        html_path = target_dir / f"{stem}_report.html"

        export_report_md(artifact, str(md_path))
        export_report_html(artifact, str(html_path))

        return ActionReport(
            name="export_report",
            ok=True,
            summary="Report esportato",
            details={"report_md": str(md_path), "report_html": str(html_path)},
        )
