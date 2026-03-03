#!/usr/bin/env python3
"""Replay a previous run and compare manifests for drift detection.

Usage::

    python tools/replay_run.py path/to/run_folder

Exits 0 if identical, 1 if drift detected.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

# Ensure project root is importable regardless of how the script is invoked.
_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.project.timeline import replay_run  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a run and detect drift.")
    parser.add_argument("run_dir", help="Path to the original run folder")
    args = parser.parse_args()

    report = replay_run(args.run_dir)
    if report.identical:
        print("REPLAY OK: manifests are identical")
        sys.exit(0)
    else:
        print("DRIFT DETECTED:", file=sys.stderr)
        if report.missing_files:
            print(f"  missing: {report.missing_files}", file=sys.stderr)
        if report.extra_files:
            print(f"  extra:   {report.extra_files}", file=sys.stderr)
        if report.hash_mismatches:
            print(f"  hash mismatches: {list(report.hash_mismatches.keys())}", file=sys.stderr)
        if report.field_diffs:
            print(f"  field diffs: {report.field_diffs}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
