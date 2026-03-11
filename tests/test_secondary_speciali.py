from __future__ import annotations

from src.codes.ntc2018.secondary_elements.speciali import (
    FamigliaSpeciale,
    check_sle,
    check_slu,
    verifica_speciale_completa,
)
from src.codes.ntc2018.secondary_elements.speciali.models import (
    RisultatoComponenteSpeciale,
)


class TestComponenteModels:
    def test_massa_totale(self):
        from src.codes.ntc2018.secondary_elements.speciali import ComponenteSpecialeSpec

        spec = ComponenteSpecialeSpec(
            famiglia=FamigliaSpeciale.INSEGNA_BANDIERA,
            massa_kg=80.0,
            schema_statico="mensola",
            esposizione_esterna=True,
            tipo_supporto="staffa_fissa",
            grado_mobilita="fisso",
        )
        assert spec.massa_totale_kg() == 80.0


class TestComponenteSLU:
    def test_check_slu_contract(self):
        inputs = {
            "famiglia": "insegna_bandiera",
            "massa_kg": 70.0,
            "esposizione_esterna": True,
            "S_a": 1.5,
        }
        result = check_slu(inputs)
        assert result["element_type"] == "speciali"
        assert "utilisation" in result


class TestComponenteSLE:
    def test_check_sle_damage(self):
        inputs = {
            "famiglia": "cancello_scorrevole",
            "massa_kg": 100.0,
            "grado_mobilita": "mobile",
            "spostamento_relativo_cm": 0.9,
        }
        result = check_sle(inputs)
        assert "stato_danno" in result


class TestComponentePipeline:
    def test_pipeline_completa(self):
        inputs = {
            "famiglia": "pannello_sospeso",
            "massa_kg": 120.0,
            "schema_statico": "sospensione",
            "esposizione_esterna": False,
        }
        risultato = verifica_speciale_completa(inputs)
        assert isinstance(risultato, RisultatoComponenteSpeciale)
