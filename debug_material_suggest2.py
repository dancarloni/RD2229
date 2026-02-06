from verification_table import VerificationTableApp
import tkinter as tk, time
root=tk.Tk(); root.withdraw()
app = VerificationTableApp(root, initial_rows=1)
app.material_names = ['M1','M2','M3']
app.suggestions_map['mat_concrete']=app.material_names
first=list(app.tree.get_children())[0]
# Wrap commit to log
orig_commit = app._commit_edit
def _commit_and_log():
    print('*** commit called')
    return orig_commit()
app._commit_edit = _commit_and_log

try:
    e = app.create_editor_for_cell(first, 'mat_concrete')
    print('create_editor_for_cell returned', e)
except Exception as ex:
    print('create_editor_for_cell raised', ex)

app._start_edit(first,'mat_concrete')
print('edit_entry after start', app.edit_entry)
# call update directly
app._update_suggestions()
print('after direct update: suggest_box', app._suggest_box, 'list', app._suggest_list)
# call source manually
src = app.suggestions_map.get('mat_concrete')
print('source', src)
if callable(src):
    print('callable result', src(''))
else:
    print('list content', list(src))
# wait for scheduled retry
for i in range(20):
    root.update_idletasks(); root.update(); time.sleep(0.01)
    if app._suggest_list:
        print('retry created suggest_list size', app._suggest_list.size())
        break
print('final suggest_box', app._suggest_box, 'list', app._suggest_list)
print('force flag', getattr(app,'_force_show_all_on_empty',None))
