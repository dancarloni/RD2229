from __future__ import annotations

from ..common import calcola_forza_sismica_locale
from .models import ContestoSLUScaffalatura, RisultatoSLUScaffalatura, ScaffalaturaSpec


def calcola_capacita_ribaltamento(spec: ScaffalaturaSpec) -> float:
    if spec.massa_totale_kg() == 0:
        return 5000.0
    momento_stabilizzante = (spec.larghezza_cm / 2.0) * spec.massa_totale_kg()
    baricentro = spec.baricentro_relativo()
    forza_ribaltamento = momento_stabilizzante / baricentro if baricentro > 0 else 5000.0
    return max(100.0, forza_ribaltamento)


def calcola_capacita_ancoraggi(spec: ScaffalaturaSpec) -> float:
    if not spec.ancorata:
        return float("inf")
    base = 200.0 if spec.tipo.value == "heavy_duty" else 100.0
    base *= 4 if spec.tipo.value == "heavy_duty" else 2
    return max(150.0, base)


def verifica_slu_scaffalatura(
    spec: ScaffalaturaSpec, contesto: ContestoSLUScaffalatura, passaggi: list[str]
) -> RisultatoSLUScaffalatura:
    passaggi.append("=== VERIFICA SLU SCAFFALATURA ===")

    domanda = calcola_forza_sismica_locale(
        spec.massa_totale_kg(), contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    cap_rib = calcola_capacita_ribaltamento(spec)
    cap_anc = calcola_capacita_ancoraggi(spec)

    passaggi.append(f"Domanda = {domanda:.2f} kg")
    passaggi.append(f"Capacità ribaltamento = {cap_rib:.2f} kg")
    passaggi.append(f"Capacità ancoraggi = {cap_anc:.2f} kg")

    meccanismo = "ribaltamento" if cap_rib <= cap_anc else "ancoraggi"
    resistenza = min(cap_rib, cap_anc)
    esito = domanda <= resistenza

    return RisultatoSLUScaffalatura(
        esito=esito,
        domanda_sismica_kg=domanda,
        capacita_ribaltamento_kg=cap_rib,
        capacita_ancoraggi_kg=cap_anc,
        meccanismo_critico=meccanismo,
    )
