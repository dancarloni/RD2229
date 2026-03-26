"""
Orchestrator — Coordina esecuzione pipeline di calcolo.

Legge configurazione, esegue moduli in sequenza, raccoglie risultati,
genera relazione tecnica.
"""

from pipeline.module_registry import ModuleRegistry
from reporting.engine.collector import ResultsCollector


class PipelineOrchestrator:
    """Orchestatore della pipeline di calcolo."""

    def __init__(self):
        """Inizializza l'orchestrator."""
        self.registry = ModuleRegistry()
        self.collector = ResultsCollector()
        self.config = {}
        self.results = {}

    def load_config(self, config: dict) -> None:
        """
        Carica configurazione pipeline.

        Args:
            config: Configurazione con:
                - norm_code: Norma di calcolo
                - limit_states: Lista stati limite da calcolare
                - modules_enabled: Dict moduli abilitati
        """
        self.config = config

    def run(self) -> dict:
        """
        Esegue la pipeline completa.

        Returns:
            Risultati aggregati
        """
        if not self.config:
            return {"ok": False, "errors": ["Configurazione non caricata"]}

        # Estrai configurazione
        norm_code = self.config.get("norm_code", "NTC2018")
        modules_enabled = self.config.get("modules_enabled", {})
        limit_states = self.config.get("limit_states", ["SLU"])

        # Esegui moduli abilitati
        results_by_module = {}
        for module_id, enabled in modules_enabled.items():
            if not enabled:
                continue

            module_info_tuple = self.registry.get(module_id)
            if not module_info_tuple:
                continue

            module_info, engine_factory, _ = module_info_tuple
            engine = engine_factory()

            # Placeholder: ottenere elementi da calcolare
            # results = engine.run_batch(elements, norm_code)
            # results_by_module[module_id] = results

        return {
            "ok": True,
            "results_by_module": results_by_module,
            "norm_code": norm_code,
            "limit_states": limit_states,
        }


__all__ = ["PipelineOrchestrator"]
