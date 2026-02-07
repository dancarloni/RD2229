from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from src.core_calculus.core.verification_core import LoadCase, MaterialProperties, ReinforcementLayer, SectionGeometry
from src.core_calculus.core.verification_engine import VerificationEngine
from core_models.materials import Material, MaterialRepository


class FrcVerificationWindow(tk.Toplevel):
    """Simple window to run a quick verification with an FRC material."""

    def __init__(
        self, master: tk.Misc, material_repository: Optional[MaterialRepository] = None
    ) -> None:
        super().__init__(master)
        self.title("FRC Quick Verification")
        self.geometry("600x420")
        self.material_repository = material_repository
        self._build_ui()

    def _build_ui(self) -> None:
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)

        # Material selection
        tk.Label(frm, text="FRC Material:").grid(row=0, column=0, sticky="w")
        self.frc_var = tk.StringVar()
        self.frc_combo = ttk.Combobox(frm, textvariable=self.frc_var, width=40)
        self.frc_combo.grid(row=0, column=1, sticky="w")

        tk.Label(frm, text="FRC area (cm²):").grid(row=1, column=0, sticky="w")
        self.ent_area = tk.Entry(frm)
        self.ent_area.insert(0, "0.5")
        self.ent_area.grid(row=1, column=1, sticky="w")

        # Section geometry
        tk.Label(frm, text="Section width (b) cm:").grid(row=2, column=0, sticky="w")
        self.ent_b = tk.Entry(frm)
        self.ent_b.insert(0, "20.0")
        self.ent_b.grid(row=2, column=1, sticky="w")

        tk.Label(frm, text="Section height (h) cm:").grid(row=3, column=0, sticky="w")
        self.ent_h = tk.Entry(frm)
        self.ent_h.insert(0, "40.0")
        self.ent_h.grid(row=3, column=1, sticky="w")

        tk.Label(frm, text="Tensile As cm²:").grid(row=4, column=0, sticky="w")
        self.ent_As = tk.Entry(frm)
        self.ent_As.insert(0, "2.0")
        self.ent_As.grid(row=4, column=1, sticky="w")

        tk.Label(frm, text="As distance from top (d) cm:").grid(row=5, column=0, sticky="w")
        self.ent_d = tk.Entry(frm)
        self.ent_d.insert(0, "35.0")
        self.ent_d.grid(row=5, column=1, sticky="w")

        tk.Label(frm, text="Moment M (kg·cm):").grid(row=6, column=0, sticky="w")
        self.ent_M = tk.Entry(frm)
        self.ent_M.insert(0, "1000.0")
        self.ent_M.grid(row=6, column=1, sticky="w")

        tk.Button(frm, text="Load materials", command=self._load_materials).grid(
            row=0, column=2, padx=8
        )
        tk.Button(frm, text="Run verification", command=self._run).grid(
            row=7, column=1, pady=(10, 0)
        )

        self.output = tk.Text(self, height=10, width=80)
        self.output.pack(fill="both", padx=8, pady=8, expand=True)

        self._load_materials()

    def _load_materials(self) -> None:
        names = ["(none)"]
        if self.material_repository:
            for m in self.material_repository.get_all():
                names.append(f"{m.name} [{m.id[:6]}]")
        self.frc_combo["values"] = names
        if names:
            self.frc_combo.set(names[0])

    def _find_selected_material(self) -> Optional[Material]:
        sel = self.frc_var.get()
        if not sel or sel == "(none)":
            return None
        # parse id in brackets
        if "[" in sel:
            id_part = sel.split("[")[-1].rstrip("]")
            # find by id
            return self.material_repository.find_by_id(id_part)
        # fallback: find by name
        return self.material_repository.find_by_name(sel)

    def _run(self) -> None:
        try:
            b = float(self.ent_b.get())
            h = float(self.ent_h.get())
            As = float(self.ent_As.get())
            d = float(self.ent_d.get())
            M = float(self.ent_M.get())
            frc_area = float(self.ent_area.get())
        except ValueError:
            messagebox.showerror("Error", "Numeric values required")
            return

        section = SectionGeometry(width=b, height=h)
        As_layer = ReinforcementLayer(area=As, distance=d)
        As_p = ReinforcementLayer(area=1.0, distance=5.0)
        material = MaterialProperties(fck=160.0)
        loads = LoadCase(N=0.0, Mx=M)

        frc_mat = self._find_selected_material()

        engine = VerificationEngine(calculation_code="TA")
        res = engine.perform_verification(
            section, As_layer, As_p, material, loads, frc_material=frc_mat, frc_area=frc_area
        )

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Verification type: {res.verification_type}\n")
        self.output.insert(tk.END, f"Sigma concrete max: {res.stress_state.sigma_c_max}\n")
        self.output.insert(tk.END, f"Sigma steel tensile: {res.stress_state.sigma_s_tensile}\n")
        self.output.insert(tk.END, f"Sigma FRC equiv: {res.stress_state.sigma_frc}\n")
        self.output.insert(tk.END, f"Messages: {res.messages}\n")
