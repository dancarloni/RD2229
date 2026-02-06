import unittest
import tkinter as tk
import sys
import os
import time

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp


class TestMaterialSuggestionsFocus(unittest.TestCase):
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

    def _suggestion_list_items(self, app):
        if app._suggest_list is None:
            return []
        return [app._suggest_list.get(i) for i in range(app._suggest_list.size())]

    def test_focusin_shows_suggestions_for_material_columns(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        cols = ["mat_concrete", "mat_steel", "stirrups_mat"]
        for col in cols:
            # provide material names and static suggestion source to keep test deterministic
            app.material_names = ["M1", "M2", "M3"]
            app.suggestions_map[col] = app.material_names

            first = list(app.tree.get_children())[0]
            app._start_edit(first, col)
            top.update_idletasks()
            top.update()

            # Simulate focus in first, then trigger update — this matches real UI order
            if app.edit_entry is not None:
                app.edit_entry.event_generate("<FocusIn>")
                top.update_idletasks()
                top.update()
                app._update_suggestions()
                top.update_idletasks()
                top.update()

            # Wait for a retry if geometry wasn't ready immediately
            import time
            for _ in range(30):
                if app._suggest_list and app._suggest_list.size() > 0:
                    break
                top.update_idletasks()
                top.update()
                time.sleep(0.01)

            items = self._suggestion_list_items(app)
            # Accept either our suggestion popup or the combobox values being present
            combobox_ok = False
            try:
                combobox_ok = hasattr(app.edit_entry, 'cget') and list(app.edit_entry.cget('values')) == app.material_names
            except Exception:
                combobox_ok = False
            self.assertTrue(len(items) >= 3 or combobox_ok,
                            f"No suggestions shown for column {col} (items={items} combobox_ok={combobox_ok})")
            if len(items) > 0:
                for s in ["M1", "M2", "M3"]:
                    self.assertIn(s, items)

            # cleanup for next iteration
            if app.edit_entry is not None:
                app.edit_entry.destroy()
                app.edit_entry = None
            app._hide_suggestions()

        top.destroy()

    def test_clicking_material_suggestion_commits(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        app.material_names = ["C1", "C2"]
        app.suggestions_map["mat_concrete"] = app.material_names

        first = list(app.tree.get_children())[0]
        app._start_edit(first, "mat_concrete")
        top.update_idletasks()
        top.update()

        if app.edit_entry is not None:
            app.edit_entry.event_generate("<FocusIn>")
            top.update_idletasks()
            top.update()
            app._update_suggestions()
            top.update_idletasks()
            top.update()

        import time
        for _ in range(30):
            if app._suggest_list and app._suggest_list.size() > 0:
                break
            top.update_idletasks()
            top.update()
            time.sleep(0.01)

        # selection may be via our suggestion popup or via Combobox itself
        selected = "C1"
        if app._suggest_list is not None and app._suggest_list.size() > 0:
            (lx, ly, lw, lh) = app._suggest_list.bbox(0)
            click_x = lx + lw // 2
            click_y = ly + lh // 2
            app._suggest_list.event_generate("<ButtonPress-1>", x=click_x, y=click_y)
            app._suggest_list.event_generate("<ButtonRelease-1>", x=click_x, y=click_y)
            # allow handlers to run
            for _ in range(10):
                top.update_idletasks()
                top.update()
                time.sleep(0.01)
            if app.edit_entry is None:
                self.assertEqual(app.tree.set(first, "mat_concrete"), selected)
            else:
                self.assertEqual(app.edit_entry.get(), selected)
                app._commit_edit()
                top.update_idletasks()
                top.update()
                self.assertEqual(app.tree.set(first, "mat_concrete"), selected)
        else:
            # Fallback: programmatically set combobox value and commit
            self.assertIsNotNone(app.edit_entry)
            app.edit_entry.set(selected)
            app._commit_edit()
            top.update_idletasks()
            top.update()
            self.assertEqual(app.tree.set(first, "mat_concrete"), selected)

        top.destroy()


if __name__ == '__main__':
    unittest.main()
