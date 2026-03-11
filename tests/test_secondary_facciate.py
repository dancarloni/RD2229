from __future__ import annotations

import pytest

from src.codes.ntc2018.secondary_elements.facciate import (
    SistemaFacciata,
    check_sle,
    check_slu,
    verifica_facciata_completa,
)
from src.codes.ntc2018.secondary_elements.facciate.models import RisultatoFacciata, StatoDannoSLE


class TestFacciataModels:
    def test_spec_massa_totale(self):
        from src.codes.ntc2018.secondary_elements.facciate import FacciataSpec

        spec = FacciataSpec(
            sistema=SistemaFacciata.CURTAIN_WALL,
            modulo_luce_cm=120.0,
            massa_superficiale_kg_m2=50.0,
            tipo_sottostruttura="alluminio",
            tipo_ancoraggio="fisso",
            area_m2=60.0,
        )
        assert spec.massa_totale_kg() == pytest.approx(3000.0, rel=1e-3)


class TestFacciataSLU:
    def test_check_slu_contract(self):
        inputs = {
            "sistema": "curtain_wall",
            "area_m2": 50.0,
            "massa_superficiale_kg_m2": 50.0,
            "S_a": 1.5,
        }
        result = check_slu(inputs)
        assert result["element_type"] == "facciate"
        assert "decision_log" in result


class TestFacciataSLE:
    def test_check_sle_damage(self):
        inputs = {
            "sistema": "ventilata",
            "area_m2": 50.0,
            "massa_superficiale_kg_m2": 40.0,
            "drift_capacita_perc": 1.5,
            "drift_calcolato_perc": 0.5,
        }
        result = check_sle(inputs)
        assert result["stato_danno"] in [s.value for s in StatoDannoSLE]


class TestFacciataPipeline:
    def test_pipeline_completa(self):
        inputs = {
            "sistema": "pannello_prefabbricato",
            "area_m2": 80.0,
            "massa_superficiale_kg_m2": 60.0,
            "tipo_sottostruttura": "acciaio",
        }
        risultato = verifica_facciata_completa(inputs)
        assert isinstance(risultato, RisultatoFacciata)
        assert len(risultato.passaggi_calcolo) > 0
