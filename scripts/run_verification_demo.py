"""Demo: apre la Verification Table e carica sezioni/materiali di test per verificare il flusso UI."""
from __future__ import annotations

import tkinter as tk
import logging
from typing import List

from sections_app.services.repository import SectionRepository
from sections_app.models.sections import RectangularSection, CircularSection, TSection

try:
    from core_models.materials import MaterialRepository, Material
except Exception:
    MaterialRepository = None
    Material = None

from verification_table import VerificationTableWindow, VerificationInput


def build_sample_sections(repo: SectionRepository) -> List[str]:
    rect = RectangularSection(name="Rect 20x30", width=20, height=30)
    circ = CircularSection(name="Circ d25", diameter=25)
    t_sec = TSection(name="T 40x5x8x25", flange_width=40, flange_thickness=5, web_thickness=8, web_height=25)
    for s in (rect, circ, t_sec):
        s.compute_properties()
        repo.add_section(s)
    return [s.name for s in repo.get_all_sections()]


class SimpleMatRepo:
    def __init__(self):
        self._m = [{"name": "C120"}, {"name": "C200"}, {"name": "A500"}]

    def get_all(self):
        return self._m

    def list_materials(self):
        return self._m


def build_sample_materials():
    if MaterialRepository is None or Material is None:
        return SimpleMatRepo()
    mr = MaterialRepository()
    mr.add(Material(name="C120", type="concrete"))
    mr.add(Material(name="C200", type="concrete"))
    mr.add(Material(name="A500", type="steel"))
    return mr


def main():
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    root.title("Verification demo launcher")

    section_repo = SectionRepository()
    material_repo = build_sample_materials()

    build_sample_sections(section_repo)

    win = VerificationTableWindow(master=root, section_repository=section_repo, material_repository=material_repo)

    # Add a few prefilled rows
    examples = [
        VerificationInput(section_id="Rect 20x30", material_concrete="C120", material_steel="A500", n_homog=10.0, N=0.0, M=0.0, T=0.0,
                          As_sup=1.2, As_inf=2.4, d_sup=40.0, d_inf=45.0, stirrup_step=20.0, stirrup_diameter=8.0, stirrup_material="A500", notes="demo1"),
        VerificationInput(section_id="Circ d25", material_concrete="C200", material_steel="A500", n_homog=15.0, N=1000.0, M=50.0, T=0.0,
                          As_sup=0.0, As_inf=0.0, d_sup=30.0, d_inf=35.0, stirrup_step=15.0, stirrup_diameter=6.0, stirrup_material="A500", notes="demo2"),
        VerificationInput(section_id="T 40x5x8x25", material_concrete="C120", material_steel="A500", n_homog=12.0, N=500.0, M=20.0, T=10.0,
                          As_sup=2.0, As_inf=2.0, d_sup=45.0, d_inf=45.0, stirrup_step=12.0, stirrup_diameter=8.0, stirrup_material="A500", notes="demo3"),
    ]

    # Ensure the frame has rows to update
    for _ in examples:
        win.app._add_row()

    for idx, ex in enumerate(examples):
        win.app.update_row_from_model(idx, ex)

    # bring window to front
    win.lift()
    win.focus_force()

    root.mainloop()


if __name__ == "__main__":
    main()
