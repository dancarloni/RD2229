MODULE_SPEC = {
    "key": "project_editor",
    "name": "Project Editor",
    "description": "GUI per creare/caricare/salvare ProjectModel"
}

class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master
    def mainloop(self):
        return None

def create_module(master=None, **context):
    # TODO: implement real window logic
    return _Placeholder(master)
