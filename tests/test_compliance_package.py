"""Tests for tools/make_compliance_package.py and updated calc_output_to_dict."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.make_compliance_package import (
    make_package,
    sha256_bytes,
    verify_package,
    main as compliance_main,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_run_dir(tmp_path: Path) -> Path:
    """Create a minimal fake run directory."""
    run_dir = tmp_path / "projects" / "test_proj" / "runs" / "run_20260101_120000_abc1234"
    run_dir.mkdir(parents=True)
    # Snapshot
    snapshot = {"project_id": "test_proj", "norm_code": "NTC2018"}
    (run_dir / "project.snapshot.json").write_text(json.dumps(snapshot), encoding="utf-8")
    # Output
    output = {"element_name": "B1", "ok": True, "norm_code": "NTC2018"}
    (run_dir / "output_checks.json").write_text(json.dumps(output), encoding="utf-8")
    # Run record
    record = {
        "run_id": "run_20260101_120000_abc1234",
        "normative_ids": ["NTC2018"],
        "commit_hash": "abc1234",
        "python_version": "3.12",
        "modules_executed": ["validate"],
    }
    (run_dir / "run_record.json").write_text(json.dumps(record), encoding="utf-8")
    return run_dir


def _make_norme_dir(tmp_path: Path) -> Path:
    """Create a minimal normative extracts directory."""
    nd = tmp_path / "norme" / "NTC2018"
    extracts = nd / "extracts"
    extracts.mkdir(parents=True)
    (nd / "metadata.json").write_text(
        json.dumps({"norm_id": "NTC2018", "title": "NTC 2018", "clauses": []}),
        encoding="utf-8",
    )
    (extracts / "4_1_2_1.md").write_text("# NTC2018 – 4.1.2.1\n\nTesto estratto.", encoding="utf-8")
    return tmp_path / "norme"


# ---------------------------------------------------------------------------
# make_package tests
# ---------------------------------------------------------------------------


class TestMakePackage:
    def test_creates_zip(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "pkg.zip"
        result = make_package(run_dir, out)
        assert out.exists()
        assert result["sha256"]
        assert result["file_count"] >= 3

    def test_zip_contains_manifest(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "pkg.zip"
        make_package(run_dir, out)
        with zipfile.ZipFile(out) as zf:
            assert "manifest.json" in zf.namelist()
            assert "README.txt" in zf.namelist()

    def test_manifest_has_norm_ids(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "pkg.zip"
        result = make_package(run_dir, out)
        assert "NTC2018" in result["manifest"]["norm_ids"]

    def test_includes_norm_extracts(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        norme_dir = _make_norme_dir(tmp_path)
        out = tmp_path / "pkg_with_norms.zip"
        make_package(run_dir, out, norme_dir=norme_dir)
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
        assert any("extracts" in n for n in names)

    def test_project_id_inferred_from_path(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "pkg.zip"
        result = make_package(run_dir, out)
        assert result["manifest"]["project_id"] == "test_proj"

    def test_explicit_project_id(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "pkg.zip"
        result = make_package(run_dir, out, project_id="explicit_proj")
        assert result["manifest"]["project_id"] == "explicit_proj"

    def test_sha256_deterministic(self, tmp_path):
        """Same content produces the same hash."""
        data = b"test data"
        h1 = sha256_bytes(data)
        h2 = sha256_bytes(data)
        assert h1 == h2


# ---------------------------------------------------------------------------
# verify_package tests
# ---------------------------------------------------------------------------


class TestVerifyPackage:
    def test_valid_package_passes(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "pkg.zip"
        make_package(run_dir, out)
        ok, errors = verify_package(out)
        assert ok, f"Unexpected errors: {errors}"
        assert errors == []

    def test_tampered_file_fails(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "pkg.zip"
        make_package(run_dir, out)

        # Tamper: add a file or modify content
        import io as _io
        buf = _io.BytesIO(out.read_bytes())
        with zipfile.ZipFile(buf, "a") as zf:
            zf.writestr("outputs/output_checks.json", b'{"tampered": true}')
        out.write_bytes(buf.getvalue())

        ok, errors = verify_package(out)
        assert not ok
        assert len(errors) > 0

    def test_missing_manifest_fails(self, tmp_path):
        # Create a zip without manifest.json
        out = tmp_path / "no_manifest.zip"
        with zipfile.ZipFile(out, "w") as zf:
            zf.writestr("README.txt", b"hello")
        ok, errors = verify_package(out)
        assert not ok
        assert any("manifest" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestComplianceCLI:
    def test_cli_make_package(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "cli_pkg.zip"
        ret = compliance_main(["--run-dir", str(run_dir), "--output", str(out)])
        assert ret == 0
        assert out.exists()

    def test_cli_verify_valid(self, tmp_path):
        run_dir = _make_run_dir(tmp_path)
        out = tmp_path / "cli_verify.zip"
        compliance_main(["--run-dir", str(run_dir), "--output", str(out)])
        ret = compliance_main(["--verify", str(out)])
        assert ret == 0

    def test_cli_missing_run_dir(self, tmp_path, capsys):
        ret = compliance_main(["--run-dir", str(tmp_path / "nonexistent")])
        assert ret == 1

    def test_cli_verify_nonexistent(self, tmp_path, capsys):
        ret = compliance_main(["--verify", str(tmp_path / "nonexistent.zip")])
        assert ret == 1


# ---------------------------------------------------------------------------
# calc_output_to_dict metadata tests
# ---------------------------------------------------------------------------


class TestCalcOutputToDictMetadata:
    def _make_output(self):
        """Create a minimal CalcOutput for testing."""
        from src.core_calculus.contracts import CalcInput, CalcOutput, ElementRole
        from src.core_calculus.core.verifier_manager import VerifierManager

        class MockSection:
            width = 0.3
            height = 0.5
            area = 0.15
            label = "rect_300x500"

        class MockMaterial:
            fck = 25.0
            fyk = 450.0
            label = "C25/30"
            gamma_c = 1.5
            gamma_s = 1.15

        ci = CalcInput(
            element_name="Test_B1",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=30.0,
            As=400.0,
            d=440.0,
            element_role=ElementRole.PRIMARY,
        )
        vm = VerifierManager()
        return vm.verify(ci)

    def test_metadata_included_by_default(self):
        from src.core_calculus.core.verifier_manager import calc_output_to_dict

        output = self._make_output()
        d = calc_output_to_dict(output)
        assert "metadata" in d
        assert d["metadata"]["schema_version"] == "1.0"
        assert d["metadata"]["tool"] == "calc_output_to_dict"
        assert "generated" in d["metadata"]

    def test_metadata_can_be_excluded(self):
        from src.core_calculus.core.verifier_manager import calc_output_to_dict

        output = self._make_output()
        d = calc_output_to_dict(output, include_metadata=False)
        assert "metadata" not in d

    def test_extra_metadata_merged(self):
        from src.core_calculus.core.verifier_manager import calc_output_to_dict

        output = self._make_output()
        d = calc_output_to_dict(output, metadata={"project_id": "proj_1", "run_id": "run_abc"})
        assert d["metadata"]["project_id"] == "proj_1"
        assert d["metadata"]["run_id"] == "run_abc"

    def test_existing_fields_preserved(self):
        from src.core_calculus.core.verifier_manager import calc_output_to_dict

        output = self._make_output()
        d = calc_output_to_dict(output)
        # Original fields still present
        assert "element_name" in d
        assert "norm_code" in d
        assert "ok" in d
        assert "checks" in d

    def test_json_serializable(self):
        from src.core_calculus.core.verifier_manager import calc_output_to_dict

        output = self._make_output()
        d = calc_output_to_dict(output)
        json_str = json.dumps(d, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["metadata"]["schema_version"] == "1.0"
