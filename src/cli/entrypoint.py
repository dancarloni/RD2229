"""Typer-based CLI entrypoint for RD2229 v0.1.0."""

from __future__ import annotations

from pathlib import Path

import typer

from src.core.pipeline import run_pipeline
from src.project.repository import load_project, save_project
from src.project.schema import ProjectModel
from src.reporting.export import export_report_html, export_report_md
from src.reporting.report_builder import build_report

app = typer.Typer(help="RD2229 CLI")


@app.command("new")
def new_project(file: str) -> None:
    project = ProjectModel()
    save_project(project, file)
    typer.echo(f"Creato progetto: {file}")


@app.command("load")
def load_project_cmd(file: str) -> None:
    project = load_project(file)
    typer.echo(
        f"Caricato: {project.project_info.name or '-'} | "
        f"schema={project.schema_version} | "
        f"elementi={len(project.geometry)}"
    )


@app.command("run")
def run_project(file: str) -> None:
    project = load_project(file)
    results = run_pipeline(project)
    typer.echo(
        f"Pipeline: ok={results.ok}, elementi={len(results.elements)}, avvisi={len(results.warnings)}"
    )


@app.command("export")
def export_project(file: str, format: str = typer.Option("md", "--format")) -> None:
    project = load_project(file)
    results = run_pipeline(project)
    artifact = build_report(project, results)

    output = Path(file).with_suffix("")
    if format == "html":
        target = output.with_name(output.name + "_report.html")
        export_report_html(artifact, str(target))
    else:
        target = output.with_name(output.name + "_report.md")
        export_report_md(artifact, str(target))

    typer.echo(f"Report esportato: {target}")


@app.command("info")
def info() -> int:
    """Print version information."""
    ver = "v0.1.0"
    typer.echo(ver)
    return 0


def main() -> int:
    """Run CLI and return integer exit code instead of exiting the process.

    Tests call `src.cli.main()` and expect an integer return value; Typer
    normally calls `sys.exit`. Use `standalone_mode=False` to prevent
    sys.exit and return an int.
    """
    import sys

    # Default to info when no args provided (legacy behaviour expected by tests)
    if len(sys.argv) <= 1:
        return info()

    try:
        # Run Typer in non-standalone mode so it raises exceptions instead of exiting
        app(prog_name="rd2229", standalone_mode=False)
        return 0
    except SystemExit as exc:
        # Typer may still raise SystemExit for usage errors; propagate as int
        return int(getattr(exc, "code", 1) or 1)
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
