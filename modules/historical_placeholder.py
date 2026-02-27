MODULE_SPEC = {
    "key": "historical",
    "name": "Historical Module (Placeholder)",
    "description": "Modulo per gestione materiali storici - attualmente placeholder, in sviluppo.",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, section_repo=None, **_):
    try:
        from libs.app_module.ui.historical_main_window import HistoricalModuleMainWindow

        return HistoricalModuleMainWindow(master, section_repo)
    except Exception:
        return _Placeholder(master)
