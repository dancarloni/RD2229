from __future__ import annotations

from src.codes.ntc2018.secondary_elements.storage_adapter import (
    clear_storage,
    list_secondary_element_records,
    save_secondary_element,
)
from src.codes.ntc2018.secondary_elements.tramezzi import (
    ContestoSLETramezzo,
    ContestoSLUTramezzo,
    SistemaTramezzo,
    StatoDannoSLE,
    TramezzoSpec,
    VincoloSuperiore,
    check_sle,
    check_slu,
    get_preset,
    lista_preset_disponibili,
    verifica_tramezzo_completa,
)
from verifications.secondary_elements import dispatcher


class DummyProjectModel:
    def __init__(self, norma: str = "NTC2018") -> None:
        self.norma_attiva = norma


def build_spec() -> TramezzoSpec:
    return TramezzoSpec(
        sistema=SistemaTramezzo.CARTONGESSO_STANDARD,
        altezza_cm=300.0,
        lunghezza_cm=400.0,
        spessore_cm=10.0,
        peso_lineare_kg_m=50.0,
        vincolo_superiore=VincoloSuperiore.SCORREVOLE,
        guida_superiore_scorrimento=True,
        ancorato_lateralmente=True,
        drift_capacita_perc=1.2,
        impianti_integrati=False,
    )


def test_spec_massa_totale():
    spec = build_spec()
    assert spec.massa_totale_kg() == 200.0


def test_check_slu_partition_dispatch_contract():
    result = check_slu(
        {
            "element_type": "partition",
            "sistema": "cartongesso_standard",
            "altezza_cm": 300.0,
            "lunghezza_cm": 400.0,
            "spessore_cm": 10.0,
            "peso_lineare_kg_m": 50.0,
            "S_a": 1.6,
        }
    )
    assert result["element_type"] == "tramezzi"
    assert "decision_log" in result and result["decision_log"]
    assert result["utilisation"] > 0


def test_check_sle_four_damage_levels():
    base = {
        "element_type": "partition",
        "sistema": "laterizio_forato",
        "drift": {"source": "GLOBAL", "value": 0.30},
    }
    assert check_sle(base)["stato_danno"] == StatoDannoSLE.ASSENTE.value
    base["drift"]["value"] = 0.45
    assert check_sle(base)["stato_danno"] in {
        StatoDannoSLE.LOCALE.value,
        StatoDannoSLE.DIFFUSO.value,
    }


def test_pipeline_completa_tramezzo():
    spec = build_spec()
    result = verifica_tramezzo_completa(
        spec,
        ContestoSLUTramezzo(accelerazione_spettrale_g=1.4),
        ContestoSLETramezzo(drift_calcolato_perc=0.7),
    )
    assert result.passaggi_calcolo
    assert result.risultato_slu.domanda_fuori_piano_kg > 0
    assert result.risultato_sle.stato_danno in set(StatoDannoSLE)


def test_presets_disponibili():
    assert "cartongesso_standard" in lista_preset_disponibili()
    assert get_preset("laterizio_forato") is not None


def test_storage_records_include_element_type():
    clear_storage()
    save_secondary_element({"element_type": "tramezzi", "norm_code": "NTC2018", "phase_id": "S2"})
    records = list_secondary_element_records("tramezzi")
    assert len(records) == 1
    assert records[0]["element_type"] == "tramezzi"


def test_dispatcher_routes_partition_to_tramezzi():
    proj = DummyProjectModel()
    res = dispatcher.run(
        {
            "element_type": "partition",
            "sistema": "cartongesso_doppia_lastra",
            "peso_lineare_kg_m": 60.0,
            "altezza_cm": 300.0,
            "lunghezza_cm": 350.0,
            "drift": {"source": "ESTIMATED", "value": 0.8, "method": "B"},
            "ta_model": "MANUAL",
            "influence_on_global_model": False,
        },
        proj,
        "SLE",
    )
    assert res["element_type"] == "tramezzi"
    assert res["confidence"] == "LOW"
    assert any("dispatcher.element_type=partition" in item for item in res["decision_log"])
