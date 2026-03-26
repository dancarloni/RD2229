"""
Dispatcher multi-norma per valutazione strutture esistenti.

Coordina le valutazioni verso il motore appropriato in base alla norma selezionata.
Supporta:
- NTC2018 — Valutazione della sicurezza strutturale
- RD2229, DM72, DM87 — Norme storiche per edifici di interesse storico
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class EsistenziInput:
    """Dati di ingresso per valutazione strutture esistenti."""

    building_id: str  # ID edificio
    year_built: int  # Anno costruzione
    construction_type: str  # Tipo costruzione (ca, muratura, acciaio)


class EsistenziEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per valutazione strutture esistenti.

    Instrada le valutazioni all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None
        self._rd2229_engine = None
        self._dm72_engine = None
        self._dm87_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("building_id"):
            errors.append("building_id mancante")
        if not isinstance(input_data.get("year_built"), int):
            errors.append("year_built non valido")
        if not input_data.get("construction_type"):
            errors.append("construction_type mancante")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue la valutazione per un edificio esistente.

        Args:
            input_data: Dati di ingresso
            norm_code: Codice norma (NTC2018, RD2229, DM72, DM87, ecc.)

        Returns:
            ModuleResult con valutazione della sicurezza
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
        elif norm_code == "RD2229":
            return self._run_rd2229(input_data)
        elif norm_code == "DM72":
            return self._run_dm72(input_data)
        elif norm_code == "DM87":
            return self._run_dm87(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("building_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue valutazioni su N edifici.

        Args:
            elements: Lista di edifici da valutare
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
        """Esegue valutazione NTC2018. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("building_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_rd2229(self, input_data: dict) -> ModuleResult:
        """Esegue valutazione RD2229. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("building_id", "unknown"),
            errors=["Implementazione RD2229 in progress"],
        )

    def _run_dm72(self, input_data: dict) -> ModuleResult:
        """Esegue valutazione DM72. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("building_id", "unknown"),
            errors=["Implementazione DM72 in progress"],
        )

    def _run_dm87(self, input_data: dict) -> ModuleResult:
        """Esegue valutazione DM87. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("building_id", "unknown"),
            errors=["Implementazione DM87 in progress"],
        )
