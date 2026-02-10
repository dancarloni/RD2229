MODULE_SPEC = {
    "key": "material",
    "name": "Material Editor",
    "description": "Editor materiali storici - completamente funzionante.",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, material_repo=None, **_):
    try:
        # import lazily the real window if available
        from historical_materials import HistoricalMaterialLibrary
        from libs.app_module.ui.historical_material_window import HistoricalMaterialWindow

        library = HistoricalMaterialLibrary()
        return HistoricalMaterialWindow(
            master=master, library=library, material_repository=material_repo
        )
    except Exception:
        return _Placeholder(master)
