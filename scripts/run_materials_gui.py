"""Avvia la GUI per la gestione dei materiali.

Esempio (PowerShell):
  $env:PYTHONPATH = "c:/workspaces/RD2229/RD2229/src"; python scripts/run_materials_gui.py
"""
from gui.materials_gui import run_app


def main():
    run_app()


if __name__ == "__main__":
    main()

