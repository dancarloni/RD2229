from __future__ import annotations

from src.codes.ntc2018.secondary_elements.impianti import (
    CategoriaImpianto,
    ImpiantoSpec,
    TipoSupporto,
    check_sle,
    check_slu,
    verifica_impianto_completa,
)
from src.codes.ntc2018.secondary_elements.impianti.models import RisultatoImpianto, StatoDannoSLE


class TestImpiantoModels:
    def test_spec_massa(self):
        spec = ImpiantoSpec(
            categoria=CategoriaImpianto.TUBAZIONE_SOSPESA,
            massa_kg=40.0,
            quota_cm=250.0,
            tipo_supporto=TipoSupporto.SOSPENSIONE,
            numero_ancoraggi=2,
            presenza_giunto_flessibile=True,
        )
        assert spec.massa_totale_kg() == 40.0


class TestImpiantoSLU:
    def test_check_slu_contract(self):
        inputs = {
            "categoria": "tubazione_sospesa",
            "massa_kg": 40.0,
            "numero_ancoraggi": 2,
        }
        result = check_slu(inputs)
        assert result["element_type"] == "impianti"
        assert "decision_log" in result


class TestImpiantoSLE:
    def test_check_sle_damage(self):
        inputs = {
            "categoria": "canale_aria",
            "massa_kg": 50.0,
            "numero_ancoraggi": 3,
            "spostamento_relativo_cm": 0.5,
        }
        result = check_sle(inputs)
        assert result["stato_danno"] in [s.value for s in StatoDannoSLE]


class TestImpiantoPipeline:
    def test_pipeline_completa(self):
        inputs = {
            "categoria": "quadro_elettrico",
            "massa_kg": 60.0,
            "quota_cm": 300.0,
            "numero_ancoraggi": 4,
        }
        risultato = verifica_impianto_completa(inputs)
        assert isinstance(risultato, RisultatoImpianto)
        assert len(risultato.passaggi_calcolo) > 0
