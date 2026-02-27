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


def main() -> int:
    app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
