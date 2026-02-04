#!/usr/bin/env python3
"""Script di demo: apre l'editor materiali, lo chiude, e testa suggerimenti in Verification Table."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
import tkinter as tk

# Ensure project root is on sys.path so local packages (sections_app, core_models, etc.) can be imported
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("manual_demo")

from sections_app.ui.module_selector import ModuleSelectorWindow
from sections_app.services.repository import SectionRepository, CsvSectionSerializer
from verification_table import VerificationTableWindow


def main():
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError as e:
        print("Tkinter not available:", e)
        return

    repo = SectionRepository()
    serializer = CsvSectionSerializer()

    # Create module selector
    sel = ModuleSelectorWindow(repo, serializer, material_repository=None)
    sel.update_idletasks(); sel.update()

    # Open material editor
    print("Opening material editor...")
    sel._open_material_editor()
    sel.update_idletasks(); sel.update()
    exists = sel._material_editor_window is not None and sel._material_editor_window.winfo_exists()
    print("Material editor exists:", exists)

    # Close material editor via X (destroy)
    print("Destroying material editor (simulate X)...")
    if sel._material_editor_window is not None:
        try:
            sel._material_editor_window.destroy()
        except Exception as e:
            print("Error destroying material editor:", e)
    sel.update_idletasks(); sel.update()
    print("Material editor reference after destroy:", sel._material_editor_window)

    # Open Verification Table
    print("Opening Verification Table...")
    vt = VerificationTableWindow(sel, section_repository=None, material_repository=None)
    app = vt.app

    vt.update_idletasks(); vt.update()
    item = list(app.tree.get_children())[0]

    # Test concrete search '160'
    print("Testing concrete suggestions for '160'")
    app._start_edit(item, "mat_concrete")
    app.edit_entry.delete(0, tk.END); app.edit_entry.insert(0, "160")
    app._update_suggestions()
    vt.update_idletasks(); vt.update()
    concrete_items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())] if app._suggest_list else []
    print("Concrete suggestions for '160':", concrete_items)

    # Test steel search '38'
    print("Testing steel suggestions for '38'")
    app._start_edit(item, "mat_steel")
    app.edit_entry.delete(0, tk.END); app.edit_entry.insert(0, "38")
    app._update_suggestions()
    vt.update_idletasks(); vt.update()
    steel_items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())] if app._suggest_list else []
    print("Steel suggestions for '38':", steel_items)

    # Clean up
    print("Cleaning up windows...")
    try:
        vt.destroy()
    except Exception:
        pass
    try:
        sel.destroy()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass

    print("Demo finished.")


if __name__ == '__main__':
    main()
