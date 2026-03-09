"""Test per i cataloghi materiali multi-normativa.

Verifica che tutti i cataloghi JSON siano caricabili e contengano
materiali con i parametri attesi per ciascuna norma.
"""

import pytest

from src.materials.material_repo import MaterialRepository


@pytest.fixture
def repo_completo() -> MaterialRepository:
    """Repository con tutti i cataloghi caricati."""
    repo = MaterialRepository()
    repo.carica_tutti_cataloghi()
    return repo


class TestCaricamentoCataloghi:
    """Test caricamento di tutti i cataloghi."""

    def test_carica_tutti_cataloghi(self, repo_completo: MaterialRepository) -> None:
        """Verifica che il caricamento completo funzioni."""
        assert repo_completo.count() >= 80

    def test_norme_disponibili(self, repo_completo: MaterialRepository) -> None:
        """Verifica che tutte le norme attese siano presenti."""
        norme = repo_completo.list_norme_disponibili()
        norme_attese = {"NTC2018", "RD2229", "DM72", "DM87", "DM92", "DM96", "NTC2008", "Circ81", "OPCM3274"}
        for norma in norme_attese:
            assert norma in norme, f"Norma {norma} non trovata"

    def test_list_by_norma(self, repo_completo: MaterialRepository) -> None:
        """Verifica il filtro per norma."""
        mats_ntc = repo_completo.list_by_norma("NTC2018")
        assert len(mats_ntc) >= 10
        for m in mats_ntc:
            assert m.norma_riferimento == "NTC2018"


class TestCatalogoRD2229:
    """Test specifici per materiali RD 2229/39."""

    def test_calcestruzzi_rd2229(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("RD2229") if m.famiglia == "calcestruzzo"]
        assert len(mats) >= 4
        for m in mats:
            assert m.sigma_c28 > 0, f"{m.material_id}: sigma_c28 mancante"
            assert m.sigma_c_adm > 0, f"{m.material_id}: sigma_c_adm mancante"
            assert m.gamma_c == 1.0, f"{m.material_id}: gamma_c deve essere 1.0 per TA"

    def test_acciai_rd2229(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("RD2229") if m.famiglia == "acciaio"]
        assert len(mats) >= 3
        for m in mats:
            assert m.sigma_s_adm > 0, f"{m.material_id}: sigma_s_adm mancante"
            assert m.gamma_s == 1.0, f"{m.material_id}: gamma_s deve essere 1.0 per TA"
            assert m.E == 2100000.0, f"{m.material_id}: Es deve essere 2100000"


class TestCatalogoDM92:
    """Test specifici per materiali DM 14/02/1992."""

    def test_calcestruzzi_dm92(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("DM92") if m.famiglia == "calcestruzzo"]
        assert len(mats) >= 5
        for m in mats:
            assert m.sigma_c28 > 0
            assert m.sigma_c_adm > 0
            assert m.gamma_c == 1.60, f"{m.material_id}: gamma_c deve essere 1.60 per DM92 SL"
            assert m.n_omogenizzazione > 0

    def test_acciai_dm92(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("DM92") if m.famiglia == "acciaio"]
        assert len(mats) >= 3
        for m in mats:
            assert m.f_yk > 0 or m.sigma_s_adm > 0
            assert m.gamma_s == 1.15


class TestCatalogoDM96:
    """Test specifici per materiali DM 09/01/1996."""

    def test_calcestruzzi_dm96(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("DM96") if m.famiglia == "calcestruzzo"]
        assert len(mats) >= 6
        for m in mats:
            assert m.sigma_c28 > 0
            assert m.gamma_c == 1.60

    def test_acciai_dm96(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("DM96") if m.famiglia == "acciaio"]
        assert len(mats) >= 3


class TestCatalogoDM72:
    """Test specifici per materiali DM 30/05/1972."""

    def test_calcestruzzi_dm72(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("DM72") if m.famiglia == "calcestruzzo"]
        assert len(mats) >= 3
        for m in mats:
            assert m.sigma_c28 > 0
            assert m.gamma_c == 1.0, "DM72 usa metodo TA puro"

    def test_acciai_dm72(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("DM72") if m.famiglia == "acciaio"]
        assert len(mats) >= 3


