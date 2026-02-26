from src.rd2229.project_store import ProjectStore


def test_project_store_basic():
    store = ProjectStore()
    assert store.list() == []
    store.add("p1", {"name": "p1"})
    assert store.get("p1")["name"] == "p1"
    assert store.list() == ["p1"]
