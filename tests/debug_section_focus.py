import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from verification_table import VerificationTableApp
root=tk.Tk(); root.withdraw()
top=tk.Toplevel(root)
app=VerificationTableApp(top, initial_rows=1)
app.section_names=['SecA','SecB']
app.suggestions_map['section']=app.section_names
top.update_idletasks(); top.update()
first=list(app.tree.get_children())[0]
app._start_edit(first,'section')
# process events briefly
# Also call update_suggestions explicitly to simulate focus handlers
app._update_suggestions()
for i in range(5):
    top.update_idletasks(); top.update(); time.sleep(0.01)
    print('iter',i,'suggest_list size=',None if app._suggest_list is None else app._suggest_list.size())
# simulate focus in as test does
if app.edit_entry is not None:
    app.edit_entry.event_generate('<FocusIn>')
    for i in range(10):
        top.update_idletasks(); top.update(); time.sleep(0.01)
        print('after focus iter',i,'suggest_list size=',None if app._suggest_list is None else app._suggest_list.size())
print('final', 'suggest_box=', app._suggest_box, 'list_size=', None if app._suggest_list is None else app._suggest_list.size())
