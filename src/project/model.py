"""High-level project model re-exports and helpers.

Keeps :pymod:`src.project.schema` as the single Pydantic source-of-truth
while providing convenience imports and thin helpers used by timeline /
run / replay tooling.

The public :class:`ProjectModel` extends the schema model with the PR #55
container fields (``meta``, ``normative_profile``, ``modules``) so that
both the schema-validation tests and the run/replay tests share one class.
"""

from __future__ import annotations

import os
import platform
import subprocess
from typing import Any

from pydantic import BaseModel, Field

from src.project.schema import (  # noqa: F401 -- re-exports
    CURRENT_SCHEMA_VERSION,
    CodeSettings,
    FireSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel as _SchemaProjectModel,
    ResultsRef,
    SeismicInputs,
)


class NormativeProfileRef(BaseModel):
    """Lightweight reference to normative sources."""

    source_ids: list[str] = Field(default_factory=list)
    clauses: list[str] = Field(default_factory=list)


class ProjectMeta(BaseModel):
    """Auditable metadata block for the project container."""

    id: str = ""
    name: str = ""
    created_at: str  # required – no default so empty meta fails JSON Schema validation
    updated_at: str = ""
    commit_hash: str = ""
    schema_version: str = ""


class ModuleConfig(BaseModel):
    """Per-module configuration entry."""

    name: str
    enabled: bool = True
    params: dict[str, Any] = Field(default_factory=dict)


def _default_meta() -> ProjectMeta:
    """Return a ProjectMeta with created_at pre-filled to now (UTC ISO-8601)."""
    import datetime as _dt

    return ProjectMeta(created_at=_dt.datetime.now(_dt.UTC).isoformat())


class ProjectModel(_SchemaProjectModel):
    """Unified project model: inherits pipeline fields and adds container fields.

    All container fields are optional (default-constructed) for back-compat.
    """

    meta: ProjectMeta = Field(default_factory=_default_meta)
    normative_profile: NormativeProfileRef = Field(default_factory=NormativeProfileRef)
    modules: list[ModuleConfig] = Field(default_factory=list)
    io_settings: dict[str, Any] = Field(default_factory=dict)


def get_commit_hash() -> str:
    """Return short git commit hash or 'UNKNOWN' if unavailable."""
    for env_var in ("GITHUB_SHA", "GIT_COMMIT", "CI_COMMIT_SHA"):
        sha = os.environ.get(env_var, "")
        if sha:
            return sha[:8]
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            .decode()
            .strip()
        )
    except Exception:
        return "UNKNOWN"


def get_python_version() -> str:
    """Return 'major.minor.patch' of the running interpreter."""
    return platform.python_version()


def project_to_snapshot(project: ProjectModel) -> dict[str, Any]:
    """Serialise *project* to a deterministic dict suitable for snapshotting."""
    return project.model_dump(mode="json")


__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "CodeSettings",
    "FireSettings",
    "GeometryEntry",
    "LoadEntry",
    "MaterialEntry",
    "ModuleConfig",
    "NormativeProfileRef",
    "ProjectInfo",
    "ProjectMeta",
    "ProjectModel",
    "ResultsRef",
    "SeismicInputs",
    "get_commit_hash",
    "get_python_version",
    "project_to_snapshot",
]