class TestCatalogoNTC2008:
    """Test specifici per materiali NTC 2008."""

    def test_calcestruzzi_ntc2008(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("NTC2008") if m.famiglia == "calcestruzzo"]
        assert len(mats) >= 8
        for m in mats:
            assert m.f_ck > 0, f"{m.material_id}: f_ck mancante"
            assert m.gamma_c == 1.50

    def test_acciai_ntc2008(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("NTC2008") if m.famiglia == "acciaio"]
        assert len(mats) >= 2
        for m in mats:
            assert m.f_yk == 4589.0  # B450C/A = 450 MPa


class TestCatalogoDM87Muratura:
    """Test specifici per muratura DM 20/11/1987."""

    def test_murature_dm87(self, repo_completo: MaterialRepository) -> None:
        mats = repo_completo.list_by_norma("DM87")
        assert len(mats) >= 6
        for m in mats:
            assert m.famiglia == "muratura"
            assert m.f_k > 0
            assert m.gamma_M >= 3.0


class TestCatalogoCirc81Muratura:
    """Test specifici per muratura Circ. 30/07/1981."""

    def test_murature_circ81(self, repo_completo: MaterialRepository) -> None:
        mats = repo_completo.list_by_norma("Circ81")
        assert len(mats) >= 4
        for m in mats:
            assert m.famiglia == "muratura"
            assert m.gamma_M >= 5.0, "Circ81 ha gamma_M ≥ 5 senza prove"


class TestCatalogoOPCM3274:
    """Test specifici per materiali OPCM 3274/2003."""

    def test_calcestruzzi_opcm3274(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("OPCM3274") if m.famiglia == "calcestruzzo"]
        assert len(mats) >= 4
        for m in mats:
            assert m.gamma_c == 1.60, f"{m.material_id}: gamma_c deve essere 1.60"
            assert m.sigma_c28 > 0

    def test_acciai_opcm3274(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("OPCM3274") if m.famiglia == "acciaio"]
        assert len(mats) >= 3
        for m in mats:
            assert m.gamma_s == 1.15
            assert m.E == 2100000.0


class TestNTC2018Completo:
    """Test per NTC2018 (deve essere il più completo)."""

    def test_tutte_le_famiglie(self, repo_completo: MaterialRepository) -> None:
        mats = repo_completo.list_by_norma("NTC2018")
        famiglie = {m.famiglia for m in mats}
        assert "calcestruzzo" in famiglie
        assert "acciaio" in famiglie
        assert "muratura" in famiglie

    def test_calcestruzzi_ntc2018_completi(self, repo_completo: MaterialRepository) -> None:
        mats = [m for m in repo_completo.list_by_norma("NTC2018") if m.famiglia == "calcestruzzo"]
        assert len(mats) >= 10  # C12/15 → C50/60 almeno
        for m in mats:
            assert m.f_ck > 0
            assert m.gamma_c == 1.50
            assert m.alpha_cc == 0.85


class TestCoerenzaValori:
    """Test di coerenza sui valori dei materiali."""

    def test_sigma_c_adm_proporzionale_rck(self, repo_completo: MaterialRepository) -> None:
        """Per le norme TA, sigma_c_adm deve essere proporzionale a Rck."""
        for norma in ["RD2229", "DM72"]:
            mats = [m for m in repo_completo.list_by_norma(norma) if m.famiglia == "calcestruzzo"]
            for m in mats:
                if m.sigma_c28 > 0 and m.sigma_c_adm > 0:
                    rapporto = m.sigma_c28 / m.sigma_c_adm
                    assert 2.5 <= rapporto <= 5.0, (
                        f"{m.material_id}: Rck/σ_c_adm = {rapporto:.1f}, fuori range"
                    )

    def test_modulo_elastico_acciaio_costante(self, repo_completo: MaterialRepository) -> None:
        """Tutti gli acciai devono avere Es = 2100000 kg/cm²."""
        for m in repo_completo.list_by_famiglia("acciaio"):
            assert m.E == 2100000.0, f"{m.material_id}: E = {m.E}, atteso 2100000"

    def test_densita_calcestruzzo_ragionevole(self, repo_completo: MaterialRepository) -> None:
        """Densità calcestruzzo deve essere tra 2200 e 2600 kg/m³."""
        for m in repo_completo.list_by_famiglia("calcestruzzo"):
            assert 2200 <= m.densita_kg_m3 <= 2600, (
                f"{m.material_id}: densità = {m.densita_kg_m3}"
            )
