from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.results import ResultsModel
    from src.project.schema import ProjectModel


class CalculationService:
    def run(self, project: ProjectModel) -> ResultsModel:
        from src.core.pipeline import run_pipeline

        return run_pipeline(project)

    def export_results(self, results: ResultsModel, path: str) -> None:
        from src.core.results import export_results

        export_results(results, path)

    def export_report(
        self,
        project: ProjectModel,
        results: ResultsModel,
        path: str,
        fmt: str = "html",
    ) -> None:
        from src.reporting.export import export_report_html, export_report_md
        from src.reporting.report_builder import build_report

        artifact = build_report(project, results)
        if fmt == "md":
            export_report_md(artifact, path)
        else:
            export_report_html(artifact, path)
