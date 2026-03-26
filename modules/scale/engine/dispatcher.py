"""
Dispatcher multi-norma per progetto scale.

Coordina il progetto verso il motore appropriato in base alla norma selezionata.
Supporta:
- NTC2018 — Scale in c.a., acciaio, legno, muratura
- EC3 — Eurocodice 3: Progettazione costruzioni in acciaio
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class ScaleInput:
    """Dati di ingresso per progetto scale."""

    stair_id: str  # ID scala
    material_type: str  # Tipo materiale (ca, steel, wood)
    span_length: float  # Lunghezza rampa (cm)
    num_steps: int  # Numero gradini


class ScaleEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per progetto scale.

    Instrada il progetto all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None
        self._ec3_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("stair_id"):
            errors.append("stair_id mancante")
        if not input_data.get("material_type"):
            errors.append("material_type mancante")
        if not isinstance(input_data.get("span_length"), (int, float)):
            errors.append("span_length non valida")
        if not isinstance(input_data.get("num_steps"), int):
            errors.append("num_steps non valido")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue il progetto scala.

        Args:
            input_data: Dati di ingresso
            norm_code: Codice norma (NTC2018, EC3, ecc.)

        Returns:
            ModuleResult con dimensionamenti e verifiche
        """
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("stair_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        elif norm_code == "EC3":
            return self._run_ec3(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("stair_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue progetto su N scale.

        Args:
            elements: Lista di scale da progettare
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
        """Esegue progetto NTC2018. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("stair_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_ec3(self, input_data: dict) -> ModuleResult:
        """Esegue progetto EC3. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("stair_id", "unknown"),
            errors=["Implementazione EC3 in progress"],
        )
