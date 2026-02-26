from __future__ import annotations

import sqlite3
from pathlib import Path

LATEST_DB_SCHEMA_VERSION = 1


class SQLiteStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            current = self._schema_version(conn)
            if current == 0:
                self._migrate_0_to_1(conn)
                conn.execute(f"PRAGMA user_version = {LATEST_DB_SCHEMA_VERSION}")
                conn.commit()
            elif current > LATEST_DB_SCHEMA_VERSION:
                raise RuntimeError(
                    f"Database schema {current} is newer than supported {LATEST_DB_SCHEMA_VERSION}"
                )

    @staticmethod
    def _schema_version(conn: sqlite3.Connection) -> int:
        row = conn.execute("PRAGMA user_version").fetchone()
        if row is None:
            return 0
        return int(row[0])

    @staticmethod
    def _migrate_0_to_1(conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                norma_attiva TEXT NOT NULL,
                created_at TEXT NOT NULL,
                schema_version INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS materials (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                code TEXT NOT NULL,
                kind TEXT NOT NULL,
                properties_json TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sections (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                dimensions_json TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS elements (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                material_id TEXT NOT NULL,
                role TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS load_cases (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                actions_json TEXT NOT NULL,
                environmental_json TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS combinations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                factors_json TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS check_requests (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                element_id TEXT NOT NULL,
                combination_id TEXT NOT NULL,
                check_code TEXT NOT NULL,
                parameters_json TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS verification_results (
                id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                value REAL NOT NULL,
                trace_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY(request_id) REFERENCES check_requests(id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("schema_version", str(LATEST_DB_SCHEMA_VERSION)),
        )
