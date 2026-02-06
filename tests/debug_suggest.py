import tkinter as tk
import time
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from verification_table import VerificationTableApp

root=tk.Tk(); root.withdraw()
top=tk.Toplevel(root)
app=VerificationTableApp(top, initial_rows=1)
top.update_idletasks(); top.update()
print('app created')
app.section_names=["SecA","SecB"]
app.suggestions_map["section"] = app.section_names
first=list(app.tree.get_children())[0]
app._start_edit(first,"section")
print('after start_edit: force flag=', getattr(app,'_force_show_all_on_empty',False))
if app.edit_entry is not None:
    print('entry width=', app.edit_entry.winfo_width(), 'height=', app.edit_entry.winfo_height())
    # generate focusin
    app.edit_entry.event_generate('<FocusIn>')
    top.update_idletasks(); top.update()
    print('after focusin immediate: suggest_box=', app._suggest_box, 'suggest_list size=', app._suggest_list.size() if app._suggest_list else None)
    # install a patch to detect hide being invoked
    orig_hide = app._hide_suggestions
    def patched_hide(*a, **kw):
        import traceback
        print('patched _hide_suggestions called, stack:')
        traceback.print_stack(limit=10)
        return orig_hide(*a, **kw)
    app._hide_suggestions = patched_hide

    # call update explicitly
    app._update_suggestions()
    top.update_idletasks(); top.update()
    print('after explicit update: suggest_box=', app._suggest_box, 'suggest_list size=', app._suggest_list.size() if app._suggest_list else None)
    # inspect over a short period to see if/when the box disappears
    for i in range(50):
        top.update_idletasks(); top.update(); time.sleep(0.01)
        print('poll', i, 'suggest_box=', app._suggest_box, 'suggest_list size=', app._suggest_list.size() if app._suggest_list else None)
        if app._suggest_list and app._suggest_list.size()>0:
            break
    print('final: suggest_list size=', app._suggest_list.size() if app._suggest_list else None, 'suggest_box geometry=', app._suggest_box.geometry() if app._suggest_box else None)
else:
    print('no edit entry?')

# Now simulate the zero-width scenario
try:
    app.edit_entry.winfo_width = lambda: 0
    print('winfo_width after patch:', app.edit_entry.winfo_width())
    app._update_suggestions()
    top.update_idletasks(); top.update()
    if app._suggest_box is None:
        print('after zero-width update: suggest_box is None')
    else:
        print('after zero-width update: suggest_box viewable=', app._suggest_box.winfo_viewable())
except Exception as e:
    print('zero-width test error', e)

# keep window open briefly to allow manual inspection if running interactively
print('done')
