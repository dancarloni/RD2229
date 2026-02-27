MODULE_SPEC = {
    "key": "geometry",
    "name": "Geometry Module",
    "description": "Modulo per calcoli geometrici di sezioni strutturali.",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, section_repo=None, serializer=None):
    try:
        from sections_app.ui.main_window import MainWindow

        # Provide None as repos if not given; MainWindow handles lazy loading
        return MainWindow(master, section_repo, serializer)
    except Exception:
        return _Placeholder(master)
