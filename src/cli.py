"""CLI entry point for rd2229.

Usage:
  rd2229 --help
  rd2229 run [project.json]
  rd2229 export [project.json] [output_dir]
"""

from __future__ import annotations

import argparse
import logging
import sys


def main() -> int:
    parser = argparse.ArgumentParser(prog="rd2229", description="RD2229 structural engineering tool")
    parser.add_argument("command", nargs="?", choices=["run", "export", "info"], default="info")
    parser.add_argument("project", nargs="?", help="Path to project JSON file")
    parser.add_argument("output", nargs="?", help="Output directory (for export)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logger = logging.getLogger("rd2229.cli")

    if args.command == "info":
        print("rd2229 v0.1.0 — Structural engineering calculations")
        print("Use 'rd2229 run <project.json>' to run calculations")
        print("Use 'rd2229 export <project.json> <output>' to export report")
        return 0
    elif args.command == "run":
        if not args.project:
            print("Error: project file required for 'run' command", file=sys.stderr)
            return 1
        try:
            from src.core.pipeline import run_pipeline  # type: ignore

            result = run_pipeline(args.project)
            print(f"Pipeline complete: ok={result.ok}, elements={len(result.elements)}")
            return 0 if result.ok else 1
        except Exception as exc:
            logger.error("Pipeline failed: %s", exc)
            return 1
    elif args.command == "export":
        if not args.project or not args.output:
            print("Error: project file and output dir required for 'export'", file=sys.stderr)
            return 1
        try:
            from src.core.pipeline import run_pipeline  # type: ignore
            from src.reporting.export import export_report  # type: ignore
            from src.reporting.report_builder import build_report  # type: ignore

            result = run_pipeline(args.project)
            artifact = build_report(result)
            export_report(artifact, args.output)
            print(f"Report exported to {args.output}")
            return 0
        except Exception as exc:
            logger.error("Export failed: %s", exc)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
