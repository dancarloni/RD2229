"""Test del modulo adapter_unita_misura — conversioni centralizzate.

Verifica:
1. Conversioni base MPa ↔ kg/cm² (round-trip, precisione 4 decimali)
2. Lettura normalizzata f_ck e f_yk da materiali con unità miste
3. Compatibilità TA: get_rck_kg_cm2, get_sigma_c_adm_kg_cm2
4. Funzioni ensure_mpa / ensure_kg_cm2
5. Campo legacy Rck_kg_cm2 nel catalogo
6. Conversioni specifiche per DM92

Tutti i messaggi di asserzione sono in italiano.
"""

from __future__ import annotations

import math
import pathlib
import sys
from types import SimpleNamespace
from typing import Any

import pytest

# --- Setup path ---
ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.core.adapter_unita_misura import (
    ensure_kg_cm2,
    ensure_mpa,
    fck_mpa_to_rck_kg_cm2,
    fck_mpa_to_sigma_c_adm_kg_cm2_dm92,
    get_fck_mpa,
    get_fyk_mpa,
    get_rck_kg_cm2,
    get_sigma_c_adm_kg_cm2,
    get_sigma_s_adm_kg_cm2,
    kg_cm2_to_mpa,
    mpa_to_kg_cm2,
    rck_kg_cm2_to_fck_mpa,
    round_trip_mpa_kg_cm2,
    verifica_unita_catalogo,
    _KG_CM2_TO_MPA,
    _MPA_TO_KG_CM2,
)


# ==============================================================================
# SEZIONE 1: COSTANTI E CONVERSIONI BASE
# ==============================================================================


class TestCostantiConversione:
    """Verifica la correttezza delle costanti di conversione."""

    def test_fattore_kg_cm2_to_mpa_esatto(self):
        """Il fattore 1 kg/cm² = 0.0980665 MPa deve essere preciso."""
        assert _KG_CM2_TO_MPA == 0.0980665, (
            "Fattore kg/cm² → MPa deve essere esattamente 0.0980665"
        )

    def test_fattore_inverso_coerente(self):
        """Il prodotto dei due fattori deve essere 1.0 con alta precisione."""
        prodotto = _KG_CM2_TO_MPA * _MPA_TO_KG_CM2
        assert abs(prodotto - 1.0) < 1e-12, (
            f"_KG_CM2_TO_MPA × _MPA_TO_KG_CM2 deve essere 1.0, ottenuto {prodotto}"
        )

    def test_mpa_to_kg_cm2_valore_noto(self):
        """9.80665 MPa = 100.0 kg/cm² (definizione esatta)."""
        risultato = mpa_to_kg_cm2(9.80665)
        assert abs(risultato - 100.0) < 1e-4, (
            f"9.80665 MPa deve corrispondere a 100.0 kg/cm², ottenuto {risultato}"
        )

    def test_kg_cm2_to_mpa_valore_noto(self):
        """100 kg/cm² = 9.80665 MPa (definizione esatta)."""
        risultato = kg_cm2_to_mpa(100.0)
        assert abs(risultato - 9.80665) < 1e-4, (
            f"100 kg/cm² deve corrispondere a 9.80665 MPa, ottenuto {risultato}"
        )

    def test_conversione_25_mpa(self):
        """25 MPa → kg/cm²: valore di riferimento calcestruzzo C25/30."""
        risultato = mpa_to_kg_cm2(25.0)
        # 25 / 0.0980665 = 254.929...
        atteso = 25.0 / 0.0980665
        assert abs(risultato - atteso) < 1e-3, (
            f"25 MPa → {atteso:.4f} kg/cm² atteso, ottenuto {risultato}"
        )

    def test_conversione_zero(self):
        """La conversione di 0 deve restituire 0."""
        assert mpa_to_kg_cm2(0.0) == 0.0, "mpa_to_kg_cm2(0) deve essere 0.0"
        assert kg_cm2_to_mpa(0.0) == 0.0, "kg_cm2_to_mpa(0) deve essere 0.0"

    def test_conversione_negativa(self):
        """Valori negativi devono essere convertiti correttamente (trazione)."""
        assert mpa_to_kg_cm2(-10.0) < 0.0, "Valori negativi devono rimanere negativi"
        assert kg_cm2_to_mpa(-100.0) < 0.0, "Valori negativi devono rimanere negativi"


