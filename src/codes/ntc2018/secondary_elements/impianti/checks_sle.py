from __future__ import annotations

from ..common import StatoDannoSLE, classifica_danno_da_rapporto
from .models import ContestoSLEImpianto, ImpiantoSpec, RisultatoSLEImpianto


def calcola_spostamento_ammissibile(spec: ImpiantoSpec) -> float:
    if spec.categoria.value == "tubazione_sospesa":
        return 2.5
    elif spec.categoria.value == "canale_aria":
        return 2.0
    elif spec.categoria.value == "sistema_sprinkler":
        return 1.5
    else:
        return 1.0


def verifica_sle_impianto(
    spec: ImpiantoSpec, contesto: ContestoSLEImpianto, passaggi: list[str]
) -> RisultatoSLEImpianto:
    passaggi.append("=== VERIFICA SLE IMPIANTO ===")

    spostamento = contesto.spostamento_relativo_cm
    spostamento_amm = calcola_spostamento_ammissibile(spec)

    passaggi.append(f"Spostamento relativo = {spostamento:.2f} cm")
    passaggi.append(f"Spostamento ammissibile = {spostamento_amm:.2f} cm")

    rapporto = spostamento / spostamento_amm if spostamento_amm > 0 else float("inf")

    stato_danno, danno_giunti, danno_pannelli, intervento, note = classifica_danno_da_rapporto(
        rapporto
    )
    passaggi.append(f"Stato danno = {stato_danno.value}")

    collisione = rapporto > 2.0
    perdita_funz = stato_danno == StatoDannoSLE.INSICUREZZA

    return RisultatoSLEImpianto(
        stato_danno=stato_danno,
        spostamento_relativo_cm=spostamento,
        spostamento_ammissibile_cm=spostamento_amm,
        collisione_rischio=collisione,
        perdita_funzionalita=perdita_funz,
        intervento_necessario=intervento,
        note=note,
    )
