from __future__ import annotations

import logging

from sections_app.services.debug_log_stream import get_in_memory_handler

from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.main_window import MainWindow

try:
    from core_models.materials import MaterialRepository
except ImportError:
    MaterialRepository = None


def configure_logging() -> None:
    """Configura il logging a livello DEBUG su console e su file 'app.log'."""
    # Basic config for console
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Add file handler
    fh = logging.FileHandler("app.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(fmt)
    logging.getLogger().addHandler(fh)
    logging.getLogger().addHandler(get_in_memory_handler())


def run_app() -> None:
    configure_logging()
    
    # Crea e carica i repository
    section_repository = SectionRepository()
    section_repository.load_from_file()
    
    material_repository = None
    if MaterialRepository is not None:
        material_repository = MaterialRepository()
        material_repository.load_from_file()
    
    serializer = CsvSectionSerializer()
    
    # Mostra il selettore di modulo come prima finestra
    from sections_app.ui.module_selector import ModuleSelectorWindow

    selector = ModuleSelectorWindow(section_repository, serializer, material_repository)
    selector.mainloop()


if __name__ == "__main__":
    run_app()

