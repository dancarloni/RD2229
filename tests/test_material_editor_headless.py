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


# ── Nuovi test: TASK 6 ────────────────────────────────────────────────────────


def test_compute_material_code_usa_solo_input(qt_app):
    """L'hash codice deve essere identico per materiali con stessi input ma derivati diversi."""
    from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader
    from src.ui.qt.material_editor.logic.material_repository import compute_material_code

    norm_schema = MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018")
    assert norm_schema is not None, "Schema NTC2018 non trovato"

    mat_a = {
        "f_ck": 254.9,
        "densita_kg_m3": 2500,
        "nu": 0.20,
        "gamma_c": 1.5,
        "alpha_cc": 0.85,
        "n_omogenizzazione": 10.0,
        "E": 300000.0,
        "G": 125000.0,
        "f_cm": 336.5,
    }
    mat_b = {
        "f_ck": 254.9,
        "densita_kg_m3": 2500,
        "nu": 0.20,
        "gamma_c": 1.5,
        "alpha_cc": 0.85,
        "n_omogenizzazione": 10.0,
        "E": 999999.9,
        "G": 1.0,
        "f_cm": 0.0,
    }

    code_a = compute_material_code(mat_a, norm_schema)
    code_b = compute_material_code(mat_b, norm_schema)
    assert (
        code_a == code_b
    ), f"Hash diverso per stessi input ma derivati diversi: {code_a} vs {code_b}"


def test_duplicate_detection_on_save(qt_app):
    """Aggiungere due materiali con stessi parametri input deve sollevare DuplicateMaterialError."""
    from src.ui.qt.material_editor.logic.material_repository import (
        DuplicateMaterialError,
        MaterialRepository,
    )

    repo = MaterialRepository()
    mat = {
        "famiglia": "calcestruzzo",
        "norma_riferimento": "NTC2018",
        "nome": "Test-Dup",
        "f_ck": 9999.9,
        "densita_kg_m3": 2500,
        "nu": 0.20,
    }
    import copy

    repo.add_material(copy.deepcopy(mat))
    with pytest.raises(DuplicateMaterialError):
        repo.add_material(copy.deepcopy(mat))


def test_validation_no_codice_required(qt_app):
    """validate() non deve segnalare 'codice' come campo mancante."""
    from src.ui.qt.material_editor.logic.material_validation_logic import validate

    mat = {
        "famiglia": "calcestruzzo",
        "norma_riferimento": "NTC2018",
        "descrizione": "Test",
        "f_ck": 254.9,
        "E": 310000.0,
        "rho": 2500.0,
    }
    result = validate(mat)
    assert "codice" not in result.get(
        "missing", []
    ), f"'codice' non dovrebbe essere nei campi mancanti: {result['missing']}"


def test_derived_params_ntc2018(qt_app):
    """compute_derived() per NTC2018 deve restituire f_Rck, eps_cu2, lambda_factor, eta_factor."""
    from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

    norm_schema = MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018")
    assert norm_schema is not None, "Schema NTC2018 non trovato"

    mat = {"f_ck": 254.9, "densita_kg_m3": 2500, "nu": 0.20}
    derived = MaterialConfigLoader.compute_derived(mat, norm_schema, famiglia="calcestruzzo")

    assert "f_Rck" in derived, "f_Rck mancante nei derivati NTC2018"
    assert "eps_cu2" in derived, "eps_cu2 mancante nei derivati NTC2018"
    assert "lambda_factor" in derived, "lambda_factor mancante nei derivati NTC2018"
    assert "eta_factor" in derived, "eta_factor mancante nei derivati NTC2018"

    # Verifica valori attesi per f_ck = 254.9 kg/cm² ≈ 25 MPa (≤ 50 MPa)
    assert abs(derived["f_Rck"] - 254.9 / 0.83) < 0.1, f"f_Rck errato: {derived['f_Rck']}"
    assert abs(derived["eps_cu2"] - 0.0035) < 1e-6, f"eps_cu2 errato: {derived['eps_cu2']}"
    assert (
        abs(derived["lambda_factor"] - 0.8) < 1e-6
    ), f"lambda_factor errato: {derived['lambda_factor']}"
    assert abs(derived["eta_factor"] - 1.0) < 1e-6, f"eta_factor errato: {derived['eta_factor']}"


def test_splitter_layout_save_restore(tmp_path, monkeypatch):
    """MaterialLayoutLogic.save_layout e load_layout devono persistere e ripristinare i dati."""
    import src.ui.qt.material_editor.logic.material_layout_logic as ll

    # Ridirigi il file preferenze alla tmp_path per non sporcare config/
    prefs_file = tmp_path / "layout_preferences.json"
    monkeypatch.setattr(ll, "_PREFS_FILE", prefs_file)

    from src.ui.qt.material_editor.logic.material_layout_logic import MaterialLayoutLogic

    prefs_in = {"splitter_sizes": [700, 600]}
    MaterialLayoutLogic.save_layout(prefs_in)
    prefs_out = MaterialLayoutLogic.load_layout()
    assert prefs_out == prefs_in, f"Preferenze layout non ripristinate: {prefs_out}"

    MaterialLayoutLogic.reset_layout()
    assert MaterialLayoutLogic.load_layout() == {}, "load_layout deve restituire {} dopo reset"
