"""
Progetto armature per telai piani c.a. — RD 2229/39.

Subfase L.7 del modulo telai piani Cross-Pozzati.
Implementa il workflow storico stile Santarella:
  1. Proposta automatica armatura teorica minima
  2. L'utente modifica / approva / copia da elemento simile
  3. Verifica finale (delegata a verifiche_telaio.py)

Struttura armatura:
  - ArmaturaSezioneSemplice: definita in verifiche_telaio.py (riusata qui)
  - Per ogni asta: 3 sezioni (estremo_i, mezzeria, estremo_j)
  - Catalogo diametri standard storici italiani

Unità di misura:
  - Geometria: cm
  - Aree: cm²
  - Diametri: mm

Riferimento: Santarella "Il Cemento Armato" vol.II; RD 2229/39 Art. 16.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.methods.rd2229.telaio.combinazioni_rd2229 import InviluppoSollecitazioniAsta
from src.methods.rd2229.telaio.modello_telaio import AstaTelaio, ModelloTelaio, TipoAsta
from src.methods.rd2229.telaio.verifiche_telaio import (
    ArmaturaSezioneSemplice,
    N_PILASTRO_KG,
    SIGMA_C_ADM_DEFAULT,
    SIGMA_S_ADM_DEFAULT,
    _MaterialeProxy,
    _SezioneProxy,
    _T_FLESSIONE,
    _T_MINIMI,
    _T_PRESSOFLESSIONE,
    _T_TAGLIO,
    verifica_sezione_ta,
)

# ==============================================================================
# CATALOGO DIAMETRI STANDARD STORICI (mm) — acciaio tondo liscio FeB32k/FeB38k
# ==============================================================================

DIAMETRI_STANDARD_MM: list[float] = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

# Numero barre standard da provare per armatura longitudinale
NUMERO_BARRE_STANDARD: list[int] = [2, 3, 4, 5, 6, 8, 10]

# Passo staffe standard (cm)
PASSI_STAFFE_STANDARD_CM: list[float] = [5, 7.5, 10, 12.5, 15, 20, 25, 30]

# Copriferro nominale (cm)
COPRIFERRO_CM = 3.0

# ==============================================================================
# HELPER — area e capacità flessionale
# ==============================================================================


def _area_barre(n: int, diam_mm: float) -> float:
    """Area totale n barre di diametro diam_mm [cm²]."""
    return n * math.pi * (diam_mm / 10.0) ** 2 / 4.0


def _momento_resistente_rett(
    b_cm: float,
    h_cm: float,
    As_cm2: float,
    sigma_c_adm: float,
    sigma_s_adm: float,
) -> float:
    """Momento resistente TA sezione rettangolare — metodo teorema di Navier.

    Metodo delle tensioni ammissibili (TA):
      n = Es / Ec
      x = posizione asse neutro (iterativa o formula diretta)
      M_R = sigma_s × As × (d - x/3)

    Formula diretta (asse neutro da equilibrio lineare):
      n·As·(d - x) = b·x²/2
      b·x² + 2n·As·x - 2n·As·d = 0
      x = (-n·As + sqrt((n·As)² + 2·b·n·As·d)) / b

    Args:
        b_cm, h_cm: Dimensioni sezione [cm].
        As_cm2: Area armatura tesa [cm²].
        sigma_c_adm, sigma_s_adm: Tensioni ammissibili [kg/cm²].

    Returns:
        M_R [kg·cm] — momento resistente.
    """
    if As_cm2 <= 0 or b_cm <= 0 or h_cm <= 0:
        return 0.0

    d_cm = h_cm - COPRIFERRO_CM

    # Coefficiente di omogeneizzazione n = Es/Ec
    mat = _MaterialeProxy(sigma_c_adm=sigma_c_adm, sigma_s_adm=sigma_s_adm)
    n = mat.n

    # Posizione asse neutro: b·x² + 2n·As·x - 2n·As·d = 0
    nAs = n * As_cm2
    discriminante = nAs**2 + 2.0 * b_cm * nAs * d_cm
    if discriminante < 0:
        return 0.0
    x_cm = (-nAs + math.sqrt(discriminante)) / b_cm

    if x_cm <= 0 or x_cm >= d_cm:
        return 0.0

    # Tensione cls al bordo compresso
    sigma_c = sigma_s_adm / n * x_cm / (d_cm - x_cm)

    # Tensione governante: min tra cls e acciaio
    # (se sigma_c > sigma_c_adm, scala sigma_s)
    if sigma_c > sigma_c_adm:
        # Cls governa → riduce sigma_s
        sigma_s_eff = sigma_c_adm * n * (d_cm - x_cm) / x_cm
    else:
        sigma_s_eff = sigma_s_adm

    M_R = sigma_s_eff * As_cm2 * (d_cm - x_cm / 3.0)
    return M_R


def _momento_resistente_pressoflessione(
    b_cm: float,
    h_cm: float,
    As_inf_cm2: float,
    As_sup_cm2: float,
    N_kg: float,
    sigma_c_adm: float,
    sigma_s_adm: float,
) -> float:
    """Momento resistente approssimato per pressoflessione (metodo elastico TA).

    Approssimazione per progetto armature:
      σ_c = N/A + M/W  ≤  sigma_c_adm
      M_R ≈ (sigma_c_adm - N/A) × W

    Args:
        N_kg: Sforzo normale [kg] (negativo = compressione).

    Returns:
        M_R [kg·cm] (valore assoluto).
    """
    A_cm2 = b_cm * h_cm
    W_cm3 = b_cm * h_cm**2 / 6.0
    sigma_N = abs(N_kg) / A_cm2  # tensione da assiale (sola compressione)
    M_R = max(0.0, (sigma_c_adm - sigma_N)) * W_cm3
    return M_R


def _taglio_resistente_rett(
    b_cm: float,
    h_cm: float,
    Asw_cm2_cm: float,
    sigma_c_adm: float,
    sigma_s_adm: float,
) -> float:
    """Taglio resistente approssimato — formula semplificata RD 2229 Art. 21.

    tau_c0 = sigma_c_adm / 5  (senza staffe)
    tau_c1 = sigma_c_adm / 2  (con staffe)
    V_R = tau_c1 × b × d  (con staffe)

    Args:
        Asw_cm2_cm: Area staffe per unità di lunghezza [cm²/cm].

    Returns:
        V_R [kg].
    """
    d_cm = h_cm - COPRIFERRO_CM
    tau_c1 = sigma_c_adm / 2.0   # kg/cm²
    V_R = tau_c1 * b_cm * d_cm
    return V_R


# ==============================================================================
# CALCOLO ARMATURA TEORICA MINIMA
# ==============================================================================


def _As_minima_flessione(
    b_cm: float,
    h_cm: float,
    M_kgcm: float,
    sigma_c_adm: float,
    sigma_s_adm: float,
) -> float:
    """Area acciaio minima per resistere al momento M [kg·cm].

    Formula inversa del momento resistente TA:
      As = M / (sigma_s × (d - x/3))
    dove (d - x/3) ≈ 0.87·d per un primo tentativo (approx. Santarella).

    Poi viene iterato.

    Returns:
        As_necessaria [cm²].
    """
    if abs(M_kgcm) < 1.0:
        return 0.0

    d_cm = h_cm - COPRIFERRO_CM
    if d_cm <= 0:
        return 0.0

    # Prima approssimazione (braccio della coppia ≈ 0.87·d)
    z_approx = 0.87 * d_cm
    As_0 = abs(M_kgcm) / (sigma_s_adm * z_approx)

    # Raffina con 3 iterazioni
    As = As_0
    for _ in range(3):
        Mr = _momento_resistente_rett(b_cm, h_cm, As, sigma_c_adm, sigma_s_adm)
        if Mr < abs(M_kgcm) and Mr > 0:
            As *= abs(M_kgcm) / Mr * 1.05
        else:
            break

    return As


def _Asw_minima_taglio(
    b_cm: float,
    h_cm: float,
    V_kg: float,
    sigma_c_adm: float,
    sigma_s_adm: float,
) -> float:
    """Area staffe minima per unità di lunghezza [cm²/cm].

    tau = V / (b × d)
    tau_c0 = sigma_c_adm / 5
    Se tau ≤ tau_c0: solo cls regge, staffe minime di progetto
    Altrimenti: Asw = (tau - tau_c0) × b / sigma_s_adm  (approssimazione)

    Returns:
        Asw [cm²/cm].
    """
    if abs(V_kg) < 1.0:
        return 0.0

    d_cm = h_cm - COPRIFERRO_CM
    if d_cm <= 0 or b_cm <= 0:
        return 0.0

    tau = abs(V_kg) / (b_cm * d_cm)
    tau_c0 = sigma_c_adm / 5.0

    if tau <= tau_c0:
        # Solo staffe minime di costruzione
        Asw_min = 0.001 * b_cm  # stima di minimo costruttivo
        return Asw_min

    # Staffe necessarie per la parte eccedente
    Asw = (tau - tau_c0) * b_cm / sigma_s_adm
    return max(Asw, 0.001 * b_cm)


def _sceglie_barre(As_necessaria: float, n_min: int = 2) -> tuple[int, float]:
    """Sceglie combinazione (n_barre, diametro_mm) con area ≥ As_necessaria.

    Criteri di scelta Santarella:
    - Preferisce numero di barre tra 2 e 6
    - Preferisce diametri nell'intervallo 12–22 mm
    - Minimizza eccesso di area (economia)

    Args:
        As_necessaria: Area teorica necessaria [cm²].
        n_min: Numero minimo di barre.

    Returns:
        (n_barre, diam_mm) — combinazione ottimale.
    """
    if As_necessaria <= 0:
        return n_min, 12.0

    migliore = None
    eccesso_min = float("inf")

    for n in NUMERO_BARRE_STANDARD:
        if n < n_min:
            continue
        for d_mm in DIAMETRI_STANDARD_MM:
            As_prov = _area_barre(n, d_mm)
            if As_prov >= As_necessaria:
                eccesso = As_prov - As_necessaria
                # Penalizza eccessi molto grandi e un numero eccessivo di barre
                score = eccesso + 0.5 * n * (d_mm - 12.0) ** 2
                if score < eccesso_min:
                    eccesso_min = score
                    migliore = (n, d_mm)

    if migliore is None:
        # Ultima risorsa: massimo diametro, numero barre crescente
        for n in range(n_min, 16):
            for d_mm in reversed(DIAMETRI_STANDARD_MM):
                if _area_barre(n, d_mm) >= As_necessaria:
                    return n, d_mm
        return 10, 30.0  # fallback

    return migliore


def _sceglie_staffe(Asw_necessaria: float) -> tuple[int, float, float]:
    """Sceglie staffe (n_bracci, diam_mm, passo_cm).

    Criterio: minimizza passo per soddisfare Asw con 2 bracci,
    con diametro standard minimo sufficiente.

    Returns:
        (n_bracci, diam_staffa_mm, passo_cm).
    """
    n_bracci = 2
    for d_mm in DIAMETRI_STANDARD_MM:
        area_1_staffa = math.pi * (d_mm / 10.0) ** 2 / 4.0
        Asw_1_cm = n_bracci * area_1_staffa  # cm² per staffa
        for p_cm in PASSI_STAFFE_STANDARD_CM:
            Asw_prov = Asw_1_cm / p_cm  # cm²/cm
            if Asw_prov >= Asw_necessaria:
                return n_bracci, d_mm, p_cm

    # Fallback con 4 bracci
    n_bracci = 4
    for d_mm in DIAMETRI_STANDARD_MM:
        area_1_staffa = math.pi * (d_mm / 10.0) ** 2 / 4.0
        Asw_1_cm = n_bracci * area_1_staffa
        for p_cm in PASSI_STAFFE_STANDARD_CM:
            Asw_prov = Asw_1_cm / p_cm
            if Asw_prov >= Asw_necessaria:
                return n_bracci, d_mm, p_cm

    return 2, 10.0, 10.0


def calcola_armatura_teorica_minima(
    asta: AstaTelaio,
    M_gov_kgcm: float,
    N_gov_kg: float,
    V_gov_kg: float,
    posizione: str,
) -> ArmaturaSezioneSemplice:
    """Calcola armatura teorica minima per una sezione.

    Algoritmo:
    1. Calcola As necessaria per M_gov (flessione/pressoflessione)
    2. Calcola Asw necessaria per V_gov (taglio)
    3. Sceglie combinazione (n, Ø) ottimale da catalogo standard
    4. Verifica minimi Art. 16 RD 2229/39

    Args:
        asta: Asta telaio con geometria sezione.
        M_gov_kgcm: Momento governante [kg·cm] (valore assoluto).
        N_gov_kg: Sforzo normale governante [kg] (negativo = compressione).
        V_gov_kg: Taglio governante [kg] (valore assoluto).
        posizione: "estremo_i" | "mezzeria" | "estremo_j".

    Returns:
        ArmaturaSezioneSemplice con proposta automatica.
    """
    sez = asta.sezione
    b_cm = sez.b
    h_cm = sez.h
    sigma_c_adm = getattr(sez, "sigma_c_adm", SIGMA_C_ADM_DEFAULT)
    sigma_s_adm = getattr(sez, "sigma_s_adm", SIGMA_S_ADM_DEFAULT)

    A_sez_cm2 = b_cm * h_cm
    e_pilastro = (
        asta.tipo in (TipoAsta.PILASTRO, TipoAsta.SETTO)
        or abs(N_gov_kg) >= N_PILASTRO_KG
    )

    # --- Armatura longitudinale ---
    if e_pilastro:
        # Pressoflessione: As_min = max(As_flessione_equiv, As_minima_pilastro)
        # Per pilastri RD 2229 Art.16: As,min = 0.30% A_sez
        As_min_norma = 0.003 * A_sez_cm2
        As_fless = _As_minima_flessione(b_cm, h_cm, abs(M_gov_kgcm), sigma_c_adm, sigma_s_adm)
        As_necessaria = max(As_fless, As_min_norma)

        # Per pilastri: armatura simmetrica (stessa area inf e sup)
        n_barre, diam_mm = _sceglie_barre(As_necessaria / 2.0, n_min=2)
        n_inf = n_barre
        diam_inf = diam_mm
        n_sup = n_barre
        diam_sup = diam_mm

    else:
        # Trave: As_min = max(As_flessione, As_minima_trave)
        # RD 2229 Art.16: As,min = 0.15% A_sez
        As_min_norma = 0.0015 * A_sez_cm2
        As_necessaria = max(
            _As_minima_flessione(b_cm, h_cm, abs(M_gov_kgcm), sigma_c_adm, sigma_s_adm),
            As_min_norma,
        )

        # Trave: armatura inferiore principale, superiore minima costruttiva
        n_inf, diam_inf = _sceglie_barre(As_necessaria, n_min=2)
        # Armatura superiore ≥ metà inferiore (prassi Santarella)
        As_sup_minima = max(
            0.5 * _area_barre(n_inf, diam_inf),
            0.0015 * A_sez_cm2,
        )
        n_sup, diam_sup = _sceglie_barre(As_sup_minima, n_min=2)

    # --- Staffe ---
    Asw_necessaria = _Asw_minima_taglio(b_cm, h_cm, abs(V_gov_kg), sigma_c_adm, sigma_s_adm)
    n_bracci_st, diam_st, passo_st = _sceglie_staffe(Asw_necessaria)

    # --- Assembla ArmaturaSezioneSemplice ---
    arm = ArmaturaSezioneSemplice(
        id_asta=asta.id,
        posizione=posizione,
        n_inf=n_inf,
        diam_inf_mm=diam_inf,
        n_sup=n_sup,
        diam_sup_mm=diam_sup,
        n_bracci_staffe=n_bracci_st,
        diam_staffa_mm=diam_st,
        passo_staffe_cm=passo_st,
        note=(
            f"Proposta automatica: M={abs(M_gov_kgcm):.0f} kg·cm, "
            f"N={N_gov_kg:.0f} kg, V={abs(V_gov_kg):.0f} kg"
        ),
        modificata_manualmente=False,
    )
    arm.aggiorna_aree()
    return arm


# ==============================================================================
# PROPOSTA AUTOMATICA ARMATURE PER TUTTO IL TELAIO
# ==============================================================================


def proponi_armature_telaio(
    modello: ModelloTelaio,
    inviluppo: dict[int, InviluppoSollecitazioniAsta],
) -> dict[int, dict[str, ArmaturaSezioneSemplice]]:
    """Genera proposta automatica armature per tutte le aste × 3 sezioni.

    Per ogni asta, per ogni sezione:
    - Estrae sollecitazioni governanti dall'inviluppo
    - Chiama calcola_armatura_teorica_minima()

    Args:
        modello: Modello telaio.
        inviluppo: Inviluppo sollecitazioni {id_asta: InviluppoSollecitazioniAsta}.

    Returns:
        Dizionario {id_asta: {"estremo_i": arm, "mezzeria": arm, "estremo_j": arm}}.
    """
    armature: dict[int, dict[str, ArmaturaSezioneSemplice]] = {}

    for id_asta, inv in inviluppo.items():
        asta = modello.asta_by_id(id_asta)
        arm_asta: dict[str, ArmaturaSezioneSemplice] = {}

        posizioni = [
            ("estremo_i", 0),
            ("mezzeria",  1),
            ("estremo_j", 2),
        ]

        for posizione, idx in posizioni:
            # Sollecitazioni governanti per flessione
            M_gov = _gov_M(inv, idx)
            N_gov = _gov_N(inv, idx)
            V_gov = _gov_V(inv, idx)

            arm = calcola_armatura_teorica_minima(
                asta=asta,
                M_gov_kgcm=M_gov,
                N_gov_kg=N_gov,
                V_gov_kg=V_gov,
                posizione=posizione,
            )
            arm_asta[posizione] = arm

        # Uniforma staffe sull'asta (prassi: passo uniforme = il più severo)
        arm_asta = _uniforma_staffe_asta(arm_asta)
        armature[id_asta] = arm_asta

    return armature


def _uniforma_staffe_asta(
    arm_asta: dict[str, ArmaturaSezioneSemplice],
) -> dict[str, ArmaturaSezioneSemplice]:
    """Uniforma le staffe sull'asta: passo = min tra le 3 sezioni.

    In progetto storico le staffe si uniformano per l'intera asta
    (o almeno per zone: zone nodali vs. campata).
    """
    # Trova passo minimo (più severo)
    passo_min = min(
        (arm.passo_staffe_cm for arm in arm_asta.values() if arm.passo_staffe_cm > 0),
        default=15.0,
    )
    diam_max = max(
        (arm.diam_staffa_mm for arm in arm_asta.values()),
        default=8.0,
    )
    n_bracci_max = max(
        (arm.n_bracci_staffe for arm in arm_asta.values()),
        default=2,
    )

    for arm in arm_asta.values():
        arm.passo_staffe_cm = passo_min
        arm.diam_staffa_mm = diam_max
        arm.n_bracci_staffe = n_bracci_max
        arm.aggiorna_aree()

    return arm_asta


# ==============================================================================
# HELPER — estrae sollecitazioni governanti dall'inviluppo
# ==============================================================================


def _gov_M(inv: InviluppoSollecitazioniAsta, idx: int) -> float:
    """Momento governante per sezione idx (da coppia sismica o max assoluto)."""
    M_gov, _N_gov, _combo = inv.M_gov(idx)
    if M_gov != 0.0:
        return M_gov
    # Fallback: max assoluto tra M_max e M_min della sezione
    if idx == 0:
        M_max, M_min = inv.M_max_i, inv.M_min_i
    elif idx == 1:
        M_max, M_min = inv.M_max_m, inv.M_min_m
    else:
        M_max, M_min = inv.M_max_j, inv.M_min_j
    return M_max if abs(M_max) >= abs(M_min) else M_min


def _gov_N(inv: InviluppoSollecitazioniAsta, idx: int) -> float:
    _M_gov, N_gov, _combo = inv.M_gov(idx)
    if N_gov != 0.0:
        return N_gov
    # Fallback: compressione governa per pilastri
    if idx == 0:
        return inv.N_min_i
    elif idx == 1:
        return inv.N_min_m
    else:
        return inv.N_min_j


def _gov_V(inv: InviluppoSollecitazioniAsta, idx: int) -> float:
    return inv.V_gov(idx)


# ==============================================================================
# UTILITÀ — copia armatura tra aste simili
# ==============================================================================


def copia_armatura(
    sorgente: ArmaturaSezioneSemplice,
    destinazioni: list[tuple[int, str]],
    catalogo: dict[int, dict[str, ArmaturaSezioneSemplice]],
) -> dict[int, dict[str, ArmaturaSezioneSemplice]]:
    """Copia l'armatura sorgente nelle sezioni di destinazione.

    Args:
        sorgente: Armatura da copiare.
        destinazioni: Lista di (id_asta, posizione) da sovrascrivere.
        catalogo: Dizionario corrente {id_asta: {posizione: armatura}}.

    Returns:
        Catalogo aggiornato.
    """
    import copy

    for id_asta, posizione in destinazioni:
        nuova = copy.deepcopy(sorgente)
        nuova.id_asta = id_asta
        nuova.posizione = posizione
        nuova.modificata_manualmente = True
        nuova.note = f"Copiata da asta {sorgente.id_asta} / {sorgente.posizione}"
        if id_asta not in catalogo:
            catalogo[id_asta] = {}
        catalogo[id_asta][posizione] = nuova

    return catalogo


# ==============================================================================
# SERIALIZZAZIONE
# ==============================================================================


def serializza_armature(
    armature: dict[int, dict[str, ArmaturaSezioneSemplice]],
) -> list[dict]:
    """Serializza catalogo armature in lista di dict (JSON-friendly)."""
    out = []
    for id_asta, sezioni in armature.items():
        for posizione, arm in sezioni.items():
            out.append(arm.to_dict())
    return out


def deserializza_armature(
    dati: list[dict],
) -> dict[int, dict[str, ArmaturaSezioneSemplice]]:
    """Ricostruisce catalogo armature da lista di dict."""
    catalogo: dict[int, dict[str, ArmaturaSezioneSemplice]] = {}
    for d in dati:
        arm = ArmaturaSezioneSemplice.from_dict(d)
        id_asta = arm.id_asta
        if id_asta not in catalogo:
            catalogo[id_asta] = {}
        catalogo[id_asta][arm.posizione] = arm
    return catalogo


# ==============================================================================
# SCHEDA SANTARELLA — riepilogo per tabulato
# ==============================================================================


@dataclass
class SchedaArmatura:
    """Riepilogo armatura stile Santarella per un'asta."""

    id_asta: int
    etichetta: str
    tipo: str
    b_cm: float
    h_cm: float

    # Dati per sezione: (posizione → dict)
    sezioni: dict[str, dict] = field(default_factory=dict)
    # Chiavi sezione: "estremo_i", "mezzeria", "estremo_j"
    # Valori: {M_gov, N_gov, V_gov, As_inf, As_sup, Asw, diam_inf, diam_sup, ...}

    note: str = ""

    def righe_tabulato(self) -> list[str]:
        """Genera righe testo stile Santarella per il tabulato ASCII."""
        righe = []
        sep = "─" * 100
        righe.append(sep)
        righe.append(
            f"ELEMENTO: {self.etichetta} ({self.tipo})  |  Sezione {self.b_cm:.0f}×{self.h_cm:.0f} cm"
        )
        righe.append(sep)
        intestazione = (
            f"{'Sezione':<14} │ {'M_gov [kg·m]':>14} │ {'N_gov [kg]':>11} │ "
            f"{'As_inf [cm²]':>13} │ {'As_sup [cm²]':>13} │ {'Staffe':>14} │ Esito"
        )
        righe.append(intestazione)
        righe.append("─" * 100)

        nomi = {
            "estremo_i": "Estremo i",
            "mezzeria": "Mezzeria",
            "estremo_j": "Estremo j",
        }

        for posizione in ("estremo_i", "mezzeria", "estremo_j"):
            sez = self.sezioni.get(posizione)
            if sez is None:
                continue
            M_kgm = sez.get("M_gov_kgcm", 0.0) / 100.0  # kg·cm → kg·m
            N_kg = sez.get("N_gov_kg", 0.0)
            As_inf = sez.get("As_inf", 0.0)
            As_sup = sez.get("As_sup", 0.0)
            n_st = sez.get("n_bracci_staffe", 2)
            d_st = sez.get("diam_staffa_mm", 0.0)
            p_st = sez.get("passo_staffe_cm", 0.0)
            ok = sez.get("ok", None)
            esito = "✅" if ok is True else ("❌" if ok is False else "—")
            staffa_str = f"Ø{d_st:.0f}/{p_st:.0f}cm {n_st}br"
            riga = (
                f"{nomi.get(posizione, posizione):<14} │ {M_kgm:>14.0f} │ {N_kg:>11.0f} │ "
                f"{As_inf:>13.2f} │ {As_sup:>13.2f} │ {staffa_str:>14} │ {esito}"
            )
            righe.append(riga)

        if self.note:
            righe.append(f"Note: {self.note}")
        righe.append("")
        return righe


