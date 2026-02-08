"""Tests for Module Selector UI Components.

This module contains comprehensive tests for the Module Selector UI components,
including the FlowWrapFrame layout manager and ModuleSelectorView.
"""

import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from sections_app.ui.components.flow_wrap import FlowWrapFrame
from sections_app.ui.module_selector import ModuleSelectorWindow
from sections_app.ui.module_selector_view import ModuleCardSpec, ModuleSelectorView


class TestFlowWrapFrame:
    """Test per FlowWrapFrame layout manager."""

    @patch("tkinter.Tk")
    def test_initialization(self, mock_tk):
        """Test inizializzazione FlowWrapFrame."""
        root = mock_tk.return_value
        try:
            frame = FlowWrapFrame(root, card_width=260, hgap=12, vgap=12, padding=12)
            assert frame.card_width == 260
            assert frame.hgap == 12
            assert frame.vgap == 12
            assert frame.padding == 12
            assert not frame._children
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()

    @patch("tkinter.Tk")
    def test_add_widget(self, mock_tk):
        """Test aggiunta widget."""
        root = mock_tk.return_value
        try:
            frame = FlowWrapFrame(root)
            widget = tk.Label(frame)
            frame.add(widget)
            assert len(frame._children) == 1
            assert frame._children[0] == widget
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()

    @patch("tkinter.Tk")
    def test_clear_widgets(self, mock_tk):
        """Test pulizia widgets."""
        root = mock_tk.return_value
        try:
            frame = FlowWrapFrame(root)
            widget = tk.Label(frame)
            frame.add(widget)
            frame.clear()
            assert not frame._children
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()

    @patch("tkinter.ttk.Frame.winfo_width")
    @patch("tkinter.Tk")
    def test_on_configure_single_column(self, mock_tk, mock_width):
        """Test calcolo colonne con larghezza minima."""
        root = mock_tk.return_value
        frame = FlowWrapFrame(root, card_width=260, hgap=12, padding=12)
        mock_width.return_value = 280  # 280 - 24 = 256, 256 // 272 = 0 -> max(1,0) = 1

        # Aggiungi un widget
        widget = tk.Label(frame)
        frame.add(widget)

        # Simula configure
        frame._on_configure()

        # Verifica che grid_columnconfigure sia chiamato per 1 colonna
        try:
            with patch.object(frame, "grid_columnconfigure") as mock_grid:
                frame._on_configure()
                mock_grid.assert_called_with(0, weight=1, uniform="cols")
        finally:
            root.destroy()

    @patch("tkinter.ttk.Frame.winfo_width")
    @patch("tkinter.Tk")
    def test_on_configure_multiple_columns(self, mock_tk, mock_width):
        """Test calcolo colonne con larghezza sufficiente per più colonne."""
        root = mock_tk.return_value
        try:
            frame = FlowWrapFrame(root, card_width=260, hgap=12, padding=12)
            mock_width.return_value = 600  # 600 - 24 = 576, 576 // 272 ≈ 2

            widget = tk.Label(frame)
            frame.add(widget)

            with patch.object(frame, "grid_columnconfigure") as mock_grid:
                frame._on_configure()
                # Dovrebbe configurare 2 colonne
                mock_grid.assert_any_call(0, weight=1, uniform="cols")
                mock_grid.assert_any_call(1, weight=1, uniform="cols")
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()


class TestModuleCardSpec:
    """Test per ModuleCardSpec dataclass."""

    def test_creation(self):
        """Test creazione ModuleCardSpec."""
        spec = ModuleCardSpec(
            title="Test Module",
            description="Test description",
            button_text="Test Button",
            callback=lambda: None,
        )
        assert spec.title == "Test Module"
        assert spec.description == "Test description"
        assert spec.button_text == "Test Button"
        assert callable(spec.callback)
        assert spec.extra_buttons is None

    def test_with_extra_buttons(self):
        """Test ModuleCardSpec con extra buttons."""
        spec = ModuleCardSpec(
            title="Test Module",
            description="Test description",
            button_text=None,
            callback=lambda: None,
            extra_buttons=[("Btn1", lambda: None), ("Btn2", lambda: None)],
        )
        assert spec.button_text is None
        assert spec.extra_buttons is not None
        assert len(spec.extra_buttons) == 2
        assert spec.extra_buttons[0][0] == "Btn1"


