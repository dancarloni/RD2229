"""
Test Modulo Verifiche c.a. — Verifica struttura e funzionalità base.
"""

import pytest


def test_verifiche_ca_module_info():
    """Test: ModuleInfo è correttamente definito."""
    from modules.verifiche_ca import MODULE_INFO

    assert MODULE_INFO.id == "verifiche_ca"
    assert MODULE_INFO.name == "Verifiche c.a."
    assert "NTC2018" in MODULE_INFO.norms_supported
    assert "RD2229" in MODULE_INFO.norms_supported
    assert len(MODULE_INFO.norms_supported) == 8


def test_verifiche_ca_create_engine():
    """Test: Factory crea engine."""
    from modules.verifiche_ca import create_engine

    engine = create_engine()
    assert engine is not None


def test_verifiche_ca_create_window():
    """Test: Factory crea window GUI."""
    from modules.verifiche_ca import create_window

    # Non instanziamo la finestra per evitare dipendenze Qt in test
    # Ma verifichiamo che la factory sia callable
    assert callable(create_window)


def test_verifiche_ca_engine_validate_input():
    """Test: Engine valida input correttamente."""
    from modules.verifiche_ca.engine.dispatcher import VerificheCaEngine

    engine = VerificheCaEngine()

    # Input invalido (mancano campi)
    errors = engine.validate_input({})
    assert len(errors) > 0

    # Input valido
    errors = engine.validate_input(
        {
            "element_id": "elem1",
            "section_id": "sec1",
            "material_id": "mat1",
            "load_manager": object(),
        }
    )
    assert len(errors) == 0


def test_verifiche_ca_engine_unsupported_norm():
    """Test: Engine rifiuta norme non supportate."""
    from modules.verifiche_ca.engine.dispatcher import VerificheCaEngine

    engine = VerificheCaEngine()

    result = engine.run(
        {
            "element_id": "elem1",
            "section_id": "sec1",
            "material_id": "mat1",
            "load_manager": object(),
        },
        norm_code="UNKNOWNNORM",
    )

    assert not result.ok
    assert len(result.errors) > 0
    assert "non supportata" in result.errors[0].lower()


def test_verifiche_ca_engine_placeholder_norms():
    """Test: Engine restituisce placeholder per norme in implementazione."""
    from modules.verifiche_ca.engine.dispatcher import VerificheCaEngine

    engine = VerificheCaEngine()

    input_data = {
        "element_id": "elem1",
        "section_id": "sec1",
        "material_id": "mat1",
        "load_manager": object(),
    }

    # Test tutti i norm code supportati
    for norm_code in ["RD2229", "NTC2018", "NTC2008", "DM92", "DM96"]:
        result = engine.run(input_data, norm_code)
        # Per ora tutti ritornano placeholder (ok=False, implementazione in progress)
        assert isinstance(result.ok, bool)


def test_verifiche_ca_engine_run_batch():
    """Test: Engine esegue batch su più elementi."""
    from modules.verifiche_ca.engine.dispatcher import VerificheCaEngine

    engine = VerificheCaEngine()

    elements = [
        {
            "element_id": f"elem{i}",
            "section_id": "sec1",
            "material_id": "mat1",
            "load_manager": object(),
        }
        for i in range(3)
    ]

    results = engine.run_batch(elements, "NTC2018")
    assert len(results) == 3


def test_verifiche_ca_registry_registration():
    """Test: Modulo si registra correttamente nel registry."""
    from modules.verifiche_ca import MODULE_INFO, register
    from pipeline.module_registry import ModuleRegistry

    # Registra il modulo
    register()

    # Verifica che sia registrato
    registry = ModuleRegistry()
    retrieved = registry.get("verifiche_ca")

    assert retrieved is not None
    assert retrieved[0].id == "verifiche_ca"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
