"""Test per src/esistenti/vulnerabilita_ca.py — Fase R.2.

Pilastro tipo 'anni '60': 30×30 cm, Ø8/20, RCk150, fc=1.35.
"""

import dataclasses
import pytest

from src.esistenti.vulnerabilita_ca import (
    TipoElemento,
    ClasseVulnerabilita,
    SoglieRho,
    ConfigVulnerabilitaCA,
    ElementoCA,
    RisultatoElementoCA,
    IndiceVulnerabilitaCA,
    verifica_elemento_ca,
    analisi_vulnerabilita_ca,
    _capacita_flessione,
    _capacita_taglio,
    _capacita_pressoflessione,
    _duttilita_chord_rotation,
)


# ─── Fixture pilastro anni '60 ───────────────────────────────────────────────

@pytest.fixture
def pilastro_60():
    """Pilastro tipico anni '60: 30×30 cm, Ø8@20, acciaio FeB32k, cls RCk150.
    d = h_sez - copriferro ≈ 30 - 3.5 = 26.5 cm.
    """
    return ElementoCA(
        id_elemento="P1",
        tipo=TipoElemento.PILASTRO,
        b=30.0,
        h_sez=30.0,
        d=26.5,
        d_primo=3.5,
        As=4 * 0.503,       # 4Ø8 = 4×0.503 cm²
        As_primo=4 * 0.503,
        Asw=None,           # senza staffe (scenario critico)
        s_staffe=None,
        f_cd=60.0,          # kg/cm² — fck già diviso per FC
        f_yd=2_200.0,       # kg/cm² — FeB32k
        N_ed=5_000.0,       # kg compressione
        Mx_ed=1_500.0,      # kg·cm
        Ty_ed=50.0,         # kg
        luce=300.0,
        piano="1",
    )


@pytest.fixture
def trave_senza_staffe():
    """Trave 20×40 cm, Ø12, senza staffe."""
    return ElementoCA(
        id_elemento="T1",
        tipo=TipoElemento.TRAVE,
        b=20.0,
        h_sez=40.0,
        d=36.0,
        d_primo=4.0,
        As=2 * 1.131,       # 2Ø12
        As_primo=0.0,
        Asw=None,
        s_staffe=None,
        f_cd=70.0,
        f_yd=2_600.0,
        N_ed=0.0,
        Mx_ed=8_000.0,
        Ty_ed=400.0,
        luce=400.0,
        piano="1",
    )


@pytest.fixture
def config_std():
    return ConfigVulnerabilitaCA()


# ─── Test _capacita_flessione ────────────────────────────────────────────────

class TestCapacitaFlessione:
    def test_mrd_positivo(self, pilastro_60):
        MRd, passi = _capacita_flessione(pilastro_60)
        assert MRd > 0

    def test_mrd_cresce_con_as(self, pilastro_60):
        """Più armatura → maggior momento resistente."""
        MRd_base, _ = _capacita_flessione(pilastro_60)
        p2 = dataclasses.replace(pilastro_60, As=pilastro_60.As * 3)
        MRd_piu, _ = _capacita_flessione(p2)
        assert MRd_piu > MRd_base

    def test_mrd_trave(self, trave_senza_staffe):
        MRd, _ = _capacita_flessione(trave_senza_staffe)
        assert MRd > 0


# ─── Test _capacita_taglio ───────────────────────────────────────────────────

class TestCapacitaTaglio:
    def test_vrd_senza_staffe(self, pilastro_60):
        """Senza staffe il contributo calcestruzzo porta il taglio (§4.1.45)."""
        VRd, passi = _capacita_taglio(pilastro_60)
        assert VRd > 0
        assert any("VRd" in p or "V_Rd" in p for p in passi)

    def test_vrd_con_staffe_maggiore(self, pilastro_60):
        """Con staffe la resistenza è ≥ caso senza staffe."""
        VRd_no, _ = _capacita_taglio(pilastro_60)
        p2 = dataclasses.replace(pilastro_60, Asw=0.503, s_staffe=15.0)
        VRd_si, _ = _capacita_taglio(p2)
        assert VRd_si >= VRd_no

    def test_vrd_trave_senza_staffe(self, trave_senza_staffe):
        VRd, _ = _capacita_taglio(trave_senza_staffe)
        assert VRd > 0


# ─── Test _capacita_pressoflessione ─────────────────────────────────────────

class TestCapacitaPressoflessione:
    def test_mrd_pf_aumenta_con_N(self, pilastro_60):
        """Compressione moderata aumenta la capacità a presso-flessione."""
        MRd_no_N, _ = _capacita_pressoflessione(
            dataclasses.replace(pilastro_60, N_ed=0.0)
        )
        MRd_N, _ = _capacita_pressoflessione(pilastro_60)
        assert MRd_N >= MRd_no_N

    def test_mrd_pf_dominio_consistente(self, pilastro_60):
        """MRd dalla presso-flessione deve essere positivo."""
        MRd, passi = _capacita_pressoflessione(pilastro_60)
        assert MRd > 0


