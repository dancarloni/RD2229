"""Tests for the src.cli package entry point."""

from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path

import pytest

pytest.importorskip("pydantic")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _restore_argv():
    """Ensure sys.argv is restored after every test."""
    original = sys.argv[:]
    yield
    sys.argv = original


def _get_cli():
    return importlib.import_module("src.cli")


def test_cli_help(capsys):
    """rd2229 --help should print usage and return 0."""
    cli = _get_cli()
    sys.argv = ["rd2229", "--help"]
    try:
        rc = cli.main()
    except SystemExit as exc:
        rc = exc.code
    assert rc == 0


def test_cli_info(capsys, caplog):
    """'rd2229 info' should print version string and return 0."""
    cli = _get_cli()
    sys.argv = ["rd2229", "info"]
    with caplog.at_level(logging.DEBUG, logger="rd2229"):
        rc = cli.main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "v0.1.0" in captured.out


def test_cli_run_missing_project(capsys, caplog):
    """'rd2229 run' without a project file should return non-zero."""
    cli = _get_cli()
    sys.argv = ["rd2229", "run"]
    with caplog.at_level(logging.DEBUG, logger="rd2229"):
        rc = cli.main()
    assert rc != 0


def test_cli_export_missing_args(capsys, caplog):
    """'rd2229 export' without project and output should return non-zero."""
    cli = _get_cli()
    sys.argv = ["rd2229", "export"]
    with caplog.at_level(logging.DEBUG, logger="rd2229"):
        rc = cli.main()
    assert rc != 0


def test_cli_default_command(capsys, caplog):
    """Calling rd2229 with no arguments defaults to 'info'."""
    cli = _get_cli()
    sys.argv = ["rd2229"]
    with caplog.at_level(logging.DEBUG, logger="rd2229"):
        rc = cli.main()
    assert rc == 0
    captured = capsys.readouterr()
    assert "v0.1.0" in captured.out
