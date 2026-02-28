"""Tests for the new src/cli.py entry point."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _reset_logging():
    """Reset centralized logging between tests."""
    from src.rd2229.logging_bridge import reset_logging

    reset_logging()
    yield
    reset_logging()


def test_cli_help():
    """rd2229 --help should print usage and exit 0."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229", "--help"]
    try:
        cli.main()
    except SystemExit as exc:
        assert exc.code == 0
    finally:
        sys.argv = old_argv


def test_cli_info(caplog):
    """'rd2229 info' should log version string and return 0."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229", "info"]
    try:
        with caplog.at_level(logging.INFO, logger="rd2229"):
            rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 0
    assert "v0.1.0" in caplog.text


def test_cli_run_missing_project(caplog):
    """'rd2229 run' without a project file should return 1."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229", "run"]
    try:
        with caplog.at_level(logging.ERROR, logger="rd2229"):
            rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 1


def test_cli_export_missing_args(caplog):
    """'rd2229 export' without project and output should return 1."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229", "export"]
    try:
        with caplog.at_level(logging.ERROR, logger="rd2229"):
            rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 1


def test_cli_default_command(caplog):
    """Calling rd2229 with no arguments defaults to 'info'."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229"]
    try:
        with caplog.at_level(logging.INFO, logger="rd2229"):
            rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 0
    assert "v0.1.0" in caplog.text
