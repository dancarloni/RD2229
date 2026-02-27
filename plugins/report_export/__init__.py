"""Report Export plugin – builds and exports a calculation report."""

from __future__ import annotations

from src.plugins import ActionSpec, ParamSpec, PluginRegistry, PluginSpec


def _export(project: str, output: str) -> dict[str, object]:
    try:
        from src.core.pipeline import run_pipeline  # type: ignore[import]
        from src.reporting.export import export_report  # type: ignore[import]
        from src.reporting.report_builder import build_report  # type: ignore[import]

        result = run_pipeline(project)
        artifact = build_report(result)
        export_report(artifact, output)
        return {"ok": True, "output": output}
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
