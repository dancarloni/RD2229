"""Report di valutazione della sicurezza ssmica — NTC2018 §8.4.

Genera il tabulato tecnico professionale in formato testo/HTML con:
- Struttura conforme alle sezioni NTC2018 §8.4
- Tabella comparativa multinorma (NTC2018 > OPCM3274 > EC8 comparativo)
- Tracciabilità completa: formula + clausola + passaggi + output
- Tabella audit override FC/LC
- Ranking interventi pre/post

Riferimenti:
- NTC2018 §8.4: Struttura della relazione di valutazione della sicurezza
- Circ. 7/2019 §C8.4: Contenuti minimi obbligatori relazione

Unità di output: stesse dell'input (kg, cm, kg/cm²).
"""

from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, field
from typing import Any

from src.esistenti.vulnerabilita_ca import IndiceVulnerabilitaCA, RisultatoElementoCA
from src.esistenti.vulnerabilita_mur import IndiceVulnerabilitaMur, RisultatoParete
from src.esistenti.modello_globale_mur import RisultatoLV3
from src.esistenti.interventi import ScenarioIntervento, VoceRanking

_MODULO_LOG = "esistenti.report_esistenti"
_SEP = "─" * 80
_SEP_DOPPIO = "═" * 80
_VERSIONE_REPORT = "1.0.0"


# ═══════════════════════════════════════════════════════════
#  Input report
# ═══════════════════════════════════════════════════════════

@dataclass
class DatiEdificio:
    """Dati descrittivi dell'edificio per la copertina del report."""
    nome: str = ""
    indirizzo: str = ""
    anno_costruzione: str = ""
    tipologia_strutturale: str = ""
    n_piani: int = 0
    superficie_tot_m2: float = 0.0
    proprietario: str = ""
    progettista: str = ""
    data_sopralluogo: str = ""
    note: str = ""


@dataclass
class DatiLC:
    """Dati livello di conoscenza e FC per il report."""
    livello: str = "LC1"       # "LC1" | "LC2" | "LC3"
    fc: float = 1.35
    tipo_rilievo: str = ""
    percentuale_elem_indagati: float | None = None
    note_indagine: str = ""
    override_fc: bool = False  # True se FC è stato sovrascritto manualmente
    fc_originale: float | None = None  # FC da norma (prima dell'override)


@dataclass
class DatiSismici:
    """Parametri sismici usati nell'analisi."""
    ag: float = 0.0      # a_g/g [adim.]
    S: float = 1.0       # coefficiente stratigrafico
    T1: float = 0.0      # periodo fondamentale [s]
    q: float = 2.0       # fattore di struttura
    FC: float = 1.35     # fattore di confidenza
    cat_suolo: str = ""  # "A" | "B" | "C" | "D" | "E"
    zona_sismica: str = ""
    comune: str = ""


@dataclass
class InputReport:
    """Aggregazione di tutti i dati per generare il report di vulnerabilità."""
    edificio: DatiEdificio = field(default_factory=DatiEdificio)
    lc: DatiLC = field(default_factory=DatiLC)
    sismici: DatiSismici = field(default_factory=DatiSismici)

    # Vulnerabilità c.a.
    indice_ca: IndiceVulnerabilitaCA | None = None
    risultati_ca: list[RisultatoElementoCA] = field(default_factory=list)

    # Vulnerabilità muratura
    indice_mur: IndiceVulnerabilitaMur | None = None
    risultati_mur: list[RisultatoParete] = field(default_factory=list)

    # LV3 muratura (se eseguito)
    lv3: RisultatoLV3 | None = None

    # Interventi
    ranking_interventi: list[VoceRanking] = field(default_factory=list)
    scenario_proposto: ScenarioIntervento | None = None

    # Confronto multinorma
    confronto_norme: dict[str, Any] = field(default_factory=dict)

    # Audit override (lista di diz.)
    audit_override: list[dict[str, Any]] = field(default_factory=list)

    # Meta
    data_report: str = ""
    normativa_principale: str = "NTC2018"


# ═══════════════════════════════════════════════════════════
#  Helper formattazione
# ═══════════════════════════════════════════════════════════

def _riga(*args: str, larghezze: list[int] | None = None) -> str:
    """Formatta una riga di tabella a larghezze fisse."""
    if larghezze is None:
        larghezze = [20] * len(args)
    return " | ".join(str(a).ljust(l) for a, l in zip(args, larghezze))


