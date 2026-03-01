"""pytest configuration for the tests/ directory.

The standard (CI) test suite excludes any legacy GUI tests under
``tests/legacy_tkinter`` and ``tests/legacy_qt``.  These directories contain
deprecated Tkinter- or Qt-based tests that are no longer run by default.
"""

from __future__ import annotations

# Directories to ignore during normal collection.  Placing legacy UI tests
# here keeps them available for manual execution while preventing failures
# in headless CI environments.

try:
    import tkinter  # noqa: F401

    _TKINTER_AVAILABLE = True
except ImportError:
    _TKINTER_AVAILABLE = False

try:
    import pytest_qt  # noqa: F401

    _PYTEST_QT_AVAILABLE = True
except ImportError:
    _PYTEST_QT_AVAILABLE = False

# Files that import tkinter (directly or transitively) at module level.
# When tkinter is absent these files fail during *collection*, not just
# during test execution, so they must be excluded before collection starts.
#
# How to maintain this list: if you add a new test file that imports tkinter
# (or any module that transitively imports tkinter) at the top level, add its
# filename here so it is skipped gracefully in headless/CI environments.
_TKINTER_DEPENDENT: list[str] = [
    "test_core_and_graphics.py",
    "test_csv_io.py",
    "test_domain_materials.py",
    "test_domain_sections.py",
    "test_fire_selection_eligibility.py",
    "test_graphics_flags.py",
    "test_main_window_gui.py",
    "test_material_suggestions_focus.py",
    "test_module_registry_refresh.py",
    "test_module_selector_controller.py",
    "test_module_selector_integration.py",
    "test_module_selector_ui.py",
    "test_persistence_edit_cycle.py",
    "test_plot_section.py",
    "test_rebar_calculator.py",
    "test_section_manager_selection.py",
    "test_shim_import.py",
    "test_step5_merge.py",
    "test_suggestion_click_realistic.py",
    "test_suggestion_persistence.py",
    "test_suggestion_positioning.py",
    "test_table_navigation.py",
    "test_ui_background_compute.py",
    "test_verification_dispatcher.py",
    "test_verification_table_click_sequence.py",
    "test_verification_table_click_suggestions.py",
    # These tests require the rd2229 package installed with src/ as root package dir
    "test_ui_qt_settings_service.py",
    "test_ui_qt_verification_service.py",
    # PyQt6/PySide6 not available – collection would abort
    "test_ui_qt_registry.py",
]

# Tests requiring pytest-qt (qtbot fixture) which may not be installed.
_PYTEST_QT_DEPENDENT: list[str] = [
    "test_regression_gui_cli.py",
]

# the base list always ignores the legacy directories
collect_ignore: list[str] = ["legacy_tkinter", "legacy_qt"]
if not _TKINTER_AVAILABLE:
    collect_ignore.extend(_TKINTER_DEPENDENT)
if not _PYTEST_QT_AVAILABLE:
    collect_ignore.extend(_PYTEST_QT_DEPENDENT)
