"""
Verifiche tensioni ammissibili (TA) per telai piani — RD 2229/39.

Subfase L.6 del modulo telai piani Cross-Pozzati.
Chiama i check esistenti da src/methods/rd2229/checks.py per ogni
asta × 3 sezioni (estremo_i, mezzeria, estremo_j).

Unità di misura interne:
  - Forze:   kg
  - Momenti: kg·cm
  - Geometria: cm
  - Tensioni: kg/cm²

Le funzioni check_* di checks.py usano CalcInput con:
  - N [kN], Mx [kNm], Tx/Ty [kN]  → convertito a kg/kg·cm internamente
  - section.width, section.height [mm]
  - As [cm²], d [cm]
  - material.sigma_c_adm, sigma_s_adm [kg/cm²]

Riferimento: RD 2229/1939 Art. 4, 16, 21; Pozzati vol.II §5.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.core_calculus.contracts import CalcInput, SingleCheckResult, VerificationTemplate
from src.methods.rd2229.checks import (
    check_flessione_ta_rett,
    check_minimi_armatura_ta,
    check_pressoflessione_ta_rett,
    check_taglio_ta_rett,
)
from src.methods.rd2229.telaio.combinazioni_rd2229 import InviluppoSollecitazioniAsta
from src.methods.rd2229.telaio.modello_telaio import AstaTelaio, ModelloTelaio, TipoAsta

if TYPE_CHECKING:
    pass  # placeholder per future importazioni circolari

# ==============================================================================
# COSTANTI MATERIALE DEFAULT (se non specificate nella SezioneTelaio)
# ==============================================================================

# Tensioni ammissibili default RD 2229/39 per calcestruzzo R16
SIGMA_C_ADM_DEFAULT = 80.0  # kg/cm²  (R16: sigma_c28=160, adm=0.5×160)
SIGMA_S_ADM_DEFAULT = 1400.0  # kg/cm²  (acciaio liscio Fe37: ~0.5×2800)

# Copriferro geometrico nominale (cm) per stima altezza utile d
COPRIFERRO_TRAVE_CM = 3.0
COPRIFERRO_PILASTRO_CM = 3.0

# Soglia (kg) sforzo normale per classificare elemento come pilastro
# (equivalente a 50 kN, usato da check_minimi_armatura_ta internamente)
N_PILASTRO_KG = 5100.0

# ==============================================================================
# PROXY INTERNI — adattano SezioneTelaio a interfaccia CalcInput
# ==============================================================================


@dataclass
class _SezioneProxy:
    """Proxy section per CalcInput: espone width/height in mm."""

    b_cm: float  # larghezza [cm]
    h_cm: float  # altezza [cm]

    @property
    def width(self) -> float:
        """Larghezza in mm (interfaccia CalcInput)."""
        return self.b_cm * 10.0

    @property
    def height(self) -> float:
        """Altezza in mm (interfaccia CalcInput)."""
        return self.h_cm * 10.0


@dataclass
class _MaterialeProxy:
    """Proxy materiale per CalcInput: espone sigma_c_adm/sigma_s_adm in kg/cm²."""

    sigma_c_adm: float  # tensione ammissibile cls [kg/cm²]
    sigma_s_adm: float  # tensione ammissibile acciaio [kg/cm²]

    @property
    def sigma_c28(self) -> float:
        """Resistenza caratteristica cls [kg/cm²] (stima: sigma_c_adm / 0.5)."""
        return self.sigma_c_adm / 0.5

    @property
    def Ec(self) -> float:
        """Modulo elastico cls [kg/cm²] (formula empirica storica)."""
        sc28 = self.sigma_c28
        return 550000.0 * sc28 / (sc28 + 200.0)

    @property
    def n(self) -> float:
        """Coefficiente di omogeneizzazione n = Es/Ec."""
        Es = 2.1e6  # kg/cm²
        return Es / self.Ec

    @property
    def sigma_sn(self) -> float:
        """Tensione snervamento nominale acciaio [kg/cm²]."""
        return self.sigma_s_adm / 0.5


# ==============================================================================
# TEMPLATES VerificationTemplate — costruiti una volta sola
# ==============================================================================


def _template_flessione() -> VerificationTemplate:
    return VerificationTemplate(
        template_id="rd2229_ta_flessione_rett",
        norm_code="RD2229",
        verification_type="flessione",
        limit_state="TA",
        description_it="Flessione TA — sezione rettangolare RD 2229/39",
        check_category="resistenza",
    )


def _template_pressoflessione() -> VerificationTemplate:
    return VerificationTemplate(
        template_id="rd2229_ta_pressoflessione_rett",
        norm_code="RD2229",
        verification_type="pressoflessione",
        limit_state="TA",
        description_it="Pressoflessione TA — sezione rettangolare RD 2229/39",
        check_category="resistenza",
    )


def _template_taglio() -> VerificationTemplate:
    return VerificationTemplate(
        template_id="rd2229_ta_taglio_rett",
        norm_code="RD2229",
        verification_type="taglio",
        limit_state="TA",
        description_it="Taglio TA — sezione rettangolare RD 2229/39",
        check_category="resistenza",
    )


def _template_minimi() -> VerificationTemplate:
    return VerificationTemplate(
        template_id="rd2229_ta_minimi_armatura",
        norm_code="RD2229",
        verification_type="minimi_armatura",
        limit_state="TA",
        description_it="Minimi armatura longitudinale — Art. 16 RD 2229/39",
        check_category="minimi_armatura",
    )


# Pre-istanzia per evitare riallocazioni nel loop di verifica
_T_FLESSIONE = _template_flessione()
_T_PRESSOFLESSIONE = _template_pressoflessione()
_T_TAGLIO = _template_taglio()
_T_MINIMI = _template_minimi()

# ==============================================================================
# SCHEMA ARMATURA SEMPLICE
# (def. completa in armature_telaio.py — qui struttura minimale per verifiche)
# ==============================================================================


@dataclass
class ArmaturaSezioneSemplice:
    """Schema armatura per sezione rettangolare storica (Santarella).

    Usato da verifiche_telaio.py e armature_telaio.py.
    """

    id_asta: int
    posizione: str  # "estremo_i" | "mezzeria" | "estremo_j"

    # Armatura longitudinale
    n_inf: int = 0  # numero barre inferiori
    diam_inf_mm: float = 0.0  # diametro [mm]
    n_sup: int = 0  # numero barre superiori
    diam_sup_mm: float = 0.0  # [mm]

    # Aree calcolate (cm²) — auto-aggiornate da aggiorna_aree()
    As_inf: float = 0.0
    As_sup: float = 0.0

    # Staffe
    n_bracci_staffe: int = 2
    diam_staffa_mm: float = 0.0  # [mm]
    passo_staffe_cm: float = 0.0  # [cm]
    Asw_cm2_cm: float = 0.0  # area staffe per unità lunghezza [cm²/cm]

    # Metadati
    note: str = ""
    modificata_manualmente: bool = False

    def aggiorna_aree(self) -> None:
        """Ricalcola As_inf, As_sup, Asw_cm2_cm dalle dimensioni barre."""
        if self.diam_inf_mm > 0 and self.n_inf > 0:
            self.As_inf = self.n_inf * math.pi * (self.diam_inf_mm / 10.0) ** 2 / 4.0
        else:
            self.As_inf = 0.0

        if self.diam_sup_mm > 0 and self.n_sup > 0:
            self.As_sup = self.n_sup * math.pi * (self.diam_sup_mm / 10.0) ** 2 / 4.0
        else:
            self.As_sup = 0.0

        if self.diam_staffa_mm > 0 and self.n_bracci_staffe > 0 and self.passo_staffe_cm > 0:
            area_1_staffa = math.pi * (self.diam_staffa_mm / 10.0) ** 2 / 4.0
            self.Asw_cm2_cm = self.n_bracci_staffe * area_1_staffa / self.passo_staffe_cm
        else:
            self.Asw_cm2_cm = 0.0

    @property
    def As_totale(self) -> float:
        """Area totale armatura longitudinale [cm²]."""
        return self.As_inf + self.As_sup

    def to_dict(self) -> dict:
        return {
            "id_asta": self.id_asta,
            "posizione": self.posizione,
            "n_inf": self.n_inf,
            "diam_inf_mm": self.diam_inf_mm,
            "n_sup": self.n_sup,
            "diam_sup_mm": self.diam_sup_mm,
            "As_inf": self.As_inf,
            "As_sup": self.As_sup,
            "n_bracci_staffe": self.n_bracci_staffe,
            "diam_staffa_mm": self.diam_staffa_mm,
            "passo_staffe_cm": self.passo_staffe_cm,
            "Asw_cm2_cm": self.Asw_cm2_cm,
            "note": self.note,
            "modificata_manualmente": self.modificata_manualmente,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ArmaturaSezioneSemplice:
        a = cls(id_asta=d["id_asta"], posizione=d["posizione"])
        for k, v in d.items():
            if hasattr(a, k):
                setattr(a, k, v)
        return a


# ==============================================================================
# COSTRUZIONE CalcInput DA DATI TELAIO
# ==============================================================================


def _crea_calc_input(
    asta: AstaTelaio,
    M_kgcm: float,
    V_kg: float,
    N_kg: float,
    armatura: ArmaturaSezioneSemplice | None,
    tipo_elemento: str,
) -> CalcInput:
    """Costruisce CalcInput da dati telaio per i check TA.

    Conversioni di unità (telaio → CalcInput):
      M [kg·cm]  → Mx [kNm]  = M / 10197
      N [kg]     → N  [kN]   = N / 101.97
      V [kg]     → Tx [kN]   = V / 101.97
      b, h [cm]  → width, height [mm] (×10)

    Args:
        asta: Asta telaio con sezione e geometria.
        M_kgcm: Momento flettente alla sezione [kg·cm].
        V_kg: Taglio alla sezione [kg].
        N_kg: Sforzo normale alla sezione [kg] (+ trazione, − compressione).
        armatura: Armatura della sezione (opzionale; se None check armatura NON eseguiti).
        tipo_elemento: "trave" o "pilastro" (sovrascrive euristica).

    Returns:
        CalcInput pronto per check_* di checks.py.
    """
    sez = asta.sezione
    b_cm = sez.b
    h_cm = sez.h

    # Materiale proxy
    sigma_c_adm = getattr(sez, "sigma_c_adm", SIGMA_C_ADM_DEFAULT)
    sigma_s_adm = getattr(sez, "sigma_s_adm", SIGMA_S_ADM_DEFAULT)
    materiale = _MaterialeProxy(
        sigma_c_adm=sigma_c_adm,
        sigma_s_adm=sigma_s_adm,
    )

    # Sezione proxy
    sezione = _SezioneProxy(b_cm=b_cm, h_cm=h_cm)

    # Conversione unità
    N_kN = N_kg / 101.97
    Mx_kNm = M_kgcm / 10197.0
    Tx_kN = V_kg / 101.97

    # Armatura
    As_cm2 = None
    As_prime_cm2 = None
    d_cm = None
    d_prime_cm = None
    Asw = None
    diam_st = None
    n_bracci = None
    passo_st = None

    if armatura is not None:
        # Per travi: As tesa = inf (momento positivo) o sup (momento negativo)
        # Per semplicità usiamo il max e il complemento come compresso
        As_cm2 = max(armatura.As_inf, armatura.As_sup)
        As_prime_cm2 = min(armatura.As_inf, armatura.As_sup)
        d_cm = h_cm - COPRIFERRO_TRAVE_CM
        d_prime_cm = COPRIFERRO_PILASTRO_CM
        Asw = armatura.Asw_cm2_cm
        diam_st = armatura.diam_staffa_mm
        n_bracci = armatura.n_bracci_staffe
        passo_st = armatura.passo_staffe_cm

    # Extra info per tipo elemento
    extra: dict[str, Any] = {"element_type": tipo_elemento}

    return CalcInput(
        element_name=f"Asta {asta.id} — {asta.etichetta or asta.tipo.value}",
        section=sezione,
        material=materiale,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=N_kN,
        Mx=Mx_kNm,
        Tx=Tx_kN,
        As=As_cm2,
        As_prime=As_prime_cm2,
        d=d_cm,
        d_prime=d_prime_cm,
        staffe_diametro=diam_st,
        staffe_num_bracci=n_bracci,
        staffe_passo=passo_st,
        extra=extra,
    )


# ==============================================================================
# RISULTATO VERIFICA PER SEZIONE
# ==============================================================================


@dataclass
class RisultatoVerificaSezione:
    """Risultato verifica TA per una singola sezione di un'asta."""

    id_asta: int
    posizione: str  # "estremo_i" | "mezzeria" | "estremo_j"
    M_kgcm: float  # sollecitazione di verifica [kg·cm]
    V_kg: float  # taglio di verifica [kg]
    N_kg: float  # sforzo normale [kg]

    # Risultati check (None se check non eseguito)
    flessione: SingleCheckResult | None = None
    taglio: SingleCheckResult | None = None
    minimi: SingleCheckResult | None = None

    @property
    def ok(self) -> bool:
        """True se tutti i check eseguiti passano."""
        checks = [c for c in (self.flessione, self.taglio, self.minimi) if c is not None]
        return all(c.ok for c in checks)

    @property
    def utilizzazione_max(self) -> float | None:
        """Utilizzazione massima tra i check eseguiti."""
        vals = [
            c.utilisation
            for c in (self.flessione, self.taglio, self.minimi)
            if c is not None and c.utilisation is not None
        ]
        return max(vals) if vals else None

    @property
    def check_governante(self) -> str | None:
        """ID del check con utilizzazione massima."""
        coppie = [
            (c.utilisation, c.template_id)
            for c in (self.flessione, self.taglio, self.minimi)
            if c is not None and c.utilisation is not None
        ]
        if not coppie:
            return None
        return max(coppie, key=lambda x: x[0])[1]

    def to_dict(self) -> dict:
        def _res(c: SingleCheckResult | None) -> dict | None:
            if c is None:
                return None
            return {
                "template_id": c.template_id,
                "ok": c.ok,
                "utilisation": c.utilisation,
                "messages_it": c.messages_it,
                "details": {k: v for k, v in c.details.items()},
            }

        return {
            "id_asta": self.id_asta,
            "posizione": self.posizione,
            "M_kgcm": self.M_kgcm,
            "V_kg": self.V_kg,
            "N_kg": self.N_kg,
            "ok": self.ok,
            "utilizzazione_max": self.utilizzazione_max,
            "check_governante": self.check_governante,
            "flessione": _res(self.flessione),
            "taglio": _res(self.taglio),
            "minimi": _res(self.minimi),
        }


