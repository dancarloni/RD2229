"""
Dispatcher multi-norma per generazione combinazioni.

Coordina la generazione verso il motore appropriato in base alla norma selezionata.
Supporta:
- NTC2018 — Combinazioni SLU, SLE, CAR
- NTC2008 — Combinazioni legacy 2008
"""

from dataclasses import dataclass
from typing import List, Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class CombinazioniInput:
    """Dati di ingresso per generazione combinazioni."""

    project_id: str  # ID progetto
    load_cases: List[str]  # Lista dei casi di carico
    num_accidental: int = 0  # Numero carichi accidentali


class CombinazioniEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per generazione combinazioni.

    Instrada la generazione all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None
        self._ntc2008_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("project_id"):
            errors.append("project_id mancante")
        if not input_data.get("load_cases"):
            errors.append("load_cases mancante")
        if not isinstance(input_data.get("load_cases"), list):
            errors.append("load_cases deve essere una lista")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Genera combinazioni per un progetto.

        Args:
            input_data: Dati di ingresso
            norm_code: Codice norma (NTC2018, NTC2008, ecc.)

        Returns:
            ModuleResult con combinazioni generate
        """
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("project_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        elif norm_code == "NTC2008":
            return self._run_ntc2008(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("project_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Genera combinazioni per N progetti.

        Args:
            elements: Lista di progetti
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
        """Genera combinazioni NTC2018. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("project_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_ntc2008(self, input_data: dict) -> ModuleResult:
        """Genera combinazioni NTC2008. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("project_id", "unknown"),
            errors=["Implementazione NTC2008 in progress"],
        )
