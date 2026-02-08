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

from core_models.materials import MaterialRepository  # type: ignore[import]
from historical_materials import HistoricalMaterialLibrary
from sections_app.services.notification import (
    notify_error,
    notify_info,
)
from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.code_settings_window import CodeSettingsWindow
from sections_app.ui.debug_viewer import DebugViewerWindow  # noqa: F401
from sections_app.ui.historical_main_window import HistoricalModuleMainWindow  # noqa: F401
from sections_app.ui.historical_material_window import HistoricalMaterialWindow  # noqa: F401
from sections_app.ui.main_window import MainWindow  # noqa: F401
from sections_app.ui.module_selector_view import ModuleSelectorView
from sections_app.ui.notification_center import NotificationCenter

logger = logging.getLogger(__name__)


class ModuleSelectorController:
    """Controller per la logica di selezione moduli e gestione dati."""

    def __init__(self):
        self.material_repo = MaterialRepository()
        self.section_repo = SectionRepository(CsvSectionSerializer())
        self.historical_lib = HistoricalMaterialLibrary()
        self.notification_center = NotificationCenter()
        self.open_windows = []
        self.modules_config = self._load_modules_config()

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

    def get_available_modules(self) -> dict[str, dict]:
        """Restituisce i moduli disponibili."""
        return self.modules_config

    def select_module(self, module_key: str) -> None:
        """Seleziona e avvia un modulo."""
        if module_key not in self.modules_config:
            notify_error(
                title="Errore",
                message=f"Modulo '{module_key}' non trovato nella configurazione.",
                source="module_selector",
            )
            return

        config = self.modules_config[module_key]
        try:
            module_class_name = config["class"]
            module_class = globals().get(module_class_name)
            if not module_class:
                raise ValueError(f"Classe '{module_class_name}' non trovata.")

            window = module_class(
                self.material_repo, self.section_repo, self.historical_lib, self.notification_center
            )
            self.open_windows.append(window)
            window.mainloop()  # Nota: in produzione, considera threading per evitare blocco
            logger.info(f"Modulo '{module_key}' avviato.")
        except Exception as e:
            logger.error(f"Errore nell'avvio del modulo '{module_key}': {e}")
            notify_error(
                title="Errore avvio modulo",
                message=f"Errore nell'avvio del modulo: {e}",
                source="module_selector",
            )

    def load_sections(self, file_path: str | None = None) -> None:
        """Carica sezioni da file CSV."""
        if not file_path:
            file_path = self.open_file_dialog()
        if file_path:
            try:
                self.section_repo.load_from_csv(file_path)
                notify_info(
                    title="Caricamento completato",
                    message="Sezioni caricate con successo.",
                    source="module_selector",
                )
                logger.info(f"Sezioni caricate da {file_path}.")
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
        CodeSettingsWindow(Tk()).mainloop()

    def open_notification_center(self) -> None:
        """Apre centro notifiche."""
        self.notification_center.show()


class ModuleSelectorWindow(Tk):
    """Finestra iniziale per selezionare il modulo da avviare (Vista semplificata)."""

    def __init__(self):
        super().__init__()
        self.controller = ModuleSelectorController()
        self.view = ModuleSelectorView(self)
        self._setup_menu()
        self._bind_events()
        self.title("RD2229 Module Selector")
        self.geometry("800x600")

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

    def _bind_events(self) -> None:
        """Collega eventi della vista al controller."""
        # Assumi che ModuleSelectorView abbia un metodo per collegare selezione
        # Es. self.view.on_module_select = self.controller.select_module
        # Adatta in base all'implementazione reale di ModuleSelectorView
        pass  # Placeholder; implementa se necessario
