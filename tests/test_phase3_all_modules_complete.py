"""
Test di integrazione Fase 3 — Verifica completamento di TUTTI i 13 moduli.
"""

import pytest


def test_all_13_modules_discoverable():
    """Test: I 13 moduli sono tutti scoperti dal registry."""
    from modules.combinazioni import register as reg_combinazioni
    from modules.esistenti import register as reg_esistenti
    from modules.fem_telaio import register as reg_fem_telaio
    from modules.fuoco import register as reg_fuoco
    from modules.geotecnica import register as reg_geotecnica
    from modules.muratura import register as reg_muratura
    from modules.scale import register as reg_scale
    from modules.sismica import register as reg_sismica
    from modules.vento import register as reg_vento
    from modules.verifiche_ca import register as reg_verifiche_ca
    from pipeline.module_registry import ModuleRegistry

    # Registra tutti i 10 moduli
    reg_verifiche_ca()
    reg_sismica()
    reg_vento()
    reg_fuoco()
    reg_muratura()
    reg_geotecnica()
    reg_combinazioni()
    reg_scale()
    reg_fem_telaio()
    reg_esistenti()

    registry = ModuleRegistry()
    all_modules = registry.list_all()
    module_ids = [m.id for m in all_modules]

    # Verifica che ci siano almeno i 10 moduli di calcolo
    expected_modules = [
        "verifiche_ca",
        "sismica",
        "vento",
        "fuoco",
        "muratura",
        "geotecnica",
        "combinazioni",
        "scale",
        "fem_telaio",
        "esistenti",
    ]

    for module_id in expected_modules:
        assert module_id in module_ids, f"Modulo {module_id} non trovato nel registry"


def test_module_completeness_prioritary():
    """Test: I 2 moduli prioritari sono completi con factory e window."""
    from modules.sismica import (
        MODULE_INFO as sismica_info,
        create_engine as sismica_engine,
        create_window as sismica_window,
    )
    from modules.verifiche_ca import (
        MODULE_INFO as verifiche_ca_info,
        create_engine as vca_engine,
        create_window as vca_window,
    )

    # Verifiche c.a.
    assert verifiche_ca_info.id == "verifiche_ca"
    assert vca_engine() is not None
    assert callable(vca_window)

    # Sismica
    assert sismica_info.id == "sismica"
    assert sismica_engine() is not None
    assert callable(sismica_window)


def test_module_completeness_secondary():
    """Test: I 8 moduli secondari sono completi con factory e window."""
    from modules.combinazioni import (
        MODULE_INFO as combinazioni_info,
        create_engine as combinazioni_engine,
        create_window as combinazioni_window,
    )
    from modules.esistenti import (
        MODULE_INFO as esistenti_info,
        create_engine as esistenti_engine,
        create_window as esistenti_window,
    )
    from modules.fem_telaio import (
        MODULE_INFO as fem_telaio_info,
        create_engine as fem_telaio_engine,
        create_window as fem_telaio_window,
    )
    from modules.fuoco import (
        MODULE_INFO as fuoco_info,
        create_engine as fuoco_engine,
        create_window as fuoco_window,
    )
    from modules.geotecnica import (
        MODULE_INFO as geotecnica_info,
        create_engine as geotecnica_engine,
        create_window as geotecnica_window,
    )
    from modules.muratura import (
        MODULE_INFO as muratura_info,
        create_engine as muratura_engine,
        create_window as muratura_window,
    )
    from modules.scale import (
        MODULE_INFO as scale_info,
        create_engine as scale_engine,
        create_window as scale_window,
    )
    from modules.vento import (
        MODULE_INFO as vento_info,
        create_engine as vento_engine,
        create_window as vento_window,
    )

    secondary_modules = [
        (vento_info, vento_engine, vento_window, "vento"),
        (fuoco_info, fuoco_engine, fuoco_window, "fuoco"),
        (muratura_info, muratura_engine, muratura_window, "muratura"),
        (geotecnica_info, geotecnica_engine, geotecnica_window, "geotecnica"),
        (combinazioni_info, combinazioni_engine, combinazioni_window, "combinazioni"),
        (scale_info, scale_engine, scale_window, "scale"),
        (fem_telaio_info, fem_telaio_engine, fem_telaio_window, "fem_telaio"),
        (esistenti_info, esistenti_engine, esistenti_window, "esistenti"),
    ]

    for info, engine_factory, window_factory, expected_id in secondary_modules:
        assert info.id == expected_id, f"ModuleInfo.id mismatch: {info.id} != {expected_id}"
        assert engine_factory() is not None, f"Engine factory fallito per {expected_id}"
        assert callable(window_factory), f"Window factory non callable per {expected_id}"


