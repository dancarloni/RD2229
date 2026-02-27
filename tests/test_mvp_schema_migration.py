import sqlite3

from src.rd2229.mvp.sqlite_store import LATEST_DB_SCHEMA_VERSION, SQLiteStore


def test_mvp_schema_migration_from_empty_db(tmp_path):
    db_path = tmp_path / "migration.db"
    sqlite3.connect(str(db_path)).close()

    store = SQLiteStore(str(db_path))
    store.initialize()

    with store.connect() as conn:
        row = conn.execute("PRAGMA user_version").fetchone()
        assert row is not None
        assert int(row[0]) == LATEST_DB_SCHEMA_VERSION

        meta = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        assert meta is not None
        assert int(meta[0]) == LATEST_DB_SCHEMA_VERSION
