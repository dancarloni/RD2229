"""Modello globale muratura LV3 — telaio equivalente semplificato.

Implementa il modello a telaio equivalente (macro-modello) per la distribuzione
del taglio sismico tra i maschi murari, con calcolo analitico di rigidezza
flessionale + taglio per ogni maschio.

Tre modelli selezionabili:
- TELAIO_EQUIVALENTE: maschi come elementi beam-column (default)
- MACRO_ELEMENTO: stiffness ridotta per cracking (placeholder Fase U)
- SOLO_LV2: fallback senza analisi globale (usa solo meccanismi locali)

Placeholder obbligatorio per Fase U (analisi modale non lineare):
- TODO_FASE_U: non implementato; avanzamento da Fase U.
  Il test test_placeholder_fase_u.py fallirà finché non viene completato.

Riferimenti:
- Lagomarsino S. & Cattari S. — TREMURI (2015) — telaio equivalente
- NTC2018 §7.3.3: azioni sismiche e distribuzione verticale
- Circ. 7/2019 §C7.3.3.3: metodo delle forze laterali equivalenti

Unità: cm, kg, kg/cm².
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core.registro_log import registro

_MODULO_LOG = "esistenti.modello_globale_mur"


# ═══════════════════════════════════════════════════════════
#  Enumerazioni
# ═══════════════════════════════════════════════════════════


class TipoModelloGlobale(str, Enum):
    """Tipo di modello globale selezionato dall'utente."""

    TELAIO_EQUIVALENTE = "telaio_equivalente"
    MACRO_ELEMENTO = "macro_elemento"
    SOLO_LV2 = "solo_lv2"


class TipoDomandaSismica(str, Enum):
    """Metodo di calcolo della domanda sismica globale."""

    FORZE_EQUIVALENTI = "forze_equivalenti"  # NTC2018 §7.3.3 — forze statiche eq.
    SPETTRO = "spettro"  # Spettro NTC2018 (modalità futuro Fase U)


# ═══════════════════════════════════════════════════════════
#  Maschio murario (elemento beam del telaio equiv.)
# ═══════════════════════════════════════════════════════════


@dataclass
class MaschioPaino:
    """Maschio murario di un piano — elemento del telaio equivalente.

    Rigidezza combinata:
    K_tot = K_flex × K_taglio / (K_flex + K_taglio)
    dove:
    K_flex = 12·E·I / h³     (flessione, doppio incastro)
    K_taglio = G·A / (χ·h)   (taglio, χ=1.2 per sez. rettang.)

    Riferimento: Lagomarsino (2015), TREMURI manual §3.2.
    """

    id_maschio: str
    piano: int

    # Geometria maschio [cm]
    h: float  # altezza [cm]
    L: float  # lunghezza [cm]
    t: float  # spessore [cm]

    # Proprietà materiale
    E: float = 150_000.0  # modulo elastico [kg/cm²] (tipico muratura mattoni)
    G: float | None = None  # modulo di taglio [kg/cm²] (default E/3)

    # Condizioni al contorno
    # chi: fattore forma taglio (1.2 sezione rettangolare)
    chi: float = 1.2

    # Carichi verticali al maschio
    N: float = 0.0  # [kg]

    # Resistenza (ridotta per FC)
    fvd0: float = 0.0  # [kg/cm²]
    fd: float = 0.0  # [kg/cm²]

    @property
    def G_eff(self) -> float:
        return self.G if self.G is not None else self.E / 3.0

    @property
    def I(self) -> float:
        """Momento di inerzia sezione trasversale [cm⁴]."""
        return self.t * self.L**3 / 12.0

    @property
    def A(self) -> float:
        """Area sezione trasversale [cm²]."""
        return self.L * self.t

    @property
    def rigidezza_flessionale(self) -> float:
        """Rigidezza flessionale K_flex = 12·E·I/h³ [kg/cm]."""
        return 12.0 * self.E * self.I / self.h**3 if self.h > 0 else 0.0

    @property
    def rigidezza_taglio(self) -> float:
        """Rigidezza taglio K_taglio = G·A/(χ·h) [kg/cm]."""
        return self.G_eff * self.A / (self.chi * self.h) if self.h > 0 else 0.0

    @property
    def rigidezza_totale(self) -> float:
        """Rigidezza combinata K = Kf·Kt/(Kf+Kt) [kg/cm]."""
        Kf = self.rigidezza_flessionale
        Kt = self.rigidezza_taglio
        den = Kf + Kt
        return Kf * Kt / den if den > 0 else 0.0

    def capacita_taglio(self) -> float:
        """Capacità a taglio del maschio per scorrimento [kg]."""
        sigma_0 = self.N / self.A if self.A > 0 else 0.0
        return (self.fvd0 + 0.4 * sigma_0) * self.A