# ==============================================================================
# SEZIONE 2: ROUND-TRIP E PRECISIONE
# ==============================================================================


class TestRoundTrip:
    """Verifica la precisione del round-trip MPa → kg/cm² → MPa."""

    @pytest.mark.parametrize("valore_mpa", [
        1.0, 5.0, 12.0, 16.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 90.0,
    ])
    def test_round_trip_mpa(self, valore_mpa: float):
        """Round-trip MPa → kg/cm² → MPa con errore < 0.001 MPa."""
        riciclo = round_trip_mpa_kg_cm2(valore_mpa)
        errore = abs(riciclo - valore_mpa)
        assert errore < 0.001, (
            f"Round-trip {valore_mpa} MPa: errore {errore:.6f} MPa "
            f"(atteso < 0.001 MPa)"
        )

    @pytest.mark.parametrize("valore_kg", [
        100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0,
    ])
    def test_round_trip_kg_cm2(self, valore_kg: float):
        """Round-trip kg/cm² → MPa → kg/cm² con errore relativo < 0.01%."""
        riciclo = mpa_to_kg_cm2(kg_cm2_to_mpa(valore_kg))
        errore_rel = abs(riciclo - valore_kg) / valore_kg
        assert errore_rel < 1e-4, (
            f"Round-trip {valore_kg} kg/cm²: errore relativo {errore_rel:.2e} "
            f"(atteso < 1e-4)"
        )

    def test_precisione_4_decimali_mpa(self):
        """mpa_to_kg_cm2 deve arrotondare a 4 decimali."""
        risultato = mpa_to_kg_cm2(1.0)
        # 1 / 0.0980665 = 10.197162...
        assert risultato == round(1.0 / 0.0980665, 4), (
            "Risultato deve essere arrotondato a 4 decimali"
        )

    def test_precisione_4_decimali_kg_cm2(self):
        """kg_cm2_to_mpa deve arrotondare a 4 decimali."""
        risultato = kg_cm2_to_mpa(1.0)
        # 1 × 0.0980665 = 0.0980665
        assert risultato == round(0.0980665, 4), (
            "Risultato deve essere arrotondato a 4 decimali"
        )


# ==============================================================================
# SEZIONE 3: LETTURA f_ck E f_yk DA MATERIALI
# ==============================================================================


