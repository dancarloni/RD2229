"""Tests for tools/fetch_norma.py – Normative Fetcher."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.fetch_norma import (
    _extracts_dir,
    add_extract,
    init_norm,
    list_norms,
    load_metadata,
    main,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def nd(tmp_path) -> Path:
    """Return a temporary norme_dir for isolated tests."""
    return tmp_path / "norme"


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


class TestInitNorm:
    def test_creates_directory_and_metadata(self, nd):
        meta = init_norm("NTC2018", norme_dir=nd)
        assert (nd / "NTC2018").is_dir()
        assert (nd / "NTC2018" / "metadata.json").exists()
        assert meta["norm_id"] == "NTC2018"
        assert meta["title"]  # non-empty title

    def test_known_norm_gets_title(self, nd):
        meta = init_norm("RD2229", norme_dir=nd)
        assert "Regio Decreto" in meta["title"]

    def test_unknown_norm_uses_id_as_title(self, nd):
        meta = init_norm("CUSTOM_NORM_XYZ", norme_dir=nd)
        assert meta["title"] == "CUSTOM_NORM_XYZ"

    def test_idempotent_repeated_calls(self, nd):
        init_norm("NTC2018", norme_dir=nd)
        init_norm("NTC2018", norme_dir=nd)  # second call should not fail
        meta = load_metadata("NTC2018", norme_dir=nd)
        assert meta["norm_id"] == "NTC2018"

    def test_records_source_url(self, nd):
        meta = init_norm("NTC2018", source_url="https://example.com/ntc.pdf", norme_dir=nd)
        assert meta["source_url"] == "https://example.com/ntc.pdf"

    def test_registers_local_source_file(self, tmp_path, nd):
        local = tmp_path / "doc.pdf"
        local.write_bytes(b"fake pdf content")
        meta = init_norm("NTC2018", source_path=str(local), norme_dir=nd)
        assert len(meta["source_files"]) == 1
        assert meta["source_files"][0]["sha256"]  # sha256 computed


class TestAddExtract:
    def test_creates_extract_file(self, nd):
        init_norm("NTC2018", norme_dir=nd)
        ep = add_extract("NTC2018", "4.1.2.1", "Testo dell'articolo 4.1.2.1", norme_dir=nd)
        assert ep.exists()
        content = ep.read_text(encoding="utf-8")
        assert "NTC2018" in content
        assert "4.1.2.1" in content

    def test_clause_filename_conversion(self, nd):
        init_norm("RD2229", norme_dir=nd)
        ep = add_extract("RD2229", "art.1", "Testo art. 1", norme_dir=nd)
        assert "art_1" in ep.name

    def test_updates_metadata_clauses(self, nd):
        init_norm("NTC2018", norme_dir=nd)
        add_extract("NTC2018", "4.1", "Testo A", norme_dir=nd)
        add_extract("NTC2018", "4.2", "Testo B", norme_dir=nd)
        meta = load_metadata("NTC2018", norme_dir=nd)
        clause_ids = {c["id"] for c in meta["clauses"]}
        assert "4.1" in clause_ids
        assert "4.2" in clause_ids


class TestListNorms:
    def test_empty_when_no_norms(self, nd):
        result = list_norms(nd)
        assert result == []

    def test_lists_registered_norms(self, nd):
        init_norm("NTC2018", norme_dir=nd)
        init_norm("RD2229", norme_dir=nd)
        result = list_norms(nd)
        ids = [r["norm_id"] for r in result]
        assert "NTC2018" in ids
        assert "RD2229" in ids


class TestCLI:
    def test_cli_list_empty(self, nd, capsys):
        ret = main(["--list", "--norme-dir", str(nd)])
        assert ret == 0

    def test_cli_norm_init(self, nd):
        ret = main(["--norm", "NTC2018", "--norme-dir", str(nd)])
        assert ret == 0
        assert load_metadata("NTC2018", norme_dir=nd)

    def test_cli_add_extract(self, nd, tmp_path):
        text_file = tmp_path / "clause.txt"
        text_file.write_text("Il calcestruzzo deve rispettare le prescrizioni.", encoding="utf-8")
        ret = main(
            [
                "--norm",
                "NTC2018",
                "--add-extract",
                "4.1.2.1",
                "--text-file",
                str(text_file),
                "--norme-dir",
                str(nd),
            ]
        )
        assert ret == 0
        ep = _extracts_dir("NTC2018", norme_dir=nd) / "4_1_2_1.md"
        assert ep.exists()

    def test_cli_show_missing_norm(self, nd, capsys):
        ret = main(["--show", "NONEXISTENT", "--norme-dir", str(nd)])
        assert ret == 1

    def test_cli_no_args(self, nd, capsys):
        ret = main([])
        assert ret == 1
