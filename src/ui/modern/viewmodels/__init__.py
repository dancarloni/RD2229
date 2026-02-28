"""Minimal ViewModel shims for tests that import `src.ui.modern.viewmodels`.

Provides `ProjectViewModel`, `RunViewModel`, `ResultsViewModel` with a
small subset of the behavior used in tests.
"""

from __future__ import annotations

from typing import Any, Callable, List


class ProjectViewModel:
    MAX_RECENT = 10

    def __init__(self) -> None:
        from src.project.schema import ProjectModel

        self._project: ProjectModel = ProjectModel()
        self._path: str | None = None
        self._dirty: bool = False
        self._recent: List[str] = []
        self._callbacks: List[Callable[[], None]] = []
        # Maximum number of recent files to keep
        self.MAX_RECENT = 10

    @property
    def recent_files(self) -> List[str]:
        return list(self._recent)

    def _add_recent(self, path: str) -> None:
        if not path:
            return
        if path in self._recent:
            self._recent.remove(path)
        self._recent.insert(0, path)
        # Trim to max
        if len(self._recent) > self.MAX_RECENT:
            self._recent = self._recent[: self.MAX_RECENT]

    def save_recent(self, settings_path: str) -> None:
        import json

        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump({"recent_files": self._recent}, f)
        except Exception:
            pass

    def load_recent(self, settings_path: str) -> None:
        import json
        from pathlib import Path

        try:
            p = Path(settings_path)
            if not p.exists():
                return
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            files = list(data.get("recent_files", []))
            # filter missing
            files = [x for x in files if Path(x).exists()]
            self._recent = files
        except Exception:
            pass

    @property
    def project(self) -> Any:
        return self._project

    @property
    def path(self) -> str | None:
        return self._path

    @property
    def dirty(self) -> bool:
        return self._dirty

    def set_project(self, project: Any, path: str | None = None) -> None:
        self._project = project
        self._path = path
        self._dirty = False
        if path:
            self._add_recent(path)
        self._notify()

    def new_project(self) -> None:
        from src.project.schema import ProjectModel

        self.set_project(ProjectModel(), path=None)

    def mark_dirty(self) -> None:
        self._dirty = True
        self._notify()

    def mark_saved(self, path: str | None = None) -> None:
        self._dirty = False
        if path:
            self._path = path
            self._add_recent(path)
        self._notify()

    def on_change(self, cb: Callable[[], None]) -> None:
        self._callbacks.append(cb)

    def _notify(self) -> None:
        for cb in list(self._callbacks):
            try:
                cb()
            except Exception:
                pass


class RunViewModel:
    def __init__(self) -> None:
        self._running = False
        self._status = "Pronto"
        self._error = None
        self._callbacks: List[Callable[[], None]] = []

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

    def on_change(self, cb: Callable[[], None]) -> None:
        self._callbacks.append(cb)

    def _notify(self) -> None:
        for cb in list(self._callbacks):
            try:
                cb()
            except Exception:
                pass


class ResultsViewModel:
    def __init__(self) -> None:
        self._results = None
        self._callbacks: List[Callable[[], None]] = []

    @property
    def has_results(self) -> bool:
        return self._results is not None

    @property
    def results(self) -> Any:
        return self._results

    @property
    def warnings(self) -> List[str]:
        if self._results is None:
            return []
        return list(getattr(self._results, "warnings", []))

    @property
    def elements(self) -> List[Any]:
        if self._results is None:
            return []
        return list(getattr(self._results, "elements", []))

    def set_results(self, results: Any) -> None:
        self._results = results
        self._notify()

    def clear(self) -> None:
        self._results = None
        self._notify()

    def on_change(self, cb: Callable[[], None]) -> None:
        self._callbacks.append(cb)

    def _notify(self) -> None:
        for cb in list(self._callbacks):
            try:
                cb()
            except Exception:
                pass


__all__ = [
    "ProjectViewModel",
    "RunViewModel",
    "ResultsViewModel",
]
