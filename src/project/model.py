<<<<<<< HEAD
"""
Project model definitions for IO, schema, and timeline MVP (copilot/project-io-timeline-mvp).

- ProjectMeta: id, name, created_at, updated_at, commit_hash, schema_version
- NormativeProfileRef: list of normative source IDs (+ optional clause/§ refs)
- ModuleConfig: name, enabled, params
- ProjectModel: meta, normative_profile, modules, io_settings

Uses Pydantic v2 (as in repo).
=======
"""High-level project model re-exports and helpers.

Keeps :pymod:`src.project.schema` as the single Pydantic source-of-truth
while providing convenience imports and thin helpers used by timeline /
run / replay tooling.
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
"""

from __future__ import annotations

<<<<<<< HEAD
from typing import Any

from pydantic import BaseModel, Field


class ProjectMeta(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    commit_hash: str
    schema_version: str


class NormativeProfileRef(BaseModel):
    source_ids: list[str]
    clauses: list[str] | None = None  # e.g. ["§4.2.1", "§5.1"]


class ModuleConfig(BaseModel):
    name: str
    enabled: bool = True
    params: dict[str, Any] = Field(default_factory=dict)


class ProjectModel(BaseModel):
    meta: ProjectMeta
    normative_profile: NormativeProfileRef
    modules: list[ModuleConfig]
    io_settings: dict[str, Any] = Field(default_factory=dict)
=======
import subprocess
import sys
from typing import Any

from src.project.schema import (  # noqa: F401 – re-exports
    CURRENT_SCHEMA_VERSION,
    CodeSettings,
    FireSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel,
    ResultsRef,
    SeismicInputs,
)

__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "CodeSettings",
    "FireSettings",
    "GeometryEntry",
    "LoadEntry",
    "MaterialEntry",
    "ProjectInfo",
    "ProjectModel",
    "ResultsRef",
    "SeismicInputs",
    "get_commit_hash",
    "get_python_version",
    "project_to_snapshot",
]


def get_commit_hash() -> str:
    """Return the short git commit hash, or ``'unknown'`` outside a repo."""
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


def get_python_version() -> str:
    """Return ``'major.minor.patch'`` of the running interpreter."""
    v = sys.version_info
    return f"{v.major}.{v.minor}.{v.micro}"


def project_to_snapshot(project: ProjectModel) -> dict[str, Any]:
    """Serialise *project* to a deterministic dict suitable for snapshotting."""
    return project.model_dump(mode="json")
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
