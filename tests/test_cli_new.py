"""Tests for the new src/cli.py entry point."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_cli_help(capsys):
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


def test_cli_info(capsys):
    """'rd2229 info' should print version string and return 0."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229", "info"]
    try:
        rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 0
    captured = capsys.readouterr()
    assert "v0.1.0" in captured.out


def test_cli_run_missing_project(capsys):
    """'rd2229 run' without a project file should return 1."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229", "run"]
    try:
        rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 1


def test_cli_export_missing_args(capsys):
    """'rd2229 export' without project and output should return 1."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229", "export"]
    try:
        rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 1


def test_cli_default_command(capsys):
    """Calling rd2229 with no arguments defaults to 'info'."""
    import importlib

    cli = importlib.import_module("src.cli")

    old_argv = sys.argv[:]
    sys.argv = ["rd2229"]
    try:
        rc = cli.main()
    finally:
        sys.argv = old_argv

    assert rc == 0
    captured = capsys.readouterr()
    assert "v0.1.0" in captured.out
