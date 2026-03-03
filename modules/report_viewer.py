MODULE_SPEC = {
    "key": "report_viewer",
    "name": "Report Viewer",
    "description": "Visualizza l’HTML/MD generato, pulsanti export",
}


class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master

    def mainloop(self):
        return None


def create_module(master=None, **context):
    # TODO: implement real window logic
    return _Placeholder(master)
