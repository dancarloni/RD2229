import pandas as pd
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "quantities_registry.csv")

def leggi_registro():
    """Legge il file CSV delle grandezze e restituisce un DataFrame."""
    return pd.read_csv(CSV_PATH)

def aggiungi_grandezza(grandezza_dict):
    """Aggiunge una nuova grandezza al registro."""
    df = leggi_registro()
    df = pd.concat([df, pd.DataFrame([grandezza_dict])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
