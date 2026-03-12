"""Calcolo forze sismiche per telai piani secondo RD 2229/39.

Calcola le forze statiche equivalenti per sisma ondulatorio (orizzontale)
e sussultorio (verticale) da applicare ai piani del telaio.

Riutilizza i moduli esistenti:
    - src/codes/seismic/rd2229.py    → coefficienti sismici per zona
    - src/rd2229/seismic/rd2229_39/  → provider forze per piano

Unità: kg [forze], cm [geometria].

Riferimenti:
    RD 2229/1939, art. 9 — Calcolo sismico
    Santarella "Il Cemento Armato" — Azione sismica sui telai
"""

from __future__ import annotations

from dataclasses import dataclass

from .modello_telaio import ModelloTelaio, PianoTelaio

# Coefficienti sismici per zona (da src/codes/seismic/rd2229.py)
_COEFF_SISMICI: dict[str, float] = {
    "non_sismico": 0.00,
    "bassa": 0.05,
    "media": 0.07,
    "alta": 0.10,
}

# Fattore sussultorio rispetto all'ondulatorio (RD2229: V = 1.25 × H)
_FATTORE_SUSSULTORIO = 1.25


@dataclass
class ForzeSismicheTelaio:
    """Forze sismiche calcolate per il telaio.

    Attributi:
        zona:               zona sismica ("non_sismico", "bassa", "media", "alta")
        C_s:                coefficiente sismico orizzontale
        ondulatorio_x:      {id_piano: F_orizz [kg]}  forze orizzontali (+X)
        sussultorio_z:      {id_piano: F_vert [kg]}   forze verticali addizionali
        peso_per_piano:     {id_piano: W_piano [kg]}  pesi per piano
        passaggi:           audit del calcolo
    """

    zona: str
    C_s: float
    ondulatorio_x: dict[int, float]
    sussultorio_z: dict[int, float]
    peso_per_piano: dict[int, float]
    passaggi: list[str]

    def to_dict(self) -> dict:
        return {
            "zona": self.zona,
            "C_s": self.C_s,
            "ondulatorio_x": {str(k): round(v, 1) for k, v in self.ondulatorio_x.items()},
            "sussultorio_z": {str(k): round(v, 1) for k, v in self.sussultorio_z.items()},
            "peso_per_piano": {str(k): round(v, 1) for k, v in self.peso_per_piano.items()},
        }


def calcola_peso_piano(
    modello: ModelloTelaio,
    id_piano: int,
    g: float = 9.81,
) -> float:
    """Calcola il peso del piano sommando:
    - Peso aste orizzontali (travi) del piano × g
    - Metà peso delle colonne soprastanti + metà colonne sottostanti

    Args:
        modello:  modello del telaio
        id_piano: piano da calcolare
        g:        accelerazione di gravità [m/s²] (usata per coerenza con provider)

    Returns:
        Peso del piano [kg]
    """
    peso = 0.0

    # Travi del piano
    for asta in modello.travi_piano(id_piano):
        L = modello.lunghezza_asta(asta.id)
        peso += asta.sezione.A * asta.sezione.gamma * L  # già in [kg]

    # Metà colonne piano soprastante
    for col in modello.colonne_piano(id_piano):
        L = modello.lunghezza_asta(col.id)
        peso += 0.5 * col.sezione.A * col.sezione.gamma * L

    # Metà colonne piano sottostante
    for col in modello.colonne_piano(id_piano - 1):
        L = modello.lunghezza_asta(col.id)
        peso += 0.5 * col.sezione.A * col.sezione.gamma * L

    return peso


def calcola_forze_sismiche(
    modello: ModelloTelaio,
    zona: str | None = None,
    C_s_override: float | None = None,
) -> ForzeSismicheTelaio:
    """Calcola le forze sismiche ondulatorio e sussultorio per ogni piano.

    Metodo (RD2229/39, Santarella):
        F_piano_i = W_piano_i × C_s       (ondulatorio orizzontale)
        F_suss_i  = F_ond_i × 1.25        (sussultorio verticale)

    Args:
        modello:      modello del telaio (usa modello.zona_sismica se zona=None)
        zona:         override zona sismica ("non_sismico", "bassa", "media", "alta")
        C_s_override: override diretto del coefficiente sismico (ignora zona)

    Returns:
        ForzeSismicheTelaio con forze per piano e audit
    """
    zona_eff = zona or modello.zona_sismica
    if zona_eff not in _COEFF_SISMICI:
        raise ValueError(
            f"Zona sismica non riconosciuta: '{zona_eff}'. "
            f"Valori validi: {list(_COEFF_SISMICI.keys())}"
        )

    C_s = C_s_override if C_s_override is not None else _COEFF_SISMICI[zona_eff]
    passaggi: list[str] = [f"Zona sismica: {zona_eff}, C_s = {C_s:.3f}"]

    ondulatorio_x: dict[int, float] = {}
    sussultorio_z: dict[int, float] = {}
    peso_per_piano: dict[int, float] = {}

    piani = sorted(modello.piani, key=lambda p: p.id_piano)

    for piano in piani:
        # Usa peso_piano dal modello se già impostato, altrimenti calcola
        if piano.peso_piano > 0:
            W = piano.peso_piano
        else:
            W = calcola_peso_piano(modello, piano.id_piano)

        peso_per_piano[piano.id_piano] = W
        F_ond = W * C_s
        F_suss = F_ond * _FATTORE_SUSSULTORIO

        ondulatorio_x[piano.id_piano] = F_ond
        sussultorio_z[piano.id_piano] = F_suss

        passaggi.append(
            f"  Piano {piano.id_piano}: W={W:.1f} kg, "
            f"F_ond={F_ond:.1f} kg, F_suss={F_suss:.1f} kg"
        )

    taglio_base = sum(ondulatorio_x.values())
    passaggi.append(f"  Taglio alla base (ondulatorio): {taglio_base:.1f} kg")

    return ForzeSismicheTelaio(
        zona=zona_eff,
        C_s=C_s,
        ondulatorio_x=ondulatorio_x,
        sussultorio_z=sussultorio_z,
        peso_per_piano=peso_per_piano,
        passaggi=passaggi,
    )


def aggiorna_forze_piani(
    modello: ModelloTelaio,
    forze: ForzeSismicheTelaio,
) -> ModelloTelaio:
    """Aggiorna i campi forza_sismica_x/z dei piani nel modello.

    Non modifica in-place: ritorna una copia aggiornata dei piani.
    """
    piani_aggiornati = []
    for piano in modello.piani:
        h = piano.id_piano
        piani_aggiornati.append(
            PianoTelaio(
                id_piano=h,
                quota=piano.quota,
                peso_piano=forze.peso_per_piano.get(h, piano.peso_piano),
                forza_sismica_x=forze.ondulatorio_x.get(h, 0.0),
                forza_sismica_z=forze.sussultorio_z.get(h, 0.0),
                descrizione=piano.descrizione,
            )
        )
    # Crea nuovo modello con piani aggiornati
    return ModelloTelaio(
        nome=modello.nome,
        nodi=modello.nodi,
        aste=modello.aste,
        piani=piani_aggiornati,
        zona_sismica=modello.zona_sismica,
        note=modello.note,
    )
