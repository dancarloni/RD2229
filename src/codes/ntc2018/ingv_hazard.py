"""Accesso ai dati di pericolosita' sismica INGV — NTC2018 Allegato B.

Due modalita' di accesso:
  INGV_WEBSERVICE — webservice INGV ESSE1 (richiede connessione internet)
  LOCAL_CSV       — griglia locale NTC2018 Allegato B (data/seismic/griglia_ingv.csv)

Flusso tipico:
  get_hazard_params_site(lat, lon, TR)
    -> prova webservice INGV -> se fallisce, prova CSV locale
    -> ritorna Ntc2018HazardRow + HazardSource utilizzata

Formato CSV griglia INGV (spettri2008.csv — NTC2008/NTC2018 Allegato B):
  Riga 1: super-header "TR = 30", "TR = 50", ...  (saltata)
  Riga 2: nomi colonne: OBJECTID, ID, LON, LAT, T30ag, T30F0, T30Tc, ...
  Righe 3+: dati (~10.751 punti griglia irregolare)

  Colonne per ogni TR: T{TR}ag, T{TR}F0, T{TR}Tc
    ag  = accelerazione al suolo [m/s^2]  — conversione a [g]: ag_g = ag / 9.81
    F0  = fattore di amplificazione spettrale [-]
    Tc  = TC* = periodo caratteristico [s]

TR disponibili nella griglia: 30, 50, 72, 101, 140, 201, 475, 975, 2475 anni.
Per TR non nella lista: interpolazione log-lineare (NTC2018 §3.2.1).

Interpolazione spaziale: nearest-neighbor (la griglia e' irregolare, ~5-6 km tra punti).

Riferimenti:
  http://esse1.mi.ingv.it/           — portale webservice INGV
  NTC2018 Allegato B                 — griglia pericolosita' sismica
"""

from __future__ import annotations

import csv as _csv_mod
import math
from enum import Enum
from pathlib import Path
from typing import Optional

from .spectrum_paste_service import Ntc2018HazardRow

DEFAULT_CSV_PATH = (
    Path(__file__).parent.parent.parent.parent / "data" / "seismic" / "griglia_ingv.csv"
)

# TR disponibili nella griglia NTC2018 Allegato B (spettri2008.csv)
_TR_DISPONIBILI = [30, 50, 72, 101, 140, 201, 475, 975, 2475]

# Costante gravitazionale per conversione ag [m/s^2] -> [g]
_G = 9.81

# URL webservice INGV ESSE1
_INGV_ESSE1_URL = "http://esse1.mi.ingv.it/index.php"

# Cache in-memory del CSV (evita rilettura ripetuta per sessione)
_csv_cache: dict[Path, list[tuple[float, float, dict]]] = {}


class HazardSource(Enum):
    """Modalita' di accesso ai dati di pericolosita' sismica."""
    INGV_WEBSERVICE = "INGV_WEBSERVICE"
    LOCAL_CSV = "LOCAL_CSV"


# ---------------------------------------------------------------------------
# Webservice INGV
# ---------------------------------------------------------------------------

def get_hazard_params_ingv(lat: float, lon: float, TR: int) -> Ntc2018HazardRow:
    """Ottieni parametri di pericolosita' dal webservice INGV ESSE1.

    Args:
        lat: latitudine WGS84 [gradi].
        lon: longitudine WGS84 [gradi].
        TR: tempo di ritorno [anni].

    Returns:
        Ntc2018HazardRow con ag_g [g], f0, tc_star_s per il TR richiesto.

    Raises:
        IOError: se il webservice non e' raggiungibile.
        ValueError: se lat/lon fuori dall'Italia.
    """
    try:
        import json
        import urllib.parse
        import urllib.request
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
    try:
        trs = data.get("tr", data.get("TR", []))
        ags = data.get("ag", [])
        f0s = data.get("fo", data.get("f0", []))
        tcs = data.get("tc", data.get("TC", []))

        if not trs:
            raise ValueError("Risposta INGV: campo 'tr' mancante o vuoto")

        tr_idx = _interpola_indice_tr_webservice(trs, TR)
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
# CSV locale — lettura e cache
# ---------------------------------------------------------------------------

