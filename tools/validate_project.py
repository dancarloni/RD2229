"""
Validate a project.json file against schemas/project.schema.json.
Exit 0 if valid, 1 if invalid, with clear message.
"""

import json
import pathlib
import sys

import jsonschema


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


if __name__ == "__main__":
    main()
