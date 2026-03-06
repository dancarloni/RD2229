"""Accesso ai dati di pericolosita' sismica INGV — NTC2018 Allegato B.

Due modalita' di accesso:
  INGV_WEBSERVICE — webservice INGV ESSE1 (richiede connessione internet)
  LOCAL_CSV       — griglia locale NTC2018 Allegato B (~1.5 MB, non inclusa nel repo)

Flusso tipico:
  get_hazard_params_site(lat, lon, TR)
    -> prova webservice INGV -> se fallisce, prova CSV locale
    -> ritorna Ntc2018HazardRow + HazardSource utilizzata

Formato CSV griglia INGV (Allegato B NTC2018):
  lat, lon, ag_10, ag_50, ag_475, ag_975, ag_2475,
            f0_10, f0_50, f0_475, f0_975, f0_2475,
            tc_10, tc_50, tc_475, tc_975, tc_2475
  (TR = 10, 50, 475, 975, 2475 anni)

Riferimenti:
  http://esse1.mi.ingv.it/           — portale webservice INGV
  NTC2018 Allegato B                 — griglia pericolosita' 0.05deg x 0.05deg
"""

from __future__ import annotations

import math
from enum import Enum
from pathlib import Path
from typing import Optional

from .spectrum_paste_service import Ntc2018HazardRow

DEFAULT_CSV_PATH = (
    Path(__file__).parent.parent.parent.parent / "data" / "seismic" / "griglia_ingv.csv"
)

# TR disponibili nella griglia NTC2018 Allegato B
_TR_DISPONIBILI = [10, 50, 475, 975, 2475]

# URL webservice INGV ESSE1
_INGV_ESSE1_URL = "http://esse1.mi.ingv.it/index.php"


class HazardSource(Enum):
    """Modalita' di accesso ai dati di pericolosita' sismica."""
    INGV_WEBSERVICE = "INGV_WEBSERVICE"
    LOCAL_CSV = "LOCAL_CSV"


# ---------------------------------------------------------------------------
# Webservice INGV
# ---------------------------------------------------------------------------

def get_hazard_params_ingv(lat: float, lon: float, TR: int) -> Ntc2018HazardRow:
    """Ottieni parametri di pericolosita' dal webservice INGV ESSE1.

    Chiama http://esse1.mi.ingv.it/index.php con lat, lon e interpola per TR.

    Args:
        lat: latitudine WGS84 [gradi].
        lon: longitudine WGS84 [gradi].
        TR: tempo di ritorno [anni].

    Returns:
        Ntc2018HazardRow con ag_g, f0, tc_star_s per il TR richiesto.

    Raises:
        IOError: se il webservice non e' raggiungibile.
        ValueError: se lat/lon fuori dall'Italia.
    """
    try:
        import urllib.request
        import urllib.parse
        import json
    except ImportError as e:
        raise IOError(f"Modulo urllib non disponibile: {e}") from e

    _valida_coordinate(lat, lon)

    params = urllib.parse.urlencode({
        "lat": f"{lat:.4f}",
        "lon": f"{lon:.4f}",
        "elev": "0",
        "depth": "0",
    })
    url = f"{_INGV_ESSE1_URL}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise IOError(
            f"Webservice INGV non raggiungibile ({url}): {e}. "
            "Usare get_hazard_params_csv() con griglia locale."
        ) from e

    return _parse_ingv_response(data, TR)