def _carica_csv_griglia(csv_path: Path) -> list[tuple[float, float, dict]]:
    """Carica la griglia INGV dal CSV e ritorna lista di (lat, lon, row_dict).

    Gestisce il doppio header del formato spettri2008.csv:
      riga 1 = super-header con etichette TR (saltata)
      riga 2 = nomi colonne (OBJECTID, ID, LON, LAT, T30ag, ...)

    Le colonne T{TR}ag sono in [m/s^2]; la conversione a [g] avviene
    in _cerca_punto_piu_vicino() al momento dell'accesso.
    """
    resolved = csv_path.resolve()
    if resolved in _csv_cache:
        return _csv_cache[resolved]

    if not resolved.exists():
        raise FileNotFoundError(
            f"Griglia INGV non trovata: {resolved}\n"
            "Salvare il file NTC2018 Allegato B (spettri2008.csv) come "
            "data/seismic/griglia_ingv.csv nella radice del progetto."
        )

    points: list[tuple[float, float, dict]] = []
    with open(resolved, newline="", encoding="utf-8") as f:
        # Riga 1: super-header o nomi colonne?
        first_line = f.readline()
        # Se la riga 1 e' gia' i nomi colonne (OBJECTID/ID), rimetti il cursore
        stripped = first_line.strip().strip('"')
        if stripped.startswith("OBJECTID") or stripped.startswith("ID"):
            f.seek(0)
        # Ora leggi con DictReader (usa la prima riga rimasta come header)
        reader = _csv_mod.DictReader(f)
        for row in reader:
            try:
                lat = float(row["LAT"])
                lon = float(row["LON"])
                points.append((lat, lon, row))
            except (KeyError, ValueError):
                continue

    _csv_cache[resolved] = points
    return points


def _invalida_cache_csv(csv_path: Optional[Path] = None) -> None:
    """Invalida la cache CSV (utile nei test)."""
    if csv_path is None:
        _csv_cache.clear()
    else:
        _csv_cache.pop(csv_path.resolve(), None)


# ---------------------------------------------------------------------------
# CSV locale — accesso e interpolazione
# ---------------------------------------------------------------------------

