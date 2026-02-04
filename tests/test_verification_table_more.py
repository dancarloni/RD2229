import unittest
import tkinter as tk

from sections_app.services.repository import SectionRepository
from sections_app.models.sections import RectangularSection

try:
    from core_models.materials import MaterialRepository, Material
except Exception:
    MaterialRepository = None
    Material = None

from verification_table import VerificationTableWindow, VerificationTableApp


class DummyMat:
    def __init__(self, name):
        self.name = name


class TestVerificationTableMore(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_material_names_resolved_from_repository(self):
        # Create a fake material repository with get_all returning objects with .name
        class FakeMatRepo:
            def get_all(self):
                return [DummyMat("C120"), DummyMat("A500")]

        repo = FakeMatRepo()
        win = VerificationTableWindow(self.root, section_repository=None, material_repository=repo)
        self.assertIn("C120", win.app.material_names)
        self.assertIn("A500", win.app.material_names)
        win.destroy()

    def test_suggestions_popup_filters(self):
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        # ensure there is at least one row and start editing the section cell
        item = list(app.tree.get_children())[0]
        # Ensure widgets have been rendered so bbox() works
        top.update_idletasks()
        top.update()
        app._start_edit(item, "section")
        # set some fake section names
        app.section_names = ["Rect-20x30", "Circ-25", "Other"]
        # propagate to suggestions map
        app.suggestions_map["section"] = app.section_names
        # ensure entry exists
        self.assertIsNotNone(app.edit_entry)
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "rect")
        app._update_suggestions()
        # allow UI to create popup
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        # should include only the matching entry
        self.assertIn("Rect-20x30", items)
        app._hide_suggestions()
        app._on_entry_cancel(None)
        app.tree.delete(item)

    def test_rebar_calculator_applies_value(self):
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        item = list(app.tree.get_children())[0]
        # Ensure widgets rendered so bbox() works
        top.update_idletasks()
        top.update()
        # Start editing As (column 'As')
        app._start_edit(item, "As")
        # ensure entry created
        self.assertIsNotNone(app.edit_entry)
        # open calculator
        app._open_rebar_calculator()
        # ensure rebar vars created
        self.assertIn(16, app._rebar_vars)
        self.assertIn(8, app._rebar_vars)
        # set 2 bars of Ø16 and 3 bars of Ø8
        app._rebar_vars[16].set("2")
        app._rebar_vars[8].set("3")
        # update and read total
        self.root.update_idletasks()
        self.root.update()
        app._update_rebar_total()
        total = float(app._rebar_total_var.get())
        # Confirm
        app._confirm_rebar_total()
        # check tree value written
        val = app.tree.set(item, "As")
        self.assertAlmostEqual(float(val), total, places=2)
        app.tree.delete(item)


if __name__ == "__main__":
    unittest.main()
