"""Module Selector Window for RD2229 Tools.

This module provides the main application window that allows users to select
and launch different modules of the RD2229 structural analysis toolkit.
Refactored to separate view, controller, and configuration for better modularity.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from tkinter import Tk, filedialog

from core_models.materials import MaterialRepository  # noqa: F401
from historical_materials import HistoricalMaterialLibrary  # noqa: F401
from sections_app.modules.registry import ModuleRegistry
from sections_app.services.notification import notify_error, notify_info
from sections_app.services.repository import CsvSectionSerializer, GeometryRepository
from sections_app.ui.code_settings_window import CodeSettingsWindow
from sections_app.ui.debug_viewer import DebugViewerWindow  # noqa: F401
from sections_app.ui.historical_main_window import HistoricalModuleMainWindow  # noqa: F401
from sections_app.ui.historical_material_window import HistoricalMaterialWindow  # noqa: F401
from sections_app.ui.main_window import MainWindow  # noqa: F401
from sections_app.ui.module_selector_view import ModuleCardSpec, ModuleSelectorView
from sections_app.ui.notification_center import NotificationCenter

logger = logging.getLogger(__name__)
# Massimo tentativi per riprovare a caricare una sezione in Geometry quando la finestra non è pronta
MAX_EDIT_LOAD_RETRIES = 6


class ModuleSelectorController:
    """Controller per la logica di selezione moduli e gestione dati."""

    def __init__(self):
        # Registry-based discovery of available modules
        self.registry = ModuleRegistry()
        self.open_windows = []
        self.windows_lock = threading.Lock()
        self.notification_center = None

    def _load_modules_config(self) -> dict[str, dict]:
        """Carica configurazione moduli da file JSON."""
        config_path = Path(__file__).parent / "modules_config.json"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        # Fallback predefinito se il file non esiste
        logger.warning("modules_config.json non trovato, uso configurazione predefinita.")
        return {
            "geometry": {
                "name": "Geometry Module",
                "class": "MainWindow",
                "description": "Modulo per calcoli geometrici di sezioni.",
            },
            "historical": {
                "name": "Historical Module",
                "class": "HistoricalModuleMainWindow",
                "description": "Modulo per materiali storici.",
            },
            "debug": {
                "name": "Debug Viewer",
                "class": "DebugViewerWindow",
                "description": "Visualizzatore di debug.",
            },
        }

    def get_available_modules(self):
        """Restituisce la lista di ModuleSpec disponibili dal registry."""
        return self.registry.get_specs()

    def refresh_modules(self) -> list:
        """Forza la riscoperta dei moduli e ritorna la lista aggiornata."""
        self.registry.discover()
        return self.registry.get_specs()

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

        debug_desc = "Real-time debug log viewer\n(all modules, live updates)"
        self._add_module_frame(modules_frame, "Debug Viewer", debug_desc, "Open Debug Viewer", self._open_debug_viewer)

        params_frame = tk.LabelFrame(modules_frame, text="Parametri Normativa")
        params_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(params_frame, text="Configura parametri TA/SLU/SLE\n(.jsoncode)", justify="left", wraplength=220).pack(padx=8, pady=8)
        tk.Button(params_frame, text="Parametri TA", command=lambda: self._open_code_settings("TA")).pack(pady=(0, 4))
        tk.Button(params_frame, text="Parametri SLU", command=lambda: self._open_code_settings("SLU")).pack(pady=(0, 4))
        tk.Button(params_frame, text="Parametri SLE", command=lambda: self._open_code_settings("SLE")).pack(pady=(0, 8))

        # Sections Archive Module
        sections_desc = "Browse and manage archived sections (import/export, edit via Geometry)"
        self._add_module_frame(modules_frame, "Sections Archive", sections_desc, "Open Sections", self._open_section_manager)

        # Materials Editor Module (last)
        material_desc = "Manage and import historical materials\n(concrete, steel, and other material libraries)"
        material_frame = tk.LabelFrame(modules_frame, text="Materials Editor")
        material_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(material_frame, text=material_desc, justify="left", wraplength=220).pack(padx=8, pady=8)
        tk.Button(material_frame, text="Open Materials", command=self._open_material_editor).pack(pady=(0, 8))

        # FRC Manager Module
        frc_desc = "Manage FRC materials (carbon/glass fibers) and properties"
        self._add_module_frame(modules_frame, "FRC Manager", frc_desc, "Open FRC Manager", self._open_frc_manager)

        # FRC Verification (quick) Module
        frc_ver_desc = "Quick verification window to test FRC contributions on simple sections"
        self._add_module_frame(modules_frame, "FRC Verification", frc_ver_desc, "Open FRC Verification", self._open_frc_verification)

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

    def _open_debug_viewer(self) -> None:
        """Apre il visualizzatore di debug come finestra Toplevel."""
        if self._debug_viewer_window is not None and self._debug_viewer_window.winfo_exists():
            self._debug_viewer_window.lift()
            self._debug_viewer_window.focus_force()
            return
        win = DebugViewerWindow(self)
        self._debug_viewer_window = win
        win.protocol("WM_DELETE_WINDOW", lambda w=win: (setattr(self, "_debug_viewer_window", None), w.destroy()))

    def _open_code_settings(self, code: str) -> None:
        settings_path = Path(__file__).resolve().parents[2] / "config" / "calculation_codes" / f"{code.upper()}.jsoncode"
        win = CodeSettingsWindow(self, code=code, settings_path=settings_path)
        win.protocol("WM_DELETE_WINDOW", lambda w=win: w.destroy())

    def _open_notification_settings(self) -> None:
        try:
            win = __import__("sections_app.ui.notification_settings_window", fromlist=["*"]).NotificationSettingsWindow(self)
            win._win.protocol("WM_DELETE_WINDOW", lambda w=win: w._on_cancel())
        except Exception:
            # Try to open headless settings window if something fails
            try:
                win = __import__("sections_app.ui.notification_settings_window", fromlist=["*"]).NotificationSettingsWindow(None)
                win.set_settings(win.get_settings())
                win.save()
            except Exception:
                logger.exception("Failed to open Notification Settings window")

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
            # Limita i retry per evitare scheduling infinito se Geometry non è mai pronta.
            if not hasattr(self, "_section_edit_retry_counts"):
                self._section_edit_retry_counts = {}
            sec_id = getattr(section, "id", str(section))
            count = self._section_edit_retry_counts.get(sec_id, 0)
            if count >= MAX_EDIT_LOAD_RETRIES:
                logger.warning(
                    "Stopped retrying to load section %s into Geometry after %d attempts",
                    sec_id,
                    count,
                )
                # Pulisci il contatore per evitare accumulo
                try:
                    self._section_edit_retry_counts.pop(sec_id, None)
                except Exception:
                    pass
                return
            # Incrementa il contatore e riprova in modo asincrono
            self._section_edit_retry_counts[sec_id] = count + 1
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
            # Reset del contatore di retry al successo
            try:
                if hasattr(self, "_section_edit_retry_counts"):
                    self._section_edit_retry_counts.pop(getattr(section, "id", str(section)), None)
            except Exception:
                pass
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
        try:
            self._material_editor_window.protocol("WM_DELETE_WINDOW", on_material_editor_close)
            # Inoltre, se la finestra viene distrutta in altro modo, assicurati di pulire il riferimento
            self._material_editor_window.bind("<Destroy>", lambda e: on_material_editor_close())
        except Exception:
            pass

    def _open_frc_manager(self) -> None:
        logger.debug("Opening FRC Manager module")
        try:
            from sections_app.ui.frc_manager import FrcManagerWindow
        except Exception:
            logger.exception("FRC Manager module not available")
            return
        win = FrcManagerWindow(self, material_repository=self.material_repository)
        win.protocol("WM_DELETE_WINDOW", lambda: win.destroy())

    def _open_frc_verification(self) -> None:
        logger.debug("Opening FRC Verification module")
        try:
            from sections_app.ui.frc_verification_window import FrcVerificationWindow
        except Exception:
            logger.exception("FRC Verification module not available")
            return
        win = FrcVerificationWindow(self, material_repository=self.material_repository)
        win.protocol("WM_DELETE_WINDOW", lambda: win.destroy())
        

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
                ("JSONS files", "*.jsons"),
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
                ("JSONS files", "*.jsons"),
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        
        # Mostra il dialogo di salvataggio
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Esporta backup",
            defaultextension=".jsons",
            initialfile=default_name,
            filetypes=filetypes
        )
        
        if not file_path:
            return
        
        # Esegui l'esportazione
        try:
            if result["choice"] == "sezioni":
                self.section_repository.export_backup(file_path)
                notify_info(
                    "Export completato",
                    f"Backup sezioni esportato correttamente in:\n{file_path}",
                    source="module_selector"
                )
            elif result["choice"] == "materiali":
                self.material_repository.export_backup(file_path)
                notify_info(
                    "Export completato",
                    f"Backup materiali esportato correttamente in:\n{file_path}",
                    source="module_selector"
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
                
                notify_info(
                    "Export completato",
                    f"Backup esportati correttamente:\n"
                    f"• Sezioni: {sections_path}\n"
                    f"• Materiali: {materials_path}",
                    source="module_selector"
                )
        except Exception as e:
            logger.exception("Errore durante l'esportazione del backup")
            notify_error(
                title="Errore",
                message=f"Modulo '{module_key}' non trovato o non disponibile.",
                source="module_selector",
            )
            return

        try:
            # create the window (factory may return placeholder)
            window = factory(master=master)
            with self.windows_lock:
                self.open_windows.append(window)

            # start the module in a separate thread to avoid blocking the selector UI
            thread = threading.Thread(target=self._run_window, args=(window, module_key), daemon=True)
            thread.start()
            logger.info("Modulo '%s' avviato in background.", module_key)
        except Exception as e:
            logger.exception("Errore nell'avvio del modulo '%s': %s", module_key, e)
            notify_error(
                title="Errore avvio modulo",
                message=f"Errore nell'avvio del modulo: {e}",
                source="module_selector",
            )

    def _run_window(self, window, module_key: str) -> None:
        """Wrapper to run a window's mainloop when appropriate and cleanup.

        Note: Tkinter Toplevel windows must be created and managed in the main thread.
        If a factory returns a Toplevel (or object exposing `winfo_exists`) we avoid
        starting a separate mainloop thread and just keep a reference to the window.
        """
        try:
            # If it's a Toplevel-like window created from the main thread, do not call mainloop
            try:
                import tkinter as _tk

                is_toplevel = isinstance(window, _tk.Toplevel)
            except Exception:
                is_toplevel = hasattr(window, "winfo_exists") and callable(window.winfo_exists)

            if is_toplevel:
                # Nothing to run — the window is a child of the main Tk and is already shown
                logger.debug("Modulo '%s' è Toplevel: non avvio mainloop separato", module_key)
                # Wait until window is destroyed to cleanup
                try:
                    while getattr(window, "winfo_exists", lambda: False)():
                        import time

                        time.sleep(0.1)
                except Exception:  # nosec
                    # If winfo_exists fails, we'll simply continue to cleanup
                    pass
            else:
                if hasattr(window, "mainloop") and callable(window.mainloop):
                    window.mainloop()
        except Exception:
            logger.exception("Errore durante l'esecuzione del modulo %s", module_key)
        finally:
            with self.windows_lock:
                try:
                    self.open_windows.remove(window)
                except ValueError:
                    pass
            logger.info("Modulo '%s' terminato.", module_key)

    def load_sections(self, file_path: str | None = None) -> None:
        """Carica sezioni da file CSV in un repository temporaneo (lazy)."""
        if not file_path:
            file_path = self.open_file_dialog()
        if file_path:
            try:
                serializer = CsvSectionSerializer()
                sections = serializer.import_from_csv(file_path)

                # create a GeometryRepository lazily if not present
                if not hasattr(self, "section_repo") or self.section_repo is None:
                    self.section_repo = GeometryRepository()

                # add imported sections
                added = 0
                for sec in sections:
                    if self.section_repo.add_section(sec):
                        added += 1

                notify_info(
                    title="Caricamento completato",
                    message=f"Sezioni caricate con successo ({added} aggiunte).",
                    source="module_selector",
                )
                logger.info(f"Sezioni caricate da {file_path}: {added} aggiunte.")
            except Exception as e:
                logger.error(f"Errore nel caricamento sezioni: {e}")
                notify_error(
                    title="Errore caricamento",
                    message=f"Errore nel caricamento: {e}",
                    source="module_selector",
                )

    def open_file_dialog(self) -> str | None:
        """Apre dialog per selezionare file."""
        return filedialog.askopenfilename(
            title="Seleziona file CSV", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

    def open_code_settings(self) -> None:
        """Apre finestra impostazioni codice."""
        CodeSettingsWindow(self, "NTC", Path("code_settings.json")).mainloop()

    def open_notification_center(self) -> None:
        """Apre centro notifiche."""
        if not self.notification_center:
            self.notification_center = NotificationCenter()
        self.notification_center.show()


class ModuleSelectorWindow(Tk):
    """Finestra iniziale per selezionare il modulo da avviare (Vista semplificata)."""

    def __init__(self):
        super().__init__()
        self.controller = ModuleSelectorController()
        specs = self._create_specs()
        self.view = ModuleSelectorView(self, specs)
        self.view.pack(fill="both", expand=True)
        self._setup_menu()
        self._bind_events()
        self.title("RD2229 Module Selector")
        self.geometry("800x600")

    def _create_specs(self) -> list[ModuleCardSpec]:
        """Crea le specifiche delle card dai moduli disponibili (usando ModuleRegistry)."""
        specs = []
        for modspec in self.controller.get_available_modules():
            spec = ModuleCardSpec(
                title=modspec.name,
                description=modspec.description,
                button_text="Launch",
                callback=lambda key=modspec.key: self.controller.select_module(key, self),
            )
            specs.append(spec)
        return specs

    def _setup_menu(self) -> None:
        """Configura il menu della finestra."""
        from tkinter import Menu

        menubar = Menu(self)
        self.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Carica Sezioni", command=self.controller.load_sections)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.quit)

        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Strumenti", menu=tools_menu)
        tools_menu.add_command(label="Impostazioni Codice", command=self.controller.open_code_settings)
        tools_menu.add_command(label="Centro Notifiche", command=self.controller.open_notification_center)
        tools_menu.add_separator()
        tools_menu.add_command(label="Aggiorna Moduli", command=self._refresh_modules)

    def _bind_events(self) -> None:
        """Collega eventi della vista al controller."""
        # Implementa eventuali callback di interazione se necessario
        # Ad esempio, potremmo avere una callback di selezione diretta sulla view
        # self.view.on_module_select = lambda key: self.controller.select_module(key, self)
        pass

    def _refresh_modules(self) -> None:
        """Ricarica la lista dei moduli dal registry e aggiorna la vista."""
        try:
            self.controller.registry.discover()
            new_specs = self._create_specs()
            self.view.set_specs(new_specs)
            notify_info(
                title="Moduli aggiornati",
                message="Lista moduli aggiornata.",
                source="module_selector",
            )
            logger.info("Lista moduli aggiornata da ModuleRegistry")
        except Exception as e:
            logger.exception("Errore aggiornamento moduli: %s", e)
            notify_error(
                title="Errore",
                message=f"Impossibile aggiornare moduli: {e}",
                source="module_selector",
            )
