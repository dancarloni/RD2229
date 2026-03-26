"""Test Modulo Sismica."""

import pytest


def test_sismica_module_info():
    """Test: ModuleInfo per sismica."""
    from modules.sismica import MODULE_INFO

    assert MODULE_INFO.id == "sismica"
    assert "NTC2018" in MODULE_INFO.norms_supported
    assert MODULE_INFO.category == "azioni"


def test_sismica_create_engine():
    """Test: Factory crea engine."""
    from modules.sismica import create_engine

    engine = create_engine()
    assert engine is not None


def test_sismica_engine_validate_input():
    """Test: Engine valida input."""
    from modules.sismica.engine.dispatcher import SismicaEngine

    engine = SismicaEngine()

    # Input invalido
    errors = engine.validate_input({})
    assert len(errors) > 0

    # Input valido
    errors = engine.validate_input(
        {
            "element_id": "elem1",
            "site_params": {},
            "structure_type": "telaio",
        }
    )
    assert len(errors) == 0


def test_sismica_registry_registration():
    """Test: Modulo si registra nel registry."""
    from modules.sismica import register
    from pipeline.module_registry import ModuleRegistry

    register()

    registry = ModuleRegistry()
    retrieved = registry.get("sismica")
    assert retrieved is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
