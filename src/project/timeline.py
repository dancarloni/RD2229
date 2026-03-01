"""
Timeline and manifest utilities for project run tracking (MVP).
- RunRecord: run_id, timestamp_path, project_id, commit_hash, python_version, normative_ids, modules_executed
- OutputManifest: files [{path, sha256}], module_outputs, warnings
- sha256_file(path): returns hex digest
- write_manifest(manifest, path): writes manifest as JSON
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class RunRecord(BaseModel):
    run_id: str
    timestamp_path: str  # e.g. 20260301T120000Z
    project_id: str
    commit_hash: str
    python_version: str
    normative_ids: list[str]
    modules_executed: list[str]


class OutputFileEntry(BaseModel):
    path: str
    sha256: str


class OutputManifest(BaseModel):
    files: list[OutputFileEntry]
    module_outputs: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(manifest: OutputManifest, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(), f, ensure_ascii=False, indent=2, sort_keys=True)
