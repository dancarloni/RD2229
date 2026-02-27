from src.rd2229.mvp.models import Material, Project
from src.rd2229.mvp.repositories import MaterialRepository, ProjectRepository
from src.rd2229.mvp.sqlite_store import SQLiteStore


def test_mvp_sqlite_roundtrip_project_and_material(tmp_path):
    db_path = tmp_path / "mvp.db"
    store = SQLiteStore(str(db_path))
    store.initialize()

    project = Project(id="p1", name="Project 1", norma_attiva="NTC2018")
    material = Material(
        id="m1",
        project_id="p1",
        code="C25/30",
        kind="concrete",
        properties={"fck": 25.0},
    )

    with store.connect() as conn:
        project_repo = ProjectRepository(conn)
        material_repo = MaterialRepository(conn)

        project_repo.save(project)
        material_repo.save(material)

        loaded_project = project_repo.get("p1")
        materials = material_repo.list_by_project("p1")

    assert loaded_project is not None
    assert loaded_project.id == "p1"
    assert loaded_project.norma_attiva == "NTC2018"
    assert len(materials) == 1
    assert materials[0].properties["fck"] == 25.0
