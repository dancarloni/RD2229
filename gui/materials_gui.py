"""GUI minima per la gestione dei materiali (Tkinter).

La GUI è separata dalle routine di calcolo: chiama `materials_manager`
per le operazioni CRUD e non contiene logica di calcolo.

Nota: è una interfaccia di utilità leggera pensata per prototipazione.
"""
from __future__ import annotations

import logging
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from tools import materials_manager
from tkinter import filedialog
try:
    from sections_app.services.event_bus import (
        EventBus,
        MATERIALS_CLEARED,
        MATERIALS_ADDED,
        MATERIALS_UPDATED,
        MATERIALS_DELETED,
    )
except Exception:
    EventBus = None
    MATERIALS_CLEARED = MATERIALS_ADDED = MATERIALS_UPDATED = MATERIALS_DELETED = None
try:
    from materials_repository import MaterialsRepository
except Exception:
    MaterialsRepository = None
from tools.concrete_strength import compute_sigma_c_all, compute_allowable_shear

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "gui_operations.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Percorso canonico per il repository materiali (workspace-relative)
MATERIALS_REPO_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "mat_repository", "Mat_repository.jsonm")
)


class MaterialEditor(simpledialog.Dialog):
    def __init__(self, parent, title: str, material: Optional[dict] = None):
        self.material = material or {}
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Name:").grid(row=0, column=0, sticky="w")
        self.ent_name = tk.Entry(master)
        self.ent_name.grid(row=0, column=1)

        tk.Label(master, text="Type:").grid(row=1, column=0, sticky="w")
        self.var_type = tk.StringVar(value=self.material.get("type", "concrete"))
        tk.OptionMenu(master, self.var_type, "concrete", "steel").grid(row=1, column=1, sticky="we")

        tk.Label(master, text="Cement type:").grid(row=2, column=0, sticky="w")
        self.var_cement = tk.StringVar(value=self.material.get("cement_type", "normal"))
        tk.OptionMenu(master, self.var_cement, "normal", "high", "aluminous", "slow").grid(row=2, column=1, sticky="we")

        tk.Label(master, text="σ_c28 (Kg/cm²):").grid(row=3, column=0, sticky="w")
        self.ent_sigma = tk.Entry(master)
        self.ent_sigma.grid(row=3, column=1)

        tk.Label(master, text="Condition:").grid(row=4, column=0, sticky="w")
        self.var_condition = tk.StringVar(value=self.material.get("condition", "semplicemente_compresa"))
        tk.OptionMenu(
            master,
            self.var_condition,
            "semplicemente_compresa",
            "inflesse_presso_inflesse",
            "conglomerato_speciale",
        ).grid(row=4, column=1, sticky="we")

        self.var_controlled = tk.BooleanVar(value=bool(self.material.get("controlled_quality", False)))
        tk.Checkbutton(master, text="Controlled quality", variable=self.var_controlled).grid(row=5, columnspan=2, sticky="w")

        tk.Label(master, text="Elastic modulus E (optional):").grid(row=6, column=0, sticky="w")
        self.ent_E = tk.Entry(master)
        self.ent_E.grid(row=6, column=1)
        self.var_E_defined = tk.BooleanVar(value=bool(self.material.get("E", None) is not None))
        tk.Checkbutton(master, text="E defined", variable=self.var_E_defined).grid(row=7, columnspan=2, sticky="w")

        # Preview area
        self.preview_label = tk.Label(master, text="Preview: no σ_c28 provided")
        self.preview_label.grid(row=8, column=0, columnspan=2, sticky="w")
        tk.Button(master, text="Preview", command=self.on_preview).grid(row=9, column=0, columnspan=2)

        # populate
        if self.material:
            self.ent_name.insert(0, self.material.get("name", ""))
            if self.material.get("sigma_c28") is not None:
                self.ent_sigma.insert(0, str(self.material.get("sigma_c28")))
            if self.material.get("E") is not None:
                self.ent_E.insert(0, str(self.material.get("E")))

        return self.ent_name

    def apply(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        mat = {
            "name": name,
            "type": self.var_type.get(),
            "cement_type": self.var_cement.get(),
            "condition": self.var_condition.get(),
            "controlled_quality": self.var_controlled.get(),
        }
        sigma = self.ent_sigma.get().strip()
        if sigma:
            try:
                mat["sigma_c28"] = float(sigma)
            except ValueError:
                messagebox.showerror("Error", "σ_c28 must be numeric")
                return
        e_value = self.ent_E.get().strip()
        if e_value:
            try:
                mat["E"] = float(e_value)
                mat["E_defined"] = bool(self.var_E_defined.get())
            except ValueError:
                messagebox.showerror("Error", "E must be numeric")
                return
        # materials_manager calcolerà i valori derivati (sigma_c, tau) al salvataggio
        self.result = mat

    def on_preview(self):
        sigma = self.ent_sigma.get().strip()
        if not sigma:
            messagebox.showinfo("Preview", "Immetti σ_c28 per ottenere anteprima dei limiti.")
            return
        try:
            s28 = float(sigma)
        except ValueError:
            messagebox.showerror("Error", "σ_c28 must be numeric")
            return
        cement_key = self.var_cement.get()
        from tools.concrete_strength import CementType

        if cement_key == "aluminous":
            cement = CementType.ALUMINOUS
        elif cement_key == "high":
            cement = CementType.HIGH
        elif cement_key == "slow":
            cement = CementType.SLOW
        else:
            cement = CementType.NORMAL
        controlled = bool(self.var_controlled.get())
        sigma_all = compute_sigma_c_all(s28, cement, controlled)
        service_tau, max_tau = compute_allowable_shear(cement)
        # compute elastic moduli using sigma_c28
        from tools.concrete_strength import compute_ec, compute_gc, compute_ec_conventional

        ec = compute_ec(s28)
        ec_conv = compute_ec_conventional(s28, cement)
        g_min, g_mean, g_max = compute_gc(ec) if ec is not None else (None, None, None)
        
        # Get calculated sigma values
        sigma_c_simple = sigma_all.get('semplice')
        sigma_c_inflessa = sigma_all.get('inflessa')
        
        # Historical resistance limits (from image)
        # Traction: 15-20 kg/cm², circa 1/9-1/10 of compression resistance
        sigma_t_min = round(sigma_c_simple / 10) if sigma_c_simple else None
        sigma_t_max = round(sigma_c_simple / 9) if sigma_c_simple else None
        # Flexural traction: circa 1/4-1/5 of compression resistance
        sigma_tf_min = round(sigma_c_simple / 5) if sigma_c_simple else None
        sigma_tf_max = round(sigma_c_simple / 4) if sigma_c_simple else None

        txt_lines = [f"σ_c28={s28} Kg/cm²"]
        txt_lines.append(f"σ_c (semplice) = {sigma_c_simple} Kg/cm²")
        txt_lines.append(f"σ_c (inflesse) = {sigma_c_inflessa} Kg/cm²")
        txt_lines.append(f"tau service = {service_tau} Kg/cm², tau max = {max_tau} Kg/cm²")
        txt_lines.append(f"")
        txt_lines.append(f"MODULI ELASTICI:")
        if ec is not None:
            txt_lines.append(f"E_c (calcolato) = {ec} Kg/cm²")
        if ec_conv is not None:
            txt_lines.append(f"E_c (convenzionale) = {ec_conv} Kg/cm²")
            if ec is not None:
                diff = abs(ec - ec_conv)
                perc = round(100 * diff / ec_conv) if ec_conv != 0 else 0
                txt_lines.append(f"  → Differenza: {diff} Kg/cm² ({perc}%)")
        if g_min and g_max:
            txt_lines.append(f"G_c = {g_mean} Kg/cm² (range: {g_min} ÷ {g_max})")
        if sigma_t_min and sigma_t_max:
            txt_lines.append(f"")
            txt_lines.append(f"LIMITI STORICI:")
            txt_lines.append(f"σ_t (trazione) = {sigma_t_min}÷{sigma_t_max} Kg/cm² (≈1/10÷1/9 σ_c)")
            txt_lines.append(f"σ_tf (flessione) = {sigma_tf_min}÷{sigma_tf_max} Kg/cm² (≈1/5÷1/4 σ_c)")
            txt_lines.append(f"σ_taglio ≈ poco maggiore di σ_t")

        # if user didn't provide E, propose the computed value in the E entry
        try:
            current_e = self.ent_E.get().strip()
            if (not current_e) and (ec is not None):
                # insert without moving cursor if possible
                self.ent_E.delete(0, tk.END)
                self.ent_E.insert(0, f"{ec}")
                self.var_E_defined.set(False)
        except Exception:
            pass

        self.preview_label.config(text="\n".join(txt_lines))


class MaterialsApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        # repository that holds current materials in-memory
        self.repo = MaterialsRepository() if MaterialsRepository is not None else None
        # current loaded materials file path (canonical repository)
        self.current_materials_path: Optional[str] = MATERIALS_REPO_PATH
        self.create_widgets()
        
        # If repo exists, attempt to load canonical repository automatically
        if self.repo is not None:
            try:
                if os.path.exists(MATERIALS_REPO_PATH):
                    # Load from canonical file
                    self.repo.load_from_jsonm(MATERIALS_REPO_PATH)
                else:
                    # Preload defaults into repo if empty
                    if not self.repo.get_all():
                        default = materials_manager.list_materials()
                        if default:
                            self.repo._materials = [m.copy() for m in default]
                            # Create directory and save to canonical path
                            try:
                                os.makedirs(os.path.dirname(MATERIALS_REPO_PATH), exist_ok=True)
                                self.repo.save_to_jsonm(MATERIALS_REPO_PATH)
                            except Exception:
                                logger.exception("Impossibile salvare il repository iniziale su %s", MATERIALS_REPO_PATH)
            except Exception:
                # ignore and proceed
                logger.exception("Errore caricamento repository materiali all'avvio")
        
        self.refresh_list()

    def create_widgets(self):
        toolbar = tk.Frame(self)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="Add", command=self.on_add).pack(side="left")
        tk.Button(toolbar, text="Edit", command=self.on_edit).pack(side="left")
        tk.Button(toolbar, text="Delete", command=self.on_delete).pack(side="left")
        tk.Button(toolbar, text="Refresh", command=self.refresh_list).pack(side="left")
        tk.Button(toolbar, text="Carica lista materiali", command=self.on_load_list).pack(side="left", padx=(8,0))
        tk.Button(toolbar, text="Salva lista materiali", command=self.on_save_list).pack(side="left")

        # Filters frame
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill="x", pady=4)
        tk.Label(filter_frame, text="Filter name:").pack(side="left")
        self.var_filter_name = tk.StringVar(value="")
        tk.Entry(filter_frame, textvariable=self.var_filter_name, width=18).pack(side="left", padx=4)
        tk.Label(filter_frame, text="Cement:").pack(side="left")
        self.var_filter_cement = tk.StringVar(value="")
        tk.OptionMenu(filter_frame, self.var_filter_cement, "", "normal", "high", "aluminous").pack(side="left", padx=4)
        tk.Label(filter_frame, text="min σ_c28:").pack(side="left")
        self.var_filter_min_sigma = tk.StringVar(value="")
        tk.Entry(filter_frame, textvariable=self.var_filter_min_sigma, width=8).pack(side="left", padx=4)
        tk.Button(filter_frame, text="Apply", command=self.apply_filters).pack(side="left", padx=6)
        tk.Button(filter_frame, text="Clear", command=self.clear_filters).pack(side="left")

        # Table view with headers
        cols = (
            "name",
            "cement",
            "sigma_c28",
            "E_user",
            "E_calc",
            "E_conv",
            "G_min",
            "G_max",
            "sigma_simple",
            "sigma_inflessa",
            "sigma_presso",
            "tau_service",
            "tau_max",
            "E_defined",
        )
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        self.tree.pack(fill="both", expand=True)

        # define headings
        # add heading text + clickable sort command
        self._sort_column = None
        self._sort_reverse = False
        self.tree.heading("name", text="Name", command=lambda c="name": self.sort_by(c))
        self.tree.heading("cement", text="Cement", command=lambda c="cement": self.sort_by(c))
        self.tree.heading("sigma_c28", text="σ_c,28 (Kg/cm²)", command=lambda c="sigma_c28": self.sort_by(c))
        self.tree.heading("E_user", text="E (utente)", command=lambda c="E_user": self.sort_by(c))
        self.tree.heading("E_calc", text="E_c calc (Kg/cm²)", command=lambda c="E_calc": self.sort_by(c))
        self.tree.heading("E_conv", text="E_c conv (Kg/cm²)", command=lambda c="E_conv": self.sort_by(c))
        self.tree.heading("G_min", text="G_c min", command=lambda c="G_min": self.sort_by(c))
        self.tree.heading("G_max", text="G_c max", command=lambda c="G_max": self.sort_by(c))
        self.tree.heading("sigma_simple", text="σ_c (semplice)", command=lambda c="sigma_simple": self.sort_by(c))
        self.tree.heading("sigma_inflessa", text="σ_c (inflesse)", command=lambda c="sigma_inflessa": self.sort_by(c))
        self.tree.heading("sigma_presso", text="σ_c (presso-inflesse)", command=lambda c="sigma_presso": self.sort_by(c))
        self.tree.heading("tau_service", text="tau service", command=lambda c="tau_service": self.sort_by(c))
        self.tree.heading("tau_max", text="tau max", command=lambda c="tau_max": self.sort_by(c))
        self.tree.heading("E_defined", text="E defined", command=lambda c="E_defined": self.sort_by(c))

        # set reasonable column widths
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("cement", width=90, anchor="center")
        self.tree.column("sigma_c28", width=90, anchor="e")
        self.tree.column("E_user", width=90, anchor="e")
        self.tree.column("E_calc", width=110, anchor="e")
        self.tree.column("E_conv", width=110, anchor="e")
        self.tree.column("G_min", width=90, anchor="e")
        self.tree.column("G_max", width=90, anchor="e")
        self.tree.column("sigma_simple", width=110, anchor="e")
        self.tree.column("sigma_inflessa", width=110, anchor="e")
        self.tree.column("sigma_presso", width=140, anchor="e")
        self.tree.column("tau_service", width=90, anchor="e")
        self.tree.column("tau_max", width=90, anchor="e")
        self.tree.column("E_defined", width=70, anchor="center")

        self.detail = tk.Text(self, height=6)
        self.detail.pack(fill="x")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.show_selected())

    def apply_filters(self):
        logger.info("Applicazione filtri alla lista materiali")
        self.refresh_list()

    def clear_filters(self):
        logger.info("Pulizia filtri lista materiali")
        self.var_filter_name.set("")
        self.var_filter_cement.set("")
        self.var_filter_min_sigma.set("")
        self.refresh_list()

    def sort_by(self, column: str):
        logger.info(f"Ordinamento lista per colonna: {column}")
        # toggle reverse if same column
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False
        self.refresh_list()

    def refresh_list(self):
        logger.info("Aggiornamento lista materiali")
        # clear tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        if self.repo is not None:
            mats = self.repo.get_all()
        else:
            try:
                mats = materials_manager.list_materials(self.current_materials_path)
            except Exception:
                mats = materials_manager.list_materials()
        logger.info(f"Elenco materiali aggiornato: {len(mats)} materiali trovati")
        for m in mats:
            name = m.get("name")
            s28 = m.get("sigma_c28")
            e_user = m.get("E") if m.get("E_defined") else None
            e_calc = m.get("E_calculated")
            e_conv = m.get("E_conventional")
            g_min = m.get("G_min")
            g_max = m.get("G_max")
            s_simple = m.get("sigma_c_simple")
            s_infl = m.get("sigma_c_inflessa")
            s_preso = m.get("sigma_c_presso_inflessa")
            tau = m.get("tau_service")
            tau_max = m.get("tau_max")
            cement = m.get("cement_type")
            e_defined = m.get("E_defined", False)
            values = (
                name,
                cement,
                f"{s28 if s28 is not None else ''}",
                f"{e_user if e_user is not None else ''}",
                f"{e_calc if e_calc is not None else ''}",
                f"{e_conv if e_conv is not None else ''}",
                f"{g_min if g_min is not None else ''}",
                f"{g_max if g_max is not None else ''}",
                f"{s_simple if s_simple is not None else ''}",
                f"{s_infl if s_infl is not None else ''}",
                f"{s_preso if s_preso is not None else ''}",
                f"{tau if tau is not None else ''}",
                f"{tau_max if tau_max is not None else ''}",
                f"{e_defined}",
            )
            # use name as iid so we can easily look up
            try:
                self.tree.insert("", tk.END, iid=name, values=values)
            except Exception:
                # fallback if name contains characters not allowed as iid
                self.tree.insert("", tk.END, values=values)
        self.detail.delete("1.0", tk.END)

    def get_selected_name(self) -> Optional[str]:
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        # if iid was set to name, return it; else get first column value
        if iid and iid in self.tree.item(iid).get("values", []):
            return iid
        vals = self.tree.item(iid).get("values", [])
        if vals:
            return str(vals[0])
        return None

    def show_selected(self):
        name = self.get_selected_name()
        self.detail.delete("1.0", tk.END)
        if not name:
            return
        logger.info(f"Visualizzazione dettagli materiale: {name}")
        if self.repo is not None:
            m = self.repo.get_by_name(name)
        else:
            try:
                m = materials_manager.get_material(name, self.current_materials_path)
            except Exception:
                m = materials_manager.get_material(name)
        if m:
            import json

            self.detail.insert(tk.END, json.dumps(m, indent=2, ensure_ascii=False))

    def on_add(self):
        logger.info("Avvio aggiunta nuovo materiale")
        dlg = MaterialEditor(self.master, "Add material")
        mat = getattr(dlg, "result", None)
        if mat:
            try:
                if self.repo is not None:
                    self.repo.add(mat)
                    # Autosave to canonical path
                    try:
                        os.makedirs(os.path.dirname(MATERIALS_REPO_PATH), exist_ok=True)
                        self.repo.save_to_jsonm(MATERIALS_REPO_PATH)
                    except Exception:
                        logger.exception("Errore autosalvataggio repository dopo add")
                    logger.info(f"Materiale aggiunto (repo): {mat.get('name')}")
                else:
                    materials_manager.add_material(mat, self.current_materials_path)
                    logger.info(f"Materiale aggiunto: {mat.get('name')}")
                    if EventBus is not None:
                        try:
                            EventBus().emit(MATERIALS_ADDED, material_id=mat.get('id') or mat.get('name'), material_name=mat.get('name'))
                        except Exception:
                            logger.exception("Errore emissione EventBus dopo add")
                self.refresh_list()
            except Exception as exc:
                logger.error(f"Errore nell'aggiunta del materiale {mat.get('name')}: {str(exc)}")
                messagebox.showerror("Error", str(exc))

    def on_edit(self):
        name = self.get_selected_name()
        if not name:
            logger.warning("Tentativo di modifica senza selezione")
            messagebox.showinfo("Info", "Select a material first")
            return
        logger.info(f"Avvio modifica materiale: {name}")
        if self.repo is not None:
            m = self.repo.get_by_name(name)
        else:
            m = materials_manager.get_material(name, self.current_materials_path)
        if not m:
            logger.error(f"Materiale non trovato per modifica: {name}")
            messagebox.showerror("Error", "Material not found")
            return
        dlg = MaterialEditor(self.master, f"Edit {name}", material=m)
        mat = getattr(dlg, "result", None)
        if mat:
            try:
                updates = mat
                if self.repo is not None:
                    self.repo.update(name, updates)
                    # Autosave to canonical path
                    try:
                        self.repo.save_to_jsonm(MATERIALS_REPO_PATH)
                    except Exception:
                        logger.exception("Errore autosalvataggio repository dopo update")
                    logger.info(f"Materiale modificato (repo): {name} -> {mat.get('name')}")
                else:
                    materials_manager.update_material(name, updates, self.current_materials_path)
                    logger.info(f"Materiale modificato: {name} -> {mat.get('name')}")
                    if EventBus is not None:
                        try:
                            EventBus().emit(MATERIALS_UPDATED, material_id=updates.get('id') or updates.get('name') or name, material_name=updates.get('name') or name)
                        except Exception:
                            logger.exception("Errore emissione EventBus dopo update")
                self.refresh_list()
            except Exception as exc:
                logger.error(f"Errore nella modifica del materiale {name}: {str(exc)}")
                messagebox.showerror("Error", str(exc))

    def on_delete(self):
        name = self.get_selected_name()
        if not name:
            logger.warning("Tentativo di cancellazione senza selezione")
            messagebox.showinfo("Info", "Select a material first")
            return
        if messagebox.askyesno("Confirm", f"Delete material '{name}'?"):
            try:
                if self.repo is not None:
                    self.repo.delete(name)
                    # Autosave to canonical path
                    try:
                        self.repo.save_to_jsonm(MATERIALS_REPO_PATH)
                    except Exception:
                        logger.exception("Errore autosalvataggio repository dopo delete")
                    logger.info(f"Materiale cancellato (repo): {name}")
                else:
                    materials_manager.delete_material(name, self.current_materials_path)
                    logger.info(f"Materiale cancellato: {name}")
                    if EventBus is not None:
                        try:
                            EventBus().emit(MATERIALS_DELETED, material_id=name, material_name=name)
                        except Exception:
                            logger.exception("Errore emissione EventBus dopo delete")
                self.refresh_list()
            except Exception as exc:
                logger.error(f"Errore nella cancellazione del materiale {name}: {str(exc)}")
                messagebox.showerror("Error", str(exc))

    def on_load_list(self):
        """Carica la lista materiali dal percorso canonico MATERIALS_REPO_PATH.

        - Carica dal file canonico mat_repository/Mat_repository.jsonm
        - Se il file non esiste, mostra info messagebox
        - Emette eventi EventBus per notificare altre finestre (es. VerificationTable)
        """
        path = MATERIALS_REPO_PATH
        if not os.path.exists(path):
            messagebox.showinfo("Carica lista materiali", f"Nessun file materiali trovato in {path}")
            return
        try:
            if self.repo is not None:
                mats = self.repo.load_from_jsonm(path)
            else:
                mats = materials_manager.load_materials(path)
            # Set current path
            self.current_materials_path = path
            # Refresh UI
            self.refresh_list()
            # Notify other windows via EventBus
            if EventBus is not None:
                try:
                    bus = EventBus()
                    bus.emit(MATERIALS_CLEARED)
                    for m in mats:
                        bus.emit(MATERIALS_ADDED, material_id=m.get('id') or m.get('name'), material_name=m.get('name'))
                except Exception:
                    logger.exception("Errore emissione eventi EventBus dopo caricamento materiali")
        except Exception as e:
            logger.exception("Errore caricamento materiali da %s: %s", path, e)
            messagebox.showerror("Carica lista materiali", f"Errore caricamento file: {e}")

    def on_save_list(self):
        """Salva la lista corrente di materiali nel percorso canonico MATERIALS_REPO_PATH."""
        path = MATERIALS_REPO_PATH
        try:
            if self.repo is not None:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                self.repo.save_to_jsonm(path)
            else:
                mats = materials_manager.list_materials(self.current_materials_path)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                materials_manager.save_materials(mats, path)
            # Update current path
            self.current_materials_path = path
            # Notify others (clear + add) so UI suggestions update
            if EventBus is not None:
                try:
                    bus = EventBus()
                    bus.emit(MATERIALS_CLEARED)
                    if self.repo is not None:
                        mats = self.repo.get_all()
                    else:
                        mats = materials_manager.list_materials(path)
                    for m in mats:
                        bus.emit(MATERIALS_ADDED, material_id=m.get('id') or m.get('name'), material_name=m.get('name'))
                except Exception:
                    logger.exception("Errore emissione eventi EventBus dopo salvataggio materiali")
            messagebox.showinfo("Salva lista materiali", f"Lista salvata in {path}")
        except Exception as e:
            logger.exception("Errore salvataggio materiali in %s: %s", path, e)
            messagebox.showerror("Salva lista materiali", f"Errore salvataggio file: {e}")


def run_app():
    logger.info("Avvio applicazione GUI Materials Manager")
    root = tk.Tk()
    root.title("Materials Manager")
    app = MaterialsApp(master=root)
    root.geometry("640x480")
    root.mainloop()
    logger.info("Chiusura applicazione GUI Materials Manager")


if __name__ == "__main__":
    run_app()

