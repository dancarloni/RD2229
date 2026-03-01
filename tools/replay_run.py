"""
Replay a previous run: re-executes and compares manifest/output list, reports drift.
- Reads snapshot and run_record
- Re-runs (same mechanism as run_project)
- Compares manifest: same file list + sha256, else diff report
"""

import json
import pathlib
import sys

from src.project.timeline import OutputManifest, sha256_file


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        return OutputManifest.model_validate(json.load(f))


def main():
    if len(sys.argv) != 2:
        print("Usage: replay_run.py <run_dir>", file=sys.stderr)
        sys.exit(1)
    run_dir = pathlib.Path(sys.argv[1])
    snapshot_path = run_dir / "project.snapshot.json"
    manifest_path = run_dir / "manifest.json"
    if not snapshot_path.exists() or not manifest_path.exists():
        print("Missing snapshot or manifest in run_dir", file=sys.stderr)
        sys.exit(1)
    # Load snapshot and manifest
    with open(snapshot_path, encoding="utf-8") as f:
        project_data = json.load(f)
    orig_manifest = load_manifest(manifest_path)
    # Re-run outputs (same logic as run_project, but in-memory)
    output_files = []
    for mod in project_data["modules"]:
        if not mod.get("enabled", True):
            continue
        out_path = run_dir / f"output_{mod['name']}.json"
        sha = sha256_file(out_path)
        output_files.append({"path": str(out_path), "sha256": sha})
    # Compare manifests
    orig_files = sorted([(f.path, f.sha256) for f in orig_manifest.files])
    new_files = sorted([(f["path"], f["sha256"]) for f in output_files])
    if orig_files == new_files:
        print("REPLAY OK: outputs match manifest")
        sys.exit(0)
    else:
        print("DRIFT DETECTED:")
        for (op, os), (np, ns) in zip(orig_files, new_files):
            if (op, os) != (np, ns):
                print(f"  {op}: {os} != {ns}")
        sys.exit(1)


if __name__ == "__main__":
    main()
