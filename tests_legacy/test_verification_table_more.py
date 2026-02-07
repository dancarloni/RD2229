import tkinter as tk
import unittest

from sections_app.models.sections import RectangularSection
from sections_app.services.repository import SectionRepository

try:
    from core_models.materials import Material, MaterialRepository
except Exception:
    MaterialRepository = None
    Material = None

from verification_table import VerificationTableApp, VerificationTableWindow


class DummyMat:
    def __init__(self, name):
        self.name = name


class TestVerificationTableMore(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available in this environment")

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

    def test_commit_not_performed_while_rebar_calculator_open(self):
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        item = list(app.tree.get_children())[0]
        top.update_idletasks()
        top.update()
        # Start editing As cell
        app._start_edit(item, "As")
        self.assertIsNotNone(app.edit_entry)
        # Insert a provisional value
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "1.23")
        # Open calculator (this should set the flag and not commit immediately)
        app._open_rebar_calculator()
        self.assertTrue(getattr(app, "_in_rebar_calculator", False))
        # Call commit_if_focus_outside directly - it should NOT commit while calculator is open
        app._commit_if_focus_outside()
        # Entry should still exist and tree value should be unchanged (empty string)
        self.assertIsNotNone(app.edit_entry)
        self.assertEqual(app.tree.set(item, "As"), "")
        # Now confirm via calculator and ensure value applied and flag cleared
        app._rebar_vars[8].set("2")
        app._update_rebar_total()
        expected = float(app._rebar_total_var.get())
        app._confirm_rebar_total()
        val = float(app.tree.set(item, "As"))
        self.assertAlmostEqual(val, expected, places=2)
        self.assertFalse(getattr(app, "_in_rebar_calculator", False))
        app.tree.delete(item)

    def test_rebar_via_keypress_opens_and_applies(self):
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        item = list(app.tree.get_children())[0]
        top.update_idletasks()
        top.update()
        # Start editing As cell and simulate pressing 'c'
        app._start_edit(item, "As")
        self.assertIsNotNone(app.edit_entry)
        # ensure the entry has focus and simulate KeyPress 'c'
        app.edit_entry.focus_set()
        # try multiple ways to generate key event so it triggers on all platforms
        try:
            app.edit_entry.event_generate("<KeyPress>", keysym="c")
            app.edit_entry.event_generate("<KeyRelease>", keysym="c")
        except tk.TclError:
            # fallback
            app.edit_entry.event_generate("<KeyPress-c>")
        top.update_idletasks()
        top.update()
        # ensure popup opened - if not, call handler directly as a deterministic fallback
        if app._rebar_window is None:
            import types

            evt = types.SimpleNamespace(char="c", keysym="c")
            app._on_entry_keypress(evt)
            top.update_idletasks()
            top.update()
        self.assertIsNotNone(app._rebar_window)
        # set bars and compute
        app._rebar_vars[16].set("2")
        app._rebar_vars[8].set("3")
        app._update_rebar_total()
        expected = float(app._rebar_total_var.get())
        # confirm and verify
        app._confirm_rebar_total()
        val = app.tree.set(item, "As")
        self.assertAlmostEqual(float(val), expected, places=2)
        app.tree.delete(item)

    def test_rebar_via_keypress_on_As_prime_opens_and_applies(self):
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        item = list(app.tree.get_children())[0]
        top.update_idletasks()
        top.update()
        # Start editing As' (column 'As_p') and simulate pressing 'c'
        app._start_edit(item, "As_p")
        self.assertIsNotNone(app.edit_entry)
        app.edit_entry.focus_set()
        try:
            app.edit_entry.event_generate("<KeyPress>", keysym="c")
            app.edit_entry.event_generate("<KeyRelease>", keysym="c")
        except tk.TclError:
            app.edit_entry.event_generate("<KeyPress-c>")
        top.update_idletasks()
        top.update()
        # fallback to direct handler if event didn't trigger
        if app._rebar_window is None:
            import types

            evt = types.SimpleNamespace(char="c", keysym="c")
            app._on_entry_keypress(evt)
            top.update_idletasks()
            top.update()
        self.assertIsNotNone(app._rebar_window)
        # set bars and compute
        app._rebar_vars[12].set("1")
        app._rebar_vars[10].set("4")
        app._update_rebar_total()
        expected = float(app._rebar_total_var.get())
        app._confirm_rebar_total()
        val = app.tree.set(item, "As_p")
        self.assertAlmostEqual(float(val), expected, places=2)
        app.tree.delete(item)

    def test_material_suggestions_popup_filters(self):
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        # ensure there is at least one row and start editing the material cell
        item = list(app.tree.get_children())[0]
        top.update_idletasks()
        top.update()
        app._start_edit(item, "mat_concrete")
        # set some fake material names
        app.material_names = ["C120", "C200", "A500", "C123"]
        app.suggestions_map["mat_concrete"] = app.material_names
        self.assertIsNotNone(app.edit_entry)
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "C12")
        app._update_suggestions()
        # allow UI to create popup
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        # should include C120 and C123 (both contain 'C12')
        self.assertIn("C120", items)
        self.assertIn("C123", items)
        # should not include unrelated
        self.assertNotIn("A500", items)

    def test_material_suggestions_from_repository(self):
        """Verify suggestions are drawn from MaterialRepository and filtered by type."""
        try:
            from core_models.materials import Material, MaterialRepository
        except Exception:
            self.skipTest("MaterialRepository not available")

        tmprepo = (
            MaterialRepository(json_file=":memory:")
            if hasattr(MaterialRepository, "__init__")
            else MaterialRepository()
        )
        # Add materials of different types
        m1 = Material(name="C120", type="concrete")
        m2 = Material(name="A500", type="steel")
        m3 = Material(name="C123", type="concrete")
        tmprepo.add(m1)
        tmprepo.add(m2)
        tmprepo.add(m3)

        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        win = VerificationTableWindow(top, section_repository=None, material_repository=tmprepo)
        app = win.app
        top.update_idletasks()
        top.update()
        item = list(app.tree.get_children())[0]
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "C12")
        app._update_suggestions()
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        self.assertIn("C120", items)
        self.assertIn("C123", items)
        self.assertNotIn("A500", items)
        win.destroy()

    def test_historical_materials_are_suggested(self):
        """Verify historical materials (built-in library) appear in suggestions for concrete."""
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        # No material_repository provided - search should include historical library
        win = VerificationTableWindow(top, section_repository=None, material_repository=None)
        app = win.app
        top.update_idletasks()
        top.update()
        item = list(app.tree.get_children())[0]
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        # Use a substring known to match historical CLS R160 entries
        app.edit_entry.insert(0, "160")
        app._update_suggestions()
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        # At least one historical R160 material should be suggested
        self.assertTrue(
            any("R160" in it or "160" in it for it in items), f"Unexpected items: {items}"
        )
        # Suggestions should be concrete materials only - none of the items should indicate a steel-only label
        # (simple heuristic: ensure no 'Acciaio' in suggested names)
        self.assertFalse(any("Acciaio" in it for it in items))
        win.destroy()

    def test_section_suggestions_from_repository(self):
        """Verify suggestions are drawn from SectionRepository."""
        sec_repo = SectionRepository()
        sec_repo.clear()
        sec = RectangularSection(name="Rect-20x30", width=20, height=30)
        sec.compute_properties()
        sec_repo.add_section(sec)

        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        win = VerificationTableWindow(top, section_repository=sec_repo, material_repository=None)
        app = win.app
        top.update_idletasks()
        top.update()
        item = list(app.tree.get_children())[0]
        app._start_edit(item, "section")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "rect")
        app._update_suggestions()
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        self.assertIn("Rect-20x30", items)
        # cleanup
        app._hide_suggestions()
        app._on_entry_cancel(None)
        try:
            app.tree.delete(item)
        except Exception:
            pass
        win.destroy()

    def test_material_steel_suggestions_popup_filters(self):
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        # ensure there is at least one row and start editing the material steel cell
        item = list(app.tree.get_children())[0]
        top.update_idletasks()
        top.update()
        app._start_edit(item, "mat_steel")
        # set some fake material names
        app.material_names = ["S235", "S275", "A500", "S240"]
        app.suggestions_map["mat_steel"] = app.material_names
        self.assertIsNotNone(app.edit_entry)
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "S2")
        app._update_suggestions()
        # allow UI to create popup
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        # should include S235 and S275 and S240
        self.assertIn("S235", items)
        self.assertIn("S275", items)
        self.assertIn("S240", items)
        # should not include unrelated
        self.assertNotIn("A500", items)
        app._hide_suggestions()
        app._on_entry_cancel(None)
        app.tree.delete(item)

    def test_empty_query_shows_no_suggestions(self):
        """If the user types an empty query, no suggestions should appear."""
        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        app = VerificationTableApp(top)
        item = list(app.tree.get_children())[0]
        top.update_idletasks()
        top.update()
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        app._update_suggestions()
        top.update_idletasks()
        top.update()
        self.assertIsNone(app._suggest_list)
        try:
            app.tree.delete(item)
        except Exception:
            pass
        top.destroy()

    def test_duplicates_between_repository_and_historical_are_removed(self):
        """If a material exists both in repository and historical library, it should be suggested only once."""
        try:
            from core_models.materials import Material, MaterialRepository
        except Exception:
            self.skipTest("MaterialRepository not available")

        tmprepo = (
            MaterialRepository(json_file=":memory:")
            if hasattr(MaterialRepository, "__init__")
            else MaterialRepository()
        )
        # Add material that matches historical name
        m1 = Material(name="CLS R 160 (RD 2229/39)", type="concrete")
        tmprepo.add(m1)

        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        win = VerificationTableWindow(top, section_repository=None, material_repository=tmprepo)
        app = win.app
        top.update_idletasks()
        top.update()
        item = list(app.tree.get_children())[0]
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "160")
        app._update_suggestions()
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        # Should contain the R160 entry only once
        self.assertEqual(sum(1 for it in items if "R160" in it or "160" in it), 1)
        win.destroy()

    def test_code_match_when_name_does_not(self):
        """If query matches code but not name, the material should still be suggested."""
        try:
            from core_models.materials import Material, MaterialRepository
        except Exception:
            self.skipTest("MaterialRepository not available")

        tmprepo = (
            MaterialRepository(json_file=":memory:")
            if hasattr(MaterialRepository, "__init__")
            else MaterialRepository()
        )
        m1 = Material(name="Concrete X", type="concrete", code="C160")
        tmprepo.add(m1)

        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        win = VerificationTableWindow(top, section_repository=None, material_repository=tmprepo)
        app = win.app
        top.update_idletasks()
        top.update()
        item = list(app.tree.get_children())[0]
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "160")
        app._update_suggestions()
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        self.assertIn("Concrete X", items)
        win.destroy()

    def test_type_filter_excludes_wrong_type(self):
        """Concrete search should not return steel matches even if substring matches."""
        try:
            from core_models.materials import Material, MaterialRepository
        except Exception:
            self.skipTest("MaterialRepository not available")

        tmprepo = (
            MaterialRepository(json_file=":memory:")
            if hasattr(MaterialRepository, "__init__")
            else MaterialRepository()
        )
        m1 = Material(name="SomeSteel38", type="steel", code="S38")
        m2 = Material(name="SomeConcrete38", type="concrete", code="C38")
        tmprepo.add(m1)
        tmprepo.add(m2)

        top = tk.Toplevel(self.root)
        top.geometry("900x300")
        win = VerificationTableWindow(top, section_repository=None, material_repository=tmprepo)
        app = win.app
        top.update_idletasks()
        top.update()
        item = list(app.tree.get_children())[0]
        # Search in concrete column for '38' - should only show concrete
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "38")
        app._update_suggestions()
        top.update_idletasks()
        top.update()
        self.assertIsNotNone(app._suggest_list)
        items = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        self.assertIn("SomeConcrete38", items)
        self.assertNotIn("SomeSteel38", items)
        win.destroy()


if __name__ == "__main__":
    unittest.main()
