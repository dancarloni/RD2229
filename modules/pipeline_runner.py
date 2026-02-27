MODULE_SPEC = {
    "key": "pipeline_runner",
    "name": "Pipeline Runner",
    "description": "Avvia la pipeline, mostra barra di progresso e risultati"
}

class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master
    def mainloop(self):
        return None

def create_module(master=None, **context):
    # TODO: implement real window logic
    return _Placeholder(master)
