"""Test per src/esistenti/report_esistenti.py — Fase R.6.

Verifica struttura sezioni, contenuto multinorma e audit override.
"""

import pytest

from src.esistenti.report_esistenti import (
    DatiEdificio,
    DatiLC,
    DatiSismici,
    InputReport,
    genera_report_vulnerabilita,
    genera_report_html,
    sezione_intestazione,
    sezione_lc_fc,
    sezione_conclusioni,
    sezione_audit_override,
    sezione_confronto_multinorma,
)


# ─── Fixture ─────────────────────────────────────────────────────────────────

@pytest.fixture
def inp_minimo():
    """Report con soli dati minimi (senza analisi effettive)."""
    return InputReport(
        edificio=DatiEdificio(
            nome="Test Building",
            anno_costruzione="1965",
            tipologia_strutturale="Muratura",
            n_piani=3,
        ),
        lc=DatiLC(livello="LC1", fc=1.35),
        sismici=DatiSismici(ag=0.15, S=1.2, q=2.0, FC=1.35),
        data_report="01/01/2025",
    )


@pytest.fixture
def inp_con_audit():
    inp = InputReport(
        edificio=DatiEdificio(nome="Edificio Audit"),
        lc=DatiLC(livello="LC2", fc=1.15, override_fc=True, fc_originale=1.20),
        data_report="15/03/2025",
    )
    inp.audit_override = [
        {
            "timestamp": "2025-03-15 10:00",
            "campo": "FC",
            "valore_norma": "1.20",
            "valore_override": "1.15",
            "motivo": "Indagine aggiuntiva locale",
        }
    ]
    return inp


# ─── Test genera_report_vulnerabilita ────────────────────────────────────────

class TestGeneraReport:
    def test_report_non_vuoto(self, inp_minimo):
        testo = genera_report_vulnerabilita(inp_minimo)
        assert len(testo) > 100

    def test_contiene_norma_principale(self, inp_minimo):
        testo = genera_report_vulnerabilita(inp_minimo)
        assert "NTC2018" in testo

    def test_contiene_nome_edificio(self, inp_minimo):
        testo = genera_report_vulnerabilita(inp_minimo)
        assert "Test Building" in testo

    def test_contiene_sezione_8_4_1(self, inp_minimo):
        testo = genera_report_vulnerabilita(inp_minimo)
        assert "8.4.1" in testo

    def test_data_report_autogenerata_se_assente(self):
        inp = InputReport(
            edificio=DatiEdificio(nome="Auto Date"),
            lc=DatiLC(),
        )
        testo = genera_report_vulnerabilita(inp)
        assert len(testo) > 0
        assert inp.data_report != ""


# ─── Test sezione_intestazione ────────────────────────────────────────────────

class TestSezioneIntestazione:
    def test_contiene_norma(self, inp_minimo):
        s = sezione_intestazione(inp_minimo)
        assert "NTC2018" in s

    def test_contiene_anno_costruzione(self, inp_minimo):
        s = sezione_intestazione(inp_minimo)
        assert "1965" in s


# ─── Test sezione_lc_fc ──────────────────────────────────────────────────────

class TestSezioneLcFc:
    def test_contiene_fc(self, inp_minimo):
        s = sezione_lc_fc(inp_minimo)
        assert "1.35" in s

    def test_override_segnalato(self, inp_con_audit):
        s = sezione_lc_fc(inp_con_audit)
        assert "OVERRIDE" in s or "override" in s.lower()


# ─── Test sezione_audit_override ─────────────────────────────────────────────

class TestSezioneAudit:
    def test_vuota_se_nessun_override(self, inp_minimo):
        s = sezione_audit_override(inp_minimo)
        assert s == ""

    def test_contiene_campo_modificato(self, inp_con_audit):
        s = sezione_audit_override(inp_con_audit)
        assert "FC" in s

    def test_contiene_motivo(self, inp_con_audit):
        s = sezione_audit_override(inp_con_audit)
        assert "Indagine" in s or "locale" in s.lower()


# ─── Test sezione_confronto_multinorma ───────────────────────────────────────

class TestSezioneMultinorma:
    def test_vuota_se_no_dati(self, inp_minimo):
        s = sezione_confronto_multinorma(inp_minimo)
        assert "non eseguito" in s.lower()

    def test_con_dati_contiene_norma(self):
        inp = InputReport(
            edificio=DatiEdificio(nome="Multi"),
            confronto_norme={
                "α_LV1": {"NTC2018": "0.75", "OPCM3274": "0.68", "EC8": "0.70", "norma_gov": "NTC2018"},
            },
        )
        s = sezione_confronto_multinorma(inp)
        assert "NTC2018" in s
        assert "OPCM3274" in s


# ─── Test genera_report_html ─────────────────────────────────────────────────

class TestGeneraReportHtml:
    def test_output_html_valido(self, inp_minimo):
        html = genera_report_html(inp_minimo)
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_html_no_xss(self):
        """Caratteri speciali HTML devono essere escaped."""
        inp = InputReport(
            edificio=DatiEdificio(nome="<script>alert(1)</script>"),
            lc=DatiLC(),
        )
        html = genera_report_html(inp)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
