MODULE_SPEC = {
    "key": "frc",
    "name": "FRC Module",
    "description": "Modulo per verifiche FRC (placeholder).",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, **_):
    # There isn't an obvious FRC main window at the moment; return a placeholder
    return _Placeholder(master)
