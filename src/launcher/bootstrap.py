"""
Bootstrap module for RD2229 application.
Orchestrates discovery, configuration, logging, and startup.
"""

from importlib import import_module


def configure_logging() -> None:
    """Configure logging for the application via the centralized bridge."""
    from src.rd2229.logging_bridge import setup_logging

    setup_logging("DEBUG", enable_file=True, log_dir=".")


def run_app() -> None:
    """Main entry point for the application."""
    configure_logging()
    # Import and run the main app from apps.sections
    app_module = import_module("apps.sections.app")
    app_module.run_app()