# ─── Test _duttilita_chord_rotation ─────────────────────────────────────────

class TestDuttilita:
    def test_theta_u_positivo(self, pilastro_60):
        θ_u, θ_y, μ = _duttilita_chord_rotation(pilastro_60)
        assert θ_u > 0
        assert θ_y > 0
        assert μ >= 1.0

    def test_theta_u_con_staffe_>=_senza(self, pilastro_60):
        """Con staffe la duttilità è ≥ caso senza staffe."""
        θ_u_no, _, _ = _duttilita_chord_rotation(pilastro_60)
        p2 = dataclasses.replace(pilastro_60, Asw=0.503, s_staffe=15.0)
        θ_u_si, _, _ = _duttilita_chord_rotation(p2)
        assert θ_u_si >= θ_u_no


# ─── Test verifica_elemento_ca ───────────────────────────────────────────────

class TestVerificaElementoCA:
    def test_risultato_ha_campi_aspettati(self, pilastro_60, config_std):
        r = verifica_elemento_ca(pilastro_60, config_std)
        assert isinstance(r, RisultatoElementoCA)
        assert r.id_elemento == "P1"
        assert 0 < r.rho_min <= r.rho_medio + 1e-9

    def test_classe_non_verificato_per_rho_basso(self, config_std):
        """Elemento con MEd >> MRd deve essere classificato NON_VERIFICATO."""
        elem = ElementoCA(
            id_elemento="P_critico",
            tipo=TipoElemento.PILASTRO,
            b=20.0, h_sez=20.0, d=16.0, d_primo=4.0,
            f_cd=50.0, f_yd=2_000.0,
            As=0.503, As_primo=0.0,
            Mx_ed=50_000.0,   # molto superiore alla capacità
            Ty_ed=2_000.0,
            N_ed=0.0,
            luce=300.0,
        )
        r = verifica_elemento_ca(elem, config_std)
        assert r.classe == ClasseVulnerabilita.NON_VERIFICATO

    def test_classe_verificato_per_elem_resistente(self, config_std):
        """Elemento sovra-resistente → VERIFICATO."""
        elem = ElementoCA(
            id_elemento="P_buono",
            tipo=TipoElemento.PILASTRO,
            b=40.0, h_sez=40.0, d=35.0, d_primo=5.0,
            f_cd=120.0, f_yd=3_600.0,
            As=20.0, As_primo=20.0,
            Asw=1.0, s_staffe=10.0,
            Mx_ed=1.0,    # domanda trascurabile
            Ty_ed=1.0,
            N_ed=0.0,
            luce=300.0,
        )
        r = verifica_elemento_ca(elem, config_std)
        assert r.classe == ClasseVulnerabilita.VERIFICATO

    def test_passaggi_popolati(self, pilastro_60, config_std):
        r = verifica_elemento_ca(pilastro_60, config_std)
        assert len(r.passaggi) > 0


# ─── Test analisi_vulnerabilita_ca ───────────────────────────────────────────

class TestAnalisiVulnerabilitaCA:
    def test_indice_base(self, pilastro_60, trave_senza_staffe, config_std):
        indice, risultati = analisi_vulnerabilita_ca(
            [pilastro_60, trave_senza_staffe], config_std
        )
        assert isinstance(indice, IndiceVulnerabilitaCA)
        assert len(risultati) == 2

    def test_n_contatori_coerenti(self, pilastro_60, config_std):
        indice, _ = analisi_vulnerabilita_ca([pilastro_60], config_std)
        totale = indice.n_verificati + indice.n_critici + indice.n_non_verificati
        assert totale == 1

    def test_rho_globale_range(self, pilastro_60, trave_senza_staffe, config_std):
        indice, _ = analisi_vulnerabilita_ca(
            [pilastro_60, trave_senza_staffe], config_std
        )
        assert 0.0 < indice.rho_globale

    def test_ranking_non_vuoto(self, pilastro_60, trave_senza_staffe, config_std):
        indice, _ = analisi_vulnerabilita_ca(
            [pilastro_60, trave_senza_staffe], config_std
        )
        assert len(indice.ranking) == 2

    def test_soglie_personalizzate(self, pilastro_60, config_std):
        """Soglie personalizzate cambiano la classificazione attesa."""
        config_stretta = ConfigVulnerabilitaCA(
            soglie=SoglieRho(verificato=1.2, critico=1.0)
        )
        r1 = verifica_elemento_ca(pilastro_60, config_std)
        r2 = verifica_elemento_ca(pilastro_60, config_stretta)
        # Con soglie più strette la classe non può essere migliore
        classes = [ClasseVulnerabilita.VERIFICATO, ClasseVulnerabilita.CRITICO, ClasseVulnerabilita.NON_VERIFICATO]
        assert classes.index(r2.classe) >= classes.index(r1.classe)
