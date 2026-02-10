MODULE_SPEC = {
    "key": "geometry",
    "name": "Geometry Module",
    "description": "Modulo per creazione e calcolo caratteristiche delle sezioni.",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, section_repo=None, **_):
    try:
        from libs.app_module.ui.main_window import MainWindow

        return MainWindow(master, section_repo)
    except Exception:
        return _Placeholder(master)