class TestGetFckFyk:
    """Verifica la lettura normalizzata di f_ck e f_yk da oggetti materiale."""

    def _materiale(self, **kwargs) -> Any:
        return SimpleNamespace(**kwargs)

    def test_fck_gia_in_mpa(self):
        """f_ck ≤ 200 è interpretato come MPa."""
        mat = self._materiale(f_ck=25.0)
        risultato = get_fck_mpa(mat)
        assert risultato == 25.0, f"f_ck=25.0 in MPa deve restituire 25.0, ottenuto {risultato}"

    def test_fck_in_kg_cm2_convertito(self):
        """f_ck > 200 è interpretato come kg/cm² e convertito a MPa."""
        # 254.93 kg/cm² ≈ 25 MPa
        mat = self._materiale(f_ck=254.9294)
        risultato = get_fck_mpa(mat)
        assert risultato is not None
        assert abs(risultato - 25.0) < 0.1, (
            f"f_ck=254.93 kg/cm² deve convertirsi a ~25 MPa, ottenuto {risultato}"
        )

    def test_fck_zero_restituisce_none(self):
        """f_ck=0 deve restituire None."""
        mat = self._materiale(f_ck=0)
        assert get_fck_mpa(mat) is None, "f_ck=0 deve restituire None"

    def test_fck_assente_restituisce_none(self):
        """Materiale senza f_ck deve restituire None."""
        mat = self._materiale(nome="calcestruzzo_senza_fck")
        assert get_fck_mpa(mat) is None, "Materiale senza f_ck deve restituire None"

    def test_fyk_gia_in_mpa(self):
        """f_yk ≤ 1000 è interpretato come MPa."""
        mat = self._materiale(f_yk=450.0)
        risultato = get_fyk_mpa(mat)
        assert risultato == 450.0, f"f_yk=450 MPa deve restituire 450.0, ottenuto {risultato}"

    def test_fyk_in_kg_cm2_convertito(self):
        """f_yk > 1000 è interpretato come kg/cm² e convertito."""
        # 4500 kg/cm² ≈ 441.3 MPa
        mat = self._materiale(f_yk=4500.0)
        risultato = get_fyk_mpa(mat)
        assert risultato is not None
        atteso = kg_cm2_to_mpa(4500.0)
        assert abs(risultato - atteso) < 1e-3, (
            f"f_yk=4500 kg/cm² deve convertirsi a {atteso:.2f} MPa, ottenuto {risultato}"
        )

    def test_fyk_zero_restituisce_none(self):
        """f_yk=0 deve restituire None."""
        mat = self._materiale(f_yk=0)
        assert get_fyk_mpa(mat) is None, "f_yk=0 deve restituire None"

    @pytest.mark.parametrize("f_ck_mpa,atteso_mpa", [
        (12.0, 12.0),
        (16.0, 16.0),
        (20.0, 20.0),
        (25.0, 25.0),
        (30.0, 30.0),
    ])
    def test_classi_calcestruzzo_ntc2018(self, f_ck_mpa: float, atteso_mpa: float):
        """Classi calcestruzzo NTC2018 in MPa devono passare invariate."""
        mat = self._materiale(f_ck=f_ck_mpa)
        assert get_fck_mpa(mat) == atteso_mpa


# ==============================================================================
# SEZIONE 4: COMPATIBILITÀ TA (kg/cm²)
# ==============================================================================


