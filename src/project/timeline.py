"""Timeline / run-record utilities for auditable project runs."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, Field

from src.project.model import ProjectModel, get_commit_hash, get_python_version, project_to_snapshot
from src.project.schema import CURRENT_SCHEMA_VERSION

UTC = UTC


class RunRecord(BaseModel):
    """Auditable record written alongside every run."""

    run_id: str
    timestamp_path: str = ""
    project_id: str = ""
    commit_hash: str
    python_version: str
    normative_ids: list[str]
    modules_executed: list[str]
    schema_version: str = CURRENT_SCHEMA_VERSION
    outputs: dict[str, str] = Field(default_factory=dict)


class OutputFileEntry(BaseModel):
    path: str
    sha256: str


class OutputManifest(BaseModel):
    files: list[OutputFileEntry]
    module_outputs: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


def sha256_file(path: str | Path) -> str:
    """Return the hex SHA-256 digest of the file at *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def write_manifest(manifest: OutputManifest, out_path: str | Path) -> None:
    """Serialise *manifest* as deterministic JSON to *out_path*."""
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_deterministic_json(manifest.model_dump(mode="json")))


def _deterministic_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def _generate_run_id() -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"run_{ts}_{get_commit_hash()[:7]}"


def _extract_normative_ids(project: ProjectModel) -> list[str]:
    ids: list[str] = []
    norm_code = project.code_settings.norm_code
    if norm_code:
        ids.append(norm_code)
    if hasattr(project, "normative_profile") and project.normative_profile:
        ids.extend(project.normative_profile.source_ids)
    return sorted(set(ids))


def _execute_modules(project: ProjectModel, run_dir: str) -> dict[str, str]:
    outputs: dict[str, str] = {}
    for step in project.pipeline_steps:
        out_name = f"output_{step}.json"
        out_path = os.path.join(run_dir, out_name)
        payload: dict[str, Any] = {
            "module": step,
            "status": "placeholder",
            "message": f"Module {step!r} executed (placeholder).",
        }
        content = _deterministic_json(payload)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        outputs[out_name] = sha256_bytes(content.encode())
    return outputs


def create_run(
    project: ProjectModel,
    base_dir: str,
    *,
    run_id: str | None = None,
) -> tuple[str, RunRecord]:
    """Create a run folder under *base_dir* and return (run_dir, record)."""
    if run_id is None:
        run_id = _generate_run_id()

    run_dir = os.path.join(base_dir, run_id)
    os.makedirs(run_dir, exist_ok=True)

    snapshot = project_to_snapshot(project)
    snapshot_content = _deterministic_json(snapshot)
    with open(os.path.join(run_dir, "project.snapshot.json"), "w", encoding="utf-8") as fh:
        fh.write(snapshot_content)

    outputs = _execute_modules(project, run_dir)
    outputs["project.snapshot.json"] = sha256_bytes(snapshot_content.encode())

    record = RunRecord(
        run_id=run_id,
        timestamp_path=datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
        project_id=getattr(getattr(project, "meta", None), "id", "") or "",
        commit_hash=get_commit_hash(),
        python_version=get_python_version(),
        schema_version=project.schema_version,
        normative_ids=_extract_normative_ids(project),
        modules_executed=list(project.pipeline_steps),
        outputs=dict(sorted(outputs.items())),
    )

    with open(os.path.join(run_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        fh.write(_deterministic_json(record.model_dump(mode="json")))

    return run_dir, record


@dataclass
class DriftReport:
    identical: bool
    missing_files: list[str] = field(default_factory=list)
    extra_files: list[str] = field(default_factory=list)
    hash_mismatches: dict[str, dict[str, str]] = field(default_factory=dict)
    field_diffs: dict[str, dict[str, str]] = field(default_factory=dict)


def load_manifest(run_dir: str) -> dict[str, Any]:
    with open(os.path.join(run_dir, "manifest.json"), encoding="utf-8") as fh:
        return cast(dict[str, Any], json.load(fh))


def replay_run(run_dir: str, replay_base: str | None = None) -> DriftReport:
    original_manifest = load_manifest(run_dir)
    with open(os.path.join(run_dir, "project.snapshot.json"), encoding="utf-8") as fh:
        snapshot = json.load(fh)

    project = ProjectModel.model_validate(snapshot)

    if replay_base is None:
        replay_base = os.path.dirname(run_dir)
    replay_id = original_manifest["run_id"] + "_replay"
    replay_dir = os.path.join(replay_base, replay_id)
    if os.path.exists(replay_dir):
        shutil.rmtree(replay_dir)

    _, replay_record = create_run(project, replay_base, run_id=replay_id)
    return compare_manifests(original_manifest, replay_record.model_dump(mode="json"))


def compare_manifests(
    original: dict[str, Any],
    replayed: dict[str, Any],
) -> DriftReport:
    report = DriftReport(identical=True)
    orig_out: dict[str, str] = original.get("outputs", {})
    rep_out: dict[str, str] = replayed.get("outputs", {})
    orig_keys = set(orig_out)
    rep_keys = set(rep_out)
    report.missing_files = sorted(orig_keys - rep_keys)
    report.extra_files = sorted(rep_keys - orig_keys)
    for key in sorted(orig_keys & rep_keys):
        if orig_out[key] != rep_out[key]:
            report.hash_mismatches[key] = {"original": orig_out[key], "replayed": rep_out[key]}
    skip = {"run_id", "outputs", "timestamp_path"}
    for f in sorted(set(original) | set(replayed)):
        if f in skip:
            continue
        o, r = original.get(f), replayed.get(f)
        if o != r:
            report.field_diffs[f] = {"original": str(o), "replayed": str(r)}
    if report.missing_files or report.extra_files or report.hash_mismatches or report.field_diffs:
        report.identical = False
    return report
