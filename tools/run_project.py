<<<<<<< HEAD
"""
Run a project.json deterministically, create run folder, snapshot, outputs, manifest.
- Loads and validates project.json
- Creates projects/<id>/runs/<run_id>/
- Writes snapshot (canonicalized input)
- For each enabled module: if no executor, writes placeholder output JSON (status="TBD", normative IDs)
- Writes manifest.json with sha256
"""

import json
import pathlib
import platform
import re
import sys
from datetime import UTC, datetime

from src.project.repository import load_project
from src.project.timeline import (
    OutputFileEntry,
    OutputManifest,
    RunRecord,
    sha256_file,
    write_manifest,
)


def sanitize_id(val: str) -> str:
    # Only allow alphanum, dash, underscore
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", val.strip()) if val else ""


def get_project_id(project, input_path: pathlib.Path) -> str:
    # Try to read raw project JSON from input_path to prefer persisted meta.id
    try:
        if input_path.exists():
            with open(input_path, encoding="utf-8") as rf:
                raw = json.load(rf)
            if isinstance(raw, dict):
                meta_raw = raw.get("meta") or raw.get("project_info")
                if isinstance(meta_raw, dict):
                    raw_id = meta_raw.get("id")
                    if raw_id:
                        return sanitize_id(str(raw_id))
                    raw_name = meta_raw.get("name")
                    if raw_name:
                        return sanitize_id(str(raw_name))
    except Exception:
        # ignore errors reading raw file and fall back to project object
        pass
    # a) meta.id if present and non-empty (handle both Pydantic v2 and dict)
    meta = None
    if hasattr(project, "meta"):
        meta = project.meta
    elif isinstance(project, dict) and "meta" in project:
        meta = project["meta"]
    if meta is not None:
        pid = getattr(meta, "id", None) if hasattr(meta, "id") else meta.get("id")
        if pid is not None and str(pid).strip():
            return sanitize_id(str(pid))
        pname = getattr(meta, "name", None) if hasattr(meta, "name") else meta.get("name")
        if pname is not None and str(pname).strip():
            return sanitize_id(str(pname))
    # b) project_info.id if present and non-empty
    if hasattr(project, "project_info"):
        pi = project.project_info
        pi_id = (
            getattr(pi, "id", None)
            if hasattr(pi, "id")
            else pi.get("id") if isinstance(pi, dict) else None
        )
        if pi_id is not None and str(pi_id).strip():
            return sanitize_id(str(pi_id))
    # c) input_path stem
    if input_path and input_path.stem:
        return sanitize_id(input_path.stem)
    # d) fallback
    return "unknown"


