"""Gestione livelli di conoscenza (LC) e fattori di confidenza (FC) per edifici esistenti.

Nota progettuale Fase R:
- Il livello LC e inserito esplicitamente dall'utente (nessun calcolo automatico in R.1).
- E sempre possibile applicare un override manuale di FC, con warning nel registro log.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.core.registro_log import registro
from src.core_calculus.lc_fc_adjustments import (
    AdjustedMaterialProperties,
    apply_lc_fc_adjustments,
    get_typical_fc_for_lc,
)

_MODULO_LOG = "esistenti.livelli_conoscenza"


class LivelloConoscenza(str, Enum):
    """Livelli di conoscenza NTC2018 per strutture esistenti."""

    LC1 = "LC1"
    LC2 = "LC2"
    LC3 = "LC3"

    @property
    def fc_default(self) -> float:
        """Ritorna il fattore di confidenza tipico associato al livello LC."""
        return get_typical_fc_for_lc(self.value)


@dataclass(frozen=True)
class ParametriIndagine:
    """Dati descrittivi della campagna conoscitiva (solo metadata in R.1).

    In R.1 il livello di conoscenza non viene derivato automaticamente da questi
    parametri: e scelto esplicitamente dall'utente.
    """

    livello_conoscenza: LivelloConoscenza
    tipo_rilievo: str = ""
    percentuale_elementi_indagati: float | None = None
    tipo_prove: str = ""
    note: str = ""


@dataclass(frozen=True)
class MaterialeConFC:
    """Risultato dell'adattamento materiale con FC applicato."""

    livello_conoscenza: LivelloConoscenza
    fc_usato: float
    proprieta: AdjustedMaterialProperties

    @classmethod
    def da_materiale(
        cls,
        materiale: Any,
        livello_conoscenza: LivelloConoscenza | str,
        fc_override: float | None = None,
        use_ntc2018: bool = True,
    ) -> MaterialeConFC:
        """Crea un adattamento materiale applicando FC a f_ck/f_yk."""
        livello = _normalizza_livello(livello_conoscenza)
        fc = risolvi_fc(livello, fc_override)

        proprieta = apply_lc_fc_adjustments(
            material=materiale,
            lc=livello.value,
            fc=fc,
            use_ntc2018=use_ntc2018,
        )

        registro.calcolo(
            modulo=_MODULO_LOG,
            operazione="Applicazione FC a materiale esistente",
            input_dati={
                "lc": livello.value,
                "fc": fc,
                "f_ck": getattr(materiale, "f_ck", None),
                "f_yk": getattr(materiale, "f_yk", None),
            },
            output_dati={
                "f_ck_adjusted": proprieta.f_ck_adjusted,
                "f_yk_adjusted": proprieta.f_yk_adjusted,
                "f_cd": proprieta.f_cd,
                "f_yd": proprieta.f_yd,
            },
            normativa="NTC2018 §8.5.4",
            formula="f_k,eff = f_k / FC",
            esito="OK",
        )

        return cls(
            livello_conoscenza=livello,
            fc_usato=fc,
            proprieta=proprieta,
        )


def risolvi_fc(
    livello_conoscenza: LivelloConoscenza | str,
    fc_override: float | None = None,
) -> float:
    """Risoluzione FC: default da LC o override utente validato.

    Regole:
    - LC e sempre input esplicito utente.
    - Override FC consentito sempre, con warning se presente.
    - Se LC1, emette avviso di elevata incertezza.
    """
    livello = _normalizza_livello(livello_conoscenza)

    if fc_override is None:
        fc = livello.fc_default
    else:
        _valida_fc(fc_override)
        fc = float(fc_override)
        registro.avviso(
            modulo=_MODULO_LOG,
            messaggio="Override manuale FC attivo",
            dettagli=f"LC={livello.value}, FC_override={fc}",
        )

    if livello is LivelloConoscenza.LC1:
        registro.avviso(
            modulo=_MODULO_LOG,
            messaggio="LC1 selezionato: elevata incertezza dei dati",
            dettagli=f"FC applicato={fc}",
        )

    return fc


def applica_fc_a_resistenza(
    f_d: float,
    livello_conoscenza: LivelloConoscenza | str,
    fc_override: float | None = None,
) -> float:
    """Applica FC a una resistenza di progetto generica.

    Formula: f_d,eff = f_d / FC
    """
    if f_d <= 0:
        raise ValueError(f"f_d deve essere positivo, ricevuto: {f_d}")

    fc = risolvi_fc(livello_conoscenza, fc_override)
    f_d_eff = f_d / fc

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Applicazione FC a resistenza di progetto",
        input_dati={"f_d": f_d, "fc": fc},
        output_dati={"f_d_eff": f_d_eff},
        normativa="NTC2018 §8.5.4",
        formula="f_d,eff = f_d / FC",
        esito="OK",
    )

    return f_d_eff


def _normalizza_livello(livello: LivelloConoscenza | str) -> LivelloConoscenza:
    if isinstance(livello, LivelloConoscenza):
        return livello
    try:
        return LivelloConoscenza(livello)
    except ValueError as exc:
        validi = [x.value for x in LivelloConoscenza]
        raise ValueError(f"Livello di conoscenza non valido: {livello}. Valori ammessi: {validi}") from exc


def _valida_fc(fc: float) -> None:
    if fc < 1.0 or fc > 1.5:
        raise ValueError(f"FC fuori range [1.0, 1.5]: {fc}")