def genera_schede_santarella(
    modello: ModelloTelaio,
    armature: dict[int, dict[str, ArmaturaSezioneSemplice]],
    inviluppo: dict[int, InviluppoSollecitazioniAsta],
    verifiche: dict | None = None,
) -> list[SchedaArmatura]:
    """Genera schede stile Santarella per tutte le aste con armatura.

    Args:
        modello: Modello telaio.
        armature: Catalogo armature.
        inviluppo: Inviluppo sollecitazioni.
        verifiche: (opzionale) risultati verifiche per esito ✅/❌.

    Returns:
        Lista di SchedaArmatura.
    """
    schede = []
    for id_asta, arm_asta in armature.items():
        asta = modello.asta_by_id(id_asta)
        inv = inviluppo.get(id_asta)

        e_pilastro = asta.tipo in (TipoAsta.PILASTRO, TipoAsta.SETTO)
        scheda = SchedaArmatura(
            id_asta=id_asta,
            etichetta=asta.etichetta or f"Asta {id_asta}",
            tipo="pilastro" if e_pilastro else "trave",
            b_cm=asta.sezione.b,
            h_cm=asta.sezione.h,
        )

        for posizione, arm in arm_asta.items():
            idx = {"estremo_i": 0, "mezzeria": 1, "estremo_j": 2}.get(posizione, 0)
            M_gov = _gov_M(inv, idx) if inv else 0.0
            N_gov = _gov_N(inv, idx) if inv else 0.0
            V_gov = _gov_V(inv, idx) if inv else 0.0

            # Esito verifica (se disponibile)
            ok = None
            if verifiche and id_asta in verifiche:
                ris_asta = verifiche[id_asta]
                if hasattr(ris_asta, "sezioni") and posizione in ris_asta.sezioni:
                    ok = ris_asta.sezioni[posizione].ok

            scheda.sezioni[posizione] = {
                "M_gov_kgcm": abs(M_gov),
                "N_gov_kg": N_gov,
                "V_gov_kg": abs(V_gov),
                "As_inf": arm.As_inf,
                "As_sup": arm.As_sup,
                "n_inf": arm.n_inf,
                "diam_inf_mm": arm.diam_inf_mm,
                "n_sup": arm.n_sup,
                "diam_sup_mm": arm.diam_sup_mm,
                "n_bracci_staffe": arm.n_bracci_staffe,
                "diam_staffa_mm": arm.diam_staffa_mm,
                "passo_staffe_cm": arm.passo_staffe_cm,
                "ok": ok,
            }

        schede.append(scheda)

    return schede
