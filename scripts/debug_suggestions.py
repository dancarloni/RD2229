import tkinter as tk

from sections_app.ui.main_window import ModuleSelectorWindow

from verification_table import VerificationTableWindow

root = tk.Tk()
root.withdraw()

sel = ModuleSelectorWindow(None, None, material_repository=None)
sel.update_idletasks()
sel.update()
sel._open_material_editor()
sel.update_idletasks()
sel.update()
sel._material_editor_window.destroy()
sel.update_idletasks()
sel.update()

vt = VerificationTableWindow(sel, section_repository=None, material_repository=None)
app = vt.app
vt.update_idletasks()
vt.update()
item = list(app.tree.get_children())[0]

app._start_edit(item, "mat_concrete")
app.edit_entry.delete(0, tk.END)
app.edit_entry.insert(0, "160")
app._update_suggestions()
vt.update_idletasks()
vt.update()
print("concrete suggest list exists:", app._suggest_list is not None)
if app._suggest_list is not None:
    print([app._suggest_list.get(i) for i in range(app._suggest_list.size())][:10])

app._start_edit(item, "mat_steel")
app.edit_entry.delete(0, tk.END)
app.edit_entry.insert(0, "38")
app._update_suggestions()
vt.update_idletasks()
vt.update()
print("steel suggest list exists:", app._suggest_list is not None)
if app._suggest_list is not None:
    print([app._suggest_list.get(i) for i in range(app._suggest_list.size())][:10])

vt.destroy()
root.destroy()
