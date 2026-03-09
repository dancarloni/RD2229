"""Test benchmark MIP — formule Santarella Tabella 9.

Subfase L.10: test unitari per carichi_fissi.py.
Toleranza: 0.1% (errore ammissibile formule TA storiche).
"""

import pytest

from src.methods.rd2229.telaio.carichi_fissi import (
    mip_cedimento,
    mip_concentrato,
    mip_momento_nodale,
    mip_trapezoidale,
    mip_triangolare_crescente,
    mip_triangolare_decrescente,
    mip_uniforme,
)

TOL = 1e-3  # 0.1%


def _check(calcolato: float, atteso: float, msg: str = "") -> None:
    if abs(atteso) < 1e-9:
        assert abs(calcolato) < 1e-6, f"{msg}: atteso ~0, calcolato {calcolato}"
    else:
        err_rel = abs((calcolato - atteso) / atteso)
        assert err_rel < TOL, f"{msg}: atteso {atteso:.4f}, calcolato {calcolato:.4f} (err={err_rel:.4%})"


# ==============================================================================
# TEST 1 — mip_uniforme
# ==============================================================================

class TestMipUniforme:
    """Santarella Tab.9 — carico distribuito uniforme."""

    def test_5_kg_cm_300_cm(self):
        """w=5 kg/cm, L=300 cm → M_i=-37500, M_j=+37500 kg·cm (wL²/12=37500)"""
        Mi, Mj = mip_uniforme(5.0, 300.0)
        _check(Mi, -37500.0, "M_i uniforme")
        _check(Mj, +37500.0, "M_j uniforme")

    def test_formula_wL2_12(self):
        """Verifica formula M = ±wL²/12 per diversi valori."""
        for w, L in [(2.0, 400.0), (0.5, 600.0), (10.0, 200.0)]:
            Mi, Mj = mip_uniforme(w, L)
            atteso = w * L**2 / 12.0
            _check(abs(Mi), atteso, f"w={w}, L={L} — |M_i|")
            _check(Mj, atteso, f"w={w}, L={L} — M_j")
            assert Mi < 0 and Mj > 0

    def test_w_zero(self):
        Mi, Mj = mip_uniforme(0.0, 300.0)
        assert Mi == pytest.approx(0.0)
        assert Mj == pytest.approx(0.0)


# ==============================================================================
# TEST 2 — mip_concentrato
# ==============================================================================

class TestMipConcentrato:
    """Santarella Tab.9 — carico concentrato."""

    def test_in_mezzeria(self):
        """P=1000 kg, a=b=L/2=150 cm → M_i=-M_j=PL/8=18750 kg·cm"""
        Mi, Mj = mip_concentrato(1000.0, 150.0, 300.0)
        atteso = 1000.0 * 300.0 / 8.0  # PL/8 = 37500/2 se a=b ... wait:
        # M_i = -Pab²/L² = -1000×150×150²/300² = -1000×150×22500/90000 = -37500 kg·cm
        atteso_i = -1000.0 * 150.0 * 150.0**2 / 300.0**2
        atteso_j = +1000.0 * 150.0**2 * 150.0 / 300.0**2
        _check(Mi, atteso_i, "M_i concentrato mezzeria")
        _check(Mj, atteso_j, "M_j concentrato mezzeria")

    def test_terzo_punto(self):
        """P=1200 kg, a=100 cm, b=200 cm, L=300 cm."""
        P, a, L = 1200.0, 100.0, 300.0
        b = L - a
        Mi, Mj = mip_concentrato(P, a, L)
        atteso_i = -P * a * b**2 / L**2
        atteso_j = +P * a**2 * b / L**2
        _check(Mi, atteso_i, "M_i terzo punto")
        _check(Mj, atteso_j, "M_j terzo punto")
        assert Mi < 0 and Mj > 0

    def test_simmetria_in_mezzeria(self):
        """In mezzeria: |M_i| = |M_j|."""
        Mi, Mj = mip_concentrato(500.0, 150.0, 300.0)
        assert abs(Mi) == pytest.approx(abs(Mj), rel=1e-9)


# ==============================================================================
# TEST 3 — mip_trapezoidale
# ==============================================================================

