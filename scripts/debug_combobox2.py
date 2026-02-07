import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tkinter as tk

from verification_table import VerificationTableApp

root = tk.Tk()
root.withdraw()
app = VerificationTableApp(root, initial_rows=1)
app.material_names = ["C120", "C200"]
items = list(app.tree.get_children())
first = items[0]
app._start_edit(first, "mat_concrete")
cb = app.edit_entry
print("before set", cb.get())
cb.set("C200")
print("after set", cb.get())
# call update_idletasks to flush
root.update_idletasks()
root.update()
print("after update", cb.get())
# now commit
app._on_entry_commit_down(None)
items = list(app.tree.get_children())
print("rows", len(items))
print("row0 mat_concr", app.tree.set(items[0], "mat_concrete"))
print("row1 mat_concr", app.tree.set(items[1], "mat_concrete"))
root.destroy()