@dataclass
class PianoEdificio:
    """Un piano dell'edificio contenente maschi murari."""

    numero: int  # N. piano (1 = piano terra)
    h_piano: float  # altezza interpiano [cm]
    W_piano: float  # peso del piano (solai + muratura) [kg]
    maschi: list[MaschioPaino] = field(default_factory=list)

    @property
    def rigidezza_piano(self) -> float:
        """Rigidezza totale del piano = Σ K_maschi [kg/cm]."""
        return sum(m.rigidezza_totale for m in self.maschi)


# ═══════════════════════════════════════════════════════════
#  Azioni sismiche equivalenti
# ═══════════════════════════════════════════════════════════


def calcola_forze_laterali_equivalenti(
    piani: list[PianoEdificio],
    a_g: float,
    S: float,
    q: float = 2.0,
    FC: float = 1.35,
) -> tuple[float, list[float]]:
    """Forze laterali equivalenti — NTC2018 §7.3.3.

    V_b = S_d(T) × M × λ / q  (taglio alla base)
    F_i = V_b × W_i × z_i / Σ(Wj × zj)  (distribuzione triangolare)

    Per T < 2·TC (standard): S_d(T) ≈ a_g × S × F₀/q (conservative plateau).

    Args:
        piani: piani dell'edificio (dal basso all'alto)
        a_g: accelerazione al suolo [g]
        S: coefficiente stratigrafico
        q: fattore di struttura
        FC: fattore di confidenza

    Returns:
        (V_taglio_base [kg], [F_i per ogni piano] [kg])
    """
    # Altezze cumulate dal basso
    quote: list[float] = []
    q_curr = 0.0
    for piano in piani:
        q_curr += piano.h_piano
        quote.append(q_curr)

    W_tot = sum(p.W_piano for p in piani)
    # S_d(T1) approssimato: plateau a_g × S × F₀ / q (F₀ ≈ 2.5)
    F_0 = 2.5
    S_d = a_g * S * F_0 / q  # [g] — domanda spettrale
    lambda_coeff = 0.85 if len(piani) >= 3 else 1.0  # NTC2018 §7.3.3.2

    V_base = W_tot * S_d * FC * lambda_coeff  # [kg]

    # Distribuzione triangolare (primo modo)
    Wz = [p.W_piano * z for p, z in zip(piani, quote)]
    Wz_tot = sum(Wz) or 1.0
    forze = [V_base * wz / Wz_tot for wz in Wz]

    return V_base, forze


# ═══════════════════════════════════════════════════════════
#  Distribuzione taglio tra maschi per piano
# ═══════════════════════════════════════════════════════════


def distribuisci_taglio_piano(
    piano: PianoEdificio,
    V_piano: float,
) -> dict[str, float]:
    """Distribuisce il taglio sismico tra i maschi del piano.

    Ipotesi: diaframma rigido → spostamento orizzontale uniforme.
    Il taglio è distribuito proporzionalmente alla rigidezza K di ogni maschio.
    F_i = V_piano × K_i / K_tot_piano

    Riferimento: Lagomarsino (2015) §3.3 — distribuzione rigidezza.
    """
    K_tot = piano.rigidezza_piano
    if K_tot <= 0 or not piano.maschi:
        return {m.id_maschio: 0.0 for m in piano.maschi}
    return {m.id_maschio: V_piano * m.rigidezza_totale / K_tot for m in piano.maschi}


