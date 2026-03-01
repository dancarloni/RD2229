"""Centralized logging bridge for the rd2229 project.

Provides ``setup_logging``, ``get_logger`` and ``reset_logging`` so that
every module obtains a child of the ``rd2229`` root logger, handlers are
added idempotently, and propagation to the root logger is disabled.

Usage (in application entry-points)::

    from src.rd2229.logging_bridge import setup_logging, get_logger
    setup_logging("DEBUG")
    logger = get_logger("cli")
    logger.info("ready")

Production code **must not** call ``logging.basicConfig(...)`` directly.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

_ROOT_NAME = "rd2229"

# Sentinel used to guarantee handler idempotency
_HANDLER_ATTR = "_rd2229_bridge_handler"

logger = logging.getLogger(_ROOT_NAME)
logger.propagate = False  # never bubble up to the root logger


def setup_logging(
    level: str = "INFO",
    *,
    enable_file: bool = False,
    log_dir: str | os.PathLike[str] = "logs",
) -> None:
    """Configure the ``rd2229`` root logger (idempotent).

    * Console handler is added only once regardless of how many times
      this function is called.
    * File handler is added only when *enable_file* is ``True`` and only
      once per *log_dir*.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # ---- console handler (idempotent) ----
    if not getattr(logger, _HANDLER_ATTR, False):
        fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        console.setLevel(numeric_level)
        logger.addHandler(console)
        setattr(logger, _HANDLER_ATTR, True)
    else:
        # Update level of existing handlers
        for h in logger.handlers:
            h.setLevel(numeric_level)

    # ---- optional file handler (idempotent) ----
    if enable_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = str(log_path / "rd2229.log")
        # Check if a file handler for this path already exists
        if not any(
            isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(log_file)
            for h in logger.handlers
        ):
            fh = logging.FileHandler(log_file)
            fh.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
            fh.setLevel(numeric_level)
            logger.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``rd2229`` namespace.

    Example: ``get_logger("cli")`` → logger named ``rd2229.cli``.
    """
    child = logger.getChild(name)
    child.propagate = True  # propagate to rd2229, but rd2229 won't propagate further
    return child


def reset_logging() -> None:
    """Remove all handlers from the root ``rd2229`` logger (for testing)."""
    logger.handlers.clear()
    setattr(logger, _HANDLER_ATTR, False)


def log_info(msg: str) -> None:
    """Legacy convenience wrapper."""
    logger.info(msg)