@dataclass
class RisultatoVerificaAsta:
    """Risultato verifiche TA per un'intera asta (3 sezioni)."""

    id_asta: int
    etichetta: str
    tipo: str  # "trave" | "pilastro" | ...
    sezioni: dict[str, RisultatoVerificaSezione] = field(default_factory=dict)
    # chiavi: "estremo_i", "mezzeria", "estremo_j"

    @property
    def ok(self) -> bool:
        return all(s.ok for s in self.sezioni.values())

    @property
    def utilizzazione_max(self) -> float | None:
        vals = [
            s.utilizzazione_max for s in self.sezioni.values() if s.utilizzazione_max is not None
        ]
        return max(vals) if vals else None

    def to_dict(self) -> dict:
        return {
            "id_asta": self.id_asta,
            "etichetta": self.etichetta,
            "tipo": self.tipo,
            "ok": self.ok,
            "utilizzazione_max": self.utilizzazione_max,
            "sezioni": {pos: sez.to_dict() for pos, sez in self.sezioni.items()},
        }


# ==============================================================================
# FUNZIONE PRINCIPALE — verifica per sezione
# ==============================================================================


def verifica_sezione_ta(
    asta: AstaTelaio,
    M_kgcm: float,
    V_kg: float,
    N_kg: float,
    posizione: str,
    armatura: ArmaturaSezioneSemplice | None = None,
) -> RisultatoVerificaSezione:
    """Verifica TA per una singola sezione di un'asta.

    Esegue:
    - Se trave (|N| < N_PILASTRO_KG):  check_flessione_ta_rett
    - Se pilastro (|N| ≥ N_PILASTRO_KG): check_pressoflessione_ta_rett
    - Sempre: check_taglio_ta_rett
    - Se armatura fornita: check_minimi_armatura_ta

    Args:
        asta: Asta telaio.
        M_kgcm: Momento flettente governante [kg·cm].
        V_kg: Taglio governante [kg].
        N_kg: Sforzo normale [kg] (− compressione).
        posizione: "estremo_i" | "mezzeria" | "estremo_j".
        armatura: Armatura sezione (opzionale).

    Returns:
        RisultatoVerificaSezione con tutti i check eseguiti.
    """
    # Classificazione elemento
    e_pilastro = asta.tipo in (TipoAsta.PILASTRO, TipoAsta.SETTO) or abs(N_kg) >= N_PILASTRO_KG
    tipo_elemento = "pilastro" if e_pilastro else "trave"

    risultato = RisultatoVerificaSezione(
        id_asta=asta.id,
        posizione=posizione,
        M_kgcm=M_kgcm,
        V_kg=V_kg,
        N_kg=N_kg,
    )

    # --- Verifica flessione / pressoflessione ---
    if armatura is not None or abs(M_kgcm) > 1.0:
        ci = _crea_calc_input(asta, M_kgcm, V_kg, N_kg, armatura, tipo_elemento)

        if e_pilastro:
            risultato.flessione = check_pressoflessione_ta_rett(ci, _T_PRESSOFLESSIONE)
        else:
            risultato.flessione = check_flessione_ta_rett(ci, _T_FLESSIONE)

    # --- Verifica taglio ---
    if abs(V_kg) > 0.1:
        ci_taglio = _crea_calc_input(asta, M_kgcm, V_kg, N_kg, armatura, tipo_elemento)
        risultato.taglio = check_taglio_ta_rett(ci_taglio, _T_TAGLIO)

    # --- Verifica minimi armatura ---
    if armatura is not None:
        ci_min = _crea_calc_input(asta, M_kgcm, V_kg, N_kg, armatura, tipo_elemento)
        risultato.minimi = check_minimi_armatura_ta(ci_min, _T_MINIMI)

    return risultato


