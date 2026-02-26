from types import SimpleNamespace

from src.ui.ui.verification_table_app import VerificationTableApp


def test_compute_target_cell_creates_new_row_when_past_end():
    # Minimal tree-like dummy with get_children and item behaviour
    class DummyTree:
        def __init__(self):
            self._items = {}
            self._order = []

        def get_children(self):
            return list(self._order)

        def item(self, item, _opt=None):
            return {"values": self._items.get(item, [])}

        def delete(self, _):
            pass

    dummy = SimpleNamespace()
    dummy.tree = DummyTree()
    app = VerificationTableApp.__new__(VerificationTableApp)
    app.tree = dummy.tree
    app.columns = ["a", "b", "c"]

    # create one row
    app.tree._order = ["r1"]
    app.tree._items["r1"] = ["v1", "v2", "v3"]

    # moving to next row beyond last should create a new row via add_row_from_previous
    # We monkeypatch add_row_from_previous to return a new id
    def fake_add_row_from_previous(item):
        new_id = "r2"
        app.tree._order.append(new_id)
        app.tree._items[new_id] = ["", "", ""]
        return new_id

    app.add_row_from_previous = fake_add_row_from_previous

    target_item, target_col, created = app._compute_target_cell("r1", "b", 0, 1)
    assert created is True
    assert target_item == "r2"
    assert target_col == "b"
