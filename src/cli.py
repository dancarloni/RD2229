"""CLI entry point for rd2229.

Usage:
  rd2229 --help
  rd2229 run [project.json]
  rd2229 export [project.json] [output_dir]
"""

from __future__ import annotations

import argparse
import sys

from src.rd2229.logging_bridge import get_logger, setup_logging

logger = get_logger("cli")


def main() -> int:
    parser = argparse.ArgumentParser(prog="rd2229", description="RD2229 structural engineering tool")
    parser.add_argument("command", nargs="?", choices=["run", "export", "info"], default="info")
    parser.add_argument("project", nargs="?", help="Path to project JSON file")
    parser.add_argument("output", nargs="?", help="Output directory (for export)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(level="DEBUG" if args.verbose else "INFO")

    if args.command == "info":
        logger.info("rd2229 v0.1.0 — Structural engineering calculations")
        logger.info("Use 'rd2229 run <project.json>' to run calculations")
        logger.info("Use 'rd2229 export <project.json> <output>' to export report")
        return 0
    elif args.command == "run":
        if not args.project:
            logger.error("project file required for 'run' command")
            return 1
        try:
            from src.core.pipeline import run_pipeline  # type: ignore[import]
            from src.project.repository import load_project  # type: ignore[import]

            project = load_project(args.project)
            result = run_pipeline(project)
            logger.info("Pipeline complete: ok=%s, elements=%d", result.ok, len(result.elements))
            return 0 if result.ok else 1
        except (ImportError, FileNotFoundError, RuntimeError) as exc:
            logger.error("Pipeline failed: %s", exc)
            return 1
    elif args.command == "export":
        if not args.project or not args.output:
            logger.error("project file and output dir required for 'export'")
            return 1
        try:
            import pathlib

            from src.core.pipeline import run_pipeline  # type: ignore[import]
            from src.project.repository import load_project  # type: ignore[import]
            from src.reporting.export import (  # type: ignore[import]
                export_report_html,
                export_report_md,
            )
            from src.reporting.report_builder import build_report  # type: ignore[import]

            project = load_project(args.project)
            results = run_pipeline(project)
            artifact = build_report(project, results)
            output_dir = pathlib.Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            export_report_html(artifact, str(output_dir / "report.html"))
            export_report_md(artifact, str(output_dir / "report.md"))
            logger.info("Report exported to %s/report.{html,md}", args.output)
            return 0
        except (ImportError, FileNotFoundError, RuntimeError) as exc:
            logger.error("Export failed: %s", exc)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
