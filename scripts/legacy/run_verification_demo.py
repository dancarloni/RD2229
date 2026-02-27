"""Legacy demo runner (Tkinter) moved to legacy location.

This file is a copy of the original demo and should only be run explicitly
when `RD2229_LEGACY_UI=1` is set or by invoking the script under `scripts/legacy/`.
"""

from __future__ import annotations

import logging
import tkinter as tk

from apps.sections.models.sections import CircularSection, RectangularSection, TSection
from apps.sections.services.repository import SectionRepository

try:
    from core_models.materials import Material, MaterialRepository
except Exception:  # pylint: disable=broad-exception-caught
    MaterialRepository = None
    Material = None

from verification_table import VerificationInput, VerificationTableWindow


def build_sample_sections(repo: SectionRepository) -> list[str]:
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
        VerificationInput(
            section_id="Rect 20x30",
            material_concrete="C120",
            material_steel="A500",
            n_homog=10.0,
            N=0.0,
            Mx=0.0,
            Ty=0.0,
            As_sup=1.2,
            As_inf=2.4,
            d_sup=40.0,
            d_inf=45.0,
            stirrup_step=20.0,
            stirrup_diameter=8.0,
            stirrup_material="A500",
            notes="demo1",
        ),
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
