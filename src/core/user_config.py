"""User-scoped GUI configuration for RD2229.

Stores lightweight preferences under ~/.rd2229/config.json.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class UserConfig:
    recent_projects: list[str] = field(default_factory=list)
    default_norm_code: str = "RD2229"
    theme: str = "light"
    last_output_dir: str = ""
    autosave_enabled: bool = False
    autosave_minutes: int = 5

    MAX_RECENT: int = 10

    @classmethod
    def default_path(cls) -> Path:
        return Path.home() / ".rd2229" / "config.json"

    @classmethod
    def load(cls, path: str | Path | None = None) -> "UserConfig":
        target = Path(path) if path is not None else cls.default_path()
        if not target.exists():
            return cls()
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return cls()

        return cls(
            recent_projects=list(data.get("recent_projects", []))[: cls.MAX_RECENT],
            default_norm_code=str(data.get("default_norm_code", "RD2229")),
            theme=str(data.get("theme", "light")),
            last_output_dir=str(data.get("last_output_dir", "")),
            autosave_enabled=bool(data.get("autosave_enabled", False)),
            autosave_minutes=max(1, int(data.get("autosave_minutes", 5))),
        )

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path is not None else self.default_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["recent_projects"] = self.recent_projects[: self.MAX_RECENT]
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def add_recent(self, project_path: str) -> None:
        normalized = str(Path(project_path))
        self.recent_projects = [p for p in self.recent_projects if p != normalized]
        self.recent_projects.insert(0, normalized)
        self.recent_projects = self.recent_projects[: self.MAX_RECENT]
