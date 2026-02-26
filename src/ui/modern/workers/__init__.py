"""PipelineWorker – esegue la pipeline in background (QRunnable/QThread).

Dipende da PySide6. Non importare questo modulo se PySide6 non è disponibile.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
    _PYSIDE6_AVAILABLE = True
except ImportError:
    _PYSIDE6_AVAILABLE = False
    QObject = object  # type: ignore[assignment, misc]
    QRunnable = object  # type: ignore[assignment, misc]


class WorkerSignals(QObject):  # type: ignore[misc]
    """Segnali emessi dal worker in background.

    Compatibile con il pattern Qt Signals/Slots.
    """

    if _PYSIDE6_AVAILABLE:
        finished = Signal(object)   # ResultsModel
        error = Signal(str)         # messaggio errore
        progress = Signal(str)      # messaggio di avanzamento


class PipelineWorker(QRunnable):  # type: ignore[misc]
    """Esegue run_pipeline in background senza bloccare la UI.

    Uso::

        worker = PipelineWorker(project, calc_service)
        worker.signals.finished.connect(on_finished)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)
    """

    def __init__(self, project: Any, calc_service: Any) -> None:
        if _PYSIDE6_AVAILABLE:
            super().__init__()
        self._project = project
        self._calc_service = calc_service
        self.signals = WorkerSignals()

    def run(self) -> None:  # type: ignore[override]
        """Esegue la pipeline di calcolo (chiamato da QThreadPool)."""
        if not _PYSIDE6_AVAILABLE:
            return
        try:
            results = self._calc_service.run(self._project)
            self.signals.finished.emit(results)
        except Exception as exc:
            self.signals.error.emit(str(exc))
