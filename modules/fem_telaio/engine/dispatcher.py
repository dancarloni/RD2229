"""
Dispatcher per analisi strutturale FEM/telai.

Coordina l'analisi verso il motore appropriato.
Supporta:
- NTC2018 — Analisi elastica lineare, non lineare geometrica
"""

from dataclasses import dataclass
from typing import List, Optional

from pipeline.module_registry import ModuleEngine, ModuleResult


@dataclass
class FemTelaioInput:
    """Dati di ingresso per analisi FEM/telai."""

    model_id: str  # ID modello strutturale
    num_nodes: int  # Numero nodi
    num_elements: int  # Numero elementi
    load_cases: List[str]  # Casi di carico


class FemTelaioEngine(ModuleEngine):
    """
    Engine dispatcher per analisi strutturale FEM/telai.

    Instrada l'analisi all'implementazione appropriata.
    Raccoglie e aggrega i risultati.
    """

    def __init__(self):
        """Inizializza il dispatcher."""
        self._ntc2018_engine = None

    def validate_input(self, input_data: dict) -> list[str]:
        """
        Valida i dati di ingresso.

        Returns:
            Lista di errori (vuota = input valido)
        """
        errors = []

        if not input_data.get("model_id"):
            errors.append("model_id mancante")
        if not isinstance(input_data.get("num_nodes"), int):
            errors.append("num_nodes non valido")
        if not isinstance(input_data.get("num_elements"), int):
            errors.append("num_elements non valido")
        if not input_data.get("load_cases"):
            errors.append("load_cases mancante")

        return errors

    def run(self, input_data: dict, norm_code: str) -> ModuleResult:
        """
        Esegue l'analisi FEM/telai.

        Args:
            input_data: Dati di ingresso
            norm_code: Codice norma (NTC2018)

        Returns:
            ModuleResult con risultati analisi (spostamenti, reazioni, sollecitazioni)
        """
        errors = self.validate_input(input_data)
        if errors:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("model_id", "unknown"),
                errors=errors,
            )

        if norm_code == "NTC2018":
            return self._run_ntc2018(input_data)
        else:
            return ModuleResult(
                ok=False,
                element_id=input_data.get("model_id", "unknown"),
                errors=[f"Norma non supportata: {norm_code}"],
            )

    def run_batch(self, elements: list[dict], norm_code: str) -> list[ModuleResult]:
        """
        Esegue analisi FEM su N modelli.

        Args:
            elements: Lista di modelli
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
            element_id=input_data.get("model_id", "unknown"),
            errors=["Implementazione NTC2018 in progress"],
        )
