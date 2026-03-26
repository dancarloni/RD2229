"""
Dispatcher multi-norma per verifiche muratura.

Coordina le verifiche verso il motore appropriato in base alla norma selezionata.
Supporta:
- NTC2018 — Verifiche di resistenza per muratura ordinaria, armata, confinata
- DM87 — Decreto Ministeriale 1987 (muratura)
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class MuratturaInput:
    """Dati di ingresso per la verifica muratura."""

    wall_id: str  # ID parete/elemento
    material_id: str  # ID materiale (da archivio)
    thickness: float  # Spessore (cm)
    height: float  # Altezza/lunghezza (cm)


class MuratturaEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per verifiche muratura.

    Instrada le verifiche all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None
        self._dm87_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("wall_id"):
            errors.append("wall_id mancante")
        if not input_data.get("material_id"):
            errors.append("material_id mancante")
        if not isinstance(input_data.get("thickness"), (int, float)):
            errors.append("thickness non valida")
        if not isinstance(input_data.get("height"), (int, float)):
            errors.append("height non valida")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue la verifica muratura per un elemento.

        Args:
            input_data: Dati di ingresso
            norm_code: Codice norma (NTC2018, DM87, ecc.)

        Returns:
            ModuleResult con verifiche muratura
        """
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("wall_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        elif norm_code == "DM87":
            return self._run_dm87(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("wall_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue verifiche muratura su N elementi.

        Args:
            elements: Lista di elementi da verificare
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
        """Esegue verifica NTC2018. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("wall_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_dm87(self, input_data: dict) -> ModuleResult:
        """Esegue verifica DM87. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("wall_id", "unknown"),
            errors=["Implementazione DM87 in progress"],
        )
