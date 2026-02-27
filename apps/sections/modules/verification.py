MODULE_SPEC = {
    "key": "verification",
    "name": "Verification Module",
    "description": "Modulo per verifiche (placeholder).",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):  # pragma: no cover - placeholder
        return None


def create_module(master=None, **_):
    # If there is a verification entrypoint, try to use it; otherwise placeholder
    try:
        from sections_app.ui.frc_verification_window import FrcVerificationWindow

        return FrcVerificationWindow(master)
    except Exception:
        return _Placeholder(master)
