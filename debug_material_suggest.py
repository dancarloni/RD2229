from verification_table import VerificationTableApp
import tkinter as tk, time
root=tk.Tk(); root.withdraw()
app = VerificationTableApp(root, initial_rows=1)
app.material_names = ['C1','C2']
app.suggestions_map['mat_concrete']=app.material_names
first=list(app.tree.get_children())[0]
# Wrap commit to see if it is called immediately
orig_commit = app._commit_edit
def _commit_and_log():
    print('commit called (wrapped)')
    return orig_commit()
app._commit_edit = _commit_and_log

try:
    app._start_edit(first,'mat_concrete')
    print('after start_edit: edit_entry', app.edit_entry)
except Exception as e:
    import traceback
    traceback.print_exc()
root.update_idletasks(); root.update(); time.sleep(0.05)
print('after 50ms: edit_entry', app.edit_entry)
print('suggest retry scheduled flag', getattr(app,'_suggest_retry_scheduled',False))
print('force flag', getattr(app,'_force_show_all_on_empty',None))
app._update_suggestions(); root.update_idletasks(); root.update(); time.sleep(0.05)
print('after manual update: suggest_box', app._suggest_box, 'suggest_list', app._suggest_list, 'list size', app._suggest_list.size() if app._suggest_list else None)
print('force flag now', getattr(app,'_force_show_all_on_empty',None))