# ═══════════════════════════════════════════════════════════
#  Risultati LV3
# ═══════════════════════════════════════════════════════════


@dataclass
class VerificaMaschio:
    """Verifica a taglio del singolo maschio murario."""

    id_maschio: str
    piano: int
    V_Ed: float  # taglio di progetto [kg]
    V_Rd: float  # capacità taglio [kg]
    rho: float  # ρ = V_Rd / V_Ed
    verificato: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_maschio": self.id_maschio,
            "piano": self.piano,
            "V_Ed": round(self.V_Ed, 0),
            "V_Rd": round(self.V_Rd, 0),
            "rho": round(self.rho, 3),
            "verificato": self.verificato,
        }


@dataclass
class RisultatoLV3:
    """Risultato analisi LV3 telaio equivalente."""

    modello: TipoModelloGlobale = TipoModelloGlobale.TELAIO_EQUIVALENTE

    V_taglio_base: float = 0.0  # taglio alla base [kg]
    forze_piano: list[float] = field(default_factory=list)

    verifiche_maschi: list[VerificaMaschio] = field(default_factory=list)

    n_verificati: int = 0
    n_non_verificati: int = 0
    rho_min: float = 0.0
    rho_globale: float = 0.0  # media pesata

    avvisi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "modello": self.modello.value,
            "V_taglio_base": round(self.V_taglio_base, 0),
            "rho_min": round(self.rho_min, 3),
            "rho_globale": round(self.rho_globale, 3),
            "n_verificati": self.n_verificati,
            "n_non_verificati": self.n_non_verificati,
            "avvisi": self.avvisi,
            "verifiche_maschi": [v.to_dict() for v in self.verifiche_maschi],
        }


# ═══════════════════════════════════════════════════════════
#  Analisi LV3 principale
# ═══════════════════════════════════════════════════════════


def analisi_lv3_telaio_equivalente(
    piani: list[PianoEdificio],
    a_g: float,
    S: float,
    q: float = 2.0,
    FC: float = 1.35,
) -> RisultatoLV3:
    """Analisi LV3 con modello a telaio equivalente.

    Sequenza:
    1. Calcola forze laterali equivalenti (NTC2018 §7.3.3)
    2. Distribuisce il taglio di ogni piano tra i maschi per rigidezza
    3. Calcola V_Ed e V_Rd per ogni maschio
    4. Verifica ρ = V_Rd / V_Ed

    Args:
        piani: piani edificio con maschi murari
        a_g, S, q, FC: parametri sismici

    Returns:
        RisultatoLV3 con verifiche per ogni maschio
    """
    avvisi: list[str] = []

    if not piani or not any(p.maschi for p in piani):
        avvisi.append("Nessun maschio murario definito — analisi LV3 non eseguibile")
        return RisultatoLV3(modello=TipoModelloGlobale.TELAIO_EQUIVALENTE, avvisi=avvisi)

    # Forze equivalenti
    V_base, forze = calcola_forze_laterali_equivalenti(piani, a_g, S, q, FC)

    # Taglio cumulato dal top (taglio sul piano i = Σ forze piani ≥ i)
    # Convenz. piani ordinati dal basso (indice 0 = PT)
    n = len(piani)
    tagli_piano: list[float] = [0.0] * n
    for i in range(n - 1, -1, -1):
        tagli_piano[i] = forze[i] + (tagli_piano[i + 1] if i + 1 < n else 0.0)

    # Verifiche maschi
    verifiche: list[VerificaMaschio] = []
    for piano, V_piano in zip(piani, tagli_piano):
        distrib = distribuisci_taglio_piano(piano, V_piano)
        for maschio in piano.maschi:
            V_Ed = distrib.get(maschio.id_maschio, 0.0)
            V_Rd = maschio.capacita_taglio()
            rho = V_Rd / V_Ed if V_Ed > 0 else 9.99
            verifiche.append(
                VerificaMaschio(
                    id_maschio=maschio.id_maschio,
                    piano=piano.numero,
                    V_Ed=V_Ed,
                    V_Rd=V_Rd,
                    rho=rho,
                    verificato=(V_Rd >= V_Ed),
                )
            )

    n_ver = sum(1 for v in verifiche if v.verificato)
    n_nonver = len(verifiche) - n_ver
    rho_vals = [v.rho for v in verifiche]
    rho_min = min(rho_vals) if rho_vals else 0.0
    rho_glob = sum(rho_vals) / len(rho_vals) if rho_vals else 0.0

    if n_nonver > 0:
        avvisi.append(f"ATTENZIONE: {n_nonver} maschi non verificati su {len(verifiche)}")

    ris = RisultatoLV3(
        modello=TipoModelloGlobale.TELAIO_EQUIVALENTE,
        V_taglio_base=V_base,
        forze_piano=forze,
        verifiche_maschi=verifiche,
        n_verificati=n_ver,
        n_non_verificati=n_nonver,
        rho_min=rho_min,
        rho_globale=rho_glob,
        avvisi=avvisi,
    )

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Analisi LV3 telaio equivalente",
        input_dati={
            "n_piani": len(piani),
            "n_maschi": len(verifiche),
            "a_g": a_g,
            "S": S,
            "q": q,
            "FC": FC,
        },
        output_dati={
            "V_taglio_base": round(V_base, 0),
            "rho_min": round(rho_min, 3),
            "n_non_verificati": n_nonver,
        },
        normativa="NTC2018 §7.3.3 + Lagomarsino (2015)",
        formula="K = Kf·Kt/(Kf+Kt); F_i = V×Ki/ΣKj",
        esito="OK" if n_nonver == 0 else "ATTENZIONE",
    )

    return ris


