"""Lightweight persistence utilities for GUI project index.

Provides an SQLite index under ~/.rd2229/projects.db.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class IndexedProject:
    path: str
    name: str
    norm_code: str
    updated_at: str
    sha256: str


class ProjectIndex:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = (
            Path(db_path) if db_path is not None else Path.home() / ".rd2229" / "projects.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    path TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    norm_code TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    sha256 TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def compute_sha256(path: str | Path) -> str:
        data = Path(path).read_bytes()
        return hashlib.sha256(data).hexdigest()

    def upsert(self, path: str | Path, name: str, norm_code: str) -> None:
        path_obj = Path(path)
        now = datetime.now(UTC).isoformat()
        digest = self.compute_sha256(path_obj) if path_obj.exists() else ""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO projects(path, name, norm_code, updated_at, sha256)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    name=excluded.name,
                    norm_code=excluded.norm_code,
                    updated_at=excluded.updated_at,
                    sha256=excluded.sha256
                """,
                (str(path_obj), name, norm_code, now, digest),
            )
            conn.commit()

    def list_recent(self, limit: int = 10) -> list[IndexedProject]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT path, name, norm_code, updated_at, sha256
                FROM projects
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [IndexedProject(*row) for row in rows]
