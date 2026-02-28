"""Centralized logging bridge for RD2229.

Provides a single configuration point for all RD2229 logging:

* Console handler (``stderr``) with configurable level.
* Optional rotating-file handler writing to ``logs/rd2229.log``.
* Consistent format: ``%(asctime)s | %(name)s | %(levelname)s | %(message)s``.

Usage::

    from src.rd2229.logging_bridge import setup_logging, get_logger

    setup_logging(level="DEBUG", enable_file=True)
    logger = get_logger("my_module")
    logger.info("Pipeline started")
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_ROOT_LOGGER_NAME = "rd2229"
_DEFAULT_LOG_DIR = "logs"
_DEFAULT_LOG_FILE = "rd2229.log"
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_BACKUP_COUNT = 3

logger = logging.getLogger(_ROOT_LOGGER_NAME)

_setup_done = False


def setup_logging(
    *,
    level: str = "INFO",
    enable_file: bool = False,
    log_dir: str | Path | None = None,
) -> None:
    """Configure the ``rd2229`` root logger.

    Calling this function more than once is safe — subsequent calls are
    no-ops unless the module-level ``_setup_done`` flag is reset (useful
    in tests via :func:`reset_logging`).

    Args:
        level: Logging level name (``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``).
        enable_file: If *True*, attach a ``RotatingFileHandler`` that writes
            to ``<log_dir>/rd2229.log``.
        log_dir: Directory for log files.  Defaults to ``logs/`` relative to
            the current working directory.
    """
    global _setup_done
    if _setup_done:
        return

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(numeric_level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Optional rotating file handler
    if enable_file:
        resolved_dir = Path(log_dir) if log_dir else Path(_DEFAULT_LOG_DIR)
        resolved_dir.mkdir(parents=True, exist_ok=True)
        log_path = resolved_dir / _DEFAULT_LOG_FILE
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _setup_done = True


def reset_logging() -> None:
    """Remove all handlers and reset state.  Intended for tests."""
    global _setup_done
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    _setup_done = False


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``rd2229`` namespace.

    Example::

        logger = get_logger("pipeline")
        # -> logging.getLogger("rd2229.pipeline")
    """
    return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")


# Backward-compatible helper
def log_info(msg: str) -> None:
    """Log an INFO message on the root rd2229 logger."""
    logger.info(msg)
