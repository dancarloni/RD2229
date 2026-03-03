"""Tests for tools/generate_rtm.py – RTM generator."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.generate_rtm import (
    compute_coverage,
    scan_doc_evidence,
    scan_norm_extracts,
    scan_src_evidence,
    scan_test_evidence,
    write_coverage_md,
    write_csv,
    write_json,
    main as rtm_main,
    NORM_ALIASES,
)


@pytest.fixture()
def sample_norme_dir(tmp_path):
    """Create a minimal normative extracts directory."""
    nd = tmp_path / "norme" / "NTC2018"
    extracts = nd / "extracts"
    extracts.mkdir(parents=True)
    (nd / "metadata.json").write_text(
        json.dumps({"norm_id": "NTC2018", "title": "NTC 2018", "clauses": [{"id": "4.1.2.1", "file": "extracts/4_1_2_1.md"}]}),
        encoding="utf-8",
    )
    (extracts / "4_1_2_1.md").write_text("# NTC2018 – 4.1.2.1\n\nTesto.", encoding="utf-8")
    return tmp_path / "norme"


@pytest.fixture()
def sample_src_dir(tmp_path):
    """Create a minimal src directory with normative references."""
    src = tmp_path / "src"
    mod = src / "my_module"
    mod.mkdir(parents=True)
    (mod / "__init__.py").write_text("")
    (mod / "ntc_checks.py").write_text(
        "# NTC2018 checks\ndef verify_slu(section, material):\n    pass\n"
    )
    (mod / "rd2229_checks.py").write_text(
        "# RD2229 reinforcement\ndef check_steel(As):\n    pass\n"
    )
    return src


@pytest.fixture()
def sample_tests_dir(tmp_path):
    """Create a minimal tests directory."""
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_ntc.py").write_text(
        "# NTC2018 test\ndef test_slu_flessione():\n    pass\ndef test_slu_taglio():\n    pass\n"
    )
    return tests


class TestScanNormExtracts:
    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty_norme"
        empty.mkdir()
        result = scan_norm_extracts(empty)
        assert result == {}

    def test_nonexistent_dir(self, tmp_path):
        result = scan_norm_extracts(tmp_path / "nonexistent")
        assert result == {}

    def test_scans_registered_norms(self, sample_norme_dir):
        result = scan_norm_extracts(sample_norme_dir)
        assert "NTC2018" in result
        assert result["NTC2018"]["has_metadata"] is True
        assert result["NTC2018"]["extract_count"] == 1


class TestScanSrcEvidence:
    def test_finds_ntc2018_references(self, sample_src_dir):
        result = scan_src_evidence(sample_src_dir)
        assert len(result["NTC2018"]["modules"]) >= 1

    def test_finds_rd2229_references(self, sample_src_dir):
        result = scan_src_evidence(sample_src_dir)
        assert len(result["RD2229"]["modules"]) >= 1

    def test_no_legacy_included(self, tmp_path):
        src = tmp_path / "src"
        legacy = src / "legacy"
        legacy.mkdir(parents=True)
        (legacy / "old.py").write_text("# NTC2018 reference\ndef old():\n    pass\n")
        result = scan_src_evidence(src)
        # Legacy files should be excluded
        for modules in result["NTC2018"]["modules"]:
            assert "legacy" not in modules


class TestScanTestEvidence:
    def test_finds_ntc_tests(self, sample_tests_dir):
        result = scan_test_evidence(sample_tests_dir)
        assert len(result["NTC2018"]["test_files"]) >= 1
        assert result["NTC2018"]["test_function_count"] >= 2


class TestComputeCoverage:
    def test_full_evidence_100_pct(self):
        norme = {"NTC2018": {"has_metadata": True, "title": "NTC 2018", "clauses": [], "extract_files": ["x.md"], "extract_count": 1}}
        src_ev = {"NTC2018": {"modules": ["src/a.py"], "function_count": 5, "stub_count": 0}}
        test_ev = {"NTC2018": {"test_files": ["tests/t.py"], "test_function_count": 2}}
        doc_ev = {"NTC2018": ["docs/ntc.md"]}
        rows = compute_coverage(norme, src_ev, test_ev, doc_ev)
        ntc_row = next(r for r in rows if r["norm_id"] == "NTC2018")
        assert ntc_row["coverage_pct"] == 100
        assert ntc_row["gaps"] == []

    def test_no_evidence_0_pct(self):
        norme = {}
        src_ev = {"NTC2018": {"modules": [], "function_count": 0, "stub_count": 0}}
        test_ev = {"NTC2018": {"test_files": [], "test_function_count": 0}}
        doc_ev = {"NTC2018": []}
        rows = compute_coverage(norme, src_ev, test_ev, doc_ev)
        ntc_row = next((r for r in rows if r["norm_id"] == "NTC2018"), None)
        if ntc_row:
            assert ntc_row["coverage_pct"] == 0
            assert len(ntc_row["gaps"]) >= 3

    def test_gaps_identified(self):
        norme = {}
        src_ev = {"RD2229": {"modules": ["src/x.py"], "function_count": 2, "stub_count": 0}}
        test_ev = {"RD2229": {"test_files": [], "test_function_count": 0}}
        doc_ev = {"RD2229": []}
        rows = compute_coverage(norme, src_ev, test_ev, doc_ev)
        rd_row = next(r for r in rows if r["norm_id"] == "RD2229")
        assert "no_tests" in rd_row["gaps"]
        assert "no_normative_extract" in rd_row["gaps"]


class TestOutputWriters:
    def test_write_csv(self, tmp_path):
        rows = [
            {"norm_id": "NTC2018", "title": "NTC 2018", "coverage_pct": 75,
             "has_extract": True, "extract_count": 2, "has_src": True,
             "src_module_count": 3, "src_function_count": 20, "stub_count": 0,
             "has_tests": True, "test_file_count": 2, "test_function_count": 8,
             "has_docs": False, "doc_file_count": 0, "gaps": ["no_documentation"]}
        ]
        path = tmp_path / "rtm.csv"
        import tools.generate_rtm as grtm
        orig = grtm._ROOT
        grtm._ROOT = tmp_path
        try:
            write_csv(rows, path)
        finally:
            grtm._ROOT = orig
        assert path.exists()
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            data = list(reader)
        assert len(data) == 1
        assert data[0]["norm_id"] == "NTC2018"
        assert data[0]["coverage_pct"] == "75"

    def test_write_json(self, tmp_path):
        rows = [{"norm_id": "RD2229", "coverage_pct": 50, "gaps": []}]
        path = tmp_path / "rtm.json"
        import tools.generate_rtm as grtm
        orig = grtm._ROOT
        grtm._ROOT = tmp_path
        try:
            write_json(rows, path, {}, {}, {})
        finally:
            grtm._ROOT = orig
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["norm_count"] == 1

    def test_write_coverage_md(self, tmp_path):
        rows = [{"norm_id": "NTC2018", "title": "NTC 2018", "coverage_pct": 100,
                 "has_extract": True, "extract_count": 1, "has_src": True,
                 "src_module_count": 2, "src_function_count": 5, "stub_count": 0,
                 "has_tests": True, "test_file_count": 1, "test_function_count": 3,
                 "has_docs": True, "doc_file_count": 1, "gaps": [],
                 "src_modules": [], "test_files": [], "doc_files": [], "extract_files": []}]
        path = tmp_path / "rtm_coverage.md"
        import tools.generate_rtm as grtm
        orig = grtm._ROOT
        grtm._ROOT = tmp_path
        try:
            write_coverage_md(rows, path)
        finally:
            grtm._ROOT = orig
        assert path.exists()
        content = path.read_text()
        assert "NTC2018" in content
        assert "100%" in content


class TestRTMCLI:
    def test_cli_runs_on_actual_repo(self, tmp_path):
        """Run generate_rtm on the actual repo (smoke test)."""
        ret = rtm_main([
            "--output-dir", str(tmp_path / "RTM"),
            "--csv", str(tmp_path / "rtm.csv"),
            "--json", str(tmp_path / "rtm.json"),
            "--md", str(tmp_path / "rtm_coverage.md"),
            "--norme-dir", str(tmp_path / "norme"),  # empty, OK
        ])
        assert ret == 0
        assert (tmp_path / "rtm.csv").exists()
        assert (tmp_path / "rtm.json").exists()
        assert (tmp_path / "rtm_coverage.md").exists()