def get_hazard_params_csv(
    lat: float,
    lon: float,
    TR: int,
    csv_path: Path = DEFAULT_CSV_PATH,
) -> Ntc2018HazardRow:
    """Ottieni parametri di pericolosita' dalla griglia NTC2018 Allegato B (CSV locale).

    Ricerca nearest-neighbor (griglia irregolare) con interpolazione log-lineare
    per TR non nella griglia.

    Args:
        lat: latitudine WGS84 [gradi].
        lon: longitudine WGS84 [gradi].
        TR: tempo di ritorno [anni] (qualsiasi valore >= 30, interpolato se necessario).
        csv_path: percorso al file CSV della griglia INGV.

    Returns:
        Ntc2018HazardRow con ag_g [g], f0 [-], tc_star_s [s] interpolati.

    Raises:
        FileNotFoundError: se il file CSV non esiste.
        ValueError: se le coordinate sono fuori dal range Italia.
    """
    _valida_coordinate(lat, lon)

    points = _carica_csv_griglia(Path(csv_path))

    # Trova i TR griglia che brackettano il TR richiesto
    tr1, tr2 = _trova_tr_bracket(TR)

    # Nearest-neighbor per tr1
    ag1, f0_1, tc1 = _cerca_punto_piu_vicino(lat, lon, tr1, points)

    if tr1 == tr2:
        return Ntc2018HazardRow(
            limit_state_label=f"TR={TR}anni",
            tr_years=float(TR),
            ag_g=ag1,
            f0=f0_1,
            tc_star_s=tc1,
        )

    # Nearest-neighbor per tr2
    ag2, f0_2, tc2 = _cerca_punto_piu_vicino(lat, lon, tr2, points)

    # Interpolazione log-lineare su TR (NTC2018 §3.2.1)
    ag_g, f0, tc_star = _interpola_log_lineare_tr(TR, tr1, tr2, ag1, f0_1, tc1, ag2, f0_2, tc2)

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
    """
    if prefer == HazardSource.LOCAL_CSV:
        row = get_hazard_params_csv(lat, lon, TR, csv_path)
        return row, HazardSource.LOCAL_CSV

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


def _trova_tr_bracket(TR: int) -> tuple[int, int]:
    """Trova i due TR della griglia che brackettano il TR richiesto.

    Ritorna (tr1, tr2) con tr1 <= TR <= tr2.
    Se TR e' nella griglia, ritorna (TR, TR).
    Se TR fuori dai limiti: clamp al valore piu' vicino.
    """
    if TR in _TR_DISPONIBILI:
        return TR, TR

    if TR < _TR_DISPONIBILI[0]:
        return _TR_DISPONIBILI[0], _TR_DISPONIBILI[0]

    if TR > _TR_DISPONIBILI[-1]:
        return _TR_DISPONIBILI[-1], _TR_DISPONIBILI[-1]

    for i in range(len(_TR_DISPONIBILI) - 1):
        if _TR_DISPONIBILI[i] < TR < _TR_DISPONIBILI[i + 1]:
            return _TR_DISPONIBILI[i], _TR_DISPONIBILI[i + 1]

    return _TR_DISPONIBILI[-1], _TR_DISPONIBILI[-1]


def _cerca_punto_piu_vicino(
    lat: float,
    lon: float,
    TR: int,
    points: list[tuple[float, float, dict]],
) -> tuple[float, float, float]:
    """Trova il punto piu' vicino nella griglia (nearest-neighbor) e ritorna ag_g, F0, TC*.

    Distanza approssimata: Euclidea su (lat, lon) in gradi (valida per piccole distanze).
    ag e' convertita da [m/s^2] a [g] = ag / 9.81.

    Returns:
        (ag_g [g], F0 [-], TC* [s]) del punto piu' vicino.
    """
    ag_key = f"T{TR}ag"
    f0_key = f"T{TR}F0"
    tc_key = f"T{TR}Tc"

    best_dist2 = float("inf")
    best_row: Optional[dict] = None

    for (plat, plon, row) in points:
        d2 = (plat - lat) ** 2 + (plon - lon) ** 2
        if d2 < best_dist2:
            best_dist2 = d2
            best_row = row

    if best_row is None:
        raise ValueError(f"Nessun punto trovato nella griglia per ({lat}, {lon})")

    # Conversione ag da [m/s^2] a [g]
    ag_ms2 = float(best_row[ag_key])
    ag_g = ag_ms2 / _G
    f0 = float(best_row[f0_key])
    tc_star = float(best_row[tc_key])

    return ag_g, f0, tc_star


def _interpola_log_lineare_tr(
    TR: int,
    tr1: int, tr2: int,
    ag1: float, f0_1: float, tc1: float,
    ag2: float, f0_2: float, tc2: float,
) -> tuple[float, float, float]:
    """Interpolazione log-lineare dei parametri spettrali tra due TR.

    NTC2018 §3.2.1: ag, F0, TC* scalano log-linearmente con TR.

    alpha = log(TR/tr1) / log(tr2/tr1)
    param(TR) = p1^(1-alpha) * p2^alpha
    """
    log_tr1 = math.log(tr1)
    log_tr2 = math.log(tr2)
    log_tr = math.log(TR)

    alpha = (log_tr - log_tr1) / (log_tr2 - log_tr1)

    def _interp_log(p1: float, p2: float) -> float:
        if p1 <= 0 or p2 <= 0:
            return p1 + alpha * (p2 - p1)
        return math.exp(math.log(p1) + alpha * (math.log(p2) - math.log(p1)))

    return _interp_log(ag1, ag2), _interp_log(f0_1, f0_2), _interp_log(tc1, tc2)


def _interpola_indice_tr_webservice(trs: list, TR: int) -> int:
    """Trova l'indice piu' vicino nella lista TR del webservice."""
    trs_float = [float(t) for t in trs]
    diffs = [abs(t - TR) for t in trs_float]
    return diffs.index(min(diffs))
