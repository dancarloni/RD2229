#!/usr/bin/env python3
"""Validate a project JSON file against the ProjectModel schema.

Usage::

    python tools/validate_project.py path/to/project.json

Exit codes:
    0 -- valid
    1 -- invalid (prints errors to stderr)
"""

from __future__ import annotations

import json
import pathlib
import sys

# Ensure project root is importable regardless of how the script is invoked.
_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import jsonschema  # noqa: E402

from src.project.schema import ProjectModel  # noqa: E402


def validate(path: str) -> list[str]:
    """Return a list of validation error messages (empty == valid)."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    schema = ProjectModel.model_json_schema()
    validator = jsonschema.Draft202012Validator(schema)
    return [e.message for e in validator.iter_errors(data)]


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: validate_project.py <project.json>", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    errors = validate(path)
    if errors:
        print(f"INVALID -- {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  * {err}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"VALID -- {path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
