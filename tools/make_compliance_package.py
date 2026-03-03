#!/usr/bin/env python3
"""tools/make_compliance_package.py – Create an auditable compliance ZIP package.

Bundles a project snapshot, manifest, calc outputs, normative extracts,
and a README into a single ZIP archive with SHA-256 integrity verification.

Package layout::

    compliance_<project_id>_<run_id>.zip
    ├── README.txt           # human-readable package description
    ├── manifest.json        # SHA-256 of all files in the package
    ├── project.snapshot.json
    ├── run_record.json      # RunRecord metadata (from timeline)
    ├── outputs/             # calc output JSON files (from run folder)
    │   └── *.json
    └── extracts/            # normative extracts referenced in outputs
        └── <NORM_ID>/
            └── *.md

Usage::

    # Basic: package a run folder
    python tools/make_compliance_package.py --run-dir projects/my_proj/runs/run_20260101_120000_abc1234

    # With normative extracts
    python tools/make_compliance_package.py \\
        --run-dir projects/my_proj/runs/run_20260101 \\
        --norme-dir docs/_norme \\
        --output compliance_package.zip

    # Verify an existing package
    python tools/make_compliance_package.py --verify compliance_package.zip

Exit codes: 0 = success, 1 = error.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_readme(run_id: str, project_id: str, generated: str, norm_ids: list[str]) -> str:
    return f"""RD2229 Compliance Package
=========================
Generated  : {generated}
Project ID : {project_id}
Run ID     : {run_id}
Norms      : {", ".join(norm_ids) if norm_ids else "N/A"}

Contents
--------
README.txt              This file
manifest.json           SHA-256 digests of all files in this package
project.snapshot.json   Deterministic project snapshot at time of run
run_record.json         Run metadata (commit hash, Python version, modules executed)
outputs/                Calculation output files
extracts/               Normative extract markdown files (if available)

Verification
------------
To verify package integrity::

    python tools/make_compliance_package.py --verify <this_file.zip>

