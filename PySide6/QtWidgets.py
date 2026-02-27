"""Re-export QtWidgets names from PyQt6.QtWidgets for compatibility."""

from PyQt6.QtWidgets import *  # noqa: F401,F403

__all__ = [name for name in dir() if not name.startswith("_")]
