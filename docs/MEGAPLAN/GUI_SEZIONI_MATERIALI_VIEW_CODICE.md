
GUI – SezioniMaterialiView (Codice Completo)
Status: FILE OPERATIVO – TKINTER
Questo file contiene tutto il codice necessario per la View SezioniMaterialiView, coerente con l’architettura GUI NTC2018 definita nel canvas.
Caratteristiche:

selezione read‑only da archivi esistenti di materiali e sezioni;
caricamento automatico di proprietà geometriche e meccaniche (solo visualizzazione);
aggiornamento esclusivo del ProjectModel;
nessuna formula e nessuna norma applicata in GUI.


1. Dipendenze e contratti (vincolanti)

GUI: Python + Tkinter (ttk)
Pattern: MVC semplificato
Archivi: repository read‑only già presenti
Contratti minimi richiesti:

ProjectModel
MaterialiRepository
SezioniRepository


2. Codice – gui/views/sezioni_materiali.py

import tkinter as tk
from tkinter import ttk, messagebox


class SezioniMaterialiView(ttk.Frame):
    """
    View GUI per la selezione di:
    - Materiale (da archivio read-only)
    - Sezione (da archivio read-only)

    Responsabilità:
    - presentare i dati
    - aggiornare ProjectModel

    Non contiene:
    - formule
    - norme
    - logica di verifica
    """

    def __init__(self, parent, project_model, materiali_repo, sezioni_repo):
        super().__init__(parent)

        self.project_model = project_model
        self.materiali_repo = materiali_repo
        self.sezioni_repo = sezioni_repo

        self.selected_materiale = None
        self.selected_sezione = None

        self._build_ui()

    # ------------------------------------------------------------------
    # UI BUILD
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self._build_materiali_panel()
        self._build_sezioni_panel()
        self._build_actions_panel()

    def _build_materiali_panel(self):
        frame = ttk.LabelFrame(self, text="Materiale")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame, text="Seleziona materiale:").grid(row=0, column=0, sticky="w")

        self.materiale_combo = ttk.Combobox(
            frame,
            state="readonly",
            values=self.materiali_repo.list_names(),
        )
        self.materiale_combo.grid(row=1, column=0, sticky="ew")
        self.materiale_combo.bind("<<ComboboxSelected>>", self._on_materiale_selected)

        self.materiale_info = tk.Text(
            frame, height=10, width=45, state="disabled"
        )
        self.materiale_info.grid(row=2, column=0, pady=5, sticky="nsew")

        frame.columnconfigure(0, weight=1)

    def _build_sezioni_panel(self):
        frame = ttk.LabelFrame(self, text="Sezione")
        frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame, text="Seleziona sezione:").grid(row=0, column=0, sticky="w")

        self.sezione_combo = ttk.Combobox(
            frame,
            state="readonly",
            values=self.sezioni_repo.list_names(),
        )
        self.sezione_combo.grid(row=1, column=0, sticky="ew")
        self.sezione_combo.bind("<<ComboboxSelected>>", self._on_sezione_selected)

        self.sezione_info = tk.Text(
            frame, height=10, width=45, state="disabled"
        )
        self.sezione_info.grid(row=2, column=0, pady=5, sticky="nsew")

        frame.columnconfigure(0, weight=1)

    def _build_actions_panel(self):
        frame = ttk.Frame(self)
        frame.grid(row=1, column=0, columnspan=2, pady=10)

        assign_btn = ttk.Button(
            frame, text="Assegna a progetto ▶", command=self._assign_to_project
        )
        assign_btn.pack()

    # ------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------

    def _on_materiale_selected(self, event=None):
        name = self.materiale_combo.get()
        materiale = self.materiali_repo.get_by_name(name)

        if materiale is None:
            return

        self.selected_materiale = materiale
        self._show_materiale_info(materiale)

    def _on_sezione_selected(self, event=None):
        name = self.sezione_combo.get()
        sezione = self.sezioni_repo.get_by_name(name)

        if sezione is None:
            return

        self.selected_sezione = sezione
        self._show_sezione_info(sezione)

    def _assign_to_project(self):
        if self.selected_materiale is None or self.selected_sezione is None:
            messagebox.showerror(
                "Errore",
                "È necessario selezionare sia un materiale che una sezione.",
            )
            return

        self.project_model.materiale = self.selected_materiale
        self.project_model.sezione = self.selected_sezione

        messagebox.showinfo(
            "Assegnazione completata",
            "Materiale e sezione assegnati correttamente al progetto.",
        )

    # ------------------------------------------------------------------
    # RENDERING (READ-ONLY)
    # ------------------------------------------------------------------

    def _show_materiale_info(self, materiale):
        text = (
            f"Classe: {materiale.classe}\n\n"
            f"Modulo elastico E: {materiale.E}\n"
            f"Resistenza caratteristica: {materiale.fk}\n"
            f"Coefficiente γ: {materiale.gamma}\n"
            f"Normativa: {materiale.normativa}"
        )
        self._update_text(self.materiale_info, text)

    def _show_sezione_info(self, sezione):
        text = (
            f"Tipo: {sezione.tipo}\n\n"
            f"Area A: {sezione.A}\n"
            f"Ix: {sezione.Ix}\n"
            f"Iy: {sezione.Iy}\n"
            f"Wx: {sezione.Wx}\n"
            f"Wy: {sezione.Wy}\n"
            f"Baricentro: {sezione.baricentro}"
        )
        self._update_text(self.sezione_info, text)

    @staticmethod
    def _update_text(widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.configure(state="disabled")




3. Interfacce minime dei repository (vincolanti)
3.1 MaterialiRepository

class MaterialiRepository:
    def list_names(self) -> list[str]:
        """Ritorna l’elenco dei nomi/classe materiali disponibili."""
        raise NotImplementedError

    def get_by_name(self, name):
        """Ritorna l’oggetto materiale completo (read-only)."""
        raise NotImplementedError


3.2 SezioniRepository

class SezioniRepository:
    def list_names(self) -> list[str]:
        """Ritorna l’elenco dei nomi/codici sezione disponibili."""
        raise NotImplementedError

    def get_by_name(self, name):
        """Ritorna l’oggetto sezione completo (read-only)."""
        raise NotImplementedError




4. Estensioni richieste al ProjectModel

class ProjectModel:
    def __init__(self):
        self.materiale = None
        self.sezione = None
        # resto del modello già definito




5. Regole di sicurezza implementate

impossibile assegnare senza materiale + sezione;
proprietà non modificabili in GUI;
la normativa di verifica non influenza la scelta di sezione/materiale;
la GUI aggiorna solo il ProjectModel.


6. Stato
✅ Codice completo e pronto ✅ Allineato al workflow NTC2018 ✅ Integrabile subito in Tkinter ✅ Nessun refactor richiesto in seguito


Questo file è vincolante per l’implementazione della SezioniMaterialiView nel software NTC2018.
