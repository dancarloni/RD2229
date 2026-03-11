from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import (
    CategoriaImpianto,
    ContestoSLUImpianto,
    ImpiantoSpec,
    RisultatoSLUImpianto,
    TipoSupporto,
)

_RESISTENZE_BASE_KG: dict[CategoriaImpianto, float] = {
    CategoriaImpianto.TUBAZIONE_SOSPESA: 35.0,
    CategoriaImpianto.CANALE_ARIA: 45.0,
    CategoriaImpianto.APPARECCHIATURA: 50.0,
    CategoriaImpianto.QUADRO_ELETTRICO: 55.0,
    CategoriaImpianto.SISTEMA_SPRINKLER: 40.0,
}


def calcola_resistenza_supporti(spec: ImpiantoSpec) -> float:
    if spec.resistenza_supporto_kn is not None:
        return spec.resistenza_supporto_kn * 1000.0

    base = _RESISTENZE_BASE_KG[spec.categoria]

    if spec.tipo_supporto == TipoSupporto.SOSPENSIONE:
        base *= 1.2
    elif spec.tipo_supporto == TipoSupporto.STAFFAGGIO:
        base *= 0.9
    elif spec.tipo_supporto == TipoSupporto.INCOLLAGGIO:
        base *= 0.7

    if spec.numero_ancoraggi < 2:
        base *= 0.7
    elif spec.numero_ancoraggi >= 4:
        base *= 1.1

    if spec.presenza_giunto_flessibile:
        base *= 1.15

    return max(50.0, base)


def verifica_slu_impianto(
    spec: ImpiantoSpec, contesto: ContestoSLUImpianto, passaggi: list[str]
) -> RisultatoSLUImpianto:
    passaggi.append("=== VERIFICA SLU IMPIANTO ===")

    domanda = calcola_forza_sismica_locale(
        spec.massa_kg, contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    passaggi.append(f"Domanda sismica = {domanda:.2f} kg")

    resistenza = calcola_resistenza_supporti(spec)
    passaggi.append(f"Resistenza supporti = {resistenza:.2f} kg")

    continuita = domanda <= resistenza
    passaggi.append(f"Continuità funzionale: {'MANTENUTA' if continuita else 'COMPROMESSA'}")

    esito = domanda <= resistenza
    passaggi.append(f"Rapporto D/R = {domanda / resistenza:.3f} {'<= 1.0' if esito else '> 1.0'}")

    return RisultatoSLUImpianto(
        esito=esito,
        domanda_totale_kg=domanda,
        resistenza_supporti_kg=resistenza,
        capacita_continuita_funzionale=continuita,
    )