def _intestazione_tabella(colonne: list[str], larghezze: list[int]) -> str:
    return (
        _riga(*colonne, larghezze=larghezze) + "\n"
        + "-+-".join("-" * l for l in larghezze)
    )


# ═══════════════════════════════════════════════════════════
#  Sezioni report
# ═══════════════════════════════════════════════════════════

def sezione_intestazione(inp: InputReport) -> str:
    """Copertina e dati generali — NTC2018 §8.4.1."""
    ed = inp.edificio
    data = inp.data_report or datetime.now().strftime("%d/%m/%Y")

    lines = [
        _SEP_DOPPIO,
        f"  RELAZIONE DI VALUTAZIONE DELLA SICUREZZA SISMICA",
        f"  Norma di riferimento: {inp.normativa_principale}",
        f"  Versione report: {_VERSIONE_REPORT} — Data: {data}",
        _SEP_DOPPIO,
        "",
        "§ 8.4.1 — DATI IDENTIFICATIVI DELL'EDIFICIO",
        _SEP,
        f"  Nome/codice edificio : {ed.nome}",
        f"  Indirizzo            : {ed.indirizzo}",
        f"  Anno di costruzione  : {ed.anno_costruzione}",
        f"  Tipologia strutturale: {ed.tipologia_strutturale}",
        f"  N. piani             : {ed.n_piani}",
        f"  Superficie totale    : {ed.superficie_tot_m2:.0f} m²",
        f"  Proprietario         : {ed.proprietario}",
        f"  Progettista          : {ed.progettista}",
        f"  Data sopralluogo     : {ed.data_sopralluogo}",
    ]
    if ed.note:
        lines.append(f"  Note                 : {ed.note}")
    lines.append("")
    return "\n".join(lines)


def sezione_lc_fc(inp: InputReport) -> str:
    """Livello di conoscenza e fattori di confidenza — NTC2018 §8.5.4."""
    lc = inp.lc

    lines = [
        "§ 8.5.4 — LIVELLO DI CONOSCENZA E FATTORI DI CONFIDENZA",
        _SEP,
        f"  Livello di conoscenza  : {lc.livello}",
        f"  Fattore di confidenza  : FC = {lc.fc:.2f}",
    ]
    if lc.override_fc:
        lines.append(
            f"  ** OVERRIDE FC: valore norma = {lc.fc_originale:.2f} "
            f"→ usato {lc.fc:.2f} (giustificare in nota) **"
        )
    if lc.tipo_rilievo:
        lines.append(f"  Tipo rilievo           : {lc.tipo_rilievo}")
    if lc.percentuale_elem_indagati is not None:
        lines.append(
            f"  % elementi indagati    : {lc.percentuale_elem_indagati:.0f}%"
        )
    if lc.note_indagine:
        lines.append(f"  Note indagini          : {lc.note_indagine}")

    lines += [
        "",
        "  Tabella livelli NTC2018 §8.5.4:",
        "   LC1 → FC = 1.35 (geometria da rilievo; materiali da default norma)",
        "   LC2 → FC = 1.20 (materiali da indagini limitate ≥ 20% elementi)",
        "   LC3 → FC = 1.00 (materiali da indagini estese > 50% elementi)",
        f"  Formula: f_d,eff = f_d / FC = f_d / {lc.fc:.2f}",
        "",
    ]
    return "\n".join(lines)


def sezione_parametri_sismici(inp: InputReport) -> str:
    """Parametri e domanda sismica — NTC2018 §3.2."""
    s = inp.sismici

    lines = [
        "§ 3.2 — PARAMETRI SISMICI",
        _SEP,
        f"  Comune / Zona sismica   : {s.comune} / {s.zona_sismica}",
        f"  Categoria suolo         : {s.cat_suolo}",
        f"  a_g/g                   : {s.ag:.3f}",
        f"  S (fattore stratigrafico): {s.S:.3f}",
        f"  Periodo fondamentale T1 : {s.T1:.3f} s",
        f"  Fattore di struttura q  : {s.q:.2f}",
        f"  Fattore confidenza FC   : {s.FC:.2f}",
        "",
    ]
    return "\n".join(lines)


