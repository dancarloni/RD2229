from __future__ import annotations

from src.codes.ntc2018.secondary_elements.camini import (
    TipoCamino,
    check_sle,
    check_slu,
    verifica_camino_completa,
)
from src.codes.ntc2018.secondary_elements.camini.models import RisultatoCamino


class TestCaminoModels:
    def test_periodo_proprio(self):
        from src.codes.ntc2018.secondary_elements.camini import CaminoSpec

        spec = CaminoSpec(
            tipo=TipoCamino.MURATURA,
            altezza_cm=400.0,
            massa_totale_kg=800.0,
            vincolo_base="fisso",
            controventato=False,
        )
        Ta = spec.periodo_proprio_s()
        assert Ta > 0


class TestCaminoSLU:
    def test_check_slu_contract(self):
        inputs = {
            "tipo": "muratura",
            "altezza_cm": 400.0,
            "massa_totale_kg": 800.0,
            "S_a": 1.5,
        }
        result = check_slu(inputs)
        assert result["element_type"] == "camini"
        assert "decision_log" in result


class TestCaminoSLE:
    def test_check_sle_damage(self):
        inputs = {
            "tipo": "acciaio",
            "altezza_cm": 500.0,
            "massa_totale_kg": 600.0,
            "spostamento_sommitale_cm": 0.8,
        }
        result = check_sle(inputs)
        assert "stato_danno" in result


class TestCaminoPipeline:
    def test_pipeline_completa(self):
        inputs = {
            "tipo": "prefabbricato",
            "altezza_cm": 350.0,
            "massa_totale_kg": 700.0,
            "controventato": True,
        }
        risultato = verifica_camino_completa(inputs)
        assert isinstance(risultato, RisultatoCamino)
