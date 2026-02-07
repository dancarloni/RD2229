# ADR 0003 — Repository schema versioning

Decision: Persist schema version as `schema_version` in repository JSON files; provide migration helpers in `src/repositories/migration.py` to upgrade older schema versions.

Rationale: Enables backward-compatible storage and future-proofing for changes in material/section formats.