def sezione_verifiche_ca(inp: InputReport) -> str:
    """Verifiche elementi in c.a. — NTC2018 §8.7.1."""
    if inp.indice_ca is None:
        return "§ 8.7.1 — VERIFICHE C.A.: non eseguita\n\n"

    idx = inp.indice_ca
    lines = [
        "§ 8.7.1 — ANALISI VULNERABILITÀ ELEMENTI IN C.A.",
        _SEP,
        f"  Indice ρ globale (ponderato) : {idx.rho_globale:.3f}",
        f"  ρ minimo (elemento peggiore) : {idx.rho_min_globale:.3f}",
        f"  Classe globale               : {idx.classe.value.upper()}",
        "",
        _intestazione_tabella(
            ["Elemento", "Tipo", "Piano", "ρ_min", "ρ_medio", "Classe"],
            [20, 12, 8, 8, 8, 14],
        ),
    ]
    for r in inp.risultati_ca:
        lines.append(_riga(
            r.id_elemento,
            r.tipo.value,
            getattr(r, "piano", "—"),
            f"{r.rho_min:.3f}",
            f"{r.rho_medio:.3f}",
            r.classe.value,
            larghezze=[20, 12, 8, 8, 8, 14],
        ))

    lines += [
        "",
        f"  RIEPILOGO: {idx.n_verificati} verificati | "
        f"{idx.n_critici} critici | {idx.n_non_verificati} non verificati",
        "",
        "  Elementi più vulnerabili (ρ_min crescente):",
    ]
    for voce in idx.ranking[:5]:
        lines.append(
            f"    [{voce['classe'].upper():14s}] "
            f"{voce['id']} ({voce['tipo']}) → ρ_min = {voce['rho_min']:.3f}"
        )

    lines.append("")
    lines.append(
        "  Riferimento: NTC2018 §8.7.1; formula ρ = C/D; "
        "duttilità θ_u da Circ.7/2019 §C8.7.2.4"
    )
    lines.append("")
    return "\n".join(lines)


def sezione_verifiche_mur(inp: InputReport) -> str:
    """Verifiche muratura — NTC2018 §8.7.1 + Circ. 7/2019."""
    if inp.indice_mur is None:
        return "§ 8.7.1 — VERIFICHE MURATURA: non eseguita\n\n"

    idx = inp.indice_mur
    lines = [
        "§ 8.7.1 — ANALISI VULNERABILITÀ MURATURA (LV1 + LV2)",
        _SEP,
    ]

    if idx.alpha_lv1 is not None:
        lines += [
            f"  LV1 ({idx.formula_lv1}): α = {idx.alpha_lv1:.3f}",
            f"  → {'VERIFICATO' if idx.alpha_lv1 >= 1.0 else 'NON VERIFICATO (LV1)'}",
            "",
        ]

    lines += [
        f"  LV2 — α globale minimo  : {idx.alpha_min_globale:.3f}",
        f"  LV2 — α globale medio   : {idx.alpha_medio_globale:.3f}",
        f"  Classe globale          : {idx.classe.value.upper()}",
        "",
        _intestazione_tabella(
            ["Parete", "Piano", "α_min", "α_medio", "Mec. critico", "Classe"],
            [20, 8, 8, 8, 22, 14],
        ),
    ]
    for r in inp.risultati_mur:
        lines.append(_riga(
            r.id_parete,
            "—",
            f"{r.alpha_min:.3f}",
            f"{r.alpha_medio:.3f}",
            r.meccanismo_critico[:22] if r.meccanismo_critico else "—",
            r.classe.value,
            larghezze=[20, 8, 8, 8, 22, 14],
        ))

    lines += [
        "",
        f"  RIEPILOGO: {idx.n_verificate} verificate | "
        f"{idx.n_critiche} critiche | {idx.n_vulnerabili} vulnerabili",
        "",
        "  Pareti più vulnerabili (α_min crescente):",
    ]
    for voce in idx.ranking[:5]:
        lines.append(
            f"    [{voce['classe'].upper():14s}] "
            f"{voce['id']} → α_min = {voce['alpha_min']:.3f} "
            f"(mec. critico: {voce['meccanismo_critico']})"
        )
    lines += [
        "",
        "  Riferimento: Circ. 7/2019 §C8A.4.1; formula α = a₀*/a_domanda",
        "  Scorrimento: Mohr-Coulomb R_hor = fvd0·A + μ·N (Circ. §C8A.4.1)",
        "",
    ]
    return "\n".join(lines)


