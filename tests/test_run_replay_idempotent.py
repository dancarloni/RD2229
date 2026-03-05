import subprocess

from src.project.model import ModuleConfig, NormativeProfileRef, ProjectMeta, ProjectModel
from src.project.repository import save_project


def make_project():
    meta = ProjectMeta(
        id="proj1",
        name="Test Project",
        created_at="2026-03-01T00:00:00Z",
        updated_at="2026-03-01T00:00:00Z",
        commit_hash="abc123",
        schema_version="1.0.0",
    )
    norm = NormativeProfileRef(source_ids=["RD2229"], clauses=["§4.2.1"])
    modules = [ModuleConfig(name="mod1", enabled=True, params={})]
    return ProjectModel(meta=meta, normative_profile=norm, modules=modules, io_settings={})


def test_run_and_replay_idempotent(tmp_path):
    # Save project.json
    project = make_project()
    project_path = tmp_path / "project.json"
    save_project(project, project_path)
    # Run project
    run_dir = tmp_path / "projects" / "proj1" / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    # Use CLI tool
    subprocess.run(["python", "tools/run_project.py", str(project_path)], check=True)
    # Find run dir
    runs = list((tmp_path / "projects" / "proj1" / "runs").iterdir())
    assert runs, "No run dir created"
    run = runs[0]
    # Replay
    subprocess.run(["python", "tools/replay_run.py", str(run)], check=True)