def analisi_lv3(
    piani: list[PianoEdificio],
    a_g: float,
    S: float,
    q: float = 2.0,
    FC: float = 1.35,
    modello: TipoModelloGlobale = TipoModelloGlobale.TELAIO_EQUIVALENTE,
) -> RisultatoLV3:
    """Entry point per analisi LV3 con selezione automatica del modello.

    Se il modello richiesto non è applicabile ai dati forniti,
    effettua fallback automatico con warning tracciato.
    """
    if modello == TipoModelloGlobale.SOLO_LV2:
        return RisultatoLV3(
            modello=TipoModelloGlobale.SOLO_LV2,
            avvisi=["Modello LV3 non richiesto: solo LV2 attivo per questo edificio."],
        )

    if modello == TipoModelloGlobale.MACRO_ELEMENTO:
        # TODO_FASE_U: implementazione macro-elemento avanzata demandata a Fase U.
        # Questo blocco viene RIMOSSO quando Fase U è completata.
        registro.avviso(
            modulo=_MODULO_LOG,
            messaggio=(
                "Modello macro-elemento non ancora implementato (Fase U). "
                "Fallback automatico a telaio equivalente."
            ),
        )
        modello = TipoModelloGlobale.TELAIO_EQUIVALENTE

    # Verifica prerequisiti dati
    if not piani or all(not p.maschi for p in piani):
        return RisultatoLV3(
            modello=modello,
            avvisi=["Dati insufficienti per LV3 (maschi non definiti). Usa LV2."],
        )

    return analisi_lv3_telaio_equivalente(piani, a_g, S, q, FC)


# ═══════════════════════════════════════════════════════════
#  PLACEHOLDER FASE U — da sostituire con implementazione avanzata
# ═══════════════════════════════════════════════════════════


def lv3_analisi_modale_placeholder() -> None:
    """Placeholder per analisi modale non lineare (Fase U).

    NOTA: questa funzione NON deve essere chiamata in produzione finché
    Fase U non è completata. Il test test_placeholder_fase_u.py verifica
    che sollevi NotImplementedError.

    TODO_FASE_U: implementare analisi modale non lineare pushover.
    """
    raise NotImplementedError(
        "LV3 analisi modale non lineare NON ancora implementata. "
        "Completare Fase U (analisi modale) prima di rimuovere questo placeholder. "
        "TODO_FASE_U: sostituire con chiamata a src/analisi_modale/pushover.py"
    )