# ==============================================================================
# VERIFICA COMPLETA TELAIO — loop su tutte le aste × 3 sezioni
# ==============================================================================


def verifica_completa_telaio(
    modello: ModelloTelaio,
    inviluppo: dict[int, InviluppoSollecitazioniAsta],
    armature: dict[int, dict[str, ArmaturaSezioneSemplice]] | None = None,
) -> dict[int, RisultatoVerificaAsta]:
    """Esegue le verifiche TA per tutte le aste e le 3 sezioni dell'inviluppo.

    Per ogni asta nell'inviluppo, verifica le 3 sezioni (estremo_i, mezzeria,
    estremo_j) usando le sollecitazioni governanti da InviluppoSollecitazioniAsta.

    Per flessione/pressoflessione usa:
      - M_gov, N_gov (coppia governante dalle combinazioni sismiche)
      - Se non disponibile, usa M_max_abs con il corrispondente N

    Per taglio usa:
      - V_max (valore assoluto massimo tra tutte le combinazioni)

    Args:
        modello: Modello telaio con geometria e sezioni.
        inviluppo: Dizionario {id_asta: InviluppoSollecitazioniAsta}.
        armature: Dizionario {id_asta: {posizione: ArmaturaSezioneSemplice}}.
                  Se None, le verifiche di flessione/taglio vengono eseguite
                  senza armatura (check "senza rinforzo" — solo cls).

    Returns:
        Dizionario {id_asta: RisultatoVerificaAsta}.
    """
    risultati: dict[int, RisultatoVerificaAsta] = {}
    armature = armature or {}

    for id_asta, inv in inviluppo.items():
        asta = modello.asta_by_id(id_asta)
        e_pilastro = asta.tipo in (TipoAsta.PILASTRO, TipoAsta.SETTO)
        tipo_str = "pilastro" if e_pilastro else "trave"

        ris_asta = RisultatoVerificaAsta(
            id_asta=id_asta,
            etichetta=asta.etichetta or f"Asta {id_asta}",
            tipo=tipo_str,
        )

        # Armature per questa asta (se disponibili)
        arm_asta = armature.get(id_asta, {})

        # --- Verifica 3 sezioni ---
        posizioni = [
            ("estremo_i", 0),  # indice sezione 0
            ("mezzeria", 1),  # indice sezione 1
            ("estremo_j", 2),  # indice sezione 2
        ]

        for posizione, idx in posizioni:
            # Sollecitazioni governanti per flessione (coppia M,N)
            M_gov, N_gov = _sollecitazioni_governanti_MN(inv, idx)
            # Taglio massimo assoluto
            V_gov = _taglio_governante(inv, idx)

            arm_sez = arm_asta.get(posizione)

            ris_sez = verifica_sezione_ta(
                asta=asta,
                M_kgcm=M_gov,
                V_kg=V_gov,
                N_kg=N_gov,
                posizione=posizione,
                armatura=arm_sez,
            )
            ris_asta.sezioni[posizione] = ris_sez

        risultati[id_asta] = ris_asta

    return risultati