def sezione_lv3(inp: InputReport) -> str:
    """Modello globale LV3 — Lagomarsino (2015) + NTC2018 §7.3.3."""
    if inp.lv3 is None:
        return "§ LV3 — ANALISI GLOBALE MURATURA: non eseguita\n\n"

    lv3 = inp.lv3
    lines = [
        "§ LV3 — MODELLO GLOBALE MURATURA",
        _SEP,
        f"  Modello                : {lv3.modello.value}",
        f"  Taglio alla base V_b   : {lv3.V_taglio_base:.0f} kg",
        f"  ρ globale maschi       : {lv3.rho_globale:.3f}",
        f"  ρ minimo maschio       : {lv3.rho_min:.3f}",
        f"  Maschi verificati      : {lv3.n_verificati} / {lv3.n_verificati + lv3.n_non_verificati}",
    ]
    for av in lv3.avvisi:
        lines.append(f"  [!] {av}")
    lines += [
        "",
        "  Riferimento: Lagomarsino & Cattari (2015) TREMURI; NTC2018 §7.3.3",
        "  Rigidezza: K = Kf·Kt/(Kf+Kt) con Kf = 12EI/h³, Kt = GA/(χh)",
        "",
    ]
    return "\n".join(lines)


def sezione_confronto_multinorma(inp: InputReport) -> str:
    """Tabella comparativa risultati NTC2018 / OPCM3274 / EC8."""
    if not inp.confronto_norme:
        return "§ CONFRONTO MULTINORMA: non eseguito\n\n"

    cf = inp.confronto_norme
    lines = [
        "§ CONFRONTO RISULTATI MULTINORMA",
        _SEP,
        "  Priorità risultati: NTC2018 > OPCM 3274/2003 > EC8 — EN 1998",
        "",
        _intestazione_tabella(
            ["Indicatore", "NTC2018", "OPCM3274", "EC8 (comp.)", "Norma gov."],
            [22, 12, 12, 12, 12],
        ),
    ]
    for nome, valori in cf.items():
        lines.append(_riga(
            nome,
            str(valori.get("NTC2018", "—")),
            str(valori.get("OPCM3274", "—")),
            str(valori.get("EC8", "—")),
            str(valori.get("norma_gov", "NTC2018")),
            larghezze=[22, 12, 12, 12, 12],
        ))
    lines.append("")
    return "\n".join(lines)


def sezione_interventi(inp: InputReport) -> str:
    """Strategie di intervento e scenario post — NTC2018 §8.4.3."""
    lines = ["§ 8.4.3 — STRATEGIE DI MIGLIORAMENTO/ADEGUAMENTO SISMICO", _SEP]

    if inp.ranking_interventi:
        lines += [
            "  Ranking interventi (ordine: migliore rapporto miglioramento/costo):",
            "",
            _intestazione_tabella(
                ["#", "Intervento", "Δρ%", "Δα%", "Costo (EUR)", "Score"],
                [3, 30, 7, 7, 12, 8],
            ),
        ]
        for i, voce in enumerate(inp.ranking_interventi[:8], 1):
            lines.append(_riga(
                str(i),
                voce.nome[:30],
                f"{voce.scenario.delta_rho_perc:+.1f}%",
                f"{voce.scenario.delta_alpha_perc:+.1f}%",
                f"€ {voce.scenario.costo_totale_eur:.0f}",
                f"{voce.score:.2f}",
                larghezze=[3, 30, 7, 7, 12, 8],
            ))
        lines.append("")

    if inp.scenario_proposto is not None:
        sc = inp.scenario_proposto
        lines += [
            "  Scenario proposto:",
            f"    Interventi combinati : {', '.join(sc.interventi_applicati)}",
            f"    ρ prima / dopo       : {sc.rho_pre:.3f} → {sc.rho_post:.3f} "
            f"({sc.delta_rho_perc:+.1f}%)",
            f"    α prima / dopo       : {sc.alpha_pre:.3f} → {sc.alpha_post:.3f} "
            f"({sc.delta_alpha_perc:+.1f}%)",
            f"    Costo stimato        : € {sc.costo_totale_eur:.0f}",
        ]
        if sc.cap_raggiunto:
            lines.append("    [!] Cap moltiplicativo attivato su almeno un indice.")
        for nota in sc.note:
            lines.append(f"    [!] {nota}")
        lines.append("")

    lines.append(
        "  Riferimenti: NTC2018 §8.4.3 — Miglioramento e adeguamento sismico;\n"
        "  Dolce et al. (2017) — Database interventi sismici; RELUIS (2019)"
    )
    lines.append("")
    return "\n".join(lines)


