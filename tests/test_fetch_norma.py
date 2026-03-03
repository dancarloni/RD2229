"""Tests for tools/fetch_norma.py – Normative Fetcher."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.fetch_norma import (
    _norm_dir,
    _NORME_DIR,
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
def isolated_norme_dir(tmp_path, monkeypatch):
    """Redirect all fetch_norma globals to a temp directory."""
    import tools.fetch_norma as fn_mod

    monkeypatch.setattr(fn_mod, "_NORME_DIR", tmp_path / "norme")
    return tmp_path / "norme"


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


class TestInitNorm:
    def test_creates_directory_and_metadata(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        meta = fn_mod.init_norm("NTC2018")
        assert (isolated_norme_dir / "NTC2018").is_dir()
        assert (isolated_norme_dir / "NTC2018" / "metadata.json").exists()
        assert meta["norm_id"] == "NTC2018"
        assert meta["title"]  # non-empty title

    def test_known_norm_gets_title(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        meta = fn_mod.init_norm("RD2229")
        assert "Regio Decreto" in meta["title"]

    def test_unknown_norm_uses_id_as_title(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        meta = fn_mod.init_norm("CUSTOM_NORM_XYZ")
        assert meta["title"] == "CUSTOM_NORM_XYZ"

    def test_idempotent_repeated_calls(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        fn_mod.init_norm("NTC2018")
        fn_mod.init_norm("NTC2018")  # second call should not fail
        meta = fn_mod.load_metadata("NTC2018")
        assert meta["norm_id"] == "NTC2018"

    def test_records_source_url(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        meta = fn_mod.init_norm("NTC2018", source_url="https://example.com/ntc.pdf")
        assert meta["source_url"] == "https://example.com/ntc.pdf"

    def test_registers_local_source_file(self, tmp_path, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        local = tmp_path / "doc.pdf"
        local.write_bytes(b"fake pdf content")
        meta = fn_mod.init_norm("NTC2018", source_path=str(local))
        assert len(meta["source_files"]) == 1
        assert meta["source_files"][0]["sha256"]  # sha256 computed


class TestAddExtract:
    def test_creates_extract_file(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        fn_mod.init_norm("NTC2018")
        ep = fn_mod.add_extract("NTC2018", "4.1.2.1", "Testo dell'articolo 4.1.2.1")
        assert ep.exists()
        content = ep.read_text(encoding="utf-8")
        assert "NTC2018" in content
        assert "4.1.2.1" in content

    def test_clause_filename_conversion(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        fn_mod.init_norm("RD2229")
        ep = fn_mod.add_extract("RD2229", "art.1", "Testo art. 1")
        assert "art_1" in ep.name

    def test_updates_metadata_clauses(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        fn_mod.init_norm("NTC2018")
        fn_mod.add_extract("NTC2018", "4.1", "Testo A")
        fn_mod.add_extract("NTC2018", "4.2", "Testo B")
        meta = fn_mod.load_metadata("NTC2018")
        clause_ids = {c["id"] for c in meta["clauses"]}
        assert "4.1" in clause_ids
        assert "4.2" in clause_ids


class TestListNorms:
    def test_empty_when_no_norms(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        result = fn_mod.list_norms()
        assert result == []

    def test_lists_registered_norms(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        fn_mod.init_norm("NTC2018")
        fn_mod.init_norm("RD2229")
        result = fn_mod.list_norms()
        ids = [r["norm_id"] for r in result]
        assert "NTC2018" in ids
        assert "RD2229" in ids


class TestCLI:
    def test_cli_list_empty(self, isolated_norme_dir, capsys):
        import tools.fetch_norma as fn_mod

        ret = fn_mod.main(["--list"])
        assert ret == 0

    def test_cli_norm_init(self, isolated_norme_dir):
        import tools.fetch_norma as fn_mod

        ret = fn_mod.main(["--norm", "NTC2018"])
        assert ret == 0
        assert fn_mod.load_metadata("NTC2018")

    def test_cli_add_extract(self, isolated_norme_dir, tmp_path):
        import tools.fetch_norma as fn_mod

        text_file = tmp_path / "clause.txt"
        text_file.write_text("Il calcestruzzo deve rispettare le prescrizioni.", encoding="utf-8")
        ret = fn_mod.main(["--norm", "NTC2018", "--add-extract", "4.1.2.1", "--text-file", str(text_file)])
        assert ret == 0
        ep = fn_mod._extracts_dir("NTC2018") / "4_1_2_1.md"
        assert ep.exists()

    def test_cli_show_missing_norm(self, isolated_norme_dir, capsys):
        import tools.fetch_norma as fn_mod

        ret = fn_mod.main(["--show", "NONEXISTENT"])
        assert ret == 1

    def test_cli_no_args(self, isolated_norme_dir, capsys):
        import tools.fetch_norma as fn_mod

        ret = fn_mod.main([])
        assert ret == 1
