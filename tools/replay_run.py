<<<<<<< HEAD
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
=======
#!/usr/bin/env python3
"""Replay a previous run and compare manifests for drift detection.

Usage::

    python tools/replay_run.py path/to/run_folder [--replay-dir DIR]

Loads the snapshot from the run folder, re-executes, and compares the
resulting manifest against the original.  Exits 0 if identical, 1 if drift
is detected.
"""

from __future__ import annotations

import argparse
import json
import sys

from src.project.timeline import replay_run


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a run and detect drift.")
    parser.add_argument("run_dir", help="Path to the original run folder")
    parser.add_argument(
        "--replay-dir",
        default=None,
        help="Base directory for the replay folder (default: sibling of run_dir)",
    )
    args = parser.parse_args()

    report = replay_run(args.run_dir, replay_base=args.replay_dir)

    if report.identical:
        print("REPLAY OK – manifests are identical.")
        sys.exit(0)
    else:
        print("DRIFT DETECTED:", file=sys.stderr)
        if report.missing_files:
            print(f"  Missing files : {report.missing_files}", file=sys.stderr)
        if report.extra_files:
            print(f"  Extra files   : {report.extra_files}", file=sys.stderr)
        if report.hash_mismatches:
            print("  Hash mismatches:", file=sys.stderr)
            for fname, diff in report.hash_mismatches.items():
                orig_short = diff["original"][:12]
                replay_short = diff["replayed"][:12]
                print(f"    {fname}: {orig_short}… → {replay_short}…", file=sys.stderr)
        if report.field_diffs:
            print("  Field diffs:", file=sys.stderr)
            for fname, diff in report.field_diffs.items():
                print(f"    {fname}: {diff['original']} → {diff['replayed']}", file=sys.stderr)
        # Also print JSON diff for machine consumption
        print(json.dumps({
            "identical": False,
            "missing_files": report.missing_files,
            "extra_files": report.extra_files,
            "hash_mismatches": report.hash_mismatches,
            "field_diffs": report.field_diffs,
        }, indent=2))
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
        sys.exit(1)


if __name__ == "__main__":
    main()
