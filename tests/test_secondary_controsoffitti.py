from __future__ import annotations

import pytest

from src.codes.ntc2018.secondary_elements.controsoffitti import (
    ControsoffittoSpec,
    TipoControsoffitto,
    check_sle,
    check_slu,
    verifica_controsoffitto_completa,
)
from src.codes.ntc2018.secondary_elements.controsoffitti.models import (
    RisultatoControsoffitto,
    StatoDannoSLE,
)


class TestControsoffittoModels:
    def test_spec_massa_totale(self):
        spec = ControsoffittoSpec(
            tipo=TipoControsoffitto.MODULARE_GESSO,
            area_m2=50.0,
            massa_superficiale_kg_m2=15.0,
            passo_pendini_cm=100.0,
            presenza_controventi=True,
            gioco_perimetrale_mm=30.0,
        )
        massa = spec.massa_totale_kg()
        assert massa == pytest.approx(750.0, rel=1e-3)


class TestControsoffittoSLU:
    def test_check_slu_contract(self):
        inputs = {
            "tipo": "modulare_gesso",
            "area_m2": 50.0,
            "massa_superficiale_kg_m2": 15.0,
            "passo_pendini_cm": 100.0,
            "presenza_controventi": True,
            "gioco_perimetrale_mm": 30.0,
        }
        result = check_slu(inputs)
        assert result["element_type"] == "controsoffitti"
        assert "decision_log" in result
        assert "utilisation" in result


class TestControsoffittoSLE:
    def test_check_sle_damage_states(self):
        inputs = {
            "tipo": "lastra_continua",
            "area_m2": 50.0,
            "massa_superficiale_kg_m2": 15.0,
            "passo_pendini_cm": 100.0,
            "presenza_controventi": True,
            "gioco_perimetrale_mm": 30.0,
            "drift_calcolato_perc": 0.8,
        }
        result = check_sle(inputs)
        assert "stato_danno" in result
        assert result["stato_danno"] in [
            StatoDannoSLE.ASSENTE.value,
            StatoDannoSLE.LOCALE.value,
            StatoDannoSLE.DIFFUSO.value,
            StatoDannoSLE.INSICUREZZA.value,
        ]


class TestControsoffittoPipeline:
    def test_pipeline_completa(self):
        inputs = {
            "tipo": "tecnico_aperto",
            "area_m2": 60.0,
            "massa_superficiale_kg_m2": 18.0,
            "passo_pendini_cm": 80.0,
            "presenza_controventi": True,
            "gioco_perimetrale_mm": 40.0,
            "S_a": 1.5,
            "drift_calcolato_perc": 0.9,
        }
        risultato = verifica_controsoffitto_completa(inputs)
        assert isinstance(risultato, RisultatoControsoffitto)
        assert len(risultato.passaggi_calcolo) > 0