# ==============================================================================
# HELPER — estrae sollecitazioni governanti dall'inviluppo
# ==============================================================================


def _sollecitazioni_governanti_MN(
    inv: InviluppoSollecitazioniAsta, idx: int
) -> tuple[float, float]:
    """Momento e sforzo normale governanti per la sezione di indice idx.

    Usa la coppia sismica governante (M_gov, N_gov) dalla struttura dati reale.
    Fallback a M_max assoluto se la coppia sismica è nulla.

    Returns:
        (M_kgcm, N_kg) — M con segno, N con segno.
    """
    # Usa il metodo M_gov(sezione) dell'InviluppoSollecitazioniAsta
    M_gov, N_gov, combo = inv.M_gov(idx)
    if M_gov != 0.0:
        return M_gov, N_gov

    # Fallback: M_max assoluto tra M_max_x e M_min_x
    # (M_max_i >= 0, M_min_i <= 0 per convenzione)
    if idx == 0:
        M_max, M_min = inv.M_max_i, inv.M_min_i
        N_max, N_min = inv.N_max_i, inv.N_min_i
    elif idx == 1:
        M_max, M_min = inv.M_max_m, inv.M_min_m
        N_max, N_min = inv.N_max_m, inv.N_min_m
    else:
        M_max, M_min = inv.M_max_j, inv.M_min_j
        N_max, N_min = inv.N_max_j, inv.N_min_j

    if abs(M_min) > abs(M_max):
        return M_min, N_min
    return M_max, N_max


