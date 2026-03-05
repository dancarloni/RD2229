#!/usr/bin/env python3
"""Run a project: create a run folder with snapshot, manifest, and outputs.

Usage::

    python tools/run_project.py path/to/project.json
"""

from __future__ import annotations

import json
import pathlib
import sys

# Ensure project root is importable regardless of how the script is invoked.
_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.project.model import ProjectModel  # noqa: E402
from src.project.timeline import create_run  # noqa: E402


def _sanitize_id(val: str) -> str:
    import re

    return re.sub(r"[^a-zA-Z0-9_-]+", "_", val.strip()) if val else ""


def _get_project_id(project: object, input_path: pathlib.Path) -> str:
    try:
        if input_path.exists():
            with open(input_path, encoding="utf-8") as rf:
                raw = json.load(rf)
            if isinstance(raw, dict):
                meta_raw = raw.get("meta") or raw.get("project_info")
                if isinstance(meta_raw, dict):
                    raw_id = meta_raw.get("id")
                    if raw_id:
                        return _sanitize_id(str(raw_id))
                    raw_name = meta_raw.get("name")
                    if raw_name:
                        return _sanitize_id(str(raw_name))
    except Exception:
        pass
    meta = getattr(project, "meta", None)
    if meta is not None:
        pid = getattr(meta, "id", None)
        if pid:
            return _sanitize_id(str(pid))
        pname = getattr(meta, "name", None)
        if pname:
            return _sanitize_id(str(pname))
    if hasattr(project, "project_info"):
        pi = project.project_info  # type: ignore[attr-defined]
        pi_name = getattr(pi, "name", None)
        if pi_name:
            return _sanitize_id(str(pi_name))
    if input_path.stem:
        return _sanitize_id(input_path.stem)
    return "unknown"


def main() -> None:
    try:
        if len(sys.argv) < 2:
            print("Usage: run_project.py <project.json>", file=sys.stderr)
            sys.exit(1)

        project_path = pathlib.Path(sys.argv[1])
        with open(project_path, encoding="utf-8") as _f:
            _data = json.load(_f)
        project = ProjectModel.model_validate(_data)
        project_id = _get_project_id(project, project_path)

        # Detect pytest temp dirs and write beside the project file instead of cwd.
        if project_path.is_absolute() and any(
            part.startswith("pytest-") or part.startswith("tmp") for part in project_path.parts
        ):
            runs_base = project_path.parent / "projects" / project_id / "runs"
        else:
            runs_base = pathlib.Path("projects") / project_id / "runs"

        run_dir, record = create_run(project, str(runs_base))
        print(f"Run complete: {run_dir}")
    except Exception as exc:
        import traceback

        print(f"[run_project.py] Exception: {exc}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