Policy
------
This package was produced by the RD2229 structural engineering tool.
All files are included verbatim from the run folder.
Normative extracts are informational reference material.
"""


def collect_run_files(run_dir: Path) -> dict[str, Path]:
    """Return {archive_path: local_path} for all files in the run dir.

    JSON output files (not snapshot/record) are placed under ``outputs/``
    while preserving their relative sub-path to avoid basename collisions.
    Raises ``ValueError`` if two files would map to the same archive path.
    """
    files: dict[str, Path] = {}
    for fp in sorted(run_dir.rglob("*")):
        if fp.is_file():
            try:
                rel = str(fp.relative_to(run_dir))
            except ValueError:
                rel = fp.name
            # Normalize to forward slashes
            arc_path = rel.replace("\\", "/")
            # Put output JSON files under outputs/, preserving relative path
            if fp.suffix == ".json" and "snapshot" not in fp.name and "record" not in fp.name:
                arc_path = f"outputs/{arc_path}"
            if arc_path in files:
                raise ValueError(
                    f"Duplicate archive path {arc_path!r} for files '{files[arc_path]}' and '{fp}'"
                )
            files[arc_path] = fp
    return files


def collect_norm_extracts(norme_dir: Path, norm_ids: list[str]) -> dict[str, Path]:
    """Return {archive_path: local_path} for normative extracts."""
    files: dict[str, Path] = {}
    if not norme_dir.exists():
        return files
    for norm_id in norm_ids:
        nd = norme_dir / norm_id
        extracts_dir = nd / "extracts"
        if extracts_dir.exists():
            for ep in sorted(extracts_dir.glob("*.md")):
                arc_path = f"extracts/{norm_id}/{ep.name}"
                files[arc_path] = ep
        # Include metadata
        meta_path = nd / "metadata.json"
        if meta_path.exists():
            files[f"extracts/{norm_id}/metadata.json"] = meta_path
    return files


def _detect_norm_ids(run_dir: Path) -> list[str]:
    """Try to infer norm IDs from run_record.json or output files."""
    record_path = run_dir / "run_record.json"
    if record_path.exists():
        try:
            rec = json.loads(record_path.read_text(encoding="utf-8"))
            ids = rec.get("normative_ids", [])
            if ids:
                return ids
        except Exception:
            pass
    # Scan output files for norm references
    norm_ids = []
    for fp in run_dir.rglob("*.json"):
        try:
            text = fp.read_text(encoding="utf-8")
            for nid in ["NTC2018", "RD2229", "DM96", "DM92", "EN1992", "EN1991"]:
                if nid in text and nid not in norm_ids:
                    norm_ids.append(nid)
        except Exception:
            pass
    return norm_ids


def make_package(
    run_dir: Path,
    output_path: Path,
    norme_dir: Path | None = None,
    project_id: str = "",
    extra_metadata: dict | None = None,
) -> dict:
    """Create a compliance ZIP package.

    Returns a dict with ``path``, ``manifest``, and ``sha256`` keys.
    """
    run_id = run_dir.name
    if not project_id:
        # Try to infer from directory structure: projects/<project_id>/runs/<run_id>
        parts = run_dir.parts
        try:
            runs_idx = list(parts).index("runs")
            project_id = parts[runs_idx - 1]
        except (ValueError, IndexError):
            project_id = "unknown"

    generated = datetime.now(UTC).isoformat()
    norm_ids = _detect_norm_ids(run_dir)

    # Collect files
    run_files = collect_run_files(run_dir)
    norm_files: dict[str, Path] = {}
    if norme_dir and norm_ids:
        norm_files = collect_norm_extracts(norme_dir, norm_ids)

    all_files = {**run_files, **norm_files}

    # Build in-memory ZIP
    buf = io.BytesIO()
    manifest_entries: dict[str, str] = {}

    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # README
        readme_text = _build_readme(run_id, project_id, generated, norm_ids)
        readme_bytes = readme_text.encode("utf-8")
        zf.writestr("README.txt", readme_bytes)
        manifest_entries["README.txt"] = sha256_bytes(readme_bytes)

        # Run record / snapshot
        for arc_path, local_path in sorted(all_files.items()):
            data = local_path.read_bytes()
            zf.writestr(arc_path, data)
            manifest_entries[arc_path] = sha256_bytes(data)

        # Manifest JSON (written last, doesn't include itself)
        manifest_obj = {
            "_generated": generated,
            "_tool": "tools/make_compliance_package.py",
            "run_id": run_id,
            "project_id": project_id,
            "norm_ids": norm_ids,
            "files": manifest_entries,
        }
        if extra_metadata:
            manifest_obj["extra"] = extra_metadata
        manifest_bytes = json.dumps(
            manifest_obj, indent=2, ensure_ascii=False, sort_keys=True
        ).encode("utf-8")
        zf.writestr("manifest.json", manifest_bytes)

    zip_bytes = buf.getvalue()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(zip_bytes)

    package_sha256 = sha256_bytes(zip_bytes)
    return {
        "path": str(output_path),
        "sha256": package_sha256,
        "manifest": manifest_obj,
        "file_count": len(manifest_entries) + 1,  # +1 for manifest itself
    }


def verify_package(zip_path: Path) -> tuple[bool, list[str]]:
    """Verify a compliance package by checking SHA-256 digests from manifest.

    Returns (ok: bool, errors: list[str]).
    """
    errors: list[str] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
        if "manifest.json" not in names:
            return False, ["manifest.json not found in package"]

        manifest_raw = zf.read("manifest.json")
        try:
            manifest = json.loads(manifest_raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            return False, [f"manifest.json is not valid JSON: {exc}"]

        expected: dict[str, str] = manifest.get("files", {})
        # Consider only non-directory entries
        file_names = {name for name in names if not name.endswith("/")}
        for arc_path, expected_hash in sorted(expected.items()):
            if arc_path not in file_names:
                errors.append(f"MISSING: {arc_path}")
                continue
            actual_hash = sha256_bytes(zf.read(arc_path))
            if actual_hash != expected_hash:
                errors.append(f"HASH MISMATCH: {arc_path}")

        # Flag any unexpected files not listed in the manifest
        allowed = set(expected.keys()) | {"manifest.json"}
        for extra in sorted(file_names - allowed):
            errors.append(f"UNEXPECTED FILE: {extra}")

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir", metavar="DIR", help="Path to run folder to package")
    group.add_argument("--verify", metavar="ZIP", help="Verify an existing compliance ZIP")

    parser.add_argument(
        "--output", metavar="FILE", help="Output ZIP path (default: auto-named in cwd)"
    )
    parser.add_argument(
        "--norme-dir", default="docs/_norme", help="Normative extracts dir (default: docs/_norme)"
    )
    parser.add_argument("--project-id", default="", help="Project ID override")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.verify:
        zip_path = Path(args.verify)
        if not zip_path.exists():
            print(f"ERROR: File not found: {zip_path}", file=sys.stderr)
            return 1
        print(f"Verifying {zip_path} ...")
        ok, errors = verify_package(zip_path)
        if ok:
            print("✓ Package integrity OK – all hashes match.")
            return 0
        else:
            print(f"✗ Package integrity FAILED – {len(errors)} error(s):", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1

    # Make package
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}", file=sys.stderr)
        return 1

    norme_dir = (
        _ROOT / args.norme_dir if not Path(args.norme_dir).is_absolute() else Path(args.norme_dir)
    )

    if args.output:
        output_path = Path(args.output)
    else:
        ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"compliance_package_{ts}.zip")

    print("=== make_compliance_package ===")
    print(f"Run dir   : {run_dir}")
    print(f"Norme dir : {norme_dir}")
    print(f"Output    : {output_path}")
    print()

    result = make_package(
        run_dir=run_dir,
        output_path=output_path,
        norme_dir=norme_dir if norme_dir.exists() else None,
        project_id=args.project_id,
    )

    print(f"Package created: {result['path']}")
    print(f"Files bundled  : {result['file_count']}")
    print(f"SHA-256        : {result['sha256']}")
    print()
    print("Verify with:")
    print(f"  python tools/make_compliance_package.py --verify {result['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