def _taglio_governante(inv: InviluppoSollecitazioniAsta, idx: int) -> float:
    """Taglio massimo assoluto per la sezione di indice idx."""
    return inv.V_gov(idx)


# ==============================================================================
# SEMAFORO ESITO — per GUI e tabulato
# ==============================================================================


def semaforo_asta(ris: RisultatoVerificaAsta) -> str:
    """Restituisce simbolo semaforo per lo stato di verifica dell'asta.

    Returns:
        "✅" se tutte le sezioni passano, "❌" se almeno una fallisce.
    """
    return "✅" if ris.ok else "❌"


def riepilogo_verifiche(
    verifiche: dict[int, RisultatoVerificaAsta],
) -> dict:
    """Riepilogo sintetico verifiche per tabulato o GUI.

    Returns:
        Dict con:
        - n_aste: totale aste verificate
        - n_ok: aste con tutte le sezioni a norma
        - n_ko: aste con almeno una sezione fuori norma
        - utilizzazione_max: massima utilizzazione su tutto il telaio
        - asta_critica: id asta con utilizzazione massima
        - per_asta: {id_asta: {"ok", "utilizzazione_max", "check_governante"}}
    """
    n_ok = sum(1 for r in verifiche.values() if r.ok)
    n_ko = len(verifiche) - n_ok

    # Trova asta critica
    asta_critica = None
    util_max_globale = 0.0
    for id_a, r in verifiche.items():
        u = r.utilizzazione_max
        if u is not None and u > util_max_globale:
            util_max_globale = u
            asta_critica = id_a

    per_asta = {}
    for id_a, r in verifiche.items():
        # Check governante (peggior sezione)
        governa = None
        u_max = 0.0
        for sez in r.sezioni.values():
            if sez.utilizzazione_max is not None and sez.utilizzazione_max > u_max:
                u_max = sez.utilizzazione_max
                governa = sez.check_governante
        per_asta[id_a] = {
            "ok": r.ok,
            "semaforo": semaforo_asta(r),
            "utilizzazione_max": r.utilizzazione_max,
            "check_governante": governa,
        }

    return {
        "n_aste": len(verifiche),
        "n_ok": n_ok,
        "n_ko": n_ko,
        "utilizzazione_max": util_max_globale if asta_critica else None,
        "asta_critica": asta_critica,
        "per_asta": per_asta,
    }
