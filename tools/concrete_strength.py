"""Calcoli di base per la resistenza del calcestruzzo.

Questo modulo fornisce funzioni per ottenere la tensione ammissibile
del calcestruzzo (`σ_c`) a partire dalla resistenza caratteristica
del provino a 28 giorni (`σ_c28`), considerando:
- il tipo di cemento (normale / alta resistenza o alluminoso)
- la condizione della sezione (semplicemente compressa, inflessa/presso-inflessa)
- controlli di qualità (quando la resistenza è determinata e controllata)

Le regole implementate si basano sulle tabelle storiche usate nel progetto.

Unità e convenzioni storiche:
- Tutti gli input e gli output principali in questo modulo sono espressi in
    `Kg/cm²` (tensione/pressione storica). Questo rispetta le consuetudini
    e la normativa storica (RD 2229).
- Sono comunque presenti funzioni di conversione verso/da MPa se necessario.
"""

from __future__ import annotations

from enum import Enum
from typing import Tuple

# Conversione: 1 Kg/cm^2 = 0.0980665 MPa
_KGCM2_TO_MPA = 0.0980665


class CementType(Enum):
    NORMAL = "normal"
    SLOW = "slow"  # cemento a lenta presa
    HIGH = "high"  # cemento ad alta resistenza
    ALUMINOUS = "aluminous"  # cemento alluminoso


class SectionCondition(Enum):
    SEMPLICEMENTE_COMPRESA = "semplicemente_compresa"
    INFLESSA_PRESSOINFLESSA = "inflesse_presso_inflesse"
    CONGLOMERATO_SPECIALE = "conglomerato_speciale"


def _kgcm2_to_mpa(x: float) -> float:
    return x * _KGCM2_TO_MPA


def _mpa_to_kgcm2(x: float) -> float:
    return x / _KGCM2_TO_MPA


def compute_allowable_compressive_stress(
    sigma_c28_kgcm2: float,
    cement: CementType = CementType.NORMAL,
    condition: SectionCondition = SectionCondition.SEMPLICEMENTE_COMPRESA,
    controlled_quality: bool = False,
) -> float:
    """Calcola la tensione ammissibile media del calcestruzzo (σ_c) in Kg/cm².

    Parametri
    - `sigma_c28_kgcm2`: resistenza caratteristica a 28 giorni (Kg/cm²)
    - `cement`: tipo di cemento (NORMAL o HIGH)
    - `condition`: condizione della sezione
    - `controlled_quality`: se True usa la regola `σ_c = sigma_c28/3` con cap

    Regole storiche implementate (tutte le grandezze qui sono in Kg/cm²):
    - SEMPLICEMENTE_COMPRESA:
        * cement NORMAL -> σ_c = 35 (se σ_c28 >= 120)
        * cement HIGH   -> σ_c = 45 (se σ_c28 >= 160)
        * se `controlled_quality`: σ_c = σ_c28/3 (ma non > 60)
    - INFLESSA_PRESSOINFLESSA:
        * cement NORMAL -> σ_c = 40 (se σ_c28 >= 120)
        * cement HIGH   -> σ_c = 50 (se σ_c28 >= 160)
        * se `controlled_quality`: σ_c = σ_c28/3 (ma non > 75)
    - CONGLOMERATO_SPECIALE (σ_c28 > 225):
        * σ_c = 75 + (σ_c28 - 225)/9

    Ritorna il valore di `σ_c` in Kg/cm².
    """
    sigma_c28_kg = float(sigma_c28_kgcm2)

    if condition == SectionCondition.CONGLOMERATO_SPECIALE and sigma_c28_kg > 225.0:
        sigma_c_kg = 75.0 + (sigma_c28_kg - 225.0) / 9.0
        return round(sigma_c_kg)

    if controlled_quality:
        sigma_c_kg = sigma_c28_kg / 3.0
        cap_kg = 60.0 if condition == SectionCondition.SEMPLICEMENTE_COMPRESA else 75.0
        return round(min(sigma_c_kg, cap_kg))

    # regole per tipo di cemento e condizione (valori fissi in Kg/cm2)
    if condition == SectionCondition.SEMPLICEMENTE_COMPRESA:
        if cement == CementType.NORMAL:
            threshold_kg = 120.0
            value_kg = 35.0
        else:
            threshold_kg = 160.0
            value_kg = 45.0
    else:  # INFLESSA_PRESSOINFLESSA
        if cement == CementType.NORMAL:
            threshold_kg = 120.0
            value_kg = 40.0
        else:
            threshold_kg = 160.0
            value_kg = 50.0

    if sigma_c28_kg >= threshold_kg:
        return value_kg

    # fallback: se σ_c28 non raggiunge la soglia, utilizzare σ_c28/3
    return round(sigma_c28_kg / 3.0)