class TestCompatibilitaTA:
    """Verifica le funzioni per il metodo delle Tensioni Ammissibili."""

    def _materiale(self, **kwargs) -> Any:
        return SimpleNamespace(**kwargs)

    def test_rck_da_sigma_c28(self):
        """get_rck_kg_cm2 deve leggere sigma_c28 direttamente."""
        mat = self._materiale(sigma_c28=250.0)
        assert get_rck_kg_cm2(mat) == 250.0, (
            "sigma_c28=250 deve essere letto come Rck=250 kg/cm²"
        )

    def test_rck_da_campo_legacy(self):
        """get_rck_kg_cm2 deve leggere Rck_kg_cm2 (campo legacy)."""
        mat = self._materiale(Rck_kg_cm2=200.0)
        assert get_rck_kg_cm2(mat) == 200.0, (
            "Rck_kg_cm2=200 deve essere letto direttamente"
        )

    def test_rck_da_fck_mpa(self):
        """get_rck_kg_cm2 deve stimare Rck da f_ck in MPa."""
        # C25/30: f_ck=25 MPa → Rck = 25/0.83 MPa = 30.12 MPa → 307.2 kg/cm²
        mat = self._materiale(f_ck=25.0)
        rck = get_rck_kg_cm2(mat)
        assert rck is not None
        atteso = mpa_to_kg_cm2(25.0 / 0.83)
        assert abs(rck - atteso) < 1.0, (
            f"Rck da f_ck=25 MPa deve essere ~{atteso:.1f} kg/cm², ottenuto {rck}"
        )

    def test_rck_da_fck_kg_cm2(self):
        """get_rck_kg_cm2 deve gestire f_ck in kg/cm² (catalogo NTC2018 storico)."""
        # f_ck=254.93 kg/cm² ≈ 25 MPa → Rck ≈ 307 kg/cm²
        mat = self._materiale(f_ck=254.9294)
        rck = get_rck_kg_cm2(mat)
        assert rck is not None
        assert rck > 200.0, f"Rck deve essere > 200 kg/cm², ottenuto {rck}"

    def test_rck_assente_restituisce_none(self):
        """Materiale senza dati di resistenza deve restituire None."""
        mat = self._materiale(nome="materiale_vuoto")
        assert get_rck_kg_cm2(mat) is None

    def test_sigma_c_adm_campo_diretto(self):
        """get_sigma_c_adm_kg_cm2 deve leggere sigma_c_adm direttamente."""
        mat = self._materiale(sigma_c_adm=75.0)
        assert get_sigma_c_adm_kg_cm2(mat) == 75.0

    def test_sigma_c_adm_da_sigma_c_adm_kg_cm2(self):
        """get_sigma_c_adm_kg_cm2 deve leggere sigma_c_adm_kg_cm2."""
        mat = self._materiale(sigma_c_adm_kg_cm2=60.0)
        assert get_sigma_c_adm_kg_cm2(mat) == 60.0

    def test_sigma_c_adm_stima_da_rck(self):
        """get_sigma_c_adm_kg_cm2 deve stimare σ_c_adm = 0.30 × Rck."""
        mat = self._materiale(sigma_c28=250.0)
        sigma_c_adm = get_sigma_c_adm_kg_cm2(mat)
        assert sigma_c_adm is not None
        atteso = 0.30 * 250.0  # = 75.0 kg/cm²
        assert abs(sigma_c_adm - atteso) < 0.01, (
            f"σ_c_adm da Rck=250 deve essere {atteso} kg/cm², ottenuto {sigma_c_adm}"
        )

    def test_sigma_s_adm_campo_diretto(self):
        """get_sigma_s_adm_kg_cm2 deve leggere sigma_s_adm direttamente."""
        mat = self._materiale(sigma_s_adm=2200.0)
        assert get_sigma_s_adm_kg_cm2(mat) == 2200.0

    def test_sigma_s_adm_stima_da_fyk(self):
        """get_sigma_s_adm_kg_cm2 deve stimare σ_s_adm = min(2/3 × f_yk_kg_cm2, 2600)."""
        # Fe B44k: f_yk ≈ 440 MPa = 4487 kg/cm²
        # σ_s_adm = min(2/3 × 4487, 2600) = min(2991, 2600) = 2600
        mat = self._materiale(f_yk=440.0)
        sigma_s_adm = get_sigma_s_adm_kg_cm2(mat)
        assert sigma_s_adm is not None
        assert sigma_s_adm == 2600.0, (
            f"σ_s_adm per Fe440 deve essere 2600 kg/cm² (limite massimo), ottenuto {sigma_s_adm}"
        )

    def test_sigma_s_adm_sotto_limite(self):
        """Per acciaio debole, σ_s_adm = 2/3 × f_yk_kg_cm2 (< 2600)."""
        # Acciaio ipotetico con f_yk=200 MPa = 2039.4 kg/cm²
        # σ_s_adm = 2/3 × 2039.4 = 1359.6 < 2600
        mat = self._materiale(f_yk=200.0)
        sigma_s_adm = get_sigma_s_adm_kg_cm2(mat)
        assert sigma_s_adm is not None
        assert sigma_s_adm < 2600.0, (
            "σ_s_adm per acciaio debole deve essere < 2600 kg/cm²"
        )
        atteso = mpa_to_kg_cm2(200.0) * 2.0 / 3.0
        assert abs(sigma_s_adm - atteso) < 1.0


# ==============================================================================
# SEZIONE 5: ensure_mpa E ensure_kg_cm2
# ==============================================================================


