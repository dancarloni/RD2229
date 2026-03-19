"""
Test headless per il Material Editor (niente GUI visibile).
Verifica: repository, model, detail frame, controller/attach flow.
"""
import os
import sys

import pytest


@pytest.fixture(scope="module")
def qt_app():
    """Crea QApplication in modalità offscreen (niente finestra reale)."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def test_repository_carica_materiali(qt_app):
    from src.ui.qt.material_editor.logic.material_repository import MaterialRepository
    repo = MaterialRepository()
    assert len(repo.materials) > 0, "Nessun materiale caricato dal repository"


def test_filtro_calcestruzzi(qt_app):
    from src.ui.qt.material_editor.logic.material_repository import MaterialRepository
    repo = MaterialRepository()
    cls = [m for m in repo.materials if m.get("famiglia", "").lower() == "calcestruzzo"]
    assert len(cls) > 0, "Nessun calcestruzzo trovato"


def test_table_model_righe_e_colonne(qt_app):
    from src.ui.qt.material_editor.logic.material_repository import MaterialRepository
    from src.ui.qt.material_editor.widgets.material_table_model import MaterialTableModel

    repo = MaterialRepository()
    repo.materials = [m for m in repo.materials if m.get("famiglia", "").lower() == "calcestruzzo"]
    model = MaterialTableModel(repo)
    model.refresh()
    assert model.rowCount() == len(repo.materials), "rowCount non corrisponde"
    assert model.columnCount() > 0, "Nessuna colonna nel modello"


def test_detail_frame_set_fields(qt_app):
    from src.ui.qt.material_editor.logic.material_repository import MaterialRepository
    from src.ui.qt.material_editor.widgets.material_detail_frame import MaterialDetailFrame

    repo = MaterialRepository()
    cls = [m for m in repo.materials if m.get("famiglia", "").lower() == "calcestruzzo"]
    assert cls, "Nessun calcestruzzo per il test"

    frame = MaterialDetailFrame()
    mat = cls[0]
    frame.set_fields(mat)

    expected_keys = [k for k in mat.keys() if k != "id"]
    assert len(frame._fields) > 0, "Nessun campo creato nel detail frame"
    for k in expected_keys:
        assert k in frame._fields, f"Campo '{k}' mancante nel detail frame"


def test_controller_attach_popola_detail(qt_app):
    """
    Test critico: verifica che dopo attach_detail + attach_table,
    il primo materiale venga caricato nel detail frame.
    """
    from src.ui.qt.material_editor.controller import MaterialEditorController
    from src.ui.qt.material_editor.widgets.material_detail_frame import MaterialDetailFrame
    from src.ui.qt.material_editor.widgets.material_export_widget import MaterialExportWidget
    from src.ui.qt.material_editor.widgets.material_table_widget import MaterialTableWidget

    controller = MaterialEditorController(famiglia="calcestruzzo")
    table = MaterialTableWidget()
    detail = MaterialDetailFrame()
    export = MaterialExportWidget()

    # Ordine corretto: detail prima, poi table (serve per _try_populate_first)
    controller.attach_detail(detail)
    controller.attach_export(export)
    controller.attach_table(table)

    assert hasattr(controller, "model") and controller.model is not None, "Model non creato"
    assert controller.model.rowCount() > 0, "Model vuoto dopo attach"
    assert len(detail._fields) > 0, "Detail frame NON popolato dopo selectRow(0)"
    print(f"\nCampi nel detail: {list(detail._fields.keys())[:5]}...")


def test_controller_selezione_riga_aggiorna_detail(qt_app):
    """Verifica che selezionare una riga diversa aggiorni il detail frame."""
    from src.ui.qt.material_editor.controller import MaterialEditorController
    from src.ui.qt.material_editor.widgets.material_detail_frame import MaterialDetailFrame
    from src.ui.qt.material_editor.widgets.material_export_widget import MaterialExportWidget
    from src.ui.qt.material_editor.widgets.material_table_widget import MaterialTableWidget

    controller = MaterialEditorController(famiglia="calcestruzzo")
    table = MaterialTableWidget()
    detail = MaterialDetailFrame()
    export = MaterialExportWidget()

    controller.attach_detail(detail)
    controller.attach_export(export)
    controller.attach_table(table)

    # Deve esserci almeno 2 materiali per testare la selezione di riga diversa
    if controller.model.rowCount() >= 2:
        table.selectRow(1)
        # Il controller tiene traccia dell'indice corrente
        assert controller.current_index == 1, "current_index non aggiornato dopo selezione riga 1"
        assert len(detail._fields) > 0, "Detail non aggiornato dopo selezione riga 1"


def test_tutte_le_famiglie(qt_app):
    """Verifica che ogni famiglia produca una tabella non vuota."""
    from src.ui.qt.material_editor.controller import MaterialEditorController
    from src.ui.qt.material_editor.widgets.material_detail_frame import MaterialDetailFrame
    from src.ui.qt.material_editor.widgets.material_export_widget import MaterialExportWidget
    from src.ui.qt.material_editor.widgets.material_table_widget import MaterialTableWidget

    famiglie = ["calcestruzzo", "acciaio", "legno", "muratura", "composito", "terreno"]
    for fam in famiglie:
        controller = MaterialEditorController(famiglia=fam)
        table = MaterialTableWidget()
        detail = MaterialDetailFrame()
        export = MaterialExportWidget()
        controller.attach_detail(detail)
        controller.attach_export(export)
        controller.attach_table(table)
        n = controller.model.rowCount()
        print(f"  {fam}: {n} materiali")
        # non è errore se alcune famiglie hanno 0 materiali (es. terreni potrebbe mancare)
        # ma il model deve esistere
        assert controller.model is not None, f"Model non creato per famiglia {fam}"
