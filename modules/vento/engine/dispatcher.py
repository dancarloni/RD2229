"""
Dispatcher multi-norma per calcolo azioni vento.

Coordina il calcolo verso il motore appropriato in base alla norma selezionata.
Supporta:
- NTC2018 — Azioni del vento su edifici e strutture
- EN1991 — Eurocodice 1: Azioni sul vento
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class VentoInput:
    """Dati di ingresso per il calcolo vento."""

    site_id: str  # ID sito/ubicazione
    building_id: str  # ID edificio
    category: str  # Categoria di esposizione (I, II, III, IV)


class VentoEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per calcolo azioni vento.

    Instrada il calcolo all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None
        self._en1991_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("site_id"):
            errors.append("site_id mancante")
        if not input_data.get("building_id"):
            errors.append("building_id mancante")
        if not input_data.get("category"):
            errors.append("category mancante")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue il calcolo vento per un edificio.

        Args:
            input_data: Dati di ingresso (site_id, building_id, category)
            norm_code: Codice norma (NTC2018, EN1991, ecc.)

        Returns:
            ModuleResult con pressioni e coefficienti
        """
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("building_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        elif norm_code == "EN1991":
            return self._run_en1991(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("building_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue calcolo vento su N edifici.

        Args:
            elements: Lista di edifici da analizzare
            norm_code: Codice norma

        Returns:
            Lista di ModuleResult
        """
        results = []
        for elem in elements:
            result = self.run(elem, norm_code)
            results.append(result)
        return results

    def _run_ntc2018(self, input_data: dict) -> ModuleResult:
        """Esegue calcolo NTC2018. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("building_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_en1991(self, input_data: dict) -> ModuleResult:
        """Esegue calcolo EN1991. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("building_id", "unknown"),
            errors=["Implementazione EN1991 in progress"],
        )