class TestEnsureMpa:
    """Verifica le funzioni di normalizzazione ensure_mpa e ensure_kg_cm2."""

    def test_ensure_mpa_da_mpa(self):
        """Valore già in MPa non deve essere modificato."""
        assert ensure_mpa(25.0, "mpa") == 25.0
        assert ensure_mpa(25.0, "MPa") == 25.0
        assert ensure_mpa(25.0, "N/mm2") == 25.0
        assert ensure_mpa(25.0, "N/mm²") == 25.0

    def test_ensure_mpa_da_kg_cm2(self):
        """Valore in kg/cm² deve essere convertito a MPa."""
        risultato = ensure_mpa(100.0, "kg/cm2")
        atteso = kg_cm2_to_mpa(100.0)
        assert abs(risultato - atteso) < 1e-6

    def test_ensure_mpa_unita_non_riconosciuta(self):
        """Unità sconosciuta deve sollevare ValueError."""
        with pytest.raises(ValueError, match="non riconosciuta"):
            ensure_mpa(25.0, "bar")

    def test_ensure_kg_cm2_da_kg_cm2(self):
        """Valore già in kg/cm² non deve essere modificato."""
        assert ensure_kg_cm2(100.0, "kg/cm2") == 100.0
        assert ensure_kg_cm2(100.0, "kg/cm²") == 100.0
        assert ensure_kg_cm2(100.0, "kgcm2") == 100.0

    def test_ensure_kg_cm2_da_mpa(self):
        """Valore in MPa deve essere convertito a kg/cm²."""
        risultato = ensure_kg_cm2(9.80665, "mpa")
        assert abs(risultato - 100.0) < 1e-3

    def test_ensure_kg_cm2_unita_non_riconosciuta(self):
        """Unità sconosciuta deve sollevare ValueError."""
        with pytest.raises(ValueError, match="non riconosciuta"):
            ensure_kg_cm2(25.0, "kPa")

    @pytest.mark.parametrize("valore,unita", [
        (25.0, "mpa"),
        (25.0, "MPa"),
        (25.0, "N/mm2"),
        (254.93, "kg/cm2"),
        (254.93, "kg/cm²"),
    ])
    def test_ensure_mpa_round_trip(self, valore: float, unita: str):
        """ensure_mpa → ensure_kg_cm2 → ensure_mpa deve ritornare al valore originale in MPa."""
        valore_mpa = ensure_mpa(valore, unita)
        valore_kg = ensure_kg_cm2(valore_mpa, "mpa")
        valore_mpa_rt = ensure_mpa(valore_kg, "kg/cm2")
        assert abs(valore_mpa_rt - valore_mpa) < 1e-3


# ==============================================================================
# SEZIONE 6: CONVERSIONI SPECIFICHE PER DM92
# ==============================================================================


class TestConversioniDM92:
    """Verifica funzioni di conversione specifiche per DM92/DM96."""

    def test_fck_mpa_to_rck_kg_cm2_c25(self):
        """C25/30: f_ck=25 MPa → Rck = 25/0.83/0.0980665 ≈ 307.1 kg/cm²."""
        rck = fck_mpa_to_rck_kg_cm2(25.0)
        atteso = 25.0 / 0.83 / 0.0980665
        assert abs(rck - atteso) < 1.0, (
            f"C25/30: Rck atteso ~{atteso:.1f} kg/cm², ottenuto {rck}"
        )

    def test_rck_kg_cm2_to_fck_mpa_coerente(self):
        """Round-trip f_ck → Rck → f_ck deve dare errore < 0.1 MPa."""
        f_ck_originale = 25.0
        rck = fck_mpa_to_rck_kg_cm2(f_ck_originale)
        f_ck_riciclato = rck_kg_cm2_to_fck_mpa(rck)
        assert abs(f_ck_riciclato - f_ck_originale) < 0.1, (
            f"Round-trip f_ck={f_ck_originale} MPa: ottenuto {f_ck_riciclato} MPa"
        )

    @pytest.mark.parametrize("f_ck_mpa,rck_atteso_kg_cm2", [
        (20.0, 20.0 / 0.83 / 0.0980665),
        (25.0, 25.0 / 0.83 / 0.0980665),
        (30.0, 30.0 / 0.83 / 0.0980665),
    ])
    def test_fck_to_rck_parametrico(self, f_ck_mpa: float, rck_atteso_kg_cm2: float):
        """Conversione f_ck → Rck parametrica."""
        rck = fck_mpa_to_rck_kg_cm2(f_ck_mpa)
        assert abs(rck - rck_atteso_kg_cm2) < 1.0

    def test_sigma_c_adm_dm92_c25(self):
        """DM92 σ_c_adm per C25/30: 0.30 × Rck [kg/cm²]."""
        sigma = fck_mpa_to_sigma_c_adm_kg_cm2_dm92(25.0)
        rck = fck_mpa_to_rck_kg_cm2(25.0)
        atteso = 0.30 * rck
        assert abs(sigma - atteso) < 0.1, (
            f"σ_c_adm DM92 per C25: atteso {atteso:.2f}, ottenuto {sigma:.2f} kg/cm²"
        )

    def test_sigma_c_adm_dm92_positivo(self):
        """σ_c_adm deve essere positivo per qualsiasi f_ck > 0."""
        for f_ck in [12.0, 16.0, 20.0, 25.0, 30.0, 35.0, 40.0]:
            sigma = fck_mpa_to_sigma_c_adm_kg_cm2_dm92(f_ck)
            assert sigma > 0.0, f"σ_c_adm per f_ck={f_ck} MPa deve essere > 0"


