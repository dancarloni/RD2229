"""ViewModels per la GUI moderna RD2229 (no PySide6 import).

I ViewModel gestiscono lo stato UI senza dipendere da Qt.
Le View (widget) osservano i ViewModel tramite callback.
"""

from __future__ import annotations

import datetime
import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from src.project.schema import CURRENT_SCHEMA_VERSION, ProjectModel

# ---------------------------------------------------------------------------
# ProjectViewModel
# ---------------------------------------------------------------------------


class ProjectViewModel:
    """Stato del progetto aperto: dirty flag, percorso, recent files."""

    MAX_RECENT = 10

    def __init__(self) -> None:
        self._project: ProjectModel = ProjectModel()
        self._path: str | None = None
        self._dirty: bool = False
        self._recent: list[str] = []
        self._on_change_callbacks: list[Callable[[], None]] = []

    # ------------------------------------------------------------------
    # Public state
    # ------------------------------------------------------------------

    @property
    def project(self) -> ProjectModel:
        return self._project

    @property
    def path(self) -> str | None:
        return self._path

    @property
    def dirty(self) -> bool:
        return self._dirty

    @property
    def recent_files(self) -> list[str]:
        return list(self._recent)

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def set_project(self, project: ProjectModel, path: str | None = None) -> None:
        """Sostituisce il progetto corrente."""
        self._project = project
        self._path = path
        self._dirty = False
        if path:
            self._add_recent(path)
        self._notify()

    def mark_dirty(self) -> None:
        """Segna il progetto come modificato (non salvato)."""
        self._dirty = True
        self._notify()

    def mark_saved(self, path: str | None = None) -> None:
        """Segna il progetto come salvato."""
        self._dirty = False
        if path:
            self._path = path
            self._add_recent(path)
        self._notify()

    def new_project(self) -> None:
        """Crea un nuovo progetto vuoto."""
        self.set_project(ProjectModel(), path=None)
        self._dirty = False
        self._notify()

    # ------------------------------------------------------------------
    # Recent files persistence
    # ------------------------------------------------------------------

    def load_recent(self, settings_path: str) -> None:
        """Carica la lista recent files da un file JSON."""
        try:
            with open(settings_path, encoding="utf-8") as f:
                data = json.load(f)
            self._recent = [p for p in data.get("recent_files", []) if os.path.exists(p)]
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self._recent = []

    def save_recent(self, settings_path: str) -> None:
        """Salva la lista recent files su file JSON."""
        try:
            os.makedirs(os.path.dirname(settings_path) or ".", exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump({"recent_files": self._recent}, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def on_change(self, callback: Callable[[], None]) -> None:
        """Registra un callback chiamato ad ogni cambio di stato."""
        self._on_change_callbacks.append(callback)

    def _notify(self) -> None:
        for cb in self._on_change_callbacks:
            try:
                cb()
            except Exception:  # pragma: no cover
                pass

    def _add_recent(self, path: str) -> None:
        self._recent = [p for p in self._recent if p != path]
        self._recent.insert(0, path)
        self._recent = self._recent[: self.MAX_RECENT]


# ---------------------------------------------------------------------------
# RunViewModel
# ---------------------------------------------------------------------------


class RunViewModel:
    """Stato dell'esecuzione della pipeline: running, errori, status."""

    def __init__(self) -> None:
        self._running: bool = False
        self._status: str = "Pronto"
        self._error: str | None = None
        self._on_change_callbacks: list[Callable[[], None]] = []

    @property
    def running(self) -> bool:
        return self._running

    @property
    def status(self) -> str:
        return self._status

    @property
    def error(self) -> str | None:
        return self._error

    def set_running(self, running: bool, status: str = "") -> None:
        self._running = running
        self._status = status or ("In esecuzione…" if running else "Pronto")
        self._error = None
        self._notify()

    def set_error(self, error: str) -> None:
        self._running = False
        self._status = "Errore"
        self._error = error
        self._notify()

    def set_done(self, status: str = "Completato") -> None:
        self._running = False
        self._status = status
        self._error = None
        self._notify()

    def on_change(self, callback: Callable[[], None]) -> None:
        self._on_change_callbacks.append(callback)

    def _notify(self) -> None:
        for cb in self._on_change_callbacks:
            try:
                cb()
            except Exception:  # pragma: no cover
                pass


# ---------------------------------------------------------------------------
# ResultsViewModel
# ---------------------------------------------------------------------------


class ResultsViewModel:
    """Stato dei risultati di calcolo: warnings, trace, elementi."""

    def __init__(self) -> None:
        self._results: Any = None  # ResultsModel | None
        self._on_change_callbacks: list[Callable[[], None]] = []

    @property
    def results(self) -> Any:
        return self._results

    @property
    def has_results(self) -> bool:
        return self._results is not None

    @property
    def global_ok(self) -> bool:
        return bool(self._results and self._results.ok)

    @property
    def warnings(self) -> list[str]:
        if self._results is None:
            return []
        return list(self._results.warnings)

    @property
    def trace(self) -> list[str]:
        if self._results is None:
            return []
        return list(self._results.trace)

    @property
    def elements(self) -> list[Any]:
        if self._results is None:
            return []
        return list(self._results.elements)

    def set_results(self, results: Any) -> None:
        self._results = results
        self._notify()

    def clear(self) -> None:
        self._results = None
        self._notify()

    def on_change(self, callback: Callable[[], None]) -> None:
        self._on_change_callbacks.append(callback)

    def _notify(self) -> None:
        for cb in self._on_change_callbacks:
            try:
                cb()
            except Exception:  # pragma: no cover
                pass
