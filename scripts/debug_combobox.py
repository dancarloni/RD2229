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
print("editor type", type(cb))
cb.set("C200")
print("cb.get()", cb.get())
app._on_entry_commit_down(None)
items = list(app.tree.get_children())
print("rows:", len(items))
print("row0 mat_concrete:", app.tree.set(items[0], "mat_concrete"))
print("row1 mat_concrete:", app.tree.set(items[1], "mat_concrete"))
root.destroy()
