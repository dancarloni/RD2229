from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from typing import Optional

from core_models.materials import MaterialRepository, Material

logger = logging.getLogger(__name__)


class FrcManagerWindow(tk.Toplevel):
    """Simple manager for FRC-enabled materials."""

    COLUMNS = [
        ("name", "Name"),
        ("type", "Type"),
        ("frc_enabled", "FRC"),
        ("frc_fFts", "fFts"),
        ("frc_fFtu", "fFtu"),
        ("frc_eps_fu", "eps_fu"),
        ("frc_note", "Note"),
    ]

    def __init__(self, master: tk.Misc, material_repository: Optional[MaterialRepository] = None) -> None:
        super().__init__(master)
        self.title("FRC Manager")
        self.geometry("900x420")
        self.material_repository = material_repository
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        frm = tk.Frame(self)
        frm.pack(fill="both", expand=True, padx=8, pady=8)

        cols = [c[0] for c in self.COLUMNS]
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=18)
        for key, label in self.COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=120, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=(6, 12))
        tk.Button(btn_frame, text="Aggiungi FRC...", command=self._on_add).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Modifica...", command=self._on_edit).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Toggle FRC", command=self._on_toggle_frc).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Chiudi", command=self.destroy).pack(side="right", padx=4)

        self.tree.bind("<Double-1>", lambda e: self._on_edit())

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if not self.material_repository:
            return
        for m in self.material_repository.get_all():
            values = [
                m.name,
                m.type,
                "Yes" if getattr(m, "frc_enabled", False) else "No",
                str(getattr(m, "frc_fFts", "")) or "",
                str(getattr(m, "frc_fFtu", "")) or "",
                str(getattr(m, "frc_eps_fu", "")) or "",
                getattr(m, "frc_note", "") or "",
            ]
            self.tree.insert("", "end", iid=m.id, values=values)

    def _on_add(self) -> None:
        if not self.material_repository:
            messagebox.showerror("Error", "Material repository not available")
            return
        dlg = _FrcEditDialog(self, title="Add FRC Material")
        self.wait_window(dlg)
        if dlg.result:
            mat = dlg.result
            # Ensure Material dataclass usage
            try:
                self.material_repository.add(mat)
                self._refresh()
            except Exception:
                logger.exception("Error adding material")
                messagebox.showerror("Error", "Could not add material")

    def _on_edit(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Edit", "Select a material first")
            return
        mid = sel[0]
        mat = self.material_repository.find_by_id(mid)
        if not mat:
            messagebox.showerror("Error", "Material not found")
            return
        dlg = _FrcEditDialog(self, title="Edit FRC Material", material=mat)
        self.wait_window(dlg)
        if dlg.result:
            try:
                # dlg.result is a Material
                self.material_repository.update(mid, dlg.result)
                self._refresh()
            except Exception:
                logger.exception("Error updating material %s", mid)
                messagebox.showerror("Error", "Could not update material")

    def _on_toggle_frc(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Toggle", "Select a material first")
            return
        mid = sel[0]
        mat = self.material_repository.find_by_id(mid)
        if not mat:
            messagebox.showerror("Error", "Material not found")
            return
        mat.frc_enabled = not getattr(mat, "frc_enabled", False)
        self.material_repository.update(mid, mat)
        self._refresh()


class _FrcEditDialog(simpledialog.Dialog):
    def __init__(self, parent, title: str, material: Optional[Material] = None):
        self.material = material
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Name:").grid(row=0, column=0, sticky="w")
        self.ent_name = tk.Entry(master)
        self.ent_name.grid(row=0, column=1)

        tk.Label(master, text="Type:").grid(row=1, column=0, sticky="w")
        self.var_type = tk.StringVar(value=(self.material.type if self.material else "frc"))
        tk.OptionMenu(master, self.var_type, "frc", "concrete", "steel").grid(row=1, column=1, sticky="we")

        self.var_enabled = tk.BooleanVar(value=bool(getattr(self.material, "frc_enabled", False)))
        tk.Checkbutton(master, text="FRC enabled", variable=self.var_enabled).grid(row=2, columnspan=2, sticky="w")

        tk.Label(master, text="fFts (design):").grid(row=3, column=0, sticky="w")
        self.ent_ffts = tk.Entry(master)
        self.ent_ffts.grid(row=3, column=1)

        tk.Label(master, text="fFtu (ultimate):").grid(row=4, column=0, sticky="w")
        self.ent_fftu = tk.Entry(master)
        self.ent_fftu.grid(row=4, column=1)

        tk.Label(master, text="eps_fu (ultimate strain):").grid(row=5, column=0, sticky="w")
        self.ent_eps = tk.Entry(master)
        self.ent_eps.grid(row=5, column=1)

        tk.Label(master, text="Note:").grid(row=6, column=0, sticky="w")
        self.ent_note = tk.Entry(master)
        self.ent_note.grid(row=6, column=1)

        if self.material:
            self.ent_name.insert(0, self.material.name)
            self.var_type.set(self.material.type)
            self.var_enabled.set(getattr(self.material, "frc_enabled", False))
            if getattr(self.material, "frc_fFts", None) is not None:
                self.ent_ffts.insert(0, str(self.material.frc_fFts))
            if getattr(self.material, "frc_fFtu", None) is not None:
                self.ent_fftu.insert(0, str(self.material.frc_fFtu))
            if getattr(self.material, "frc_eps_fu", None) is not None:
                self.ent_eps.insert(0, str(self.material.frc_eps_fu))
            self.ent_note.insert(0, getattr(self.material, "frc_note", ""))

        return self.ent_name

    def apply(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        mat = Material(
            name=name,
            type=self.var_type.get(),
            properties={},
            frc_enabled=bool(self.var_enabled.get()),
        )
        ff = self.ent_ffts.get().strip()
        if ff:
            try:
                mat.frc_fFts = float(ff)
            except ValueError:
                messagebox.showerror("Error", "fFts must be numeric")
                return
        fu = self.ent_fftu.get().strip()
        if fu:
            try:
                mat.frc_fFtu = float(fu)
            except ValueError:
                messagebox.showerror("Error", "fFtu must be numeric")
                return
        eps = self.ent_eps.get().strip()
        if eps:
            try:
                mat.frc_eps_fu = float(eps)
            except ValueError:
                messagebox.showerror("Error", "eps must be numeric")
                return
        mat.frc_note = self.ent_note.get().strip()
        # reuse code field as name-based id for readability
        self.result = mat
