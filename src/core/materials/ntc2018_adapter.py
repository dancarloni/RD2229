"""
Adapter (skeleton) to expose NTC2018 material lookups to the rest of the system.
Relies on existing loaders under `config/` and `data/` (SPEC only).
"""

def get_material_by_code(code: str) -> dict:
    """Return material descriptor (SKELETON)."""
    return {"code": code, "TODO": "supply authoritative material properties via loader"}
