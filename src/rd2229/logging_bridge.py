"""Simple logging bridge to centralize UI <-> core logging.

Provides an adapter to Python's logging module for later integration.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("rd2229")


def log_info(msg: str) -> None:
    logger.info(msg)
