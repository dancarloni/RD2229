"""Adapter centralizzato per conversioni di unità di misura nel motore di calcolo.

Questo modulo è la **unica fonte di verità** per tutte le conversioni di unità
nel motore di calcolo di RD2229. Tutti i moduli di verifica devono importare
le funzioni di conversione da qui, evitando duplicazione e inconsistenze.

Standard interno del motore di calcolo
---------------------------------------
- **Tensioni / Resistenze**: MPa (N/mm²) — sistema SI moderno
- **Geometria**: cm
- **Forze**: kN
- **Momenti**: kN·m

Compatibilità con codici storici (TA)
----------------------------------------
Il metodo delle Tensioni Ammissibili (TA) — RD2229, DM92, DM96 — opera
internamente in kg/cm². Le funzioni ``*_ta`` di questo modulo gestiscono
la conversione trasparente tra MPa (standard interno) e kg/cm² (TA).

Fattore di conversione esatto:
    1 kg/cm² = 0.0980665 MPa  (per definizione da g_n = 9.80665 m/s²)
    1 MPa    = 1 / 0.0980665 = 10.19716 kg/cm²

Utilizzo::

    from src.core.adapter_unita_misura import (
        mpa_to_kg_cm2,
        kg_cm2_to_mpa,
        get_fck_mpa,
        get_fyk_mpa,
        get_sigma_c_adm_kg_cm2,
        ensure_mpa,
    )

    # Conversioni base
    sigma_ta = mpa_to_kg_cm2(25.0)    # 25 MPa → 254.93 kg/cm²
    sigma_si = kg_cm2_to_mpa(100.0)   # 100 kg/cm² → 9.807 MPa

    # Lettura proprietà materiale normalizzata a MPa
    fck = get_fck_mpa(materiale)       # Sempre in MPa, indipendente dalla sorgente
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ==============================================================================
# COSTANTI DI CONVERSIONE
# ==============================================================================

#: Fattore di conversione esatto: 1 kg/cm² = g_n / 10000 MPa
#: g_n = 9.80665 m/s² (valore SI ufficiale per accelerazione di gravità standard)
_KG_CM2_TO_MPA: float = 0.0980665

#: Fattore inverso: 1 MPa = 10.19716... kg/cm²
_MPA_TO_KG_CM2: float = 1.0 / _KG_CM2_TO_MPA  # ≈ 10.19716

#: Precisione minima richiesta per confronti (4 decimali)
_PRECISIONE_DECIMALI: int = 4


# ==============================================================================
# FUNZIONI BASE DI CONVERSIONE
# ==============================================================================


def mpa_to_kg_cm2(mpa: float) -> float:
    """Converte una tensione da MPa a kg/cm².

    Conversione: σ [kg/cm²] = σ [MPa] / 0.0980665

    Parametri
    ----------
    mpa : float
        Tensione in MPa (N/mm²).

    Restituisce
    -----------
    float
        Tensione equivalente in kg/cm², arrotondata a 4 decimali.

    Esempi
    ------
    >>> mpa_to_kg_cm2(9.80665)
    100.0
    >>> mpa_to_kg_cm2(25.0)
    254.929...
    """
    return round(mpa * _MPA_TO_KG_CM2, _PRECISIONE_DECIMALI)


def kg_cm2_to_mpa(kg_cm2: float) -> float:
    """Converte una tensione da kg/cm² a MPa.

    Conversione: σ [MPa] = σ [kg/cm²] × 0.0980665

    Parametri
    ----------
    kg_cm2 : float
        Tensione in kg/cm².

    Restituisce
    -----------
    float
        Tensione equivalente in MPa, arrotondata a 4 decimali.

    Esempi
    ------
    >>> kg_cm2_to_mpa(100.0)
    9.8067
    >>> kg_cm2_to_mpa(254.9294)
    25.0
    """
    return round(kg_cm2 * _KG_CM2_TO_MPA, _PRECISIONE_DECIMALI)


def round_trip_mpa_kg_cm2(valore_mpa: float) -> float:
    """Verifica la precisione del round-trip MPa → kg/cm² → MPa.

    Utile nei test per verificare che la conversione doppia non introduca
    errori superiori alla precisione richiesta (4 decimali).

    Parametri
    ----------
    valore_mpa : float
        Valore di partenza in MPa.

    Restituisce
    -----------
    float
        Valore in MPa dopo round-trip (deve coincidere con l'ingresso).
    """
    return kg_cm2_to_mpa(mpa_to_kg_cm2(valore_mpa))


# ==============================================================================
# LETTURA NORMALIZZATA DA OGGETTI MATERIALE
# ==============================================================================


def get_fck_mpa(materiale: Any) -> float | None:
    """Estrae f_ck dal materiale, garantendo il risultato in MPa.

    Il catalogo interno di RD2229 può memorizzare f_ck in kg/cm² (sistema
    storico) o in MPa (sistema SI). Questa funzione rileva automaticamente
    l'unità in base alla grandezza del valore e restituisce sempre MPa.

    Logica di rilevamento automatico dell'unità:
    - f_ck > 200 → presumibilmente kg/cm² (valori tipici: 150–500 kg/cm²)
    - f_ck ≤ 200 → presumibilmente MPa (valori tipici: 12–90 MPa per calcestruzzo normale)

    Nota: la soglia 200 è convenzionale. C200/245 (f_ck=200 MPa) non esiste
    in pratica; il calcestruzzo strutturale ordinario non supera C90/105 (f_ck=90 MPa).

    Parametri
    ----------
    materiale : Any
        Oggetto materiale con attributo ``f_ck``.

    Restituisce
    -----------
    float | None
        f_ck in MPa, oppure ``None`` se il campo non è disponibile o zero.
    """
    f_ck_raw = getattr(materiale, "f_ck", None)
    if f_ck_raw is None or f_ck_raw == 0:
        return None

    if f_ck_raw > 200.0:
        # Probabilmente in kg/cm² — converti a MPa
        f_ck_mpa = kg_cm2_to_mpa(f_ck_raw)
        logger.debug(
            "get_fck_mpa: f_ck=%.1f interpretato come kg/cm² → %.4f MPa",
            f_ck_raw,
            f_ck_mpa,
        )
        return f_ck_mpa
    else:
        # Già in MPa
        return float(f_ck_raw)


def get_fyk_mpa(materiale: Any) -> float | None:
    """Estrae f_yk dal materiale, garantendo il risultato in MPa.

    Applica la stessa logica di rilevamento automatico dell'unità di ``get_fck_mpa``.
    L'acciaio da c.a. ha tipicamente f_yk nell'intervallo 240–500 MPa, oppure
    2400–5000 kg/cm². La soglia di discriminazione è 1000.

    Parametri
    ----------
    materiale : Any
        Oggetto materiale con attributo ``f_yk``.

    Restituisce
    -----------
    float | None
        f_yk in MPa, oppure ``None`` se non disponibile.
    """
    f_yk_raw = getattr(materiale, "f_yk", None)
    if f_yk_raw is None or f_yk_raw == 0:
        return None

    if f_yk_raw > 1000.0:
        # Probabilmente in kg/cm² — converti a MPa
        f_yk_mpa = kg_cm2_to_mpa(f_yk_raw)
        logger.debug(
            "get_fyk_mpa: f_yk=%.1f interpretato come kg/cm² → %.4f MPa",
            f_yk_raw,
            f_yk_mpa,
        )
        return f_yk_mpa
    else:
        return float(f_yk_raw)


def get_rck_kg_cm2(materiale: Any) -> float | None:
    """Estrae Rck (resistenza cubica) in kg/cm² dal materiale.

    Cerca nei seguenti attributi, in ordine di priorità:
    1. ``sigma_c28`` — usato nei cataloghi RD2229/DM92 (già in kg/cm²)
    2. ``Rck_kg_cm2`` — campo legacy esplicito in kg/cm²
    3. ``Rck`` — assume kg/cm² se > 20, MPa altrimenti
    4. ``f_ck`` — via ``get_fck_mpa()`` con conversione inversa

    Parametri
    ----------
    materiale : Any
        Oggetto materiale.

    Restituisce
    -----------
    float | None
        Rck in kg/cm², oppure ``None`` se non determinabile.
    """
    # 1. sigma_c28 (cataloghi storici RD2229/DM92)
    sigma_c28 = getattr(materiale, "sigma_c28", None)
    if sigma_c28 and sigma_c28 > 0:
        return float(sigma_c28)

    # 2. Rck_kg_cm2 (campo legacy esplicito)
    rck_legacy = getattr(materiale, "Rck_kg_cm2", None)
    if rck_legacy and rck_legacy > 0:
        return float(rck_legacy)

    # 3. Rck generico — rileva unità dalla grandezza
    rck = getattr(materiale, "Rck", None)
    if rck and rck > 0:
        if rck > 20.0:
            return float(rck)  # Assumo già kg/cm²
        else:
            return mpa_to_kg_cm2(rck)  # Converti da MPa

    # 4. Stima da f_ck: Rck ≈ f_ck / 0.83
    f_ck_mpa = get_fck_mpa(materiale)
    if f_ck_mpa is not None:
        rck_mpa = f_ck_mpa / 0.83  # Relazione approssimata f_ck = 0.83 × Rck
        return mpa_to_kg_cm2(rck_mpa)

    return None


def get_sigma_c_adm_kg_cm2(materiale: Any) -> float | None:
    """Estrae la tensione ammissibile a compressione del calcestruzzo in kg/cm².

    Usata per le verifiche TA (Tensioni Ammissibili) secondo RD2229/DM92/DM96.

    Cerca nei seguenti attributi:
    1. ``sigma_c_adm`` — campo diretto in kg/cm² (cataloghi storici)
    2. ``sigma_c_adm_kg_cm2`` — campo esplicito in kg/cm²
    3. Stima da Rck: σ_c_adm ≈ 0.30 × Rck [kg/cm²] (DM92 §5.2.1)

    Parametri
    ----------
    materiale : Any
        Oggetto materiale.

    Restituisce
    -----------
    float | None
        σ_c_adm in kg/cm², oppure ``None`` se non determinabile.
    """
    # 1. Campo diretto sigma_c_adm
    sigma_c_adm = getattr(materiale, "sigma_c_adm", None)
    if sigma_c_adm and sigma_c_adm > 0:
        return float(sigma_c_adm)

    # 2. Campo esplicito con suffisso unità
    sigma_c_adm_explicit = getattr(materiale, "sigma_c_adm_kg_cm2", None)
    if sigma_c_adm_explicit and sigma_c_adm_explicit > 0:
        return float(sigma_c_adm_explicit)

    # 3. Stima da Rck: formula DM92 §5.2.1
    rck = get_rck_kg_cm2(materiale)
    if rck is not None:
        sigma_stima = 0.30 * rck
        logger.debug(
            "get_sigma_c_adm_kg_cm2: stima da Rck=%.1f → σ_c_adm=%.2f kg/cm²",
            rck,
            sigma_stima,
        )
        return sigma_stima

    return None


def get_sigma_s_adm_kg_cm2(materiale: Any) -> float | None:
    """Estrae la tensione ammissibile dell'acciaio in kg/cm².

    Usata per le verifiche TA secondo RD2229/DM92/DM96.

    Formula DM92: σ_s_adm = min(2/3 × σ_sn, 2600) kg/cm²
    dove σ_sn è la tensione nominale di snervamento.

    Parametri
    ----------
    materiale : Any
        Oggetto materiale.

    Restituisce
    -----------
    float | None
        σ_s_adm in kg/cm², oppure ``None`` se non determinabile.
    """
    # 1. Campo diretto
    sigma_s_adm = getattr(materiale, "sigma_s_adm", None)
    if sigma_s_adm and sigma_s_adm > 0:
        return float(sigma_s_adm)

    # 2. Campo esplicito con suffisso unità
    sigma_s_adm_explicit = getattr(materiale, "sigma_s_adm_kg_cm2", None)
    if sigma_s_adm_explicit and sigma_s_adm_explicit > 0:
        return float(sigma_s_adm_explicit)

    # 3. sigma_sn_kg_cm2 — tensione nominale di snervamento in kg/cm²
    sigma_sn_legacy = getattr(materiale, "sigma_sn_kg_cm2", None)
    if sigma_sn_legacy and sigma_sn_legacy > 0:
        return min(sigma_sn_legacy * 2.0 / 3.0, 2600.0)

    # 4. Stima da f_yk — formula DM92
    f_yk_mpa = get_fyk_mpa(materiale)
    if f_yk_mpa is not None:
        sigma_sn_kg_cm2 = mpa_to_kg_cm2(f_yk_mpa)
        sigma_s_adm = min(sigma_sn_kg_cm2 * 2.0 / 3.0, 2600.0)
        logger.debug(
            "get_sigma_s_adm_kg_cm2: stima da f_yk=%.1f MPa → σ_s_adm=%.2f kg/cm²",
            f_yk_mpa,
            sigma_s_adm,
        )
        return sigma_s_adm

    return None


# ==============================================================================
# NORMALIZZAZIONE INPUT CALCOLO
# ==============================================================================


def ensure_mpa(valore: float, unita_sorgente: str) -> float:
    """Normalizza un valore di tensione a MPa in base all'unità di partenza.

    Funzione di utilità per garantire che i valori di tensione siano sempre
    in MPa prima di essere usati nel motore di calcolo.

    Parametri
    ----------
    valore : float
        Valore della tensione da normalizzare.
    unita_sorgente : str
        Unità della sorgente. Valori accettati:
        - ``"mpa"`` o ``"MPa"`` o ``"N/mm2"`` o ``"N/mm²"``
        - ``"kg/cm2"`` o ``"kg/cm²"`` o ``"kgcm2"``

    Restituisce
    -----------
    float
        Valore normalizzato in MPa.

    Eccezioni
    ---------
    ValueError
        Se ``unita_sorgente`` non è riconosciuta.

    Esempi
    ------
    >>> ensure_mpa(100.0, "kg/cm2")
    9.8067
    >>> ensure_mpa(25.0, "mpa")
    25.0
    """
    unita_norm = unita_sorgente.strip().lower().replace(" ", "")

    if unita_norm in ("mpa", "n/mm2", "n/mm²", "nmm2"):
        return float(valore)
    elif unita_norm in ("kg/cm2", "kg/cm²", "kgcm2", "kgf/cm2", "kgf/cm²"):
        return kg_cm2_to_mpa(valore)
    else:
        raise ValueError(
            f"Unità sorgente '{unita_sorgente}' non riconosciuta. "
            f"Usare 'mpa' oppure 'kg/cm2'."
        )


def ensure_kg_cm2(valore: float, unita_sorgente: str) -> float:
    """Normalizza un valore di tensione a kg/cm² in base all'unità di partenza.

    Complementare a ``ensure_mpa``, per i moduli TA che operano in kg/cm².

    Parametri
    ----------
    valore : float
        Valore della tensione da normalizzare.
    unita_sorgente : str
        Unità della sorgente. Valori come in ``ensure_mpa``.

    Restituisce
    -----------
    float
        Valore normalizzato in kg/cm².

    Eccezioni
    ---------
    ValueError
        Se ``unita_sorgente`` non è riconosciuta.
    """
    unita_norm = unita_sorgente.strip().lower().replace(" ", "")

    if unita_norm in ("mpa", "n/mm2", "n/mm²", "nmm2"):
        return mpa_to_kg_cm2(valore)
    elif unita_norm in ("kg/cm2", "kg/cm²", "kgcm2", "kgf/cm2", "kgf/cm²"):
        return float(valore)
    else:
        raise ValueError(
            f"Unità sorgente '{unita_sorgente}' non riconosciuta. "
            f"Usare 'mpa' oppure 'kg/cm2'."
        )


# ==============================================================================
# UTILITÀ PER VERIFICA CATALOGHI
# ==============================================================================


def verifica_unita_catalogo(
    record: dict[str, Any], campi_tensione: list[str] | None = None
) -> dict[str, Any]:
    """Verifica e documenta le unità di misura di un record di catalogo materiale.

    Analizza i campi tensione di un record JSON del catalogo e riporta
    l'unità presunta per ciascuno, senza modificare il record originale.

    Parametri
    ----------
    record : dict
        Record del catalogo materiale (da JSON).
    campi_tensione : list[str] | None
        Lista dei campi da analizzare. Se ``None``, usa lista predefinita:
        ``["f_ck", "f_yk", "sigma_c28", "sigma_c_adm", "E"]``.

    Restituisce
    -----------
    dict
        Dizionario ``{campo: {"valore": ..., "unita_presunta": ...}}``.
    """
    if campi_tensione is None:
        campi_tensione = ["f_ck", "f_yk", "sigma_c28", "sigma_c_adm", "sigma_s_adm", "E"]

    risultato: dict[str, Any] = {}

    for campo in campi_tensione:
        valore = record.get(campo)
        if valore is None or valore == 0:
            continue

        # Euristiche per rilevare l'unità
        if campo in ("sigma_c28", "sigma_c_adm", "sigma_s_adm", "tau_c0_adm", "tau_c1_adm"):
            unita = "kg/cm²"  # Campi TA — sempre kg/cm² per definizione storica
        elif campo == "f_ck":
            unita = "kg/cm²" if valore > 200.0 else "MPa"
        elif campo == "f_yk":
            unita = "kg/cm²" if valore > 1000.0 else "MPa"
        elif campo == "E":
            unita = "kg/cm²" if valore > 10000.0 else "MPa"
        else:
            unita = "sconosciuta"

        risultato[campo] = {"valore": valore, "unita_presunta": unita}

    return risultato


# ==============================================================================
# CONVERSIONI SPECIFICHE PER MODULI TA
# ==============================================================================


def fck_mpa_to_rck_kg_cm2(f_ck_mpa: float) -> float:
    """Calcola Rck in kg/cm² da f_ck in MPa.

    Relazione: Rck ≈ f_ck / 0.83 (EN 206-1 / NTC2018)
    con conversione MPa → kg/cm².

    Parametri
    ----------
    f_ck_mpa : float
        Resistenza caratteristica cilindrica f_ck in MPa.

    Restituisce
    -----------
    float
        Resistenza cubica Rck in kg/cm².
    """
    rck_mpa = f_ck_mpa / 0.83
    return mpa_to_kg_cm2(rck_mpa)


def rck_kg_cm2_to_fck_mpa(rck_kg_cm2: float) -> float:
    """Calcola f_ck in MPa da Rck in kg/cm².

    Relazione inversa: f_ck = 0.83 × Rck.

    Parametri
    ----------
    rck_kg_cm2 : float
        Resistenza cubica Rck in kg/cm².

    Restituisce
    -----------
    float
        Resistenza caratteristica cilindrica f_ck in MPa.
    """
    rck_mpa = kg_cm2_to_mpa(rck_kg_cm2)
    return round(0.83 * rck_mpa, _PRECISIONE_DECIMALI)


def fck_mpa_to_sigma_c_adm_kg_cm2_dm92(f_ck_mpa: float) -> float:
    """Calcola σ_c_adm in kg/cm² da f_ck in MPa secondo DM92.

    Formula DM 14/02/1992 §5.2.1:
        Rck = f_ck / 0.83   [MPa]
        σ_c_adm = 0.30 × Rck [kg/cm²]

    Parametri
    ----------
    f_ck_mpa : float
        Resistenza caratteristica cilindrica f_ck in MPa.

    Restituisce
    -----------
    float
        Tensione ammissibile a compressione in kg/cm².

    Riferimento normativo
    ---------------------
    DM 14/02/1992, §5.2.1 (Tensioni ammissibili calcestruzzo)
    """
    rck_kg_cm2 = fck_mpa_to_rck_kg_cm2(f_ck_mpa)
    return round(0.30 * rck_kg_cm2, _PRECISIONE_DECIMALI)
