MODULE_SPEC = {
    "key": "code_settings",
    "name": "Code Settings Dialog",
    "description": "Dialog di configurazione codici"
}

class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master
    def mainloop(self):
        return None

def create_module(master=None, **context):
    # TODO: implement real window logic
    return _Placeholder(master)
