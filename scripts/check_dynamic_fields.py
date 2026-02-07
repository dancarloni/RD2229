from __future__ import annotations

from sections_app.ui.main_window import MainWindow

from sections_app.services.repository import CsvSectionSerializer, SectionRepository

repo = SectionRepository()
serializer = CsvSectionSerializer()

# Istanzia la MainWindow (ma non chiami mainloop) e nascondila
win = MainWindow(repo, serializer)
win.withdraw()

print("Tipo iniziale:", win.section_var.get())
print("Campi iniziali:", list(win.inputs.keys()))

# Cambia selezione a Circolare
win.section_var.set("Circolare")
win._on_section_change()
print("Dopo cambio -> Circolare, campi:", list(win.inputs.keys()))

# Cambia selezione a A T
win.section_var.set("A T")
win._on_section_change()
print("Dopo cambio -> A T, campi:", list(win.inputs.keys()))

# Torna a Rettangolare
win.section_var.set("Rettangolare")
win._on_section_change()
print("Dopo cambio -> Rettangolare, campi:", list(win.inputs.keys()))

# Pulisce il window
win.destroy()
print("Done")
