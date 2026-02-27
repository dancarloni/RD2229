"""Minimal services shim for `src.ui.modern.services` expected by tests."""

from __future__ import annotations

from typing import Any


class ProjectIOService:
    def new_project(self) -> object:
        from src.project.schema import ProjectModel

        return ProjectModel()

    def open_project(self, path: str) -> object:
        from src.project.repository import load_project

        return load_project(path)

    def save_project(self, project: Any, path: str) -> None:
        from src.project.repository import save_project

        save_project(project, path)


class CalculationService:
    def run(self, project: Any) -> Any:
        from src.core.pipeline import run_pipeline

        return run_pipeline(project)

    def export_results(self, results: Any, path: str) -> None:
        from src.core.results import export_results

        export_results(results, path)

    def export_report(self, project: Any, results: Any, path: str, fmt: str = "html") -> None:
        from src.reporting.export import export_report_html, export_report_md
        from src.reporting.report_builder import build_report

        artifact = build_report(project, results)
        if fmt == "md":
            export_report_md(artifact, path)
        else:
            export_report_html(artifact, path)


__all__ = ["ProjectIOService", "CalculationService"]
