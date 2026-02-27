MODULE_SPEC = {
    "key": "historical",
    "name": "Historical Module",
    "description": "Modulo per gestione materiali storici.",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, section_repo=None, **_):
    try:
        from sections_app.ui.historical_main_window import HistoricalModuleMainWindow

        return HistoricalModuleMainWindow(master, section_repo)
    except Exception:
        return _Placeholder(master)
