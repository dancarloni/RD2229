"""
Dispatcher multi-norma per verifiche resistenza fuoco.

Coordina le verifiche verso il motore appropriato in base alla norma selezionata.
Supporta:
- NTC2018 — Verifiche di resistenza al fuoco per elementi
- ISO834 — Curva di incendio standard
"""

from dataclasses import dataclass
from typing import Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class FuocoInput:
    """Dati di ingresso per la verifica fuoco."""

    element_id: str  # ID elemento
    material_type: str  # Tipo materiale (ca, acciaio, legno)
    section_id: str  # ID sezione
    required_time: float  # Tempo resistenza richiesto (min)


class FuocoEngine(ModuleEngine):
    """
    Engine dispatcher multi-norma per verifiche fuoco.

    Instrada le verifiche all'implementazione appropriata basata sulla norma.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None
        self._iso834_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("element_id"):
            errors.append("element_id mancante")
        if not input_data.get("material_type"):
            errors.append("material_type mancante")
        if not input_data.get("section_id"):
            errors.append("section_id mancante")
        if not isinstance(input_data.get("required_time"), (int, float)):
            errors.append("required_time non valido")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue la verifica fuoco per un elemento.

        Args:
            input_data: Dati di ingresso
            norm_code: Codice norma (NTC2018, ISO834, ecc.)

        Returns:
            ModuleResult con verifiche fuoco
        """
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("element_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        elif norm_code == "ISO834":
            return self._run_iso834(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("element_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue verifiche fuoco su N elementi.

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
            element_id=input_data.get("element_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )

    def _run_iso834(self, input_data: dict) -> ModuleResult:
        """Esegue verifica ISO834. Placeholder in implementazione."""
        return ModuleResult(
            ok=False,
            element_id=input_data.get("element_id", "unknown"),
            errors=["Implementazione ISO834 in progress"],
        )
