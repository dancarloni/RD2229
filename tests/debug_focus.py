import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from verification_table import VerificationTableApp
root=tk.Tk(); root.withdraw()
top=tk.Toplevel(root)
app=VerificationTableApp(top, initial_rows=1)
first=list(app.tree.get_children())[0]
top.update_idletasks(); top.update()
app._start_edit(first,'section')
print('after start_edit force_flag=', getattr(app,'_force_show_all_on_empty',None))
app.edit_entry.event_generate('<FocusIn>')
# process events
for i in range(10):
    top.update_idletasks(); top.update(); time.sleep(0.01)
    print('iter',i,'force_flag=',getattr(app,'_force_show_all_on_empty',None),'suggest_list=',None if app._suggest_list is None else app._suggest_list.size())
