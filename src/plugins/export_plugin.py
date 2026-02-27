"""Example plugin: export report."""

from __future__ import annotations

from pathlib import Path

from src.plugins import ActionSpec, PluginRegistry, PluginSpec
from src.plugins.base import BasePlugin


class ExportPlugin(BasePlugin):
    plugin_id = "export"
    name = "Export report"
    description = "Genera report markdown/html dal progetto"

    def execute(self, project_path: str, output_dir: str) -> str:
        from src.core.pipeline import run_pipeline
        from src.project.repository import load_project
        from src.reporting.export import export_report_html, export_report_md
        from src.reporting.report_builder import build_report

        project = load_project(project_path)
        results = run_pipeline(project)
        artifact = build_report(project, results)

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        md_path = out / "report.md"
        html_path = out / "report.html"

        export_report_md(artifact, str(md_path))
        export_report_html(artifact, str(html_path))

        return f"Report esportati: {md_path} | {html_path}"

    def to_spec(self) -> PluginSpec:
        return PluginSpec(
            id=self.plugin_id,
            title=self.name,
            category="reporting",
            icon="📄",
            description=self.description,
            actions=[
                ActionSpec(
                    id="export_report",
                    label="Esporta report",
                    handler=self.execute,
                    description="Esporta report.md e report.html.",
                    icon="📄",
                )
            ],
        )


def register(registry: PluginRegistry) -> None:
    registry.register(ExportPlugin().to_spec())