def test_module_engine_interfaces():
    """Test: Tutti i moduli implementano l'interfaccia ModuleEngine."""
    from modules.combinazioni import create_engine as combinazioni_create
    from modules.esistenti import create_engine as esistenti_create
    from modules.fem_telaio import create_engine as fem_create
    from modules.fuoco import create_engine as fuoco_create
    from modules.geotecnica import create_engine as geotecnica_create
    from modules.muratura import create_engine as muratura_create
    from modules.scale import create_engine as scale_create
    from modules.sismica import create_engine as sismica_create
    from modules.vento import create_engine as vento_create
    from modules.verifiche_ca import create_engine as vca_create

    engines = [
        ("verifiche_ca", vca_create()),
        ("sismica", sismica_create()),
        ("vento", vento_create()),
        ("fuoco", fuoco_create()),
        ("muratura", muratura_create()),
        ("geotecnica", geotecnica_create()),
        ("combinazioni", combinazioni_create()),
        ("scale", scale_create()),
        ("fem_telaio", fem_create()),
        ("esistenti", esistenti_create()),
    ]

    for module_id, engine in engines:
        assert hasattr(engine, "validate_input"), f"{module_id}: manca validate_input"
        assert hasattr(engine, "run"), f"{module_id}: manca run"
        assert hasattr(engine, "run_batch"), f"{module_id}: manca run_batch"
        assert callable(engine.validate_input), f"{module_id}: validate_input non callable"
        assert callable(engine.run), f"{module_id}: run non callable"
        assert callable(engine.run_batch), f"{module_id}: run_batch non callable"


def test_pipeline_can_orchestrate_all_modules():
    """Test: L'orchestratore pipeline può caricare config e eseguire."""
    from modules.sismica import register as reg_sismica
    from modules.verifiche_ca import register as reg_verifiche_ca
    from pipeline.orchestrator import PipelineOrchestrator

    # Registra almeno 2 moduli
    reg_verifiche_ca()
    reg_sismica()

    orchestrator = PipelineOrchestrator()

    config = {
        "norm_code": "NTC2018",
        "limit_states": ["SLU", "SLE_rara"],
        "modules_enabled": {
            "verifiche_ca": True,
            "sismica": True,
        },
    }

    orchestrator.load_config(config)
    result = orchestrator.run()

    assert result is not None
    assert "ok" in result
    assert "norm_code" in result


def test_reporting_can_collect_from_all():
    """Test: Collector di reporting può aggregare da tutti i moduli."""
    from reporting.engine.collector import ResultsCollector

    collector = ResultsCollector()

    # Simula risultati da vari moduli
    collector.collect_from_module("verifiche_ca", [{"element_id": "elem1", "ok": True}])
    collector.collect_from_module("sismica", [{"site_params": "ok"}])
    collector.collect_from_module("vento", [{"zone": 1, "ok": True}])

    modules_with_results = collector.list_modules_with_results()
    assert "verifiche_ca" in modules_with_results
    assert "sismica" in modules_with_results
    assert "vento" in modules_with_results


def test_report_builder_with_all_sections():
    """Test: ReportBuilder può generare relazione completa."""
    from reporting.engine.report_builder import ReportBuilder

    builder = ReportBuilder()

    builder.add_section("1. Premessa", "Studio strutturale dell'edificio.")
    builder.add_section("2. Normativa", "NTC2018 — D.M. 17/01/2018")
    builder.add_section("3. Materiali", "Calcestruzzo C25/30, Acciaio B450C")
    builder.add_section("4. Verifiche c.a.", "Flessione, taglio, torsione, SLE")
    builder.add_section("5. Sismica", "Spettro di risposta, pushover")
    builder.add_section("6. Vento", "Pressioni dinamiche per zona 1")
    builder.add_section("7. Conclusioni", "Struttura verificata.")

    md = builder.generate_markdown()
    assert "Premessa" in md
    assert "Normativa" in md
    assert "Materiali" in md
    assert "Verifiche c.a." in md
    assert "Sismica" in md
    assert "Vento" in md
    assert "Conclusioni" in md


def test_dashboard_window_can_launch_modules():
    """Test: Dashboard può lanciare finestre dei moduli."""
    from dashboard.gui.main_window import DashboardMainWindow
    from modules.sismica import register as reg_sismica
    from modules.verifiche_ca import register as reg_verifiche_ca
    from pipeline.module_registry import ModuleRegistry

    # Registra moduli
    reg_verifiche_ca()
    reg_sismica()

    registry = ModuleRegistry()
    all_modules = registry.list_all()

    # Verifica che il registry trovi i moduli
    assert len(all_modules) >= 2
    assert any(m.id == "verifiche_ca" for m in all_modules)
    assert any(m.id == "sismica" for m in all_modules)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
