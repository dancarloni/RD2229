from unittest.mock import patch
from sections_app.ui.module_selector import ModuleSelectorController


def test_controller_selects_module_calls_factory(monkeypatch):
    controller = ModuleSelectorController()

    class Dummy:
        def mainloop(self):
            return None

    def factory(master=None, **_):
        return Dummy()

    # inject dummy factory into registry
    monkeypatch.setattr(controller.registry, "_factories", {"dummy": factory})

    with patch("threading.Thread") as mock_thread:
        controller.select_module("dummy")
        mock_thread.assert_called_once()
