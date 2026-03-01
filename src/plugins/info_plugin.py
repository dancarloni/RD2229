"""Example plugin: project info."""

from __future__ import annotations

from src.plugins import ActionSpec, ParamSpec, PluginRegistry, PluginSpec
from src.plugins.base import BasePlugin


class InfoPlugin(BasePlugin):
    plugin_id = "info"
    name = "Info progetto"
    description = "Visualizza metadati del progetto"

    def execute(self, project_path: str) -> str:
        from src.project.repository import load_project

        project = load_project(project_path)
        info = project.project_info
        return (
            f"Nome: {info.name or '-'}\n"
            f"Autore: {info.author or '-'}\n"
            f"Descrizione: {info.description or '-'}\n"
            f"Schema: {project.schema_version}"
        )

    def to_spec(self) -> PluginSpec:
        return PluginSpec(
            id=self.plugin_id,
            title=self.name,
            category="project",
            icon="ℹ️",
            description=self.description,
            actions=[
                ActionSpec(
                    id="show_info",
                    label="Mostra info progetto",
                    handler=self.execute,
                    params=[
                        ParamSpec(
                            name="project",
                            label="Project file",
                            type="file",
                            required=False,
                            description="Path to the project JSON file (optional).",
                        )
                    ],
                    description="Carica e mostra i metadati principali.",
                    icon="ℹ️",
                )
            ],
        )


def register(registry: PluginRegistry) -> None:
    registry.register(InfoPlugin().to_spec())
