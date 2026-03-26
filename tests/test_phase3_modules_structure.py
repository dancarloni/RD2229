"""
Test Fase 3 — Verifica che tutti i 10 moduli hanno la struttura corretta.
Focus: verificare che i moduli siano importabili e abbiano le interfacce giuste.
"""

import pytest


class TestPhase3ModulesStructure:
    """Test della struttura di base per tutti i moduli Phase 3."""

    @pytest.mark.parametrize(
        "module_name,module_id",
        [
            ("modules.vento", "vento"),
            ("modules.fuoco", "fuoco"),
            ("modules.muratura", "muratura"),
            ("modules.geotecnica", "geotecnica"),
            ("modules.combinazioni", "combinazioni"),
            ("modules.scale", "scale"),
            ("modules.fem_telaio", "fem_telaio"),
            ("modules.esistenti", "esistenti"),
        ],
    )
    def test_module_has_module_info(self, module_name, module_id):
        """Test: Ogni modulo ha MODULE_INFO correttamente definito."""
        module = __import__(module_name, fromlist=["MODULE_INFO"])
        assert hasattr(module, "MODULE_INFO")
        assert module.MODULE_INFO.id == module_id

    @pytest.mark.parametrize(
        "module_name",
        [
            "modules.vento",
            "modules.fuoco",
            "modules.muratura",
            "modules.geotecnica",
            "modules.combinazioni",
            "modules.scale",
            "modules.fem_telaio",
            "modules.esistenti",
        ],
    )
    def test_module_has_factory_functions(self, module_name):
        """Test: Ogni modulo ha le factory functions."""
        module = __import__(module_name, fromlist=["create_engine", "create_window"])
        assert hasattr(module, "create_engine")
        assert hasattr(module, "create_window")
        assert callable(module.create_engine)
        assert callable(module.create_window)

    @pytest.mark.parametrize(
        "module_name",
        [
            "modules.vento",
            "modules.fuoco",
            "modules.muratura",
            "modules.geotecnica",
            "modules.combinazioni",
            "modules.scale",
            "modules.fem_telaio",
            "modules.esistenti",
        ],
    )
    def test_module_engine_has_interfaces(self, module_name):
        """Test: Engine implementa le interfacce richieste."""
        module = __import__(module_name, fromlist=["create_engine"])
        engine = module.create_engine()

        assert hasattr(engine, "validate_input")
        assert hasattr(engine, "run")
        assert hasattr(engine, "run_batch")
        assert callable(engine.validate_input)
        assert callable(engine.run)
        assert callable(engine.run_batch)

    @pytest.mark.parametrize(
        "module_name",
        [
            "modules.vento",
            "modules.fuoco",
            "modules.muratura",
            "modules.geotecnica",
            "modules.combinazioni",
            "modules.scale",
            "modules.fem_telaio",
            "modules.esistenti",
        ],
    )
    def test_module_register_function_exists(self, module_name):
        """Test: Ogni modulo ha funzione register()."""
        module = __import__(module_name, fromlist=["register"])
        assert hasattr(module, "register")
        assert callable(module.register)


def test_all_phase3_modules_can_be_registered():
    """Test: Tutti i moduli Phase 3 possono registrarsi nel registry."""
    from modules.combinazioni import register as reg_combinazioni
    from modules.esistenti import register as reg_esistenti
    from modules.fem_telaio import register as reg_fem_telaio
    from modules.fuoco import register as reg_fuoco
    from modules.geotecnica import register as reg_geotecnica
    from modules.muratura import register as reg_muratura
    from modules.scale import register as reg_scale
    from modules.vento import register as reg_vento
    from pipeline.module_registry import ModuleRegistry

    # Registra tutti i moduli Phase 3
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

    expected_phase3 = [
        "vento",
        "fuoco",
        "muratura",
        "geotecnica",
        "combinazioni",
        "scale",
        "fem_telaio",
        "esistenti",
    ]

    for module_id in expected_phase3:
        assert module_id in module_ids, f"Modulo {module_id} non trovato"


def test_phase3_modules_with_prioritary_form_complete_suite():
    """Test: I 10 moduli (2 prioritari + 8 secondari) formano suite completa."""
    from modules.combinazioni import register as reg_combinazioni
    from modules.esistenti import register as reg_esistenti
    from modules.fem_telaio import register as reg_fem_telaio
    from modules.fuoco import register as reg_fuoco
    from modules.geotecnica import register as reg_geotecnica
    from modules.muratura import register as reg_muratura
    from modules.scale import register as reg_scale
    from modules.sismica import register as reg_sismica
    from modules.vento import register as reg_vento
    from modules.verifiche_ca import register as reg_vca
    from pipeline.module_registry import ModuleRegistry

    # Registra tutti i 10 moduli
    reg_vca()
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

    expected_all_10 = [
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

    assert len(module_ids) >= 10, f"Attesi almeno 10 moduli, trovati {len(module_ids)}"

    for module_id in expected_all_10:
        assert module_id in module_ids, f"Modulo {module_id} non trovato (trovati: {module_ids})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
