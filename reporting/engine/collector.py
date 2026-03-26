"""
Collector — Raccoglie risultati da tutti i moduli registrati.

Interroga il ModuleRegistry e raccoglie i risultati di ogni modulo
per comporre la relazione tecnica completa.
"""

from typing import Optional

from pipeline.module_registry import ModuleRegistry


class ResultsCollector:
    """Raccoglie risultati da tutti i moduli."""

    def __init__(self):
        """Inizializza il collector."""
        self.registry = ModuleRegistry()
        self.results_by_module: dict[str, list] = {}

    def collect_from_module(self, module_id: str, results: list) -> None:
        """
        Aggiunge risultati di un modulo.

        Args:
            module_id: ID modulo (es. "verifiche_ca")
            results: Lista di ModuleResult
        """
        self.results_by_module[module_id] = results

    def get_all_results(self) -> dict[str, list]:
        """Ritorna tutti i risultati raccolti."""
        return self.results_by_module

    def get_module_results(self, module_id: str) -> Optional[list]:
        """Ritorna risultati di un modulo specifico."""
        return self.results_by_module.get(module_id)

    def list_modules_with_results(self) -> list[str]:
        """Elenca i moduli che hanno fornito risultati."""
        return list(self.results_by_module.keys())

    def get_summary(self) -> dict:
        """Ritorna un riepilogo dei risultati."""
        return {
            "num_modules": len(self.results_by_module),
            "modules": list(self.results_by_module.keys()),
            "total_elements": sum(len(results) for results in self.results_by_module.values()),
        }