class TestMipTrapezoidale:
    """Decomposizione: uniforme + triangolare."""

    def test_uniforme_come_caso_speciale(self):
        """Trapezoidale con w_sx=w_dx deve dare stesso risultato di uniforme."""
        w = 3.0
        L = 400.0
        Mi_trap, Mj_trap = mip_trapezoidale(w, w, L)
        Mi_unif, Mj_unif = mip_uniforme(w, L)
        assert Mi_trap == pytest.approx(Mi_unif, rel=1e-6)
        assert Mj_trap == pytest.approx(Mj_unif, rel=1e-6)

    def test_solo_triangolare_crescente(self):
        """w_sx=0, w_dx=w_max → stessa formula triangolare crescente."""
        w_max, L = 4.0, 300.0
        Mi_trap, Mj_trap = mip_trapezoidale(0.0, w_max, L)
        Mi_tri, Mj_tri = mip_triangolare_crescente(w_max, L)
        assert Mi_trap == pytest.approx(Mi_tri, rel=1e-6)
        assert Mj_trap == pytest.approx(Mj_tri, rel=1e-6)

    def test_solo_triangolare_decrescente(self):
        """w_sx=w_max, w_dx=0 → stessa formula triangolare decrescente."""
        w_max, L = 4.0, 300.0
        Mi_trap, Mj_trap = mip_trapezoidale(w_max, 0.0, L)
        Mi_tri, Mj_tri = mip_triangolare_decrescente(w_max, L)
        assert Mi_trap == pytest.approx(Mi_tri, rel=1e-6)
        assert Mj_trap == pytest.approx(Mj_tri, rel=1e-6)


# ==============================================================================
# TEST 4 — mip_triangolare_crescente e decrescente
# ==============================================================================

class TestMipTriangolare:
    """Santarella Tab.9 — triangolare."""

    def test_crescente_formula(self):
        """Triangolare crescente: M_i = -wL²/20, M_j = +wL²/30."""
        w, L = 6.0, 300.0
        Mi, Mj = mip_triangolare_crescente(w, L)
        _check(Mi, -w * L**2 / 20.0, "M_i triangolare crescente")
        _check(Mj, +w * L**2 / 30.0, "M_j triangolare crescente")
        assert Mi < 0 and Mj > 0

    def test_decrescente_formula(self):
        """Triangolare decrescente: M_i = -wL²/30, M_j = +wL²/20."""
        w, L = 6.0, 300.0
        Mi, Mj = mip_triangolare_decrescente(w, L)
        _check(Mi, -w * L**2 / 30.0, "M_i triangolare decrescente")
        _check(Mj, +w * L**2 / 20.0, "M_j triangolare decrescente")
        assert Mi < 0 and Mj > 0

    def test_simmetria_inversa(self):
        """crescente e decrescente sono simmetrici: |Mi_c|=|Mj_d|, |Mj_c|=|Mi_d|."""
        w, L = 5.0, 400.0
        Mi_c, Mj_c = mip_triangolare_crescente(w, L)
        Mi_d, Mj_d = mip_triangolare_decrescente(w, L)
        # Con inversione di segno per simmetria dei casi
        assert abs(Mi_c) == pytest.approx(abs(Mj_d), rel=1e-9)
        assert abs(Mj_c) == pytest.approx(abs(Mi_d), rel=1e-9)


# ==============================================================================
# TEST 5 — mip_cedimento (sway)
# ==============================================================================

class TestMipCedimento:
    """MIP cedimento unitario per correzione sway."""

    def test_formula_6EI_L2(self):
        """M_i = M_j = -6EIδ/L² (entrambi negativi per sway)."""
        E, I, L, delta = 300000.0, 312500.0, 300.0, 1.0
        Mi, Mj = mip_cedimento(delta, E, I, L)
        atteso = -6.0 * E * I * delta / L**2
        _check(Mi, atteso, "M_i cedimento")
        _check(Mj, atteso, "M_j cedimento")
        assert Mi < 0 and Mj < 0  # Entrambi negativi per sway

    def test_proporzionale_a_EI(self):
        """Raddoppiando EI si raddoppia il momento."""
        E, I, L, delta = 200000.0, 100000.0, 200.0, 1.0
        Mi1, _ = mip_cedimento(delta, E, I, L)
        Mi2, _ = mip_cedimento(delta, E, 2 * I, L)
        assert Mi2 == pytest.approx(2 * Mi1, rel=1e-9)


# ==============================================================================
# TEST 6 — mip_momento_nodale
# ==============================================================================

class TestMipMomentoNodale:
    """MIP per momento applicato al nodo."""

    def test_momento_al_nodo_i(self):
        """Momento applicato al nodo i: M_i = M, M_j = M/2 (carry-over 0.5)."""
        M_ext, L = 10000.0, 300.0
        Mi, Mj = mip_momento_nodale(M_ext, al_nodo_i=True, L=L)
        assert Mi == pytest.approx(M_ext, rel=1e-9) or abs(Mi - M_ext) < 1.0
        assert Mj == pytest.approx(M_ext / 2.0, rel=0.01)

    def test_momento_al_nodo_j(self):
        """Momento applicato al nodo j: simmetrico."""
        M_ext, L = 10000.0, 300.0
        Mi, Mj = mip_momento_nodale(M_ext, al_nodo_i=False, L=L)
        assert Mj == pytest.approx(M_ext, rel=1e-9) or abs(Mj - M_ext) < 1.0
        assert Mi == pytest.approx(M_ext / 2.0, rel=0.01)
