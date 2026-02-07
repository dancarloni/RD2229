import tkinter as tk
import unittest

from sections_app.services.repository import CsvSectionSerializer, SectionRepository

try:
    from historical_materials import HistoricalMaterialLibrary
    from sections_app.ui.module_selector import ModuleSelectorWindow
    from verification_table import VerificationTableWindow
except Exception:
    ModuleSelectorWindow = None
    VerificationTableWindow = None
    HistoricalMaterialLibrary = None


class TestManualDemo(unittest.TestCase):
    """Automated version of the manual demo used during debugging.

    - Opens Material Editor from Module Selector and makes sure it closes with X
    - Opens Verification Table and verifies suggestions for '160' in concrete
      and '38' in steel using historical materials when no repository provided
    """

    def setUp(self):
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available in this environment")

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_demo_flow_open_close_and_suggestions(self):
        if ModuleSelectorWindow is None or VerificationTableWindow is None:
            self.skipTest("GUI modules not available")

        # Quick sanity check that historical library has relevant entries
        if HistoricalMaterialLibrary is None:
            self.skipTest("HistoricalMaterialLibrary not available")
        hist_lib = HistoricalMaterialLibrary()
        hist_all = hist_lib.get_all()
        # Need at least one concrete and one steel historical material for this demo
        has_conc = any(
            (getattr(m.type, "value", str(getattr(m, "type", ""))) == "concrete") for m in hist_all
        )
        has_steel = any(
            (getattr(m.type, "value", str(getattr(m, "type", ""))) == "steel") for m in hist_all
        )
        if not (has_conc and has_steel):
            self.skipTest("Historical library does not contain both concrete and steel samples")

        repo = SectionRepository()
        serializer = CsvSectionSerializer()

        # Create Module Selector and open material editor
        sel = ModuleSelectorWindow(repo, serializer, material_repository=None)
        sel.update_idletasks()
        sel.update()

        sel._open_material_editor()
        sel.update_idletasks()
        sel.update()
        self.assertIsNotNone(sel._material_editor_window)

        # Close material editor via destroy (simulate clicking X)
        sel._material_editor_window.destroy()
        sel.update_idletasks()
        sel.update()
        # Reference should have been cleared
        self.assertIsNone(sel._material_editor_window)

        # Open Verification Table (no material repository => historical materials used)
        vt = VerificationTableWindow(sel, section_repository=None, material_repository=None)
        app = vt.app
        vt.update_idletasks()
        vt.update()

        item = list(app.tree.get_children())[0]

        # Concrete search '160' should yield at least one suggestion containing '160'
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "160")
        app._update_suggestions()
        vt.update_idletasks()
        vt.update()
        self.assertIsNotNone(app._suggest_list, "Concrete suggestions popup did not appear")
        concrete_items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        self.assertTrue(
            any("160" in it or "R160" in it for it in concrete_items),
            f"Unexpected concrete suggestions: {concrete_items}",
        )
        # Ensure concrete suggestions don't contain obvious 'Acciaio' labels
        self.assertFalse(any("Acciaio" in it for it in concrete_items))

        # Steel search '38' should yield suggestions containing '38'
        app._start_edit(item, "mat_steel")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "38")
        app._update_suggestions()
        vt.update_idletasks()
        vt.update()
        self.assertIsNotNone(app._suggest_list, "Steel suggestions popup did not appear")
        steel_items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        self.assertTrue(
            any("38" in it for it in steel_items), f"Unexpected steel suggestions: {steel_items}"
        )

        # Cleanup
        try:
            vt.destroy()
        except Exception:
            pass
        try:
            sel.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
