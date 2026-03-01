"""
RD2229 UI Logic - Registry and Service Validation (PySide6)
Ensures all Qt modules are correctly discovered and accessible.
"""
import pytest

from modules.registry import ModuleRegistry
from src.project.schema import ProjectModel
from src.ui.qt.services import get_services


@pytest.fixture
def registry():
    return ModuleRegistry(package="src.ui.qt")

@pytest.fixture
def services():
    from PySide6.QtWidgets import QApplication
    _app = QApplication.instance() or QApplication([])
    return get_services()

def test_registry_discovery(registry):
    """Checks for core modules in the registry."""
    specs = registry.get_specs()
    keys = [s.key for s in specs]

    # Fundamental modules that must be present
    assert "project_editor" in keys
    assert "pipeline_runner" in keys
    assert "report_viewer" in keys
    assert "material_editor" in keys

def test_registry_factories(registry, services):
    """Ensures each module has a factory that doesn't crash on standard context."""
    for spec in registry.get_specs():
        factory = registry.get_factory(spec.key)
        assert factory is not None, f"Module {spec.key} missing factory"

        try:
            # We don't actually .show() or exec_(), just check instantiation
            window = factory(
                master=None,
                project_service=services.project_service,
                registry=registry
            )
            assert window is not None
        except Exception as e:
            pytest.fail(f"Factory for module '{spec.key}' failed to initialize: {e}")

def test_project_service_singleton():
    """Validates the GUIServiceProvider singleton behavior."""
    s1 = get_services()
    s2 = get_services()
    assert s1 is s2
    assert s1.project_service is s2.project_service

def test_project_model_propagation():
    """Mocks a project load and checks signal emission."""
    services = get_services()
    # Use real ProjectModel or a robust mock
    mock_p = ProjectModel()
    if mock_p.project_info:
        mock_p.project_info.name = "Test Project"

    received = []
    services.project_service.project_changed.connect(lambda p: received.append(p))

    services.project_service.set_project(mock_p)

    # We use >= because it's a singleton and other tests might have fired it
    assert len(received) >= 1
    assert received[-1] is mock_p
