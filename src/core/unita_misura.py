"""Sistema Unità di Misura Selezionabile.

Tre sistemi disponibili, selezionabili dall'utente da menu Impostazioni:
- **kg-cm**: kg/cm² per tensioni, cm per geometria, kg⋅cm per momenti (default storico)
- **kN-m**: kN/m² (kPa) per tensioni, m per geometria, kN⋅m per momenti
- **N-mm**: N/mm² (MPa) per tensioni, mm per geometria, N⋅mm per momenti

Tutte le formule interne lavorano in un sistema normalizzato (kg-cm).
La GUI mostra i valori convertiti nel sistema selezionato dall'utente.
Le label delle unità si aggiornano dinamicamente.

Utilizzo::

    from src.core.unita_misura import gestore_unita, SistemaUnita

    # Seleziona sistema (tipicamente da impostazioni utente)
    gestore_unita.imposta_sistema(SistemaUnita.KN_M)

    # Converti un valore per la visualizzazione nella GUI
    tensione_gui = gestore_unita.converti_tensione(141.7)  # da kg/cm² interno
    label_tensione = gestore_unita.label_tensione()         # "kPa"

    # Converti un valore dall'input utente al sistema interno
    tensione_interna = gestore_unita.da_input_tensione(14170.0)  # kPa → kg/cm²
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class SistemaUnita(Enum):
    """Sistemi di unità di misura disponibili."""
    KG_CM = "kg-cm"   # kg/cm² per tensioni, cm per geometria, kg⋅cm per momenti
    KN_M = "kN-m"     # kPa per tensioni, m per geometria, kN⋅m per momenti
    N_MM = "N-mm"     # MPa per tensioni, mm per geometria, N⋅mm per momenti


# Fattori di conversione DAL sistema interno (kg-cm) AL sistema target
# Formato: {SistemaUnita: {grandezza: fattore_moltiplicativo}}
_FATTORI_CONVERSIONE: dict[SistemaUnita, dict[str, float]] = {
    SistemaUnita.KG_CM: {
        "lunghezza": 1.0,        # cm → cm
        "area": 1.0,             # cm² → cm²
        "volume": 1.0,           # cm³ → cm³
        "forza": 1.0,            # kg → kg
        "momento": 1.0,          # kg⋅cm → kg⋅cm
        "tensione": 1.0,         # kg/cm² → kg/cm²
        "rigidezza_lineare": 1.0,  # kg/cm → kg/cm
        "peso_specifico": 1.0,   # kg/cm³ → kg/cm³
        "carico_lineare": 1.0,   # kg/cm → kg/cm
        "carico_superficie": 1.0,  # kg/cm² → kg/cm²
    },
    SistemaUnita.KN_M: {
        "lunghezza": 0.01,       # cm → m
        "area": 1e-4,            # cm² → m²
        "volume": 1e-6,          # cm³ → m³
        "forza": 0.00980665,     # kg → kN
        "momento": 0.0000980665, # kg⋅cm → kN⋅m
        "tensione": 0.980665,    # kg/cm² → kPa
        "rigidezza_lineare": 0.980665,  # kg/cm → kN/m
        "peso_specifico": 9.80665e3,    # kg/cm³ → kN/m³
        "carico_lineare": 0.0980665,    # kg/cm → kN/m
        "carico_superficie": 0.980665,  # kg/cm² → kN/m²
    },
    SistemaUnita.N_MM: {
        "lunghezza": 10.0,       # cm → mm
        "area": 100.0,           # cm² → mm²
        "volume": 1000.0,        # cm³ → mm³
        "forza": 9.80665,        # kg → N
        "momento": 98.0665,      # kg⋅cm → N⋅mm
        "tensione": 0.0980665,   # kg/cm² → MPa (N/mm²)
        "rigidezza_lineare": 0.980665,  # kg/cm → N/mm
        "peso_specifico": 9.80665e-6,   # kg/cm³ → N/mm³
        "carico_lineare": 0.0980665,    # kg/cm → N/mm
        "carico_superficie": 0.0980665, # kg/cm² → N/mm² (MPa)
    },
}

# Label delle unità per ogni grandezza e sistema
_LABEL_UNITA: dict[SistemaUnita, dict[str, str]] = {
    SistemaUnita.KG_CM: {
        "lunghezza": "cm",
        "area": "cm²",
        "volume": "cm³",
        "forza": "kg",
        "momento": "kg⋅cm",
        "tensione": "kg/cm²",
        "rigidezza_lineare": "kg/cm",
        "peso_specifico": "kg/cm³",
        "carico_lineare": "kg/cm",
        "carico_superficie": "kg/cm²",
        "deformazione": "—",
    },
    SistemaUnita.KN_M: {
        "lunghezza": "m",
        "area": "m²",
        "volume": "m³",
        "forza": "kN",
        "momento": "kN⋅m",
        "tensione": "kPa",
        "rigidezza_lineare": "kN/m",
        "peso_specifico": "kN/m³",
        "carico_lineare": "kN/m",
        "carico_superficie": "kN/m²",
        "deformazione": "—",
    },
    SistemaUnita.N_MM: {
        "lunghezza": "mm",
        "area": "mm²",
        "volume": "mm³",
        "forza": "N",
        "momento": "N⋅mm",
        "tensione": "MPa",
        "rigidezza_lineare": "N/mm",
        "peso_specifico": "N/mm³",
        "carico_lineare": "N/mm",
        "carico_superficie": "MPa",
        "deformazione": "—",
    },
}


class GestoreUnita:
    """Gestore centralizzato del sistema di unità di misura.

    Singleton globale utilizzato da tutti i moduli GUI per
    conversione e visualizzazione delle unità.

    Il sistema interno del software è sempre kg-cm.
    Le conversioni avvengono solo all'interfaccia (input/output GUI).
    """

    def __init__(self) -> None:
        self._sistema = SistemaUnita.KG_CM
        self._listener: list[Callable[[SistemaUnita], None]] = []

    @property
    def sistema(self) -> SistemaUnita:
        """Sistema di unità attualmente selezionato."""
        return self._sistema

    def imposta_sistema(self, sistema: SistemaUnita) -> None:
        """Cambia il sistema di unità di misura.

        Parametri:
            sistema: Nuovo sistema di unità.
        """
        if sistema != self._sistema:
            vecchio = self._sistema
            self._sistema = sistema
            logger.info("Sistema unità cambiato: %s → %s", vecchio.value, sistema.value)
            for listener in self._listener:
                try:
                    listener(sistema)
                except Exception:
                    logger.debug("Errore in listener cambio unità", exc_info=True)

    def aggiungi_listener(self, callback: Callable[[SistemaUnita], None]) -> None:
        """Aggiunge un listener notificato al cambio sistema."""
        self._listener.append(callback)

    def rimuovi_listener(self, callback: Callable[[SistemaUnita], None]) -> None:
        """Rimuove un listener."""
        try:
            self._listener.remove(callback)
        except ValueError:
            pass

    # --- Conversioni da sistema interno (kg-cm) al sistema utente ---

    def converti(self, valore: float, grandezza: str) -> float:
        """Converte un valore dal sistema interno al sistema utente.

        Parametri:
            valore: Valore nel sistema interno (kg-cm).
            grandezza: Tipo di grandezza ("lunghezza", "tensione", "forza", etc.).

        Restituisce:
            Valore convertito nel sistema utente.
        """
        fattore = _FATTORI_CONVERSIONE[self._sistema].get(grandezza, 1.0)
        return valore * fattore

    def da_input(self, valore: float, grandezza: str) -> float:
        """Converte un valore dall'input utente al sistema interno (kg-cm).

        Parametri:
            valore: Valore nel sistema utente.
            grandezza: Tipo di grandezza.

        Restituisce:
            Valore convertito nel sistema interno (kg-cm).
        """
        fattore = _FATTORI_CONVERSIONE[self._sistema].get(grandezza, 1.0)
        if fattore == 0:
            return 0.0
        return valore / fattore

    # --- Metodi di convenienza per grandezze comuni ---

    def converti_lunghezza(self, valore_cm: float) -> float:
        """Converte una lunghezza da cm al sistema utente."""
        return self.converti(valore_cm, "lunghezza")

    def da_input_lunghezza(self, valore: float) -> float:
        """Converte una lunghezza dall'input utente a cm."""
        return self.da_input(valore, "lunghezza")

    def converti_tensione(self, valore_kgcm2: float) -> float:
        """Converte una tensione da kg/cm² al sistema utente."""
        return self.converti(valore_kgcm2, "tensione")

    def da_input_tensione(self, valore: float) -> float:
        """Converte una tensione dall'input utente a kg/cm²."""
        return self.da_input(valore, "tensione")

    def converti_forza(self, valore_kg: float) -> float:
        """Converte una forza da kg al sistema utente."""
        return self.converti(valore_kg, "forza")

    def da_input_forza(self, valore: float) -> float:
        """Converte una forza dall'input utente a kg."""
        return self.da_input(valore, "forza")

    def converti_momento(self, valore_kgcm: float) -> float:
        """Converte un momento da kg⋅cm al sistema utente."""
        return self.converti(valore_kgcm, "momento")

    def da_input_momento(self, valore: float) -> float:
        """Converte un momento dall'input utente a kg⋅cm."""
        return self.da_input(valore, "momento")

    def converti_area(self, valore_cm2: float) -> float:
        """Converte un'area da cm² al sistema utente."""
        return self.converti(valore_cm2, "area")

    def da_input_area(self, valore: float) -> float:
        """Converte un'area dall'input utente a cm²."""
        return self.da_input(valore, "area")

    # --- Label delle unità ---

    def label(self, grandezza: str) -> str:
        """Restituisce la label dell'unità di misura per la grandezza specificata.

        Parametri:
            grandezza: Tipo di grandezza ("lunghezza", "tensione", etc.).

        Restituisce:
            Stringa con l'unità di misura (es. "kg/cm²", "MPa", "kPa").
        """
        return _LABEL_UNITA[self._sistema].get(grandezza, "?")

    def label_lunghezza(self) -> str:
        """Label unità di lunghezza."""
        return self.label("lunghezza")

    def label_tensione(self) -> str:
        """Label unità di tensione."""
        return self.label("tensione")

    def label_forza(self) -> str:
        """Label unità di forza."""
        return self.label("forza")

    def label_momento(self) -> str:
        """Label unità di momento."""
        return self.label("momento")

    def label_area(self) -> str:
        """Label unità di area."""
        return self.label("area")

    def descrizione_sistema(self) -> str:
        """Restituisce una descrizione leggibile del sistema corrente."""
        descrizioni = {
            SistemaUnita.KG_CM: "kg/cm² — cm — kg⋅cm (sistema storico italiano)",
            SistemaUnita.KN_M: "kPa — m — kN⋅m (sistema internazionale)",
            SistemaUnita.N_MM: "MPa — mm — N⋅mm (sistema tecnico)",
        }
        return descrizioni.get(self._sistema, self._sistema.value)


# --- Istanza singleton globale ---
gestore_unita = GestoreUnita()
