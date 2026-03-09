"""Test GUI Qt — CordoliWidget.

Richiede PyQt6 o PySide6 installato e pytest-qt.
Se Qt non e' disponibile i test vengono saltati automaticamente.
"""

import pytest

# Skip dell'intero modulo se ne' PyQt6 ne' PySide6 sono disponibili
try:
    import PyQt6  # noqa: F401
except ImportError:
    try:
        import PySide6  # noqa: F401
    except ImportError:
        pytest.skip("Ne' PyQt6 ne' PySide6 disponibili", allow_module_level=True)

try:
    from PyQt6.QtWidgets import QApplication  # noqa: F401
except ImportError:
    pass  # type: ignore[no-redef]

from src.ui.qt.cordoli_widget import CordoliWidget

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def widget(qtbot):
    """CordoliWidget istanziato e registrato con qtbot."""
    w = CordoliWidget()
    qtbot.addWidget(w)
    return w


# ── Test ──────────────────────────────────────────────────────────────────────

class TestCordoliWidgetQt:
    def test_crea_senza_errori(self, widget):
        """Il widget deve crearsi senza eccezioni."""
        assert widget is not None
        assert hasattr(widget, "combo_tipo")
        assert hasattr(widget, "tabella_profili")
        assert hasattr(widget, "btn_calcola")

    def test_tipo_iniziale_metallico(self, widget):
        """Il tipo iniziale deve essere Metallico."""
        assert widget.combo_tipo.currentText() == "Metallico"
        assert not widget.combo_famiglia.isHidden()

    def test_cambio_tipo_ca_nasconde_combo_famiglia(self, widget, qtbot):
        """Passando a CA, combo_famiglia deve sparire."""
        widget.combo_tipo.setCurrentText("CA")
        qtbot.waitSignal(widget.combo_tipo.currentTextChanged, timeout=500)
        assert widget.combo_famiglia.isHidden()

    def test_cambio_tipo_reticolare_nasconde_combo_famiglia(self, widget, qtbot):
        """Passando a Reticolare, combo_famiglia deve sparire."""
        widget.combo_tipo.setCurrentText("Reticolare")
        qtbot.waitSignal(widget.combo_tipo.currentTextChanged, timeout=500)
        assert widget.combo_famiglia.isHidden()

    def test_tabella_profili_popolata(self, widget):
        """La tabella deve avere profili dopo l'inizializzazione."""
        assert widget.tabella_profili.rowCount() > 0

    def test_calcola_metallico_senza_selezione_mostra_errore(self, widget, qtbot):
        """Calcolare senza selezionare un profilo deve mostrare un messaggio di errore."""
        # Nessuna riga selezionata esplicitamente
        widget._profilo_corrente = None
        # Il bottone calcola deve gestire l'errore senza crash
        # (mostra QMessageBox.critical — non testabile headless, verifichiamo no crash)
        try:
            widget._calcola_metallico()
            assert False, "Atteso ValueError"
        except ValueError as exc:
            assert "profilo" in str(exc).lower()

    def test_calcola_metallico_con_profilo_produce_tabulato(self, widget, qtbot):
        """Con un profilo selezionato, il calcolo deve produrre un tabulato."""
        # Seleziona prima riga
        if widget.tabella_profili.rowCount() > 0:
            widget.tabella_profili.selectRow(0)
            widget._on_profilo_selezionato(0)
        assert widget._profilo_corrente is not None

        tab, verificato = widget._calcola_metallico()
        ascii_out = tab.come_ascii()
        assert ascii_out
        assert isinstance(verificato, bool)
