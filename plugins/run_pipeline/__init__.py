"""Run Pipeline plugin – triggers the calculation pipeline."""

from __future__ import annotations

from src.plugins import ActionSpec, ParamSpec, PluginRegistry, PluginSpec


def _run(project: str) -> dict[str, object]:
    try:
        from src.core.pipeline import run_pipeline  # type: ignore[import]

        result = run_pipeline(project)
        return {"ok": result.ok, "elements": len(result.elements)}
    except (ImportError, FileNotFoundError, RuntimeError) as exc:  # plugin errors must not crash the app
        return {"ok": False, "error": str(exc)}


def register(registry: PluginRegistry) -> None:
    spec = PluginSpec(
        id="run_pipeline",
        title="Run Pipeline",
        category="calculation",
        icon="⚙️",
        description="Runs the full verification pipeline on a project file.",
        actions=[
            ActionSpec(
                id="run",
                label="Run",
                handler=_run,
                params=[
                    ParamSpec(
                        name="project",
                        label="Project file",
                        type="file",
                        required=True,
                        description="Path to the project JSON file.",
                    )
                ],
                description="Execute the pipeline and return results.",
            )
        ],
    )
    registry.register(spec)
