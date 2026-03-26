"""
Test di integrazione — Verifica che pipeline completa funziona.
"""

import pytest


def test_all_modules_registered():
    """Test: Verifica che tutti i moduli sono disponibili."""
    from pipeline.module_registry import ModuleRegistry

    registry = ModuleRegistry()

    # Registra moduli prioritari
    from modules.sismica import register as reg_sismica
    from modules.verifiche_ca import register as reg_verifiche_ca

    reg_verifiche_ca()
    reg_sismica()

    # Verifica
    all_modules = registry.list_all()
    module_ids = [m.id for m in all_modules]

    assert "verifiche_ca" in module_ids
    assert "sismica" in module_ids


def test_module_retrieval():
    """Test: Recupera modulo dal registry."""
    from modules.verifiche_ca import register as reg_verifiche_ca
    from pipeline.module_registry import ModuleRegistry

    registry = ModuleRegistry()
    reg_verifiche_ca()

    # Recupera modulo
    result = registry.get("verifiche_ca")
    assert result is not None

    module_info, engine_factory, window_factory = result
    assert module_info.name == "Verifiche c.a."
    assert engine_factory is not None


def test_pipeline_orchestrator():
    """Test: Orchestrator pipeline."""
    from pipeline.orchestrator import PipelineOrchestrator

    orchestrator = PipelineOrchestrator()

    # Carica configurazione
    config = {
        "norm_code": "NTC2018",
        "limit_states": ["SLU", "SLE_rara"],
        "modules_enabled": {
            "verifiche_ca": True,
            "sismica": True,
        },
    }

    orchestrator.load_config(config)

    # Esegui pipeline
    result = orchestrator.run()
    assert result["ok"] is True
    assert result["norm_code"] == "NTC2018"


def test_results_collector():
    """Test: Collector raccoglie risultati."""
    from reporting.engine.collector import ResultsCollector

    collector = ResultsCollector()

    # Simula risultati da modulo
    collector.collect_from_module("verifiche_ca", [])
    collector.collect_from_module("sismica", [])

    # Verifica
    modules_with_results = collector.list_modules_with_results()
    assert "verifiche_ca" in modules_with_results
    assert "sismica" in modules_with_results


def test_report_builder():
    """Test: Report builder."""
    from reporting.engine.report_builder import ReportBuilder

    builder = ReportBuilder()

    builder.add_section("Introduzione", "Questo è il testo introduttivo.")
    builder.add_section("Risultati", "Ecco i risultati del calcolo.")

    md = builder.generate_markdown()
    assert "Introduzione" in md
    assert "Risultati" in md
    assert "# Relazione Tecnica Strutturale" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
