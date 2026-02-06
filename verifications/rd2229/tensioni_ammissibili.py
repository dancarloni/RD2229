"""Stub: tensioni ammissibili storiche (RD2229)."""


def tensione_ammissibile(categoria: str) -> float:
    """Restituisce valore fittizio; sostituire con tabelle reali."""
    mapping = {"cemento": 2.0, "acciaio": 20.0}
    return mapping.get(categoria, 1.0)
