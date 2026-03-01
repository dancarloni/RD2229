<<<<<<< HEAD
"""
Timeline and manifest utilities for project run tracking (MVP).
- RunRecord: run_id, timestamp_path, project_id, commit_hash, python_version, normative_ids, modules_executed
- OutputManifest: files [{path, sha256}], module_outputs, warnings
- sha256_file(path): returns hex digest
- write_manifest(manifest, path): writes manifest as JSON
=======
"""Timeline / run-record utilities for auditable project runs.

Responsibilities
----------------
* Create a **run folder** containing a frozen snapshot of the project input,
  deterministic module outputs, and a ``manifest.json`` with hashes.
* **Replay** a previous run by re-executing from its snapshot and comparing
  the resulting manifest to the stored one, reporting any drift.

Design constraints (from issue #42, sub-issue 01):
* Determinism – outputs and manifest must be identical for the same input
  (no variable timestamps inside compared artefacts; timestamps only in the
  run-folder name / ``run_id``).
* No new structural-calculation algorithms – modules produce placeholder
  outputs when they have no real computation to perform.
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
"""

from __future__ import annotations

import hashlib
import json
<<<<<<< HEAD
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
=======
import os
import shutil
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.project.model import (
    ProjectModel,
    get_commit_hash,
    get_python_version,
    project_to_snapshot,
)

# ---------------------------------------------------------------------------
# RunRecord dataclass
# ---------------------------------------------------------------------------


@dataclass
class RunRecord:
    """Immutable record that describes a single pipeline run."""

    run_id: str
    commit_hash: str
    python_version: str
    schema_version: str
    normative_ids: list[str] = field(default_factory=list)
    modules_executed: list[str] = field(default_factory=list)
    outputs: dict[str, str] = field(default_factory=dict)  # filename → sha256


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    """Return the hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    """Return the hex SHA-256 digest of the file at *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
            h.update(chunk)
    return h.hexdigest()


<<<<<<< HEAD
def write_manifest(manifest: OutputManifest, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(), f, ensure_ascii=False, indent=2, sort_keys=True)
=======
# ---------------------------------------------------------------------------
# Deterministic JSON encoding
# ---------------------------------------------------------------------------


def _deterministic_json(obj: Any) -> str:
    """Encode *obj* as JSON with sorted keys and no trailing whitespace."""
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Run creation
# ---------------------------------------------------------------------------


def _generate_run_id() -> str:
    """Create a run ID that embeds a UTC timestamp (allowed in path only)."""
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    short_hash = get_commit_hash()[:7]
    return f"run_{ts}_{short_hash}"


def _extract_normative_ids(project: ProjectModel) -> list[str]:
    """Extract normative reference IDs from the project (metadata only)."""
    ids: list[str] = []
    norm_code = project.code_settings.norm_code
    if norm_code:
        ids.append(norm_code)
    return sorted(set(ids))


def _execute_modules(
    project: ProjectModel,
    run_dir: str,
) -> dict[str, str]:
    """Run each pipeline step, writing deterministic output files.

    Returns a mapping *filename → sha256* of every produced file.
    """
    outputs: dict[str, str] = {}

    for step in project.pipeline_steps:
        out_name = f"output_{step}.json"
        out_path = os.path.join(run_dir, out_name)

        # Deterministic placeholder – content depends only on step name and
        # project snapshot (never on wall-clock time).
        payload: dict[str, Any] = {
            "module": step,
            "status": "placeholder",
            "message": f"Module '{step}' executed (placeholder).",
        }
        content = _deterministic_json(payload)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        outputs[out_name] = sha256_bytes(content.encode("utf-8"))

    return outputs


def create_run(
    project: ProjectModel,
    base_dir: str,
    *,
    run_id: str | None = None,
) -> tuple[str, RunRecord]:
    """Create a run folder under *base_dir* and return ``(run_dir, record)``.

    Steps performed:
    1. Generate ``run_id`` (or accept a caller-supplied one).
    2. Create ``<base_dir>/<run_id>/``.
    3. Write ``project.snapshot.json`` (frozen input).
    4. Execute modules → write output files.
    5. Build ``manifest.json`` and write it.

    Returns the absolute path to the run directory and the :class:`RunRecord`.
    """
    if run_id is None:
        run_id = _generate_run_id()

    run_dir = os.path.join(base_dir, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # 1) Snapshot
    snapshot = project_to_snapshot(project)
    snapshot_path = os.path.join(run_dir, "project.snapshot.json")
    snapshot_content = _deterministic_json(snapshot)
    with open(snapshot_path, "w", encoding="utf-8") as fh:
        fh.write(snapshot_content)

    # 2) Execute modules
    outputs = _execute_modules(project, run_dir)

    # Add snapshot hash
    outputs["project.snapshot.json"] = sha256_bytes(snapshot_content.encode("utf-8"))

    # 3) Build record
    record = RunRecord(
        run_id=run_id,
        commit_hash=get_commit_hash(),
        python_version=get_python_version(),
        schema_version=project.schema_version,
        normative_ids=_extract_normative_ids(project),
        modules_executed=list(project.pipeline_steps),
        outputs=dict(sorted(outputs.items())),
    )

    # 4) Write manifest
    manifest_path = os.path.join(run_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        fh.write(_deterministic_json(asdict(record)))

    return run_dir, record


# ---------------------------------------------------------------------------
# Replay & drift detection
# ---------------------------------------------------------------------------


@dataclass
class DriftReport:
    """Result of comparing two manifests."""

    identical: bool
    missing_files: list[str] = field(default_factory=list)
    extra_files: list[str] = field(default_factory=list)
    hash_mismatches: dict[str, dict[str, str]] = field(default_factory=dict)
    field_diffs: dict[str, dict[str, str]] = field(default_factory=dict)


def load_manifest(run_dir: str) -> dict[str, Any]:
    """Load ``manifest.json`` from *run_dir*."""
    path = os.path.join(run_dir, "manifest.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def replay_run(run_dir: str, replay_base: str | None = None) -> DriftReport:
    """Replay a run from its snapshot and compare manifests.

    Parameters
    ----------
    run_dir:
        Path to the original run directory (must contain
        ``project.snapshot.json`` and ``manifest.json``).
    replay_base:
        Directory where the replay run folder will be created.
        Defaults to a sibling ``<run_id>_replay`` folder next to *run_dir*.

    Returns
    -------
    DriftReport:
        Comparison between original and replayed manifests.
    """
    # Load original manifest & snapshot
    original_manifest = load_manifest(run_dir)
    snapshot_path = os.path.join(run_dir, "project.snapshot.json")
    with open(snapshot_path, encoding="utf-8") as fh:
        snapshot = json.load(fh)

    project = ProjectModel.model_validate(snapshot)

    # Create replay run
    if replay_base is None:
        replay_base = os.path.dirname(run_dir)
    replay_id = original_manifest["run_id"] + "_replay"

    replay_dir = os.path.join(replay_base, replay_id)
    if os.path.exists(replay_dir):
        shutil.rmtree(replay_dir)

    _, replay_record = create_run(
        project,
        replay_base,
        run_id=replay_id,
    )

    replay_manifest = asdict(replay_record)

    # Compare manifests
    return compare_manifests(original_manifest, replay_manifest)


def compare_manifests(
    original: dict[str, Any],
    replayed: dict[str, Any],
) -> DriftReport:
    """Compare two manifest dicts and return a :class:`DriftReport`."""
    report = DriftReport(identical=True)

    # Compare output hashes
    orig_outputs: dict[str, str] = original.get("outputs", {})
    replay_outputs: dict[str, str] = replayed.get("outputs", {})

    orig_keys = set(orig_outputs)
    replay_keys = set(replay_outputs)

    report.missing_files = sorted(orig_keys - replay_keys)
    report.extra_files = sorted(replay_keys - orig_keys)

    for key in sorted(orig_keys & replay_keys):
        if orig_outputs[key] != replay_outputs[key]:
            report.hash_mismatches[key] = {
                "original": orig_outputs[key],
                "replayed": replay_outputs[key],
            }

    # Compare top-level fields (except run_id and outputs which are already handled)
    skip_fields = {"run_id", "outputs"}
    for field_name in sorted(set(original) | set(replayed)):
        if field_name in skip_fields:
            continue
        o_val = original.get(field_name)
        r_val = replayed.get(field_name)
        if o_val != r_val:
            report.field_diffs[field_name] = {
                "original": str(o_val),
                "replayed": str(r_val),
            }

    if report.missing_files or report.extra_files or report.hash_mismatches or report.field_diffs:
        report.identical = False

    return report
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
