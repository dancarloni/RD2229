from __future__ import annotations

import pytest

from src.codes.ntc2018.secondary_elements.parapetti import (
    ParapettoSpec,
    TipoAncoraggio,
    TipoParapetto,
    check_sle,
    check_slu,
    spec_from_dict,
    verifica_parapetto_completa,
)
from src.codes.ntc2018.secondary_elements.parapetti.models import RisultatoParapetto, StatoDannoSLE


class TestParapettoModels:
    def test_spec_massa_totale(self):
        spec = ParapettoSpec(
            tipo=TipoParapetto.CONTINUO_MURATURA,
            altezza_cm=120.0,
            lunghezza_cm=500.0,
            massa_lineare_kg_m=200.0,
            tipo_ancoraggio=TipoAncoraggio.BASE_CONTINUA,
        )
        massa = spec.massa_totale_kg()
        assert massa == pytest.approx(1000.0, rel=1e-3)


class TestParapettoSLU:
    def test_check_slu_partition_dispatch_contract(self):
        inputs = {
            "tipo": "continuo_muratura",
            "altezza_cm": 120.0,
            "lunghezza_cm": 500.0,
            "massa_lineare_kg_m": 200.0,
            "tipo_ancoraggio": "base_continua",
            "S_a": 1.5,
            "P_servizio": 100.0,
            "gamma_i": 1.0,
        }
        result = check_slu(inputs)
        assert "element_type" in result
        assert result["element_type"] == "parapetti"
        assert "decision_log" in result
        assert isinstance(result["decision_log"], list)
        assert "utilisation" in result
        assert result["ok"] in [True, False]


class TestParapettoSLE:
    def test_check_sle_damage_classification(self):
        inputs = {
            "tipo": "continuo_muratura",
            "altezza_cm": 120.0,
            "lunghezza_cm": 500.0,
            "massa_lineare_kg_m": 200.0,
            "tipo_ancoraggio": "base_continua",
            "spostamento_bordo_cm": 0.5,
        }
        result = check_sle(inputs)
        assert "stato_danno" in result
        assert result["stato_danno"] in [
            StatoDannoSLE.ASSENTE.value,
            StatoDannoSLE.LOCALE.value,
            StatoDannoSLE.DIFFUSO.value,
            StatoDannoSLE.INSICUREZZA.value,
        ]
        assert "confidence" in result


class TestParapettoPipeline:
    def test_pipeline_completa(self):
        inputs = {
            "tipo": "continuo_muratura",
            "altezza_cm": 120.0,
            "lunghezza_cm": 500.0,
            "massa_lineare_kg_m": 200.0,
            "tipo_ancoraggio": "base_continua",
            "S_a": 1.5,
            "P_servizio": 100.0,
            "gamma_i": 1.0,
            "spostamento_bordo_cm": 0.5,
        }
        risultato = verifica_parapetto_completa(inputs)
        assert isinstance(risultato, RisultatoParapetto)
        assert risultato.spec.tipo == TipoParapetto.CONTINUO_MURATURA
        assert len(risultato.passaggi_calcolo) > 0
        assert "SLU" in "\n".join(risultato.passaggi_calcolo)
        assert "SLE" in "\n".join(risultato.passaggi_calcolo)


class TestParapettoStorage:
    def test_storage_records_include_element_type(self):
        inputs = {
            "tipo": "continuo_acciaio",
            "altezza_cm": 150.0,
            "lunghezza_cm": 600.0,
            "massa_lineare_kg_m": 250.0,
            "tipo_ancoraggio": "tasselli_puntuali",
        }
        result = check_slu(inputs)
        assert result["element_type"] == "parapetti"
        assert "norm_references" in result
        assert "Fase S3" in result["norm_references"]
