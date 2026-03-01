import json

from src.project.timeline import (
    OutputFileEntry,
    OutputManifest,
    RunRecord,
    sha256_file,
    write_manifest,
)


def test_sha256_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello world")
    h = sha256_file(f)
    assert h == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_write_manifest(tmp_path):
    manifest = OutputManifest(
        files=[OutputFileEntry(path="foo.txt", sha256="abc")],
        module_outputs={"mod1": {"status": "TBD"}},
        warnings=["none"],
    )
    out = tmp_path / "manifest.json"
    write_manifest(manifest, out)
    data = json.loads(out.read_text())
    assert data["files"][0]["path"] == "foo.txt"
    assert data["module_outputs"]["mod1"]["status"] == "TBD"
    assert data["warnings"] == ["none"]


def test_runrecord_model():
    rec = RunRecord(
        run_id="run1",
        timestamp_path="20260301T120000Z",
        project_id="proj1",
        commit_hash="abc123",
        python_version="3.11.0",
        normative_ids=["RD2229"],
        modules_executed=["mod1"],
    )
    assert rec.run_id == "run1"
    assert rec.normative_ids == ["RD2229"]
