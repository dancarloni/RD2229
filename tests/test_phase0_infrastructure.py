"""
Test Phase 0 Infrastructure — Verifica che tutti i moduli infrastructure siano importabili.
"""

import pytest


def test_pipeline_module_registry_import():
    """Test: pipeline.module_registry è importabile."""
    from pipeline.module_registry import (
        CheckResult,
        KnowledgeLevel,
        LoadCondition,
        ModuleEngine,
        ModuleInfo,
        ModuleRegistry,
        ModuleResult,
    )

    assert ModuleInfo is not None
    assert ModuleRegistry is not None


def test_loads_models_import():
    """Test: shared.loads.engine.models è importabile."""
    from shared.loads.engine.models import LimitState, LoadCondition, LoadConditionManager

    assert LoadCondition is not None
    assert LimitState.SLU is not None
    assert LimitState.SLE_rara is not None


def test_materials_knowledge_level_import():
    """Test: shared.materials.engine.knowledge_level è importabile."""
    from shared.materials.engine.knowledge_level import (
        KnowledgeLevel,
        KnowledgeLevelFactory,
        KnowledgeLevelType,
    )

    assert KnowledgeLevel is not None
    assert KnowledgeLevelType.LC1 is not None


def test_norms_material_map_import():
    """Test: shared.norms.engine.norm_material_map è importabile."""
    from shared.norms.engine.norm_material_map import NormMaterialMap

    assert NormMaterialMap is not None


def test_shared_ui_base_module_window_import():
    """Test: shared.ui.base_module_window è importabile (con fallback Qt)."""
    from shared.ui.base_module_window import QT_BACKEND, BaseModuleWindow

    assert BaseModuleWindow is not None
    assert QT_BACKEND in ["PySide6", "PyQt6"]


def test_load_condition_creation():
    """Test: Creazione LoadCondition."""
    from shared.loads.engine.models import LimitState, LoadCondition

    cond = LoadCondition(
        name="PP+Perm",
        limit_state=LimitState.SLU,
        N=50.0,
        Mx=120.0,
    )
    assert cond.name == "PP+Perm"
    assert cond.limit_state == LimitState.SLU
    assert cond.N == 50.0


def test_load_condition_manager():
    """Test: LoadConditionManager."""
    from shared.loads.engine.models import LimitState, LoadCondition, LoadConditionManager

    manager = LoadConditionManager()

    cond1 = LoadCondition(name="PP", limit_state=LimitState.SLU, N=50.0)
    cond2 = LoadCondition(name="Acc", limit_state=LimitState.SLE_rara, N=80.0)

    manager.add_condition(cond1)
    manager.add_condition(cond2)

    assert len(manager.conditions) == 2
    assert manager.get_by_name("PP") == cond1
    assert len(manager.get_by_limit_state(LimitState.SLU)) == 1


def test_knowledge_level_factory():
    """Test: KnowledgeLevelFactory."""
    from shared.materials.engine.knowledge_level import KnowledgeLevelFactory, KnowledgeLevelType

    lc1 = KnowledgeLevelFactory.create_lc1()
    lc2 = KnowledgeLevelFactory.create_lc2()
    lc3 = KnowledgeLevelFactory.create_lc3()

    assert lc1.fc == 1.35
    assert lc2.fc == 1.20
    assert lc3.fc == 1.00

    # Test strength reduction
    strength_lc1 = lc1.apply_to_strength(270.0)  # C25/30
    strength_lc2 = lc2.apply_to_strength(270.0)
    strength_lc3 = lc3.apply_to_strength(270.0)

    assert strength_lc1 < strength_lc2 < strength_lc3


def test_norm_material_map():
    """Test: NormMaterialMap filtering."""
    from shared.norms.engine.norm_material_map import NormMaterialMap

    # Test NTC2018 materials
    ntc2018_mats = NormMaterialMap.get_materials_for_norm("NTC2018")
    assert "C25/30" in ntc2018_mats
    assert "B450C" in ntc2018_mats

    # Test RD2229 materials
    rd2229_mats = NormMaterialMap.get_materials_for_norm("RD2229")
    assert "R200" in rd2229_mats
    assert "AQ42" in rd2229_mats

    # Test compatibility
    assert NormMaterialMap.is_compatible("NTC2018", "C25/30")
    assert not NormMaterialMap.is_compatible("RD2229", "C25/30")

    # Test norms for material
    ntc_norms = NormMaterialMap.list_norms_for_material("C25/30")
    assert "NTC2018" in ntc_norms


def test_module_registry():
    """Test: ModuleRegistry singleton."""
    from pipeline.module_registry import ModuleInfo, ModuleRegistry

    registry1 = ModuleRegistry()
    registry2 = ModuleRegistry()

    # Singleton pattern
    assert registry1 is registry2

    # Test registration
    info = ModuleInfo(
        id="test_module",
        name="Test Module",
        version="1.0.0",
        category="testing",
        icon="🧪",
        description="Test module",
        norms_supported=["NTC2018"],
    )

    # Mock engine factory
    def mock_engine_factory():
        pass

    registry1.register(info, mock_engine_factory)

    retrieved = registry1.get("test_module")
    assert retrieved is not None
    assert retrieved[0].id == "test_module"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
