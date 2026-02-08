"""Test per il sistema di auto-refresh del Section Manager tramite EventBus."""

import tkinter as tk
import unittest
from unittest.mock import MagicMock, patch

from sections_app.services.event_bus import (
    SECTIONS_ADDED,
    SECTIONS_CLEARED,
    SECTIONS_DELETED,
    SECTIONS_UPDATED,
    EventBus,
)
from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.section_manager import SectionManager


class TestSectionManagerAutoRefresh(unittest.TestCase):
    """Test per auto-refresh e gestione eventi nel Section Manager."""

    def setUp(self):
        """Setup per ogni test."""
        # Crea finestra root Tk
        self.root = tk.Tk()
        self.root.withdraw()  # Nascondi finestra durante test

        # Mock repository e serializer
        self.repository = MagicMock(spec=SectionRepository)
        self.repository.get_all_sections.return_value = []

        self.serializer = MagicMock(spec=CsvSectionSerializer)

        # Mock callback on_edit
        self.on_edit = MagicMock()

        # Reset EventBus singleton
        EventBus._instance = None
        EventBus()._listeners = {}

    def tearDown(self):
        """Cleanup dopo ogni test."""
        try:
            if hasattr(self, "manager") and self.manager.winfo_exists():
                self.manager.destroy()
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

        # Reset EventBus
        EventBus._instance = None

    def test_sottoscrizione_eventi_all_init(self):
        """Verifica che __init__ sottoscriva tutti gli eventi necessari."""
        # Crea manager
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Verifica che EventBus abbia listener per tutti gli eventi
        event_bus = EventBus()

        self.assertIn(SECTIONS_ADDED, event_bus._listeners)
        self.assertIn(SECTIONS_UPDATED, event_bus._listeners)
        self.assertIn(SECTIONS_DELETED, event_bus._listeners)
        self.assertIn(SECTIONS_CLEARED, event_bus._listeners)

        # Verifica che _on_sections_changed sia registrato per ogni evento
        self.assertIn(manager._on_sections_changed, event_bus._listeners[SECTIONS_ADDED])
        self.assertIn(manager._on_sections_changed, event_bus._listeners[SECTIONS_UPDATED])
        self.assertIn(manager._on_sections_changed, event_bus._listeners[SECTIONS_DELETED])
        self.assertIn(manager._on_sections_changed, event_bus._listeners[SECTIONS_CLEARED])

    def test_callback_on_sections_changed_chiama_refresh(self):
        """Verifica che _on_sections_changed chiami refresh_sections."""
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Mock refresh_sections
        with patch.object(manager, "refresh_sections") as mock_refresh:
            # Chiama callback
            manager._on_sections_changed()

            # Verifica che refresh_sections sia stato chiamato
            mock_refresh.assert_called_once()

    def test_cleanup_eventi_su_destroy(self):
        """Verifica che il cleanup rimuova tutte le sottoscrizioni."""
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        event_bus = EventBus()

        # Verifica che ci siano listener registrati
        self.assertTrue(len(event_bus._listeners[SECTIONS_ADDED]) > 0)

        # Chiama cleanup
        manager._cleanup_event_subscriptions()

        # Verifica che _on_sections_changed sia stato rimosso
        self.assertNotIn(manager._on_sections_changed, event_bus._listeners.get(SECTIONS_ADDED, []))
        self.assertNotIn(
            manager._on_sections_changed, event_bus._listeners.get(SECTIONS_UPDATED, [])
        )
        self.assertNotIn(
            manager._on_sections_changed, event_bus._listeners.get(SECTIONS_DELETED, [])
        )
        self.assertNotIn(
            manager._on_sections_changed, event_bus._listeners.get(SECTIONS_CLEARED, [])
        )

    def test_autorefresh_quando_repository_emette_sections_added(self):
        """Verifica che il manager si aggiorni automaticamente quando si aggiungono sezioni."""
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Mock refresh_sections per verificare la chiamata
        with patch.object(manager, "refresh_sections") as mock_refresh:
            # Emetti evento SECTIONS_ADDED
            event_bus = EventBus()
            event_bus.emit(SECTIONS_ADDED, section_id="test_id", section_name="Test")

            # Verifica che refresh_sections sia stato chiamato
            mock_refresh.assert_called_once()

    def test_protocol_wm_delete_window_chiama_cleanup(self):
        """Verifica che la chiusura via WM_DELETE_WINDOW esegua cleanup."""
        manager = SectionManager(self.root, self.repository, self.serializer, self.on_edit)
        self.manager = manager

        # Mock cleanup
        with patch.object(manager, "_cleanup_event_subscriptions") as mock_cleanup:
            # Simula chiusura finestra
            manager._on_close()

            # Verifica che cleanup sia stato chiamato (potrebbe essere chiamato più volte per <Destroy>)
            self.assertTrue(mock_cleanup.called)
            self.assertGreaterEqual(mock_cleanup.call_count, 1)


if __name__ == "__main__":
    unittest.main()
