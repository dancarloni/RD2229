"""Package geotecnica (Fase P).

Espone API pubbliche per:
- P.1: portanza fondazioni superficiali
- P.2: cedimenti (elastico e consolidazione)
- P.3: fondazioni profonde su pali
- P.4: muri di sostegno
- P.5: rischio liquefazione (Seed-Idriss)
"""

from .cedimenti import (
    calcola_cedimenti,
    cedimento_consolidazione_primaria,
    cedimento_elastico_boussinesq,
    coefficiente_tempo_consolidazione,
    grado_consolidazione_medio,
)
from .fondazioni_superficiali import verifica_portanza_slu
from .liquefazione import (
    calcola_crr_7_5,
    calcola_csr,
    calcola_liquefazione,
    calcola_msf,
    classifica_liquefazione,
    correggi_n160,
    fattore_riduzione_r_d,
)
from .models import (
    ApproccioSLU,
    CaricoFondazione,
    ClasseLiquefazione,
    CombinazioneDA1,
    CorrelazioneSPTCPT,
    GeometriaFondazione,
    GeometriaMuro,
    InputCedimenti,
    InputGruppoPali,
    InputLiquefazione,
    InputMuroSostegno,
    InputPortanzaFondazione,
    InputPortanzaPalo,
    NormaGeotecnica,
    ParametriTerreno,
    RisultatoCedimenti,
    RisultatoLiquefazione,
    RisultatoMuroSostegno,
    RisultatoPortanzaFondazione,
    RisultatoPortanzaPalo,
    RisultatoStratoLiquefazione,
    RisultatoVerificaMuro,
    RisultatoVerificaSLU,
    StratoLiquefazione,
    TipologiaPalo,
    TipoMuro,
    UnitaTensione,
)
from .muri_sostegno import (
    ka_coulomb,
    ka_rankine,
    kp_rankine,
    spinta_attiva_totale_kg_cm,
    verifica_muro_sostegno,
)
from .norme import CoefficientiParzialiGeotecnici, NormaGeotecnicaBase, crea_norma_geotecnica
from .pali import (
    calcola_efficienza_gruppo,
    calcola_portanza_palo,
    efficienza_gruppo_converse_labarre,
)
from .utils import kg_cm2_to_kpa, kpa_to_kg_cm2, sovraccarico_geostatico_kg_cm2

__all__ = [
    # Enums
    "ApproccioSLU",
    "ClasseLiquefazione",
    "CombinazioneDA1",
    "CorrelazioneSPTCPT",
    "NormaGeotecnica",
    "TipologiaPalo",
    "TipoMuro",
    "UnitaTensione",
    # Dataclass input
    "CaricoFondazione",
    "GeometriaFondazione",
    "GeometriaMuro",
    "InputCedimenti",
    "InputGruppoPali",
    "InputLiquefazione",
    "InputMuroSostegno",
    "InputPortanzaFondazione",
    "InputPortanzaPalo",
    "ParametriTerreno",
    "StratoLiquefazione",
    # Dataclass output
    "RisultatoCedimenti",
    "RisultatoLiquefazione",
    "RisultatoMuroSostegno",
    "RisultatoPortanzaFondazione",
    "RisultatoPortanzaPalo",
    "RisultatoStratoLiquefazione",
    "RisultatoVerificaMuro",
    "RisultatoVerificaSLU",
    # Norme
    "CoefficientiParzialiGeotecnici",
    "NormaGeotecnicaBase",
    "crea_norma_geotecnica",
    # P.1 — Fondazioni superficiali
    "verifica_portanza_slu",
    # P.2 — Cedimenti
    "calcola_cedimenti",
    "cedimento_consolidazione_primaria",
    "cedimento_elastico_boussinesq",
    "coefficiente_tempo_consolidazione",
    "grado_consolidazione_medio",
    # P.3 — Pali
    "calcola_efficienza_gruppo",
    "calcola_portanza_palo",
    "efficienza_gruppo_converse_labarre",
    # P.4 — Muri di sostegno
    "ka_coulomb",
    "ka_rankine",
    "kp_rankine",
    "spinta_attiva_totale_kg_cm",
    "verifica_muro_sostegno",
    # P.5 — Liquefazione
    "calcola_crr_7_5",
    "calcola_csr",
    "calcola_liquefazione",
    "calcola_msf",
    "classifica_liquefazione",
    "correggi_n160",
    "fattore_riduzione_r_d",
    # Utils
    "kg_cm2_to_kpa",
    "kpa_to_kg_cm2",
    "sovraccarico_geostatico_kg_cm2",
]