# ==============================================================================
# SEZIONE 7: VERIFICA CATALOGO JSON
# ==============================================================================


class TestVerificaCatalogo:
    """Verifica la funzione di analisi unità nei cataloghi JSON."""

    def test_catalogo_ntc2018_fck_kg_cm2(self):
        """Il catalogo NTC2018 usa f_ck in kg/cm² (>200): deve essere rilevato."""
        record = {
            "material_id": "cls_C25/30",
            "f_ck": 254.9,  # kg/cm² (= 25 MPa × 10.197)
            "gamma_c": 1.50,
        }
        analisi = verifica_unita_catalogo(record)
        assert "f_ck" in analisi
        assert analisi["f_ck"]["unita_presunta"] == "kg/cm²", (
            "f_ck=254.9 deve essere rilevato come kg/cm²"
        )

    def test_catalogo_fck_mpa(self):
        """Campo f_ck con valore ≤ 200 deve essere rilevato come MPa."""
        record = {"f_ck": 25.0, "f_yk": 450.0}
        analisi = verifica_unita_catalogo(record)
        assert analisi["f_ck"]["unita_presunta"] == "MPa"

    def test_catalogo_rd2229_sigma_c28(self):
        """Campo sigma_c28 è sempre in kg/cm² per definizione."""
        record = {
            "sigma_c28": 250.0,
            "sigma_c_adm": 62.5,
        }
        analisi = verifica_unita_catalogo(record)
        assert analisi["sigma_c28"]["unita_presunta"] == "kg/cm²"
        assert analisi["sigma_c_adm"]["unita_presunta"] == "kg/cm²"

    def test_catalogo_campo_assente_non_incluso(self):
        """Campi assenti o a zero non devono comparire nel risultato."""
        record = {"f_ck": 0, "gamma_c": 1.5}
        analisi = verifica_unita_catalogo(record)
        assert "f_ck" not in analisi, "f_ck=0 non deve comparire nell'analisi"

    def test_catalogo_campi_personalizzati(self):
        """La funzione deve accettare una lista personalizzata di campi."""
        record = {"resistenza_caratteristica": 25.0, "modulo_elastico": 210000.0}
        analisi = verifica_unita_catalogo(
            record, campi_tensione=["resistenza_caratteristica", "modulo_elastico"]
        )
        # Con campi non riconosciuti, unita_presunta = "sconosciuta"
        assert "resistenza_caratteristica" in analisi
        assert analisi["resistenza_caratteristica"]["unita_presunta"] == "sconosciuta"


# ==============================================================================
# SEZIONE 8: CAMPO LEGACY Rck_kg_cm2
# ==============================================================================