def _parse_ingv_response(data: dict, TR: int) -> Ntc2018HazardRow:
    """Interpreta la risposta JSON del webservice INGV."""
    # Il formato INGV ESSE1 restituisce array di valori per diversi TR
    # Struttura attesa: {"ag": [...], "fo": [...], "tc": [...], "tr": [...]}
    try:
        trs = data.get("tr", data.get("TR", []))
        ags = data.get("ag", [])
        f0s = data.get("fo", data.get("f0", []))
        tcs = data.get("tc", data.get("TC", []))

        if not trs:
            raise ValueError("Risposta INGV: campo 'tr' mancante o vuoto")

        tr_idx = _interpola_indice_tr(trs, TR)
        ag_g = float(ags[tr_idx])
        f0 = float(f0s[tr_idx])
        tc_star = float(tcs[tr_idx])

    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Risposta INGV in formato inatteso: {e}. Data: {data}") from e

    return Ntc2018HazardRow(
        limit_state_label=f"TR={TR}anni",
        tr_years=float(TR),
        ag_g=ag_g,
        f0=f0,
        tc_star_s=tc_star,
    )


# ---------------------------------------------------------------------------
# CSV locale
# ---------------------------------------------------------------------------

def get_hazard_params_csv(
    lat: float,
    lon: float,
    TR: int,
    csv_path: Path = DEFAULT_CSV_PATH,
) -> Ntc2018HazardRow:
    """Ottieni parametri di pericolosita' dalla griglia NTC2018 Allegato B (CSV locale).

    Interpolazione bilineare sui 4 nodi della griglia 0.05deg x 0.05deg piu' vicini.

    Args:
        lat: latitudine WGS84 [gradi].
        lon: longitudine WGS84 [gradi].
        TR: tempo di ritorno [anni] (tra quelli disponibili: 10, 50, 475, 975, 2475).
        csv_path: percorso al file CSV della griglia INGV.

    Returns:
        Ntc2018HazardRow con ag_g, f0, tc_star_s interpolati.

    Raises:
        FileNotFoundError: se il file CSV non esiste.
        ValueError: se TR non e' nella griglia o le coordinate sono fuori range.
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(
            f"Griglia INGV non trovata: {csv_path}\n"
            "Scaricare il file NTC2018 Allegato B da https://esse1.mi.ingv.it/ "
            "e salvarlo come griglia_ingv.csv nella directory data/seismic/."
        )

    try:
        import csv as csv_mod
    except ImportError as e:
        raise ImportError("Modulo csv non disponibile") from e

    _valida_coordinate(lat, lon)
    _valida_tr(TR)

    tr_col = _tr_col_name(TR)

    rows_data: list[dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv_mod.DictReader(f)
        for row in reader:
            rows_data.append(row)

    if not rows_data:
        raise ValueError(f"File CSV vuoto: {csv_path}")

    ag_g, f0, tc_star = _interpolazione_bilineare(lat, lon, tr_col, rows_data)

    return Ntc2018HazardRow(
        limit_state_label=f"TR={TR}anni",
        tr_years=float(TR),
        ag_g=ag_g,
        f0=f0,
        tc_star_s=tc_star,
    )


# ---------------------------------------------------------------------------
# Funzione principale (webservice + fallback)
# ---------------------------------------------------------------------------

def get_hazard_params_site(
    lat: float,
    lon: float,
    TR: int,
    prefer: HazardSource = HazardSource.INGV_WEBSERVICE,
    csv_path: Path = DEFAULT_CSV_PATH,
) -> tuple[Ntc2018HazardRow, HazardSource]:
    """Ottieni parametri di pericolosita': prova webservice, fallback su CSV.

    Args:
        lat: latitudine WGS84 [gradi].
        lon: longitudine WGS84 [gradi].
        TR: tempo di ritorno [anni].
        prefer: sorgente preferita (default INGV_WEBSERVICE).
        csv_path: percorso al file CSV per fallback locale.

    Returns:
        Tupla (Ntc2018HazardRow, HazardSource utilizzata).

    Raises:
        IOError: se webservice non raggiungibile e CSV non disponibile.
        FileNotFoundError: se prefer=LOCAL_CSV e CSV non esiste.
    """
    if prefer == HazardSource.LOCAL_CSV:
        row = get_hazard_params_csv(lat, lon, TR, csv_path)
        return row, HazardSource.LOCAL_CSV

    # Prova webservice, fallback su CSV
    try:
        row = get_hazard_params_ingv(lat, lon, TR)
        return row, HazardSource.INGV_WEBSERVICE
    except IOError:
        row = get_hazard_params_csv(lat, lon, TR, csv_path)
        return row, HazardSource.LOCAL_CSV


# ---------------------------------------------------------------------------
# Utilita' interne
# ---------------------------------------------------------------------------

def _valida_coordinate(lat: float, lon: float) -> None:
    """Verifica che le coordinate siano nel range Italia (approssimativo)."""
    if not (35.0 <= lat <= 48.0):
        raise ValueError(f"Latitudine {lat} fuori dal range Italia (35-48 gradi N)")
    if not (6.0 <= lon <= 19.0):
        raise ValueError(f"Longitudine {lon} fuori dal range Italia (6-19 gradi E)")


def _valida_tr(TR: int) -> None:
    """Verifica che TR sia tra i valori disponibili nella griglia."""
    if TR not in _TR_DISPONIBILI:
        raise ValueError(
            f"TR={TR} non disponibile. Valori ammessi: {_TR_DISPONIBILI}. "
            "Usare interpolazione manuale per TR intermedi."
        )


def _tr_col_name(TR: int) -> str:
    """Ritorna il suffisso della colonna CSV per il TR dato (es. '475' -> 'ag_475')."""
    return str(TR)


def _interpola_indice_tr(trs: list, TR: int) -> int:
    """Trova l'indice piu' vicino nella lista TR del webservice."""
    trs_float = [float(t) for t in trs]
    diffs = [abs(t - TR) for t in trs_float]
    return diffs.index(min(diffs))


def _interpolazione_bilineare(
    lat: float, lon: float, tr_suffix: str, rows: list[dict]
) -> tuple[float, float, float]:
    """Interpolazione bilineare sui 4 nodi griglia piu' vicini.

    Cerca i nodi con lat/lon nella griglia 0.05deg x 0.05deg e interpola
    ag, f0, tc_star per il TR richiesto.

    Formato colonne CSV atteso: ag_{TR}, f0_{TR}, tc_{TR}
    """
    # Trova i nodi nella griglia
    lats = sorted(set(float(r["lat"]) for r in rows))
    lons = sorted(set(float(r["lon"]) for r in rows))

    # Trova i 2 lat e 2 lon piu' vicini
    lat0 = max((l for l in lats if l <= lat), default=lats[0])
    lat1 = min((l for l in lats if l >= lat), default=lats[-1])
    lon0 = max((l for l in lons if l <= lon), default=lons[0])
    lon1 = min((l for l in lons if l >= lon), default=lons[-1])

    def _get_node(lt: float, ln: float, key: str) -> float:
        for r in rows:
            if abs(float(r["lat"]) - lt) < 1e-6 and abs(float(r["lon"]) - ln) < 1e-6:
                return float(r[key])
        raise ValueError(f"Nodo ({lt}, {ln}) non trovato nel CSV")

    ag_key = f"ag_{tr_suffix}"
    f0_key = f"f0_{tr_suffix}"
    tc_key = f"tc_{tr_suffix}"

    # Coefficienti interpolazione bilineare
    if abs(lat1 - lat0) < 1e-9:
        t = 0.0
    else:
        t = (lat - lat0) / (lat1 - lat0)

    if abs(lon1 - lon0) < 1e-9:
        u = 0.0
    else:
        u = (lon - lon0) / (lon1 - lon0)

    def _bilinear(key: str) -> float:
        v00 = _get_node(lat0, lon0, key)
        v10 = _get_node(lat1, lon0, key)
        v01 = _get_node(lat0, lon1, key)
        v11 = _get_node(lat1, lon1, key)
        return (1 - t) * (1 - u) * v00 + t * (1 - u) * v10 + (1 - t) * u * v01 + t * u * v11

    return _bilinear(ag_key), _bilinear(f0_key), _bilinear(tc_key)
