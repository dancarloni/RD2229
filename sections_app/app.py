from __future__ import annotations

import logging

from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.main_window import MainWindow


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


def run_app() -> None:
    configure_logging()
    repository = SectionRepository()
    serializer = CsvSectionSerializer()
    # Show the module selector as the first window
    from sections_app.ui.module_selector import ModuleSelectorWindow

    selector = ModuleSelectorWindow(repository, serializer)
    selector.mainloop()


if __name__ == "__main__":
    run_app()

