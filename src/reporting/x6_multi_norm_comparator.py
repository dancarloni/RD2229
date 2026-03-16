"""Mappatura check_type → (norma, sezione) per Fase X6.

Fornisce la tabella di raffronto multi-norma (storico vs vigente) per ciascun
tipo di verifica strutturale. Usato da x6_report_pipeline per popolare
``formula_table`` e ``normative_extracts`` quando non forniti dai passi X3-X5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NormRef:
    """Riferimento normativo per un tipo di verifica."""

    norm: str
    section: str
    extract: str
    formula_symbol: str = ""


# ---------------------------------------------------------------------------
# Tabella di mapping: check_type → {norm_key: NormRef}
# ---------------------------------------------------------------------------

_NORM_MAPPING: dict[str, dict[str, NormRef]] = {
    "flessione": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§4.1.2.4",
            extract=(
                "La verifica di resistenza a flessione deve essere condotta verificando che "
                "il momento sollecitante di calcolo Md non superi il momento resistente MRd."
            ),
            formula_symbol="Md ≤ MRd",
        ),
        "DM96": NormRef(
            norm="DM 9/1/96",
            section="§5.3",
            extract=(
                "Per la verifica a flessione con armatura singola: "
                "x/d ≤ 0.259 (acciaio FeB38k); Msd ≤ 0.85·fck·b·d²·ξ·(1-0.4·ξ)."
            ),
            formula_symbol="Msd ≤ 0.85·fck·b·d²",
        ),
        "DM92": NormRef(
            norm="DM 14/02/92",
            section="§2.2",
            extract=(
                "Strutture in c.a.: la verifica a flessione semplice comprende "
                "il calcolo del momento resistente con armatura tesa e compressa."
            ),
            formula_symbol="σ_max ≤ σ_amm",
        ),
        "RD2229": NormRef(
            norm="RD 2229/1939",
            section="Art. 13",
            extract=(
                "Le fibre più compresse del calcestruzzo non devono essere sottoposte "
                "a tensioni superiori a quelle ammissibili. Metodo delle tensioni ammissibili."
            ),
            formula_symbol="σ ≤ σ_amm",
        ),
        "EC2": NormRef(
            norm="EN 1992-1-1",
            section="§6.1",
            extract=(
                "The design value of the applied internal bending moment MEd "
                "shall not exceed the design flexural resistance of the cross-section MRd."
            ),
            formula_symbol="MEd ≤ MRd",
        ),
    },
    "taglio": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§4.1.2.5",
            extract=(
                "La resistenza di calcolo a taglio VRd = min(VRsd, VRcd) deve essere ≥ VEd. "
                "Per membrature senza armatura trasversale specifica: VRd,c = CRd,c·k·(ρl·fck)^(1/3)·bw·d."
            ),
            formula_symbol="VEd ≤ VRd",
        ),
        "DM96": NormRef(
            norm="DM 9/1/96",
            section="§5.4",
            extract=(
                "Verifica a taglio: τ = V/(bw·jd) ≤ τ_amm. "
                "Contributo dell'armatura a taglio: A_st·σ_st/(s·bw) + cotanθ·A_sc·σ_sc."
            ),
            formula_symbol="τ = V/(bw·jd) ≤ τ_amm",
        ),
        "RD2229": NormRef(
            norm="RD 2229/1939",
            section="Art. 14",
            extract=(
                "Le tensioni tangenziali di taglio nel calcestruzzo non devono superare "
                "i valori ammissibili. Gli staffe devono assorbire l'eccesso di taglio."
            ),
            formula_symbol="τ ≤ τ_amm",
        ),
        "EC2": NormRef(
            norm="EN 1992-1-1",
            section="§6.2",
            extract=(
                "Design shear resistance without shear reinforcement: "
                "VRd,c = [CRd,c·k·(100·ρl·fck)^(1/3) + k1·σcp]·bw·d. "
                "Members requiring design shear reinforcement: VEd ≤ VRd,max."
            ),
            formula_symbol="VEd ≤ VRd,c + VRd,s",
        ),
    },
    "deformazione": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§7.2.6",
            extract=(
                "La freccia totale in esercizio non deve superare l/350 (valore totale) "
                "oppure l/500 per la componente successiva al completamento dei tamponamenti."
            ),
            formula_symbol="δ ≤ l/350",
        ),
        "DM96": NormRef(
            norm="DM 9/1/96",
            section="§7.2",
            extract=(
                "La freccia elastica massima non deve superare l/300 "
                "per travi e solai con carichi uniformemente distribuiti."
            ),
            formula_symbol="f ≤ l/300",
        ),
        "EC2": NormRef(
            norm="EN 1992-1-1",
            section="§7.4",
            extract=(
                "Limiting values of maximum calculated deflection for quasi-permanent "
                "loading condition: δ ≤ L/500 per attività di normale esercizio."
            ),
            formula_symbol="δ ≤ L/500",
        ),
    },
    "vibrazioni": {
        "NTC2018": NormRef(
            norm="NTC2018 + Circ. 7/2019",
            section="§C7.10.5",
            extract=(
                "Circ. 7/2019 §C7.10.5 — Verifica dell'accelerazione limite per strutture "
                "soggette a vibrazione da traffico pedonale: a_max ≤ a_lim(f0)."
            ),
            formula_symbol="a_max ≤ a_lim",
        ),
        "EN_ISO_10137": NormRef(
            norm="EN ISO 10137",
            section="§6.4",
            extract=(
                "Bases for design of structures — vibration serviceability. "
                "Admissible acceleration limits in function of natural frequency f0 "
                "and destination of use (offices, residential, footbridges)."
            ),
            formula_symbol="a(f) ≤ a_lim(f)",
        ),
    },
    "punzonamento": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§4.1.2.5",
            extract=(
                "La verifica a punzonamento si conduce lungo il perimetro di controllo "
                "u1 = 2πd + perimetro del pilastro. VEd ≤ VRd,c · u1 · d."
            ),
            formula_symbol="VEd ≤ VRd,c · u1 · d",
        ),
        "EC2": NormRef(
            norm="EN 1992-1-1",
            section="§6.4",
            extract=(
                "Punching shear resistance: vEd = VEd/(u·d) ≤ vRd,c. "
                "Basic control perimeter u1 at 2d from face of loaded area."
            ),
            formula_symbol="vEd ≤ vRd,c",
        ),
    },
    "lc_fc": {
        "NTC2018": NormRef(
            norm="NTC2018 + Circ. 7/2019",
            section="§C8.5.4",
            extract=(
                "Fattori di confidenza FC e indice del livello di conoscenza LC "
                "per strutture esistenti in c.a./acciaio/muratura. "
                "FC dipende da LC1, LC2, LC3 e dalla qualità delle informazioni disponibili."
            ),
            formula_symbol="m_d = m_k / (γM · FC)",
        ),
    },
    "laterocemento": {
        "DM96": NormRef(
            norm="DM 9/1/96",
            section="§7",
            extract=(
                "Calcolo dei solai in laterocemento con nervature e piastra collaborante. "
                "Distribuzione dei momenti sulle nervature parallele. "
                "Verifica della piastra di copertura superiore."
            ),
            formula_symbol="M_sol = M_totale / n_nerv",
        ),
        "RD2229": NormRef(
            norm="RD 2229/1939",
            section="Art. 1",
            extract=(
                "Norme per la esecuzione delle opere in conglomerato cementizio semplice ed armato. "
                "I solai misti in laterizio e c.a. devono rispettare le prescrizioni "
                "sulla sezione resistente equivalente."
            ),
            formula_symbol="σ ≤ σ_amm",
        ),
    },
    "legno": {
        "DM96_legno": NormRef(
            norm="DM 16/1/96",
            section="§4",
            extract=(
                "Strutture di legno — verifiche tensionali con metodo delle tensioni ammissibili. "
                "Tensioni di compressione, trazione e taglio limitate ai valori caratteristici "
                "ridotti dal coefficiente di servizio kmod."
            ),
            formula_symbol="σ ≤ σ_amm_legno",
        ),
    },
    "acciaio": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§4.2",
            extract=(
                "Strutture di acciaio — verifiche SLU: resistenza di sezioni e membrature. "
                "Classe di sezione, resistenza a flessione, taglio, torsione e interazione."
            ),
            formula_symbol="Ed ≤ Rd",
        ),
        "EC3": NormRef(
            norm="EN 1993-1-1",
            section="§6.2",
            extract=(
                "Resistance of cross-sections to bending, shear and combined loading. "
                "For Class 1 and 2 sections: MEd ≤ MRd = Wpl·fy/γM0."
            ),
            formula_symbol="MEd/MRd + VEd/VRd ≤ 1",
        ),
        "DM92": NormRef(
            norm="DM 14/02/92",
            section="§6",
            extract=(
                "Strutture di acciaio — metodo delle tensioni ammissibili. "
                "Le tensioni di snervamento σs non devono superare σ_amm = fy/1.5."
            ),
            formula_symbol="σ ≤ σ_amm = σ_s/1.5",
        ),
    },
    "pressoflessione": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§4.1.2.4",
            extract=(
                "Verifica a pressoflessione con dominio di interazione M-N. "
                "Costruzione del dominio con ascissa NEd e ordinata MEd. "
                "Il punto (NEd, MEd) deve risultare interno al dominio."
            ),
            formula_symbol="(NEd, MEd) nel dominio M-N",
        ),
        "RD2229": NormRef(
            norm="RD 2229/1939",
            section="Art. 15",
            extract=(
                "Sezioni sottoposte a pressoflessione — metodo elastico lineare. "
                "σ_max = N/A ± M·y/I ≤ σ_amm. Per pilastri: verifica di stabilità."
            ),
            formula_symbol="σ_max = N/A ± M·y/I ≤ σ_amm",
        ),
        "EC2": NormRef(
            norm="EN 1992-1-1",
            section="§5.8",
            extract=(
                "Second order effects in slender columns: "
                "design moment MEd includes first order moment and second order effect."
            ),
            formula_symbol="MEd,tot = MEd + M2",
        ),
    },
    "torsione": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§4.1.2.6",
            extract=(
                "Verifica a torsione per membrature in c.a.: effetto combinato di taglio e torsione. "
                "VEd/VRd,max + TEd/TRd,max ≤ 1."
            ),
            formula_symbol="VEd/VRd + TEd/TRd ≤ 1",
        ),
        "RD2229": NormRef(
            norm="RD 2229/1939",
            section="Art. 14",
            extract=(
                "Sollecitazioni torcenti nelle travi inflesse. "
                "Metodo di Saint-Venant per sezioni rettangolari."
            ),
            formula_symbol="τ_max = T·(a+b)·k / (a²·b²)",
        ),
    },
    "aperture": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§7.2.6.2",
            extract=(
                "Ampiezza massima delle fessure: wk ≤ wlim in funzione della classe di esposizione. "
                "Per strutture ordinarie in zona sismica: wk ≤ 0.3 mm (XC2-XC4) o 0.2 mm (XS, XD)."
            ),
            formula_symbol="wk ≤ w_lim",
        ),
        "EC2": NormRef(
            norm="EN 1992-1-1",
            section="§7.3",
            extract=(
                "Crack control: limiting crack width wmax depends on exposure class. "
                "Simplified method using maximum bar diameter or maximum bar spacing."
            ),
            formula_symbol="wk ≤ w_max",
        ),
        "DM96": NormRef(
            norm="DM 9/1/96",
            section="§3.1.4",
            extract=(
                "Limitazione dell'apertura delle fessure: σ_s ≤ 0.6·fyk. "
                "Armatura minima di coesione non inferiore allo 0.2% della sezione."
            ),
            formula_symbol="σ_s ≤ 0.6·fyk",
        ),
    },
    "trazione": {
        "NTC2018": NormRef(
            norm="NTC2018",
            section="§4.1.2.4",
            extract=(
                "Verifica di resistenza a trazione pura: NEd ≤ NRd = As·fyd. "
                "Per elementi misti con calcestruzzo, la trazione è assorbita solo dall'armatura."
            ),
            formula_symbol="NEd ≤ NRd = As·fyd",
        ),
    },
}


# ---------------------------------------------------------------------------
# Interfaccia pubblica
# ---------------------------------------------------------------------------


def get_norm_refs_for(check_type: str) -> dict[str, NormRef]:
    """Restituisce la mappa norma_key → NormRef per il tipo di verifica.

    Args:
        check_type: Tipo di verifica (es. ``"flessione"``, ``"taglio"``).

    Returns:
        Dizionario norma_key → NormRef, oppure dict vuoto se non trovato.
    """
    return dict(_NORM_MAPPING.get(check_type.lower().replace(" ", "_"), {}))


def get_formula_table_entry(check_type: str, norm_code: str) -> dict[str, Any]:
    """Restituisce una voce per ``formula_table`` per tipo e norma.

    Args:
        check_type: Tipo di verifica (es. ``"flessione"``).
        norm_code: Codice della norma primaria (es. ``"NTC2018"``).

    Returns:
        Dizionario compatibile con il contratto X6 ``formula_table``.
    """
    refs = get_norm_refs_for(check_type)
    ref = refs.get(norm_code) or (next(iter(refs.values()), None) if refs else None)
    if ref is None:
        return {
            "sezione": check_type,
            "formula_usata": "N/D",
            "estratto": "",
            "fallback": "N/D",
            "motivo_selezione": "Tipo verifica non nel comparatore X6",
        }
    fallback_ref = next(
        (r for k, r in refs.items() if k != norm_code and r.norm != norm_code),
        None,
    )
    return {
        "sezione": check_type,
        "norma": ref.norm,
        "sezione_normativa": ref.section,
        "formula_usata": f"{ref.norm} {ref.section}: {ref.formula_symbol}",
        "estratto": ref.extract,
        "fallback": (f"{fallback_ref.norm} {fallback_ref.section}" if fallback_ref else "N/D"),
        "motivo_selezione": f"Norma primaria applicabile per {check_type}",
    }


def build_formula_table(check_types: list[str], norm_code: str) -> list[dict[str, Any]]:
    """Costruisce la tabella formule per una lista di verifiche e la norma.

    Args:
        check_types: Lista di tipi di verifica.
        norm_code: Codice della norma (es. ``"NTC2018"``).

    Returns:
        Lista di dict compatibili con il contratto X6 ``formula_table``.
    """
    return [get_formula_table_entry(ct, norm_code) for ct in check_types]


def get_normative_extracts(check_types: list[str], norm_code: str) -> list[str]:
    """Restituisce estratti normativi per una lista di verifiche.

    Args:
        check_types: Lista di tipi di verifica.
        norm_code: Codice della norma (es. ``"NTC2018"``).

    Returns:
        Lista di stringhe ``"Norma §sezione — estratto testuale"``.
    """
    extracts: list[str] = []
    for ct in check_types:
        refs = get_norm_refs_for(ct)
        ref = refs.get(norm_code) or (next(iter(refs.values()), None) if refs else None)
        if ref:
            extracts.append(f"{ref.norm} {ref.section} — {ref.extract}")
    return extracts


def list_all_check_types() -> list[str]:
    """Restituisce tutti i tipi di verifica registrati nel comparatore.

    Returns:
        Lista ordinata dei tipi di verifica (es. ``["acciaio", "aperture", ...]``).
    """
    return sorted(_NORM_MAPPING.keys())


def compare_norms(check_type: str) -> list[dict[str, Any]]:
    """Restituisce una tabella comparativa multi-norma per un tipo di verifica.

    Utile per il report doppia colonna storico/vigente.

    Args:
        check_type: Tipo di verifica (es. ``"flessione"``).

    Returns:
        Lista di dict con campi ``norma``, ``sezione``, ``formula``, ``estratto``.
    """
    refs = get_norm_refs_for(check_type)
    return [
        {
            "norma": ref.norm,
            "sezione": ref.section,
            "formula": ref.formula_symbol,
            "estratto": ref.extract,
        }
        for ref in refs.values()
    ]
