<<<<<<< HEAD
"""
Validate a project.json file against schemas/project.schema.json.
Exit 0 if valid, 1 if invalid, with clear message.
"""

import json
import pathlib
=======
#!/usr/bin/env python3
"""Validate a project JSON file against the ProjectModel schema.

Usage::

    python tools/validate_project.py path/to/project.json

Exit codes:
    0 – valid
    1 – invalid (prints errors to stderr)
"""

from __future__ import annotations

import json
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))
import sys

import jsonschema

<<<<<<< HEAD

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_project.py <project.json>", file=sys.stderr)
        sys.exit(1)
    project_path = pathlib.Path(sys.argv[1])
    schema_path = pathlib.Path(__file__).parent.parent / "schemas" / "project.schema.json"
    with open(project_path, encoding="utf-8") as f:
        data = json.load(f)
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        print(f"INVALID: {e.message}", file=sys.stderr)
        sys.exit(1)
    print("VALID")
    sys.exit(0)
=======
from src.project.schema import ProjectModel


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
        print(f"INVALID – {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  • {err}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"VALID – {path}")
        sys.exit(0)
>>>>>>> 101a292 (feat: project IO + schema + timeline/replay MVP (sub-issue 01))


if __name__ == "__main__":
    main()
