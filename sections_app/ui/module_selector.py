from __future__ import annotations

import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
from pathlib import Path

from sections_app.ui.main_window import MainWindow
from sections_app.ui.historical_main_window import HistoricalModuleMainWindow
from sections_app.ui.historical_material_window import HistoricalMaterialWindow
from sections_app.ui.section_manager import SectionManager
from verification_table import VerificationTableWindow
from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from core_models.materials import MaterialRepository
from historical_materials import HistoricalMaterialLibrary
from sections_app.models.sections import Section

logger = logging.getLogger(__name__)


class ModuleSelectorWindow(tk.Tk):
    """Finestra iniziale per selezionare il modulo da avviare."""

    def __init__(
        self,
        repository: SectionRepository,
        serializer: CsvSectionSerializer,
        material_repository: Optional[MaterialRepository] = None,
    ):
        # Forza locale msgcat su EN per evitare errori quando i file lingua non sono presenti
        os.environ.setdefault("LANG", "en_US")
        os.environ.setdefault("LC_ALL", "en_US")
        super().__init__()
        self.title("Module Selector - RD2229 Tools")
        self.geometry("1200x340")
        self.repository = repository
        self.serializer = serializer
        # For compatibility with modules expecting named attributes
        self.section_repository: SectionRepository = repository
        # Usa il material_repository passato, oppure creane uno nuovo
        self.material_repository: MaterialRepository = material_repository or MaterialRepository()
        self._material_editor_window: Optional[HistoricalMaterialWindow] = None
        # Riferimenti a finestre aperte dal ModuleSelector
        self._geometry_window: Optional[MainWindow] = None
        self._section_manager_window: Optional[SectionManager] = None
        self._create_menu()
        self._build_ui()

    def _create_menu(self) -> None:
        """Crea il menu della finestra."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Esporta backup...", command=self._export_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.quit)

    def _build_ui(self) -> None:
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        label = tk.Label(frame, text="Select a module to start", font=(None, 12, "bold"))
        label.pack(anchor="w", pady=(0, 8))

        modules_frame = tk.Frame(frame)
        modules_frame.pack(fill="both", expand=True)

        # Geometry Module (first, different padding)
        geom_desc = "Compute and manage section geometry\n(areas, centroids, inertia, drawings, CSV archive)"
        geom_frame = tk.LabelFrame(modules_frame, text="Geometry module")
        geom_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(geom_frame, text=geom_desc, justify="left", wraplength=220).pack(padx=8, pady=8)
        tk.Button(geom_frame, text="Open Geometry", command=self._open_geometry).pack(pady=(0, 8))

        # Historical Module
        hist_desc = "Historical allowable-stress verifications\n(stubs and data connectors for now)"
        self._add_module_frame(modules_frame, "Historical RD 2229 / Santarella", hist_desc, "Open Historical", self._open_historical)

        # Verification Table Module
        verify_desc = "Rapid data entry for multiple verifications\n(tabular grid with autocomplete)"
        self._add_module_frame(modules_frame, "Verification Table", verify_desc, "Open Verification Table", self._open_verification_table)

        # Sections Archive Module
        sections_desc = "Browse and manage archived sections (import/export, edit via Geometry)"
        self._add_module_frame(modules_frame, "Sections Archive", sections_desc, "Open Sections", self._open_section_manager)

        # Materials Editor Module (last)
        material_desc = "Manage and import historical materials\n(concrete, steel, and other material libraries)"
        material_frame = tk.LabelFrame(modules_frame, text="Materials Editor")
        material_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(material_frame, text=material_desc, justify="left", wraplength=220).pack(padx=8, pady=8)
        tk.Button(material_frame, text="Open Materials", command=self._open_material_editor).pack(pady=(0, 8))

    def _open_geometry(self) -> None:
        """Apre il modulo Geometry come finestra Toplevel.
        
        La finestra principale ModuleSelector rimane visibile in background.
        """
        logger.debug("Opening Geometry module")
        # Se la finestra è già aperta, portala in primo piano
        if self._geometry_window is not None and getattr(self._geometry_window, 'winfo_exists', None) and self._geometry_window.winfo_exists():
            try:
                self._geometry_window.lift()
                self._geometry_window.focus_force()
                logger.debug("Geometry window già aperta, portata in primo piano")
                return
            except Exception:
                pass

        # Crea la finestra Geometry e memorizza il riferimento
        win = MainWindow(self, self.repository, self.serializer, self.material_repository)
        self._geometry_window = win
        # Pulizia del riferimento quando la finestra viene chiusa
        try:
            win.protocol("WM_DELETE_WINDOW", lambda w=win: (setattr(self, "_geometry_window", None), w.destroy()))
            win.bind("<Destroy>", lambda e, w=win: setattr(self, "_geometry_window", None))
        except Exception:
            pass

    def _open_historical(self) -> None:
        """Apre il modulo Historical come finestra Toplevel.
        
        La finestra principale ModuleSelector rimane visibile in background.
        """
        logger.debug("Opening Historical module")
        # ✅ HistoricalModuleMainWindow è già un Toplevel
        win = HistoricalModuleMainWindow(self, self.repository)
        win.protocol("WM_DELETE_WINDOW", lambda: win.destroy())

    def _open_verification_table(self) -> None:
        """Apre il modulo Verification Table come finestra Toplevel.
        
        La finestra principale ModuleSelector rimane visibile in background.
        """
        logger.debug("Opening Verification Table module")
        # ✅ VerificationTableWindow è già un Toplevel
        win = VerificationTableWindow(
            master=self,
            section_repository=self.section_repository,
            material_repository=self.material_repository,
        )
        win.protocol("WM_DELETE_WINDOW", lambda: win.destroy())

    def _open_section_manager(self) -> None:
        """Apre il Section Manager come finestra Toplevel.

        Se la finestra è già aperta, la porta in primo piano.
        """
        logger.debug("Opening Section Manager module")
        # Se la finestra è già aperta, portala in primo piano
        if self._section_manager_window is not None and getattr(self._section_manager_window, 'winfo_exists', None) and self._section_manager_window.winfo_exists():
            try:
                self._section_manager_window.lift()
                self._section_manager_window.focus_force()
                logger.debug("Section Manager già aperto, portato in primo piano")
                return
            except Exception:
                pass

        # Crea nuova istanza del manager con callback on_edit che rimanda a Geometry
        manager = SectionManager(self, self.repository, self.serializer, self._on_section_edit)
        self._section_manager_window = manager
        # Assicura che quando il manager viene chiuso si rimuova il riferimento
        manager.protocol("WM_DELETE_WINDOW", lambda m=manager: (setattr(self, "_section_manager_window", None), m.destroy()))
        manager.bind("<Destroy>", lambda e, m=manager: setattr(self, "_section_manager_window", None))
        logger.debug("Section Manager aperto")

    def _on_section_edit(self, section: Section) -> None:
        """Callback invocata dal SectionManager quando l'utente richiede la modifica di una sezione.

        Apre il modulo Geometry (se necessario) e carica la sezione nel form. Tenta una creazione
        sincrona di fallback se la finestra non è pronta.
        """
        logger.debug("Forwarding edit to Geometry for section %s", getattr(section, 'id', None))
        # Prova ad aprire/portare in primo piano Geometry
        try:
            self._open_geometry()
        except Exception:
            logger.exception("Errore nell'aprire Geometry per edit sezione")

        # Se la finestra non è stata inizializzata dal metodo precedente, prova a crearla direttamente
        if getattr(self, "_geometry_window", None) is None:
            try:
                win = MainWindow(self, self.repository, self.serializer, self.material_repository)
                self._geometry_window = win
                try:
                    win.protocol("WM_DELETE_WINDOW", lambda w=win: (setattr(self, "_geometry_window", None), w.destroy()))
                    win.bind("<Destroy>", lambda e, w=win: setattr(self, "_geometry_window", None))
                except Exception:
                    pass
            except Exception:
                logger.exception("Fallback: impossibile creare Geometry window")

        gw = getattr(self, "_geometry_window", None)
        if gw is None or not getattr(gw, "load_section_into_form", None):
            # Programmiamo un ultimo tentativo asincrono e poi abbandoniamo
            try:
                self.after(50, lambda: self._on_section_edit(section))
            except Exception:
                logger.exception("Cannot schedule retry for loading section into Geometry")
            return

        # Carica la sezione nella finestra Geometry
        try:
            gw.load_section_into_form(section)
            gw.lift()
            gw.focus_force()
        except Exception:
            logger.exception("Errore caricamento sezione in Geometry")

    def _open_material_editor(self) -> None:
        """Apre il modulo Materials Editor come finestra Toplevel.
        
        Se la finestra è già aperta, la porta in primo piano.
        """
        logger.debug("Opening Material Editor module")
        # Se la finestra è già aperta, portala in primo piano
        if self._material_editor_window is not None and self._material_editor_window.winfo_exists():
            self._material_editor_window.lift()
            self._material_editor_window.focus()
            return
        
        # Crea la libreria dei materiali storici
        library = HistoricalMaterialLibrary()
        
        # Crea e mostra la finestra dell'editor materiali
        self._material_editor_window = HistoricalMaterialWindow(
            master=self,
            library=library,
            material_repository=self.material_repository
        )
        
        # Collega il callback di chiusura per pulire il riferimento e chiudere la finestra
        def on_material_editor_close():
            # Assicura che la finestra venga distrutta e il riferimento ripulito
            if self._material_editor_window is not None and self._material_editor_window.winfo_exists():
                try:
                    self._material_editor_window.destroy()
                except Exception:
                    pass
            self._material_editor_window = None

        # Imposta handler per la X della finestra che distrugge il Toplevel
        self._material_editor_window.protocol("WM_DELETE_WINDOW", on_material_editor_close)
        # Inoltre, se la finestra viene distrutta in altro modo, assicurati di pulire il riferimento
        self._material_editor_window.bind("<Destroy>", lambda e: on_material_editor_close())

    def _add_module_frame(self, parent, title: str, description: str, button_text: str, command: Callable) -> tk.LabelFrame:
        """Helper per creare un LabelFrame di modulo con descrizione e bottone."""
        frm = tk.LabelFrame(parent, text=title)
        frm.pack(side="left", fill="both", expand=True, padx=(6, 6))
        tk.Label(frm, text=description, justify="left", wraplength=220).pack(padx=8, pady=8)
        tk.Button(frm, text=button_text, command=command).pack(pady=(0, 8))
        return frm

    def _export_backup(self) -> None:
        """Gestisce l'esportazione del backup."""
        # Chiedi all'utente cosa esportare
        dialog = tk.Toplevel(self)
        dialog.title("Esporta backup")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        result = {"choice": None}
        
        def on_choice(choice: str):
            result["choice"] = choice
            dialog.destroy()
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(
            frame,
            text="Cosa vuoi esportare?",
            font=(None, 11, "bold")
        ).pack(pady=(0, 20))
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Sezioni",
            width=15,
            command=lambda: on_choice("sezioni")
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Materiali",
            width=15,
            command=lambda: on_choice("materiali")
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Entrambi",
            width=15,
            command=lambda: on_choice("entrambi")
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Annulla",
            width=15,
            command=dialog.destroy
        ).pack(pady=5)
        
        # Aspetta che l'utente scelga
        self.wait_window(dialog)
        
        if not result["choice"]:
            return
        
        # Determina il nome file predefinito e i filtri
        if result["choice"] == "sezioni":
            default_name = "backup_sezioni"
            filetypes = [
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        elif result["choice"] == "materiali":
            default_name = "backup_materiali"
            filetypes = [
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        else:  # entrambi
            default_name = "backup"
            filetypes = [
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        
        # Mostra il dialogo di salvataggio
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Esporta backup",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=filetypes
        )
        
        if not file_path:
            return
        
        # Esegui l'esportazione
        try:
            if result["choice"] == "sezioni":
                self.section_repository.export_backup(file_path)
                messagebox.showinfo(
                    "Export completato",
                    f"Backup sezioni esportato correttamente in:\n{file_path}",
                    parent=self
                )
            elif result["choice"] == "materiali":
                self.material_repository.export_backup(file_path)
                messagebox.showinfo(
                    "Export completato",
                    f"Backup materiali esportato correttamente in:\n{file_path}",
                    parent=self
                )
            else:  # entrambi
                # Salva in due file separati
                path_obj = Path(file_path)
                base_name = path_obj.stem
                extension = path_obj.suffix
                parent_dir = path_obj.parent
                
                # File sezioni
                sections_path = parent_dir / f"{base_name}_sezioni{extension}"
                self.section_repository.export_backup(sections_path)
                
                # File materiali
                materials_path = parent_dir / f"{base_name}_materiali.json"
                self.material_repository.export_backup(materials_path)
                
                messagebox.showinfo(
                    "Export completato",
                    f"Backup esportati correttamente:\n"
                    f"• Sezioni: {sections_path}\n"
                    f"• Materiali: {materials_path}",
                    parent=self
                )
        except Exception as e:
            logger.exception("Errore durante l'esportazione del backup")
            messagebox.showerror(
                "Errore",
                f"Errore durante l'esportazione:\n{str(e)}",
                parent=self
            )

