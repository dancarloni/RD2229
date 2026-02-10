"""
Bootstrap module for RD2229 application.
Orchestrates discovery, configuration, logging, and startup.
"""

import logging
from importlib import import_module


def configure_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    fh = logging.FileHandler("app.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(fmt)
    logging.getLogger().addHandler(fh)


def run_app():
    """Main entry point for the application."""
    configure_logging()
    # Import and run the main app from apps.sections
    app_module = import_module("apps.sections.app")
    app_module.run_app()