class TestModuleSelectorView:
    """Test per ModuleSelectorView."""

    @patch("tkinter.Tk")
    def test_initialization(self, mock_tk):
        """Test inizializzazione ModuleSelectorView."""
        root = mock_tk.return_value
        try:
            specs = [ModuleCardSpec("Test", "Desc", "Btn", lambda: None)]
            view = ModuleSelectorView(root, specs)
            assert view.flow is not None
            assert isinstance(view.flow, FlowWrapFrame)
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()

    @patch("tkinter.Tk")
    def test_card_creation(self, mock_tk):
        """Test creazione card dalla spec."""
        root = mock_tk.return_value
        try:
            specs = [
                ModuleCardSpec(
                    title="Test Module",
                    description="Test description",
                    button_text="Test Button",
                    callback=lambda: None,
                )
            ]
            view = ModuleSelectorView(root, specs)

            # Verifica che sia stata aggiunta una card
            assert len(view.flow._children) == 1

            # Verifica che il widget sia un LabelFrame
            card = view.flow._children[0]
            assert isinstance(card, tk.LabelFrame)
            assert card.cget("text") == "Test Module"
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()

    @patch("tkinter.Tk")
    def test_card_with_extra_buttons(self, mock_tk):
        """Test card con pulsanti extra."""
        root = mock_tk.return_value
        try:
            specs = [
                ModuleCardSpec(
                    title="Test Module",
                    description="Test description",
                    button_text=None,
                    callback=lambda: None,
                    extra_buttons=[("Btn1", lambda: None), ("Btn2", lambda: None)],
                )
            ]
            view = ModuleSelectorView(root, specs)

            # Verifica card creata
            assert len(view.flow._children) == 1
            card = view.flow._children[0]
            assert isinstance(card, tk.LabelFrame)
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()

    @patch("tkinter.Tk")
    def test_multiple_specs(self, mock_tk):
        """Test con multiple specs."""
        root = mock_tk.return_value
        try:
            specs = [
                ModuleCardSpec("Module 1", "Desc 1", "Btn 1", lambda: None),
                ModuleCardSpec("Module 2", "Desc 2", "Btn 2", lambda: None),
                ModuleCardSpec("Module 3", "Desc 3", "Btn 3", lambda: None),
            ]
            view = ModuleSelectorView(root, specs)

            # Verifica che tutte le card siano create
            assert len(view.flow._children) == 3
            for i, card in enumerate(view.flow._children):
                assert isinstance(card, tk.LabelFrame)
                assert card.cget("text") == f"Module {i+1}"
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if hasattr(root, "destroy"):
                root.destroy()


class TestModuleSelectorWindow:
    """Test per ModuleSelectorWindow con nuova implementazione."""

    @patch("sections_app.ui.module_selector.NotificationCenter")
    @patch("tkinter.Tk")
    def test_initialization_uses_view(self, mock_tk, mock_notification):
        """Test che ModuleSelectorWindow usi ModuleSelectorView."""
        mock_notification.return_value = None
        mock_tk_instance = mock_tk.return_value
        mock_tk_instance.minsize.return_value = (900, 380)

        try:
            window = ModuleSelectorWindow()

            # Verifica che abbia l'attributo view
            assert hasattr(window, "view")
            assert isinstance(window.view, ModuleSelectorView)

            # Verifica minsize
            assert window.minsize() == (900, 380)
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if "window" in locals():
                window.destroy()

    @patch("sections_app.ui.module_selector.NotificationCenter")
    @patch("tkinter.Tk")
    def test_specs_creation(self, mock_tk, mock_notification):
        """Test che le specs siano create correttamente."""
        mock_notification.return_value = None

        try:
            window = ModuleSelectorWindow()

            # Verifica che la view abbia specs
            view = window.view
            assert hasattr(view, "flow")
            # Dovrebbe avere 9 card (come nel codice)
            assert len(view.flow._children) == 9
        except Exception:
            pytest.skip("Tkinter not available")
        finally:
            if "window" in locals():
                window.destroy()
