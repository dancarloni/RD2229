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
import sys
from datetime import datetime

from src.project.repository import load_project
from src.project.timeline import (
    OutputFileEntry,
    OutputManifest,
    RunRecord,
    sha256_file,
    write_manifest,
)


def canonicalize_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: run_project.py <project.json>", file=sys.stderr)
            sys.exit(1)
        project_path = pathlib.Path(sys.argv[1])
        project = load_project(str(project_path))
        # Support both new MVP ProjectModel and legacy ProjectModel
        # Modern ProjectModel: always use meta.id if present
        # Use meta.id if present, else project_info.id, else 'unknown'
        if hasattr(project, "meta") and hasattr(project, "modules"):
            print(f"[DEBUG] project.meta = {repr(project.meta)}")
            print(f"[DEBUG] project.meta.id = {getattr(project.meta, 'id', None)}")
            project_id = getattr(project.meta, "id", None)
            if not project_id and hasattr(project, "project_info"):
                project_id = getattr(project.project_info, "id", None)
            if not project_id:
                project_id = "unknown"
            modules = project.modules
            normative_ids = getattr(getattr(project, "normative_profile", None), "source_ids", [])
            commit_hash = getattr(project.meta, "commit_hash", "N/A")
            snapshot_data = (
                project.model_dump() if hasattr(project, "model_dump") else dict(project)
            )
        elif isinstance(project, dict) and "meta" in project and "modules" in project:
            project_id = project["meta"].get("id", None)
            if not project_id and "project_info" in project:
                project_id = project["project_info"].get("id", None)
            if not project_id:
                project_id = "unknown"
            modules = project["modules"]
            normative_ids = project.get("normative_profile", {}).get("source_ids", [])
            commit_hash = project["meta"].get("commit_hash", "N/A")
            snapshot_data = dict(project)
        elif hasattr(project, "project_info") and hasattr(project, "modules"):
            # legacy ProjectModel with project_info
            project_info = project.project_info
            project_id = getattr(project_info, "id", None) or (
                project_info["id"]
                if isinstance(project_info, dict) and "id" in project_info
                else "unknown"
            )
            modules = project.modules
            normative_profile = getattr(project, "normative_profile", None)
            if normative_profile is not None:
                normative_ids = getattr(normative_profile, "source_ids", None) or (
                    normative_profile["source_ids"]
                    if isinstance(normative_profile, dict) and "source_ids" in normative_profile
                    else []
                )
            else:
                normative_ids = []
            commit_hash = getattr(getattr(project, "meta", {}), "commit_hash", "N/A")
            snapshot_data = (
                project.model_dump() if hasattr(project, "model_dump") else dict(project)
            )
        else:
            # fallback: try to access id and modules as dict
            project_id = getattr(project, "id", "unknown")
            modules = getattr(project, "modules", [])
            normative_ids = []
            commit_hash = "N/A"
            snapshot_data = (
                project.model_dump() if hasattr(project, "model_dump") else dict(project)
            )
        now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
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


if __name__ == "__main__":
    main()
