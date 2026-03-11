from __future__ import annotations

import pytest

from src.codes.ntc2018.secondary_elements.scaffalature import (
    TipoScaffalatura,
    check_sle,
    check_slu,
    verifica_scaffalatura_completa,
)
from src.codes.ntc2018.secondary_elements.scaffalature.models import (
    RisultatoScaffalatura,
    StatoDannoSLE,
)


class TestScaffalaturaModels:
    def test_massa_totale(self):
        from src.codes.ntc2018.secondary_elements.scaffalature import ScaffalaturaSpec

        spec = ScaffalaturaSpec(
            tipo=TipoScaffalatura.LIGHT_DUTY,
            altezza_cm=200.0,
            larghezza_cm=100.0,
            profondita_cm=80.0,
            massa_vuota_kg=100.0,
            massa_contenuto_kg=200.0,
            ancorata=False,
        )
        assert spec.massa_totale_kg() == 300.0


class TestScaffalaturaSLU:
    def test_check_slu_contract(self):
        inputs = {
            "tipo": "heavy_duty",
            "massa_vuota_kg": 150.0,
            "massa_contenuto_kg": 300.0,
            "altezza_cm": 250.0,
            "larghezza_cm": 120.0,
            "S_a": 1.5,
        }
        result = check_slu(inputs)
        assert result["element_type"] == "scaffalature"
        assert "meccanismo_critico" in result


class TestScaffalaturaSLE:
    def test_check_sle_damage(self):
        inputs = {
            "tipo": "armadio_tecnico",
            "massa_vuota_kg": 80.0,
            "massa_contenuto_kg": 150.0,
            "altezza_cm": 180.0,
            "spostamento_relativo_cm": 0.5,
        }
        result = check_sle(inputs)
        assert "stato_danno" in result


class TestScaffalaturaPipeline:
    def test_pipeline_completa(self):
        inputs = {
            "tipo": "archivio",
            "massa_vuota_kg": 200.0,
            "massa_contenuto_kg": 400.0,
            "altezza_cm": 220.0,
            "larghezza_cm": 100.0,
            "profondita_cm": 60.0,
            "ancorata": True,
        }
        risultato = verifica_scaffalatura_completa(inputs)
        assert isinstance(risultato, RisultatoScaffalatura)
