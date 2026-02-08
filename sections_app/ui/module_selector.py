"""Module Selector Window for RD2229 Tools.

This module provides the main application window that allows users to select
and launch different modules of the RD2229 structural analysis toolkit.
Refactored to separate view, controller, and configuration for better modularity.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from tkinter import Tk, filedialog

from core_models.materials import MaterialRepository  # noqa: F401
from historical_materials import HistoricalMaterialLibrary  # noqa: F401
from sections_app.services.notification import (
    notify_error,
    notify_info,
)
from sections_app.services.repository import CsvSectionSerializer, GeometryRepository
from sections_app.ui.code_settings_window import CodeSettingsWindow
from sections_app.ui.debug_viewer import DebugViewerWindow  # noqa: F401
from sections_app.ui.historical_main_window import HistoricalModuleMainWindow  # noqa: F401
from sections_app.ui.historical_material_window import HistoricalMaterialWindow  # noqa: F401
from sections_app.ui.main_window import MainWindow  # noqa: F401
from sections_app.ui.module_selector_view import ModuleCardSpec, ModuleSelectorView
from sections_app.ui.notification_center import NotificationCenter
from sections_app.modules.registry import ModuleRegistry
import threading

logger = logging.getLogger(__name__)


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
            with open(config_path, "r", encoding="utf-8") as f:
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

    def select_module(self, module_key: str, master=None) -> None:
        """Seleziona e avvia un modulo tramite il ModuleRegistry."""
        factory = self.registry.get_factory(module_key)
        if not factory:
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
            thread = threading.Thread(
                target=self._run_window, args=(window, module_key), daemon=True
            )
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
                except Exception:
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
        tools_menu.add_command(
            label="Impostazioni Codice", command=self.controller.open_code_settings
        )
        tools_menu.add_command(
            label="Centro Notifiche", command=self.controller.open_notification_center
        )
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
