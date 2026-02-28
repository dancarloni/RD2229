"""Tests for the centralized logging bridge (src/rd2229/logging_bridge.py)."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from src.rd2229.logging_bridge import (
    get_logger,
    log_info,
    reset_logging,
    setup_logging,
)


@pytest.fixture(autouse=True)
def _clean_logging():
    """Ensure a fresh logging state for each test."""
    reset_logging()
    yield
    reset_logging()


def test_get_logger_returns_child():
    """get_logger() should return a child of the rd2229 root logger."""
    child = get_logger("pipeline")
    assert child.name == "rd2229.pipeline"


def test_setup_logging_console(caplog):
    """After setup_logging(), messages should be logged via the rd2229 logger."""
    setup_logging(level="DEBUG")
    logger = get_logger("test")
    with caplog.at_level(logging.DEBUG, logger="rd2229"):
        logger.debug("hello debug")
    assert "hello debug" in caplog.text


def test_setup_logging_idempotent():
    """Calling setup_logging() twice should NOT add duplicate handlers."""
    setup_logging(level="INFO")
    from src.rd2229.logging_bridge import logger as root

    count_after_first = len(root.handlers)
    setup_logging(level="INFO")
    assert len(root.handlers) == count_after_first


def test_setup_logging_with_file(tmp_path):
    """When enable_file=True, a rotating file handler should be created."""
    setup_logging(level="INFO", enable_file=True, log_dir=tmp_path)
    logger = get_logger("file_test")
    logger.info("file log entry")

    log_file = tmp_path / "rd2229.log"
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "file log entry" in content


def test_reset_logging_clears_handlers():
    """reset_logging() should remove all handlers."""
    setup_logging(level="INFO")
    from src.rd2229.logging_bridge import logger as root

    assert len(root.handlers) > 0
    reset_logging()
    assert len(root.handlers) == 0


def test_log_info_backward_compat(caplog):
    """log_info() backward-compatible helper should work."""
    setup_logging(level="INFO")
    with caplog.at_level(logging.INFO, logger="rd2229"):
        log_info("backward compat message")
    assert "backward compat message" in caplog.text
