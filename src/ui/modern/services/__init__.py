"""Services – adapter verso core e repository (no GUI).

Separazione rigorosa: nessuna dipendenza da Qt/PySide6 in questo modulo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.project.schema import ProjectModel


class ProjectIOService:
    """Gestisce new/open/save/save-as del ProjectModel JSON."""

    def new_project(self) -> ProjectModel:
        """Crea e restituisce un ProjectModel vuoto."""
        from src.project.schema import ProjectModel

        return ProjectModel()

    def open_project(self, path: str) -> ProjectModel:
        """Carica un ProjectModel da file JSON con migrazione automatica.

        Args:
            path: Percorso del file .json del progetto.

        Returns:
            :class:`src.project.schema.ProjectModel` caricato e migrato.

        Raises:
            FileNotFoundError: Se il file non esiste.
            ValueError: Se il file non è un JSON valido.
        """
        from src.project.repository import load_project

        return load_project(path)

    def save_project(self, project: Any, path: str) -> None:
        """Serializza un ProjectModel su file JSON (scrittura atomica).

        Args:
            project: :class:`src.project.schema.ProjectModel` da salvare.
            path: Percorso destinazione.
        """
        from src.project.repository import save_project

        save_project(project, path)


class CalculationService:
    """Wrapper su run_pipeline per eseguire il calcolo da GUI."""

    def run(self, project: Any) -> Any:
        """Esegue la pipeline di calcolo sul progetto.

        Args:
            project: :class:`src.project.schema.ProjectModel`.

        Returns:
            :class:`src.core.results.ResultsModel`.

        Non solleva eccezioni per input incompleto:
        gli errori sono nei ``warnings`` del risultato.
        """
        from src.core.pipeline import run_pipeline

        return run_pipeline(project)

    def export_results(self, results: Any, path: str) -> None:
        """Esporta i risultati in JSON.

        Args:
            results: :class:`src.core.results.ResultsModel`.
            path: Percorso destinazione.
        """
        from src.core.results import export_results

        export_results(results, path)

    def export_report(self, project: Any, results: Any, path: str, fmt: str = "html") -> None:
        """Esporta il report in HTML o Markdown.

        Args:
            project: :class:`src.project.schema.ProjectModel`.
            results: :class:`src.core.results.ResultsModel`.
            path: Percorso destinazione.
            fmt: ``"html"`` o ``"md"`` (default: ``"html"``).
        """
        from src.reporting.export import export_report_html, export_report_md
        from src.reporting.report_builder import build_report

        artifact = build_report(project, results)
        if fmt == "md":
            export_report_md(artifact, path)
        else:
            export_report_html(artifact, path)
