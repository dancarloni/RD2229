"""
Script: generate_modules_from_docs.py
Genera/aggiorna modules_config.json e stub Python per tutti i moduli richiesti dalla documentazione.
"""

import json
import os

MODULES = [
    {
        "key": "project_editor",
        "name": "Project Editor",
        "description": "GUI per creare/caricare/salvare ProjectModel",
        "path": "modules/project_editor.py",
    },
    {
        "key": "pipeline_runner",
        "name": "Pipeline Runner",
        "description": "Avvia la pipeline, mostra barra di progresso e risultati",
        "path": "modules/pipeline_runner.py",
    },
    {
        "key": "report_viewer",
        "name": "Report Viewer",
        "description": "Visualizza l’HTML/MD generato, pulsanti export",
        "path": "modules/report_viewer.py",
    },
    {
        "key": "material_editor",
        "name": "Historical Material Editor",
        "description": "Editor materiali storici",
        "path": "modules/material_editor.py",
    },
    {
        "key": "code_settings",
        "name": "Code Settings Dialog",
        "description": "Dialog di configurazione codici",
        "path": "modules/code_settings.py",
    },
    # Add more as needed from MODULES_MAPPING.md
]

CONFIG_PATH = "modules/modules_config.json"

MODULE_SPEC_TEMPLATE = """MODULE_SPEC = {{
    "key": "{key}",
    "name": "{name}",
    "description": "{description}"
}}

class _Placeholder:
    def __init__(self, master=None, **_):
        self.master = master
    def mainloop(self):
        return None

def create_module(master=None, **context):
    # TODO: implement real window logic
    return _Placeholder(master)
"""


def main():
    # Update modules_config.json
    config = {m["key"]: {"enabled": True, "order": i} for i, m in enumerate(MODULES)}
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    # Create stub files if missing
    for m in MODULES:
        if not os.path.exists(m["path"]):
            with open(m["path"], "w", encoding="utf-8") as f:
                f.write(MODULE_SPEC_TEMPLATE.format(**m))
    print(f"Aggiornato {CONFIG_PATH} e stub moduli.")


if __name__ == "__main__":
    main()
