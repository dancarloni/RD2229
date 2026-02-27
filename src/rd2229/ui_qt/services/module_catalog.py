from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleDescriptor:
    module_id: str
    title: str
    description: str
    status: str


def build_module_catalog() -> list[ModuleDescriptor]:
    return [
        ModuleDescriptor(
            module_id="mvp_structural",
            title="MVP Structural Check",
            description="Esegue il check MVP (SQLite + trace) con configurazione jsoncode.",
            status="ready",
        ),
        ModuleDescriptor(
            module_id="vba_migration",
            title="VBA Migration",
            description="Stream C: baseline macro bandiera e golden tests (in pianificazione).",
            status="planned",
        ),
        ModuleDescriptor(
            module_id="reporting_audit",
            title="Reporting Audit",
            description="Stream E1: export JSON/HTML auditabile (in pianificazione).",
            status="planned",
        ),
    ]
