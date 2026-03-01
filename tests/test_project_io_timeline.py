"""Tests for the project IO + schema + timeline/replay MVP.

Covers:
* JSON Schema validation (good / bad examples)
* Roundtrip save/load with model.py helpers
* Migration version handling
* Run → replay idempotence (manifest consistency)
"""

from __future__ import annotations

import json
import os

import pytest

from src.project.model import (
    CURRENT_SCHEMA_VERSION,
    CodeSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel,
    project_to_snapshot,
)
from src.project.repository import load_project, migrate_dict, save_project
from src.project.timeline import (
    compare_manifests,
    create_run,
    load_manifest,
    replay_run,
    sha256_bytes,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_project() -> ProjectModel:
    return ProjectModel(
        project_info=ProjectInfo(
            name="Test",
            description="unit-test project",
            author="pytest",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        ),
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", material_class="C25/30", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0, description="Combo 1")],
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]),
        pipeline_steps=["validate", "checks"],
    )


# =====================================================================
# 1. Schema validation
# =====================================================================


class TestSchemaValidation:
    """JSON Schema validation accepts good inputs and rejects bad ones."""

    def test_valid_project_validates(self):
        """A well-formed ProjectModel dict passes Pydantic validation."""
        data = _minimal_project().model_dump(mode="json")
        project = ProjectModel.model_validate(data)
        assert project.project_info.name == "Test"

    def test_from_dict_roundtrip(self):
        """from_dict(to_dict(m)) produces an equivalent model."""
        original = _minimal_project()
        data = original.to_dict()
        restored = ProjectModel.from_dict(data)
        assert restored.schema_version == original.schema_version
        assert restored.project_info.name == original.project_info.name
        assert len(restored.geometry) == len(original.geometry)

    def test_json_schema_is_dict(self):
        """json_schema_dict() returns a valid dict with $defs."""
        schema = ProjectModel.json_schema_dict()
        assert isinstance(schema, dict)
        assert "$defs" in schema or "properties" in schema

    def test_schema_file_matches_model(self):
        """schemas/project.schema.json matches the model's generated schema."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "schemas", "project.schema.json"
        )
        if not os.path.exists(schema_path):
            pytest.skip("schemas/project.schema.json not found")
        with open(schema_path, encoding="utf-8") as fh:
            on_disk = json.load(fh)
        from_model = ProjectModel.model_json_schema()
        # Compare with sorted keys to ensure determinism
        assert json.dumps(on_disk, sort_keys=True) == json.dumps(from_model, sort_keys=True)


# =====================================================================
# 2. Roundtrip save / load
# =====================================================================


class TestRoundtrip:
    def test_save_load_key_fields(self, tmp_path):
        project = _minimal_project()
        path = str(tmp_path / "project.json")
        save_project(project, path)
        loaded = load_project(path)
        assert loaded.schema_version == project.schema_version
        assert loaded.project_info.name == project.project_info.name
        assert len(loaded.geometry) == 1
        assert loaded.geometry[0].id == "P1"

    def test_snapshot_determinism(self):
        """Two snapshots of the same project must be byte-identical."""
        p = _minimal_project()
        s1 = json.dumps(project_to_snapshot(p), sort_keys=True)
        s2 = json.dumps(project_to_snapshot(p), sort_keys=True)
        assert s1 == s2


# =====================================================================
# 3. Migration version
# =====================================================================


class TestMigration:
    def test_migrate_none_to_current(self):
        data: dict = {}
        migrated = migrate_dict(data)
        assert migrated.get("schema_version") == CURRENT_SCHEMA_VERSION

    def test_migrate_1_0_0_to_current(self):
        data = {"schema_version": "1.0.0"}
        migrated = migrate_dict(data)
        assert migrated["schema_version"] == CURRENT_SCHEMA_VERSION

    def test_already_current_is_noop(self):
        data = {"schema_version": CURRENT_SCHEMA_VERSION}
        migrated = migrate_dict(data)
        assert migrated is data  # same object, no copy


# =====================================================================
# 4. Timeline: RunRecord & hashing
# =====================================================================


class TestTimeline:
    def test_sha256_bytes_deterministic(self):
        h1 = sha256_bytes(b"hello")
        h2 = sha256_bytes(b"hello")
        assert h1 == h2
        assert len(h1) == 64

    def test_create_run_produces_folder(self, tmp_path):
        project = _minimal_project()
        run_dir, record = create_run(project, str(tmp_path), run_id="test_run_001")
        assert os.path.isdir(run_dir)
        assert os.path.isfile(os.path.join(run_dir, "project.snapshot.json"))
        assert os.path.isfile(os.path.join(run_dir, "manifest.json"))
        # One output per pipeline step
        for step in project.pipeline_steps:
            assert os.path.isfile(os.path.join(run_dir, f"output_{step}.json"))

    def test_manifest_fields(self, tmp_path):
        project = _minimal_project()
        _, record = create_run(project, str(tmp_path), run_id="test_run_002")
        assert record.run_id == "test_run_002"
        assert record.schema_version == CURRENT_SCHEMA_VERSION
        assert "RD2229" in record.normative_ids
        assert record.modules_executed == ["validate", "checks"]
        assert "project.snapshot.json" in record.outputs

    def test_manifest_json_loadable(self, tmp_path):
        project = _minimal_project()
        run_dir, _ = create_run(project, str(tmp_path), run_id="test_run_003")
        manifest = load_manifest(run_dir)
        assert manifest["run_id"] == "test_run_003"
        assert "outputs" in manifest


# =====================================================================
# 5. Integration: run → replay idempotent
# =====================================================================


class TestReplayIdempotent:
    def test_replay_identical(self, tmp_path):
        """A replay of a fresh run with the same code must report no drift."""
        project = _minimal_project()
        run_dir, _ = create_run(project, str(tmp_path), run_id="test_run_replay")
        report = replay_run(run_dir, replay_base=str(tmp_path))
        assert report.identical, (
            f"Expected identical replay but got drift: "
            f"missing={report.missing_files}, extra={report.extra_files}, "
            f"hash_mismatches={report.hash_mismatches}, field_diffs={report.field_diffs}"
        )

    def test_replay_detects_tampered_output(self, tmp_path):
        """If an output file is altered, replay must detect the hash mismatch."""
        project = _minimal_project()
        run_dir, _ = create_run(project, str(tmp_path), run_id="test_run_tamper")

        # Tamper with one output file's hash in the manifest
        manifest_path = os.path.join(run_dir, "manifest.json")
        with open(manifest_path, encoding="utf-8") as fh:
            manifest = json.load(fh)
        first_output = next(k for k in manifest["outputs"] if k.startswith("output_"))
        manifest["outputs"][first_output] = "0" * 64  # fake hash
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)

        report = replay_run(run_dir, replay_base=str(tmp_path))
        assert not report.identical
        assert first_output in report.hash_mismatches

    def test_compare_manifests_identical(self):
        m = {"run_id": "r1", "outputs": {"a.json": "abc123"}, "version": "1"}
        report = compare_manifests(m, m)
        assert report.identical

    def test_compare_manifests_drift(self):
        m1 = {"run_id": "r1", "outputs": {"a.json": "aaa"}, "version": "1"}
        m2 = {"run_id": "r2", "outputs": {"a.json": "bbb"}, "version": "1"}
        report = compare_manifests(m1, m2)
        assert not report.identical
        assert "a.json" in report.hash_mismatches


# =====================================================================
# 6. Validate tool (subprocess)
# =====================================================================


class TestValidateTool:
    def test_validate_good_project(self, tmp_path):
        project = _minimal_project()
        path = str(tmp_path / "good.json")
        save_project(project, path)

        import subprocess

        result = subprocess.run(
            ["python", "tools/validate_project.py", path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "VALID" in result.stdout

    def test_validate_bad_project(self, tmp_path):
        path = str(tmp_path / "bad.json")
        # schema_version must be string, give it an int to trigger validation error
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"schema_version": 999, "project_info": {"name": 123}}, fh)

        import subprocess

        result = subprocess.run(
            ["python", "tools/validate_project.py", path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "INVALID" in result.stderr