def canonicalize_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: run_project.py <project.json>", file=sys.stderr)
            sys.exit(1)
        project_path = pathlib.Path(sys.argv[1])
        project = load_project(str(project_path))
        # Also read the raw input file to preserve original keys (meta/modules)
        raw_project_data = {}
        try:
            with open(project_path, encoding="utf-8") as rf:
                raw_project_data = json.load(rf)
        except Exception:
            raw_project_data = {}
        project_id = get_project_id(project, project_path)
        # Prefer modules from the original raw JSON when present (preserves new ProjectModel shape)
        if hasattr(project, "modules"):
            modules = project.modules
        elif (
            raw_project_data
            and isinstance(raw_project_data, dict)
            and "modules" in raw_project_data
        ):
            modules = raw_project_data["modules"]
        elif isinstance(project, dict) and "modules" in project:
            modules = project["modules"]
        else:
            modules = []
        if raw_project_data and isinstance(raw_project_data, dict):
            normative_ids = raw_project_data.get("normative_profile", {}).get("source_ids", [])
            commit_hash = raw_project_data.get("meta", {}).get("commit_hash", "N/A")
        else:
            if hasattr(project, "normative_profile"):
                normative_ids = getattr(project.normative_profile, "source_ids", [])
            elif isinstance(project, dict) and "normative_profile" in project:
                normative_ids = project["normative_profile"].get("source_ids", [])
            else:
                normative_ids = []
            if hasattr(project, "meta"):
                commit_hash = getattr(project.meta, "commit_hash", "N/A")
            elif isinstance(project, dict) and "meta" in project:
                commit_hash = project["meta"].get("commit_hash", "N/A")
            else:
                commit_hash = "N/A"
        # Prefer the original raw project JSON for snapshot so replay sees same keys
        snapshot_data = (
            raw_project_data
            if raw_project_data
            else (project.model_dump() if hasattr(project, "model_dump") else dict(project))
        )
        now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"run_{now}"
        # If the input project_path is in a temp dir (pytest), write output there
        if project_path.is_absolute() and any(
            part.startswith("pytest-") or part.startswith("tmp") for part in project_path.parts
        ):
            base_dir = project_path.parent / "projects"
        else:
            base_dir = pathlib.Path("projects")
        run_dir = base_dir / project_id / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        # Write canonicalized snapshot
        snapshot_path = run_dir / "project.snapshot.json"
        with open(snapshot_path, "w", encoding="utf-8") as f:
            f.write(canonicalize_json(snapshot_data))
        # Generate outputs for enabled modules
        output_files = []
        module_outputs = {}
        for mod in modules:
            mod_name = getattr(mod, "name", mod.get("name", "mod"))
            mod_enabled = getattr(mod, "enabled", mod.get("enabled", True))
            if not mod_enabled:
                continue
            out_path = run_dir / f"output_{mod_name}.json"
            # Placeholder output: status TBD, normative IDs
            out_data = {
                "status": "TBD",
                "normative_ids": normative_ids,
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(out_data, f, ensure_ascii=False, indent=2, sort_keys=True)
            sha = sha256_file(out_path)
            output_files.append(OutputFileEntry(path=str(out_path), sha256=sha))
            module_outputs[mod_name] = out_data
        # Write manifest
        manifest = OutputManifest(
            files=output_files,
            module_outputs=module_outputs,
            warnings=[],
        )
        manifest_path = run_dir / "manifest.json"
        write_manifest(manifest, manifest_path)
        # Write run record
        run_record = RunRecord(
            run_id=run_id,
            timestamp_path=now,
            project_id=project_id,
            commit_hash=commit_hash,
            python_version=platform.python_version(),
            normative_ids=normative_ids,
            modules_executed=[
                getattr(mod, "name", mod.get("name", "mod"))
                for mod in modules
                if getattr(mod, "enabled", mod.get("enabled", True))
            ],
        )
        with open(run_dir / "run_record.json", "w", encoding="utf-8") as f:
            json.dump(run_record.model_dump(), f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"Run complete: {run_dir}")
    except Exception as e:
        import traceback

        print("[run_project.py] Exception:", e, file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
=======
#!/usr/bin/env python3
"""Run a project: create a run folder with snapshot, manifest, and outputs.

Usage::

    python tools/run_project.py path/to/project.json [--output-dir DIR]

Creates ``<output-dir>/<run_id>/`` containing:
* ``project.snapshot.json`` – frozen copy of the input
* ``manifest.json`` – commit hash, python version, normative IDs, output hashes
* ``output_<module>.json`` – deterministic output per pipeline step
"""

from __future__ import annotations

import argparse
import sys

from src.project.model import ProjectModel
from src.project.repository import load_project
from src.project.timeline import create_run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a project and produce auditable artefacts.")
    parser.add_argument("project", help="Path to project.json")
    parser.add_argument(
        "--output-dir",
        default="projects",
        help="Base directory for run folders (default: projects)",
    )
    args = parser.parse_args()

    project: ProjectModel = load_project(args.project)
    run_dir, record = create_run(project, args.output_dir)

    print(f"Run created: {run_dir}")
    print(f"  run_id         : {record.run_id}")
    print(f"  commit_hash    : {record.commit_hash}")
    print(f"  python_version : {record.python_version}")
    print(f"  modules        : {record.modules_executed}")
    print(f"  outputs        : {len(record.outputs)} file(s)")
    sys.exit(0)
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))


if __name__ == "__main__":
    main()
