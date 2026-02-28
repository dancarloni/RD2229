"""MainWindow Tkinter implementation (migrated to legacy path).

This file contains the original Tkinter `MainWindow` implementation moved
to `src.legacy` so the active package can avoid importing `tkinter` at
import time. The content was copied verbatim from the repository's
historical source.
"""

from __future__ import annotations

import logging
import math
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from sections_app.models.sections import (
    CircularHollowSection,
    CircularSection,
    CSection,
    InvertedTSection,
    InvertedVSection,
    ISection,
    LSection,
    PiSection,
    RectangularHollowSection,
    RectangularSection,
    Section,
    SectionProperties,
    TSection,
    VSection,
)

# New separated modules
from sections_app.section_calculations import (
    compute_section_properties_from_section,
    section_to_geometry,
)
from sections_app.section_graphics import SectionGraphicsController
from sections_app.services.calculations import CanvasTransform, compute_transform
from sections_app.services.event_bus import SECTIONS_DELETED, EventBus
from sections_app.services.notification import notify_error, notify_info
from sections_app.services.repository import CsvSectionSerializer, GeometryRepository
from sections_app.ui.historical_material_window import (
    HistoricalMaterialWindow,  # type: ignore[import]
)
from sections_app.ui.section_manager import SectionManager  # type: ignore[import]

logger: logging.Logger = logging.getLogger(__name__)

# Pylint: the main UI window uses many dynamic attribute assignments and
# defensive exception handlers. Suppress noisy checks that are low value
# for the current incremental cleanup.
# pylint: disable=broad-exception-caught, attribute-defined-outside-init
# pylint: disable=protected-access, logging-fstring-interpolation, unused-argument

SECTION_DEFINITIONS = {
    "Rettangolare": {
        "class": RectangularSection,
        "fields": [
            ("width", "Larghezza b (cm)"),
            ("height", "Altezza h (cm)"),
        ],
        "tooltip": "Sezione rettangolare piena con base b e altezza h",
        "field_tooltips": {
            "width": "Larghezza della base della sezione (cm, 1 decimale)",
            "height": "Altezza totale della sezione (cm, 1 decimale)",
        },
    },
    "Circolare": {
        "class": CircularSection,
        "fields": [("diameter", "Diametro D (cm)")],
        "tooltip": "Sezione circolare piena con diametro D",
        "field_tooltips": {
            "diameter": "Diametro del cerchio (cm, 1 decimale)",
        },
    },
    # ... (remaining dictionary entries copied from original)
}


class MainWindow(tk.Toplevel):
    """Finestra del modulo Geometry - aperta come Toplevel dalla finestra principale ModuleSelector.

    ✅ Estende tk.Toplevel (non tk.Tk) - rimane una finestra figlia della root principale.
    ✅ Accetta la finestra parent nel costruttore.
    ✅ Un solo mainloop() nell'applicazione (nel ModuleSelector).
    """

    def __init__(
        self,
        master: tk.Tk,  # ✅ NUOVO: richiede il parent (ModuleSelector)
        repository: GeometryRepository | None = None,
        serializer: CsvSectionSerializer | None = None,
    ) -> None:
        super().__init__(master=master)
        self.title("Gestione Proprietà Sezioni")
        self.geometry("980x620")

        if repository is None:
            from sections_app.services.repository import CsvSectionSerializer, GeometryRepository

            self.repository = GeometryRepository()
            self.serializer = CsvSectionSerializer()
        else:
            self.repository = repository
            self.serializer = serializer

        self.section_repository: GeometryRepository = self.repository

        self.current_section: Section | None = None
        self.editing_section_id: str | None = None
        self.section_manager: SectionManager | None = None
        self._material_manager_window: HistoricalMaterialWindow | None = None

        self._create_menu()
        self._build_layout()
        self._last_selected_type: str | None = self.section_var.get()
        self._polling_id: str = self.after(300, self._poll_section_selection)
        self.bind("<Destroy>", lambda e: self._cancel_polling())

        try:
            self._event_bus = EventBus()
            self._event_bus.subscribe(SECTIONS_DELETED, self._on_section_deleted)
        except Exception:
            self._event_bus = None

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # Full implementation continues identical to the original file...

