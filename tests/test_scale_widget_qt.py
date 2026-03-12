from __future__ import annotations

import pytest

try:
    import pytestqt  # noqa: F401
except ImportError:
    pytest.skip("pytest-qt non disponibile", allow_module_level=True)

try:
    import PyQt6  # noqa: F401
except ImportError:
    try:
        import PySide6  # noqa: F401
    except ImportError:
        pytest.skip("Ne' PyQt6 ne' PySide6 disponibili", allow_module_level=True)

from src.ui.qt.scala_widget import ScalaWidget


@pytest.fixture
def widget(qtbot):
    instance = ScalaWidget()
    qtbot.addWidget(instance)
    return instance


def test_widget_creazione(widget) -> None:
    assert widget is not None
    assert hasattr(widget, "combo_tipo")
    assert hasattr(widget, "btn_calcola")


def test_widget_calcolo_ca(widget) -> None:
    widget.combo_tipo.setCurrentText("CA")
    risultato = widget._calcola_corrente()
    assert risultato.tipo == "ca"
    assert "Scala in c.a." in widget._calcola_corrente().tabulato_ascii


def test_widget_calcolo_acciaio(widget) -> None:
    widget.combo_tipo.setCurrentText("Acciaio")
    risultato = widget._calcola_corrente()
    assert risultato.tipo == "acciaio"
    assert "Scala metallica" in risultato.tabulato_ascii
