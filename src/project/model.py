"""
Project model definitions for IO, schema, and timeline MVP (copilot/project-io-timeline-mvp).

- ProjectMeta: id, name, created_at, updated_at, commit_hash, schema_version
- NormativeProfileRef: list of normative source IDs (+ optional clause/§ refs)
- ModuleConfig: name, enabled, params
- ProjectModel: meta, normative_profile, modules, io_settings

Uses Pydantic v2 (as in repo).
"""

from __future__ import annotations

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