def sezione_audit_override(inp: InputReport) -> str:
    """Tabella audit degli override FC/LC — tracciabilità decisioni."""
    if not inp.audit_override:
        return ""

    lines = [
        "§ AUDIT OVERRIDE — DECISIONI MANUALI",
        _SEP,
        "  Le seguenti impostazioni sono state modificate manualmente rispetto ai valori",
        "  prescritti dalla norma. Ogni modifica deve essere giustificata nella relazione.",
        "",
        _intestazione_tabella(
            ["Data/Ora", "Campo", "Valore norma", "Valore usato", "Motivo"],
            [18, 15, 13, 13, 25],
        ),
    ]
    for ov in inp.audit_override:
        lines.append(_riga(
            str(ov.get("timestamp", ""))[:18],
            str(ov.get("campo", ""))[:15],
            str(ov.get("valore_norma", ""))[:13],
            str(ov.get("valore_override", ""))[:13],
            str(ov.get("motivo", ""))[:25],
            larghezze=[18, 15, 13, 13, 25],
        ))
    lines.append("")
    return "\n".join(lines)


def sezione_conclusioni(inp: InputReport) -> str:
    """Conclusioni e classificazione finale — NTC2018 §8.4.5."""
    lines = ["§ 8.4.5 — CONCLUSIONI E CLASSIFICAZIONE", _SEP]

    if inp.indice_ca is not None:
        lines.append(
            f"  Vulnerabilità c.a.  : ρ = {inp.indice_ca.rho_min_globale:.3f} "
            f"({inp.indice_ca.classe.value.upper()})"
        )
    if inp.indice_mur is not None:
        lines.append(
            f"  Vulnerabilità mur.  : α = {inp.indice_mur.alpha_min_globale:.3f} "
            f"({inp.indice_mur.classe.value.upper()})"
        )
    if inp.scenario_proposto is not None:
        sc = inp.scenario_proposto
        lines += [
            "",
            f"  Con interventi proposti:",
            f"    ρ_post = {sc.rho_post:.3f}  (era {sc.rho_pre:.3f})",
            f"    α_post = {sc.alpha_post:.3f}  (era {sc.alpha_pre:.3f})",
        ]
        lines.append(
            "  Il miglioramento proposto "
            + ("SUPERA" if sc.rho_post >= 1.0 and sc.alpha_post >= 1.0
               else "NON raggiunge")
            + " il livello di adeguamento (C/D ≥ 1.0)."
        )

    lines += [
        "",
        _SEP_DOPPIO,
        "  Fine relazione.",
        _SEP_DOPPIO,
        "",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
#  Generazione report completo
# ═══════════════════════════════════════════════════════════

def genera_report_vulnerabilita(inp: InputReport) -> str:
    """Genera il report completo di vulnerabilità sismica in formato testo.

    Il report è conforme alla struttura NTC2018 §8.4 (§8.4.1 – §8.4.5).

    Args:
        inp: dati aggregati per il report

    Returns:
        Stringa con report completo (testo ASCII con tabelle allineate)
    """
    if not inp.data_report:
        inp.data_report = datetime.now().strftime("%d/%m/%Y")

    sezioni = [
        sezione_intestazione(inp),
        sezione_lc_fc(inp),
        sezione_parametri_sismici(inp),
        sezione_verifiche_ca(inp),
        sezione_verifiche_mur(inp),
        sezione_lv3(inp),
        sezione_confronto_multinorma(inp),
        sezione_interventi(inp),
        sezione_audit_override(inp),
        sezione_conclusioni(inp),
    ]
    return "\n".join(sezioni)


def genera_report_html(inp: InputReport) -> str:
    """Genera il report in formato HTML semplice.

    Wrappa il testo ASCII in un documento HTML con font monospace
    per preservare l'allineamento.
    """
    testo = genera_report_vulnerabilita(inp)
    testo_escaped = (
        testo
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"it\">\n"
        "<head><meta charset=\"UTF-8\">"
        "<title>Report Vulnerabilità Sismica</title>\n"
        "<style>"
        "body{font-family:monospace;white-space:pre;margin:2em;background:#fff;color:#111;}"
        "h1{font-size:1.0em;}"
        "</style></head>\n"
        "<body>\n"
        + testo_escaped
        + "\n</body></html>"
    )
