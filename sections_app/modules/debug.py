MODULE_SPEC = {
    "key": "debug",
    "name": "Debug Viewer",
    "description": "Strumento per visualizzare log e debug.",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, **_):
    try:
        from sections_app.ui.debug_viewer import DebugViewerWindow

        return DebugViewerWindow(master)
    except Exception:
        return _Placeholder(master)
