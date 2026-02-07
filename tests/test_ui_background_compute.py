from types import SimpleNamespace

from src.ui.ui.verification_table_app import VerificationTableApp


class FakeTree:
    def __init__(self):
        self.data = {}

    def set(self, item, col, val):
        self.data[(item, col)] = val


class DummyResult:
    def __init__(self, esito, sigma_c_max=None, sigma_c_min=None):
        self.esito = esito
        self.sigma_c_max = sigma_c_max
        self.sigma_c_min = sigma_c_min


def test_apply_result_to_item_updates_notes_field():
    fake_tree = FakeTree()
    # Create minimal app-like object
    app = SimpleNamespace(tree=fake_tree)
    item_id = "row1"
    res = DummyResult("VERIFICATO", sigma_c_max=1.234, sigma_c_min=0.123)
    # Call the method unbound
    VerificationTableApp._apply_result_to_item(app, item_id, res)
    assert (item_id, "notes") in fake_tree.data
    val = fake_tree.data[(item_id, "notes")]
    assert "VERIFICATO" in val
    assert "σc_max=1.234" in val or "1.234" in val
