"""Azione sismica storica — RD 2229/1939 e coefficienti empirici regionali.

Nota: il RD 2229/1939 non codifica esplicitamente coefficienti sismici orizzontali.
I coefficienti seguenti sono quelli empirici usati nella pratica professionale italiana
per edifici in zone sismiche ante-legge 64/1974, con riferimento alla zonazione
storica per regione (Marsica, Calabria, Sicilia = alta; Campania, Basilicata = media;
Appennino centro-settentrionale = bassa).

Coefficienti:
    non_sismico: 0.00  — zone non classificate sismicamente
    bassa:       0.05  — sismicità bassa
    media:       0.07  — sismicità media
    alta:        0.10  — sismicità alta (Calabria, Sicilia orientale, Marsica)
"""

from __future__ import annotations

from typing import Any

from .base import PianoEdificio, _base_contract, distribuzione_triangolare

_NORM_REF = "RD 2229/1939 (coefficienti empirici storici)"

RD2229_COEFF: dict[str, float] = {
    "non_sismico": 0.00,
    "bassa":       0.05,
    "media":       0.07,
    "alta":        0.10,
}

_ZONE_VALIDE = set(RD2229_COEFF)


def calcola_azione_sismica_rd2229(
    piani: list[PianoEdificio],
    zona: str,
    I: float = 1.0,  # noqa: E741
) -> dict[str, Any]:
    """Calcola l'azione sismica con coefficienti storici RD2229.

    Args:
        piani: lista PianoEdificio (ordinata dal basso verso l'alto).
        zona:  zona sismica storica (non_sismico | bassa | media | alta).
        I:     coefficiente di importanza (default 1.0).

    Returns:
        Dict con contratto base + F_base_kN, C_effettivo, metodo, distribuzione.
    """
    result = _base_contract(_NORM_REF)
    log = result["decision_log"]

    zona_norm = zona.lower().strip()
    if zona_norm not in _ZONE_VALIDE:
        raise ValueError(
            f"Zona '{zona}' non valida. Valori ammessi: {sorted(_ZONE_VALIDE)}"
        )

    C = RD2229_COEFF[zona_norm]
    W_tot = sum(p.W_kN for p in piani)

    log.append(
        f"RD2229 coefficienti storici: zona={zona_norm}, C={C}, I={I}"
    )
    log.append(
        "AVVISO: RD 2229/1939 non codifica ufficialmente l'azione sismica. "
        "I coefficienti C sono di uso professionale storico (ante-L64/1974)."
    )

    F_base = C * I * W_tot
    log.append(f"F_base = C({C}) * I({I}) * W_tot({W_tot:.3f}) = {F_base:.3f} kN")

    C_eff = F_base / W_tot if W_tot > 0 else 0.0
    distribuzione = distribuzione_triangolare(F_base, piani) if F_base > 0 else [
        {"piano": p.piano, "h_m": p.h_m, "W_kN": p.W_kN, "F_kN": 0.0}
        for p in piani
    ]

    result.update({
        "F_base_kN": round(F_base, 3),
        "C_effettivo": round(C_eff, 6),
        "metodo": "STATICO_EQUIVALENTE",
        "distribuzione": distribuzione,
        "zona": zona_norm,
        "C_storico": C,
    })
    return result
