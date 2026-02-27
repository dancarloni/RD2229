"""Example plugin: run calculation pipeline."""

from __future__ import annotations

from src.plugins import ActionSpec, PluginRegistry, PluginSpec
from src.plugins.base import BasePlugin


class RunPlugin(BasePlugin):
    plugin_id = "run"
    name = "Esecuzione pipeline"
    description = "Esegue la pipeline di verifiche sul progetto"

    def execute(self, project_path: str) -> str:
        from src.core.pipeline import run_pipeline
        from src.project.repository import load_project

        project = load_project(project_path)
        results = run_pipeline(project)
        return (
            f"Pipeline completata: ok={results.ok}, "
            f"elementi={len(results.elements)}, avvisi={len(results.warnings)}"
        )

    def to_spec(self) -> PluginSpec:
        return PluginSpec(
            id=self.plugin_id,
            title=self.name,
            category="pipeline",
            icon="▶️",
            description=self.description,
            actions=[
                ActionSpec(
                    id="run_pipeline",
                    label="Esegui pipeline",
                    handler=self.execute,
                    description="Esegue run_pipeline(ProjectModel).",
                    icon="▶️",
                )
            ],
        )


def register(registry: PluginRegistry) -> None:
    registry.register(RunPlugin().to_spec())