def compute_sigma_c_all(
    sigma_c28_kgcm2: float,
    cement: CementType = CementType.NORMAL,
    controlled_quality: bool = False,
) -> dict:
    """Calcola le tensioni ammissibili per le diverse condizioni.

    Ritorna dizionario con chiavi (Kg/cm²):
      - 'semplice' : per sezioni semplicemente compresse
      - 'inflessa' : per sezioni inflesse
      - 'presso_inflessa' : per sezioni presso-inflesse (storicamente uguale a 'inflessa')

    Applica la regola per conglomerati con σ_c28 > 225 quando opportuno.
    """
    cement_effective = cement
    if cement == CementType.ALUMINOUS:
        cement_effective = CementType.HIGH

    # semplice
    semplice = compute_allowable_compressive_stress(
        sigma_c28_kgcm2,
        cement_effective,
        SectionCondition.SEMPLICEMENTE_COMPRESA,
        controlled_quality,
    )

    # inflessa / presso-inflessa
    inflessa = compute_allowable_compressive_stress(
        sigma_c28_kgcm2,
        cement_effective,
        SectionCondition.INFLESSA_PRESSOINFLESSA,
        controlled_quality,
    )

    return {
        "semplice": semplice,
        "inflessa": inflessa,
        "presso_inflessa": inflessa,
    }


def compute_allowable_shear(cement: CementType = CementType.NORMAL) -> Tuple[float, float]:
    """Ritorna una tupla `(service_tau, max_tau)` in Kg/cm².

    - `service_tau`: carico di sicurezza al taglio. Valori storici:
        * NORMAL: 4 Kg/cm²
        * HIGH: 6 Kg/cm²
    - `max_tau`: tensione tangenziale massima non superabile:
        * NORMAL: 14 Kg/cm²
        * HIGH: 16 Kg/cm²
    """
    if cement == CementType.NORMAL:
        service = 4.0
        maximum = 14.0
    else:
        service = 6.0
        maximum = 16.0
    return service, maximum


def compute_ec(sigma_c28_kgcm2: float) -> float:
    """Calcola il modulo elastico di compressione `E_c` (Kg/cm²) a partire da
    la resistenza caratteristica a 28 giorni `σ_c28` (Kg/cm²).

    Formula adottata (da fonti storiche riportate nell'immagine):
        E_c = 550000 * σ_c28 / (σ_c28 + 200)

    Restituisce `E_c` in Kg/cm².
    """
    sigma = float(sigma_c28_kgcm2)
    if sigma <= 0.0:
        return 0.0
    return round(550000.0 * sigma / (sigma + 200.0))


def compute_ec_conventional(sigma_c28_kgcm2: float, cement: CementType) -> float | None:
    """Determina il valore convenzionale di E_c (Kg/cm²) secondo regole storiche.

    Regole:
    - Se cemento a lenta presa e σ_c28 < 120 kg/cm² (tolleranza +5%), E_c = 200000
    - Se cemento normale e σ_c28 >= 160 kg/cm², E_c = 250000
    - Se cemento alta resistenza, E_c = 300000
    - Se cemento alluminoso, E_c = 330000

    Ritorna `None` se non applicabile.
    """
    try:
        s28 = float(sigma_c28_kgcm2)
    except Exception:
        return None

    # tolerance +5%
    tol_120 = 120.0 * 1.05
    if cement == CementType.SLOW and s28 < tol_120:
        return 200000.0
    if cement == CementType.NORMAL and s28 >= 160.0:
        return 250000.0
    if cement == CementType.HIGH:
        return 300000.0
    if cement == CementType.ALUMINOUS:
        return 330000.0
    return None


def compute_gc(ec_kgcm2: float) -> tuple:
    """Calcola il modulo tangenziale `G_c` a partire da `E_c`.

    La relazione storica è approssimativamente:
        G_c = (0.430 ÷ 0.445) * E_c

    La funzione ritorna una tupla `(g_min, g_mean, g_max)` in Kg/cm².
    """
    e = float(ec_kgcm2)
    g_min = round(0.430 * e)
    g_max = round(0.445 * e)
    g_mean = round(0.5 * (g_min + g_max))
    return g_min, g_mean, g_max


__all__ = [
    "CementType",
    "SectionCondition",
    "compute_allowable_compressive_stress",
    "compute_allowable_shear",
]
