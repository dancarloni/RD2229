import time
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from verification_table import VerificationTableApp

root = tk.Tk()
root.withdraw()
top = tk.Toplevel(root)
app = VerificationTableApp(top, initial_rows=1)
top.update_idletasks()
top.update()
app.material_names = ["C120","C200"]
app.suggestions_map['mat_concrete'] = app.material_names
first = list(app.tree.get_children())[0]
app._start_edit(first,'mat_concrete')
# process events a few times
for _ in range(10):
    top.update_idletasks()
    top.update()
    time.sleep(0.01)
print('suggest_box:', app._suggest_box)
if app._suggest_list is None:
    print('suggest_list is None')
else:
    print('items:', [app._suggest_list.get(i) for i in range(app._suggest_list.size())])
# try calling update_suggestions explicitly
print('calling _update_suggestions explicitly')
print('edit_entry:', getattr(app,'edit_entry',None))
print('edit_column:', getattr(app,'edit_column',None))
app._update_suggestions()
for _ in range(10):
    top.update_idletasks()
    top.update()
    time.sleep(0.01)
print('after explicit call suggest_box:', app._suggest_box)
if app._suggest_list is None:
    print('after explicit call suggest_list is None')
else:
    print('after explicit call items:', [app._suggest_list.get(i) for i in range(app._suggest_list.size())])
# close
try: top.destroy()
except: pass
try: root.destroy()
except: pass
