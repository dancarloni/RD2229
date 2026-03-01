import json
import pathlib

import jsonschema
import pytest

PROJECT_SCHEMA = pathlib.Path(__file__).parent.parent / "schemas" / "project.schema.json"
VALID_PROJECT = {
    "meta": {
        "id": "proj1",
        "name": "Test Project",
        "created_at": "2026-03-01T00:00:00Z",
        "updated_at": "2026-03-01T00:00:00Z",
        "commit_hash": "abc123",
        "schema_version": "1.0.0",
    },
    "normative_profile": {"source_ids": ["RD2229"], "clauses": ["§4.2.1"]},
    "modules": [{"name": "mod1", "enabled": True, "params": {}}],
    "io_settings": {},
}
INVALID_PROJECT = {"meta": {}, "normative_profile": {}, "modules": [], "io_settings": {}}


def test_valid_project_schema():
    with open(PROJECT_SCHEMA, encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=VALID_PROJECT, schema=schema)


def test_invalid_project_schema():
    with open(PROJECT_SCHEMA, encoding="utf-8") as f:
        schema = json.load(f)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=INVALID_PROJECT, schema=schema)
