"""
Dispatcher multi-norma per analisi geotecnica.

Coordina le analisi verso il motore appropriato in base alla norma selezionata.
Supporta:
- NTC2018 — Verifiche di fondazioni, spinte, cedimenti
- EC7 — Eurocodice 7: Progettazione geotecnica
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class GeotecnicaInput:
    """Dati di ingresso per analisi geotecnica."""

    foundation_id: str  # ID fondazione
    soil_id: str  # ID profilo geotecnico
    depth: float  # Profondità di posa (cm)


class GeotecnicaEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per analisi geotecnica.

    Instrada le analisi all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None
        self._ec7_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("foundation_id"):
            errors.append("foundation_id mancante")
        if not input_data.get("soil_id"):
            errors.append("soil_id mancante")
        if not isinstance(input_data.get("depth"), (int, float)):
            errors.append("depth non valida")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue l'analisi geotecnica per una fondazione.

        Args:
            input_data: Dati di ingresso
            norm_code: Codice norma (NTC2018, EC7, ecc.)

        Returns:
            ModuleResult con analisi geotecnica
        """
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("foundation_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        elif norm_code == "EC7":
            return self._run_ec7(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("foundation_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue analisi geotecnica su N fondazioni.

        Args:
            elements: Lista di fondazioni da analizzare
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
        """Esegue analisi NTC2018. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("foundation_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_ec7(self, input_data: dict) -> ModuleResult:
        """Esegue analisi EC7. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("foundation_id", "unknown"),
            errors=["Implementazione EC7 in progress"],
        )
