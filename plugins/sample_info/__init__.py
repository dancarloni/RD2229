"""Sample Info plugin – displays project information."""

from __future__ import annotations

from src.plugins import ActionSpec, PluginRegistry, PluginSpec


def _show_info(project: str = "") -> dict[str, str]:
    return {"status": "ok", "project": project or "(none)", "version": "0.1.0"}


def register(registry: PluginRegistry) -> None:
    spec = PluginSpec(
        id="sample_info",
        title="Project Info",
        category="utility",
        icon="ℹ️",
        description="Displays basic project information.",
        actions=[
            ActionSpec(
                id="show_info",
                label="Show Info",
                handler=_show_info,
                description="Print project metadata to console.",
            )
        ],
    )
    registry.register(spec)
