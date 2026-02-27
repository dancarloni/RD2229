"""Report Export plugin – builds and exports a calculation report."""

from __future__ import annotations

from pathlib import Path

from src.plugins import ActionSpec, ParamSpec, PluginRegistry, PluginSpec


def _export(project: str, output: str) -> dict[str, object]:
    try:
        from src.core.pipeline import run_pipeline  # type: ignore[import]
        from src.project.repository import load_project  # type: ignore[import]
        from src.reporting.export import (  # type: ignore[import]
            export_report_html,
            export_report_md,
        )
        from src.reporting.report_builder import build_report  # type: ignore[import]

        Path(project)
        output_dir = Path(output)

        project_model = load_project(project)
        results = run_pipeline(project_model)
        artifact = build_report(project_model, results)

        output_dir.mkdir(parents=True, exist_ok=True)
        html_path = output_dir / "report.html"
        md_path = output_dir / "report.md"

        export_report_html(artifact, str(html_path))
        export_report_md(artifact, str(md_path))

        return {
            "ok": True,
            "html": str(html_path),
            "markdown": str(md_path),
        }
    except (ImportError, FileNotFoundError, RuntimeError) as exc:  # plugin errors must not crash the app
        return {"ok": False, "error": str(exc)}


def register(registry: PluginRegistry) -> None:
    spec = PluginSpec(
        id="report_export",
        title="Report Export",
        category="reporting",
        icon="📄",
        description="Exports a calculation report to a directory.",
        actions=[
            ActionSpec(
                id="export",
                label="Export Report",
                handler=_export,
                params=[
                    ParamSpec(
                        name="project",
                        label="Project file",
                        type="file",
                        required=True,
                        description="Path to the project JSON file.",
                    ),
                    ParamSpec(
                        name="output",
                        label="Output directory",
                        type="dir",
                        required=True,
                        description="Directory where the report will be written.",
                    ),
                ],
                description="Run pipeline, build report, and write to output dir.",
            )
        ],
    )
    registry.register(spec)