class TestCampoLegacyRck:
    """Verifica la gestione del campo legacy Rck_kg_cm2."""

    def _mat(self, **kwargs) -> Any:
        return SimpleNamespace(**kwargs)

    def test_rck_legacy_priorita_su_fck(self):
        """Rck_kg_cm2 deve avere priorità su sigma_c28 (viene dopo nel codice)."""
        # sigma_c28 ha priorità maggiore (primo check)
        mat = self._mat(sigma_c28=200.0, Rck_kg_cm2=250.0)
        rck = get_rck_kg_cm2(mat)
        assert rck == 200.0, "sigma_c28 ha priorità su Rck_kg_cm2"

    def test_rck_legacy_senza_sigma_c28(self):
        """Senza sigma_c28, Rck_kg_cm2 deve essere usato."""
        mat = self._mat(Rck_kg_cm2=300.0)
        assert get_rck_kg_cm2(mat) == 300.0

    def test_sigma_c_adm_da_rck_legacy(self):
        """σ_c_adm stimata da Rck_kg_cm2 deve essere 0.30 × Rck."""
        mat = self._mat(Rck_kg_cm2=300.0)
        sigma = get_sigma_c_adm_kg_cm2(mat)
        assert sigma is not None
        assert abs(sigma - 0.30 * 300.0) < 0.01

    def test_get_rck_priorita_ordine(self):
        """Verifica l'ordine di priorità: sigma_c28 > Rck_kg_cm2 > Rck > f_ck."""
        # Solo sigma_c28
        mat1 = self._mat(sigma_c28=150.0)
        assert get_rck_kg_cm2(mat1) == 150.0

        # Solo Rck_kg_cm2
        mat2 = self._mat(Rck_kg_cm2=200.0)
        assert get_rck_kg_cm2(mat2) == 200.0

        # Solo f_ck (stima)
        mat3 = self._mat(f_ck=25.0)
        rck3 = get_rck_kg_cm2(mat3)
        assert rck3 is not None and rck3 > 0.0


# ==============================================================================
# SEZIONE 9: INTEGRAZIONE CON CATALOGHI REALI
# ==============================================================================


class TestIntegrazioneCatalogReal:
    """Test di integrazione con i cataloghi JSON del progetto."""

    def test_catalogo_ntc2018_caricabile(self):
        """Il catalogo NTC2018 deve essere caricabile e le f_ck convertibili."""
        import json

        catalogo_path = (
            pathlib.Path(__file__).resolve().parents[1]
            / "data" / "materials" / "catalogo_ntc2018.json"
        )
        with open(catalogo_path, encoding="utf-8") as f:
            catalogo = json.load(f)

        assert len(catalogo) > 0, "Catalogo NTC2018 non deve essere vuoto"

        for record in catalogo:
            mat = SimpleNamespace(**record)
            f_ck_mpa = get_fck_mpa(mat)
            if f_ck_mpa is not None:
                assert f_ck_mpa > 0.0, (
                    f"f_ck per {record.get('material_id')} deve essere > 0 MPa"
                )
                assert f_ck_mpa < 200.0, (
                    f"f_ck per {record.get('material_id')} deve essere < 200 MPa "
                    f"(ottenuto {f_ck_mpa})"
                )

    def test_catalogo_rd2229_caricabile(self):
        """Il catalogo RD2229 deve avere sigma_c28 leggibile come Rck."""
        import json

        catalogo_path = (
            pathlib.Path(__file__).resolve().parents[1]
            / "data" / "materials" / "catalogo_rd2229.json"
        )
        with open(catalogo_path, encoding="utf-8") as f:
            catalogo = json.load(f)

        for record in catalogo:
            if "sigma_c28" in record and record["sigma_c28"] > 0:
                mat = SimpleNamespace(**record)
                rck = get_rck_kg_cm2(mat)
                assert rck == record["sigma_c28"], (
                    f"sigma_c28={record['sigma_c28']} deve corrispondere a Rck={rck}"
                )

    def test_catalogo_dm92_sigma_c_adm(self):
        """Il catalogo DM92 deve avere sigma_c_adm leggibile direttamente."""
        import json

        catalogo_path = (
            pathlib.Path(__file__).resolve().parents[1]
            / "data" / "materials" / "catalogo_dm92.json"
        )
        with open(catalogo_path, encoding="utf-8") as f:
            catalogo = json.load(f)

        for record in catalogo:
            if "sigma_c_adm" in record and record["sigma_c_adm"] > 0:
                mat = SimpleNamespace(**record)
                sigma = get_sigma_c_adm_kg_cm2(mat)
                assert sigma == record["sigma_c_adm"], (
                    f"sigma_c_adm={record['sigma_c_adm']} deve essere letto "
                    f"direttamente, ottenuto {sigma}"
                )
