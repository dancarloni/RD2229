from pathlib import Path
from typing import Dict

import pandas as pd

CSV_PATH = Path(__file__).with_name("quantities_registry.csv")


def leggi_registro() -> pd.DataFrame:
    """Legge il file CSV delle grandezze e restituisce un DataFrame.

    Raises:
        FileNotFoundError: se il file CSV non esiste.

    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Quantities registry not found: {CSV_PATH}")
    return pd.read_csv(CSV_PATH, encoding="utf-8")


def aggiungi_grandezza(grandezza_dict: Dict) -> None:
    """Aggiunge una nuova grandezza al registro.

    Appende una riga al CSV esistente o lo crea se mancasse.
    """
    if CSV_PATH.exists():
        df = leggi_registro()
        df = pd.concat([df, pd.DataFrame([grandezza_dict])], ignore_index=True)
    else:
        df = pd.DataFrame([grandezza_dict])
        # Ensure parent directory exists
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8")
