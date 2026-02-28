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

    from __future__ import annotations

    import importlib
    import warnings

    warnings.warn(
        "sections_app.ui.module_selector is deprecated and moved to src.legacy.sections_app.ui.module_selector",
        DeprecationWarning,
    )

    def _load_legacy():
        return importlib.import_module("src.legacy.sections_app.ui.module_selector")

    def __getattr__(name: str):
        return getattr(_load_legacy(), name)

    def __dir__():
        return dir(_load_legacy())
            },
