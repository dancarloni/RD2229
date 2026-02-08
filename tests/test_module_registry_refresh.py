from sections_app.ui.module_selector import ModuleSelectorController


def test_refresh_modules():
    ctrl = ModuleSelectorController()
    before = {m.key for m in ctrl.get_available_modules()}
    updated = ctrl.refresh_modules()
    assert isinstance(updated, list)
    after = {m.key for m in updated}
    assert before <= after  # at least same or more modules present
