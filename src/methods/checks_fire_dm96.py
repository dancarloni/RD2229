"""
Verifiche di resistenza al fuoco - DM 9/3/2007, DM 16/2/2007.

Modulo per le verifiche di resistenza al fuoco di elementi in cemento armato
normale (e ganci per c.a.p.) secondo la normativa italiana sull'incendio.

Riferimenti normativi principali:
- DM 9 marzo 2007: criteri generali di resistenza al fuoco
  (metodi tabellare, semplificato, analitico, sperimentale)
- DM 16 febbraio 2007: classi di resistenza al fuoco (R30, R60, R90, R120, ...)
- DM 9/1/1996 e DM 14/02/1992: proprieta meccaniche di base
- EC2 Parte 1-2: formule di dettaglio (se richiamate)

Struttura del modulo:
- FireVerificationConfig: dataclass di configurazione incendio
- check_fire_resistance_beam_rc: trave c.a.
- check_fire_resistance_column_rc: pilastro c.a.
- check_fire_resistance_slab_rc: solaio c.a.
- check_fire_resistance_beam_cap: trave c.a.p. (gancio futuro)

Implementazione iniziale: placeholder ben documentati con TODO.
Tutti i parametri incendio (classe R, lati esposti, protezione, metodo di calcolo)
NON sono hardcodati e devono essere forniti tramite FireVerificationConfig
o template.extra_params.

Tutti i messaggi utente sono in italiano.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from src.core_calculus.contracts import (
    CalcInput,
    NormReference,
    SingleCheckResult,
    VerificationTemplate,
)

# ==============================================================================
# CONFIGURAZIONE INCENDIO
# ==============================================================================


@dataclass
class FireVerificationConfig:
    """Configurazione per la verifica di resistenza al fuoco di un elemento.

    Questa struttura dati raccoglie tutti i parametri necessari per eseguire
    una verifica di resistenza al fuoco. E' pensata per essere compilata dalla
    GUI e passata al core di calcolo tramite CalcInput.extra o template.extra_params.

    Nessun parametro a scelta dell'utente e' hardcodato nel core.

    Attributi
    ---------
    fire_exposure_class : str
        Descrittore dell'esposizione al fuoco (es. livello di carico d'incendio).
    required_fire_resistance_class : str
        Classe di resistenza richiesta: 'R30', 'R60', 'R90', 'R120', ecc.
    exposed_sides : int
        Numero di lati della sezione esposti al fuoco (1, 2, 3, 4).
    protection_type : str
        Tipo di protezione aggiuntiva: 'none', 'intonaco', 'cartongesso', ecc.
    protection_thickness_mm : float
        Spessore della protezione [mm] (0 se nessuna protezione).
    design_method : str
        Metodo di verifica scelto dall'utente:
        'tabellare', 'semplificato', 'analitico'.
    user_temperature_limits : dict
        Temperature critiche personalizzate dall'utente [gradi C].
        Es. {"steel": 500.0, "concrete": 500.0}.
        Se vuoto, si usano i valori standard da norma (quando implementati).
    note : str
        Note libere per tracciabilita.

    NormReference: DM 9/3/2007, DM 16/2/2007

    TODO: valutare aggiunta campo fire_config: Optional[FireVerificationConfig]
    in CalcInput, previo allineamento con il maintainer del core.
    """

    fire_exposure_class: str = ""
    required_fire_resistance_class: str = ""
    exposed_sides: int = 1
    protection_type: str = "none"
    protection_thickness_mm: float = 0.0
    design_method: str = "tabellare"
    user_temperature_limits: dict = dataclasses.field(default_factory=dict)
    note: str = ""


def _extract_fire_config(calc_input: CalcInput, template: VerificationTemplate) -> FireVerificationConfig | None:
    """Estrae la configurazione incendio da CalcInput.extra o template.extra_params.

    Ritorna None se la configurazione non e' presente.
    """
    # Prova da CalcInput.extra
    fire_cfg = calc_input.extra.get("fire_config", None)
    if isinstance(fire_cfg, FireVerificationConfig):
        return fire_cfg
    if isinstance(fire_cfg, dict):
        return FireVerificationConfig(
            **{k: v for k, v in fire_cfg.items() if k in FireVerificationConfig.__dataclass_fields__}
        )

    # Prova da template.extra_params
    fire_cfg = template.extra_params.get("fire_config", None)
    if isinstance(fire_cfg, FireVerificationConfig):
        return fire_cfg
    if isinstance(fire_cfg, dict):
        return FireVerificationConfig(
            **{k: v for k, v in fire_cfg.items() if k in FireVerificationConfig.__dataclass_fields__}
        )

    # Prova campi singoli da template.extra_params
    rfc = template.extra_params.get("required_fire_resistance_class", None)
    if rfc:
        return FireVerificationConfig(
            required_fire_resistance_class=rfc,
            exposed_sides=template.extra_params.get("exposed_sides", 1),
            design_method=template.extra_params.get("design_method", "tabellare"),
            protection_type=template.extra_params.get("protection_type", "none"),
        )

    return None


_FIRE_NORM_REF = NormReference(
    norm_code="FIRE_DM2007",
    chapter="DM 9/3/2007",
    paragraph="Resistenza al fuoco",
    description_it="Verifica di resistenza al fuoco secondo DM 9/3/2007 e DM 16/2/2007",
)


# ==============================================================================
# CHECK INCENDIO C.A.
# ==============================================================================


def check_fire_resistance_beam_rc(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica di resistenza al fuoco di una trave in c.a.

    Utilizza il metodo tabellare/semplificato (se definito) in base alla
    classe R richiesta, copriferro, dimensioni, esposizione (exposed_sides).

    Legge la configurazione FireVerificationConfig da CalcInput.extra
    o template.extra_params.

    Parametri
    ---------
    calc_input : CalcInput
        Dati di input (sezione, armature, copriferro).
    template : VerificationTemplate
        Template della verifica incendio.

    Ritorna
    -------
    SingleCheckResult
        Risultato della verifica.

    NormReference: DM 9/3/2007, DM 16/2/2007, EC2 Parte 1-2

    TODO: implementare logica tabellare (spessori minimi, copriferri minimi
    da tabelle DM 9/3/2007 per travi in funzione di classe R e esposizione).
    """
    fire_cfg = _extract_fire_config(calc_input, template)

    if fire_cfg is None or not fire_cfg.required_fire_resistance_class:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"implementation_status": "missing_config"},
            messages_it=[
                "Configurazione incendio non specificata.",
                "Impostare required_fire_resistance_class in fire_config.",
            ],
            limit_state="FIRE",
            norm_references=[_FIRE_NORM_REF],
        )

    section = calc_input.section
    b_info = ""
    if section and hasattr(section, "width"):
        b_info = f"Larghezza trave: b = {section.width/10:.1f} cm"

    messages_it = [
        "Verifica resistenza al fuoco: TRAVE C.A.",
        f"Classe richiesta: {fire_cfg.required_fire_resistance_class}",
        f"Lati esposti: {fire_cfg.exposed_sides}",
        f"Metodo: {fire_cfg.design_method}",
        f"Protezione: {fire_cfg.protection_type}"
        + (f" ({fire_cfg.protection_thickness_mm} mm)" if fire_cfg.protection_thickness_mm > 0 else ""),
        b_info,
        "",
        "TODO: implementazione metodo tabellare/semplificato.",
        "Richiede tabelle DM 9/3/2007: spessori minimi e copriferri",
        "minimi per travi in funzione di classe R e numero lati esposti.",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={
            "required_class": fire_cfg.required_fire_resistance_class,
            "exposed_sides": fire_cfg.exposed_sides,
            "design_method": fire_cfg.design_method,
            "implementation_status": "TODO",
        },
        messages_it=messages_it,
        limit_state="FIRE",
        norm_references=[_FIRE_NORM_REF],
    )


def check_fire_resistance_column_rc(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica di resistenza al fuoco di un pilastro in c.a.

    In prima fase, placeholder con TODO ben documentato.

    NormReference: DM 9/3/2007, DM 16/2/2007, EC2 Parte 1-2

    TODO: implementare metodo tabellare per pilastri
    (dimensioni minime, copriferri minimi, snellezza a caldo).
    """
    fire_cfg = _extract_fire_config(calc_input, template)

    if fire_cfg is None or not fire_cfg.required_fire_resistance_class:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"implementation_status": "missing_config"},
            messages_it=[
                "Configurazione incendio non specificata.",
                "Impostare required_fire_resistance_class in fire_config.",
            ],
            limit_state="FIRE",
            norm_references=[_FIRE_NORM_REF],
        )

    section = calc_input.section
    dims_info = ""
    if section and hasattr(section, "width") and hasattr(section, "height"):
        dims_info = f"Sezione: {section.width/10:.1f} x {section.height/10:.1f} cm"

    messages_it = [
        "Verifica resistenza al fuoco: PILASTRO C.A.",
        f"Classe richiesta: {fire_cfg.required_fire_resistance_class}",
        f"Lati esposti: {fire_cfg.exposed_sides}",
        f"Metodo: {fire_cfg.design_method}",
        dims_info,
        "",
        "TODO: implementazione metodo tabellare per pilastri.",
        "Richiede tabelle DM 9/3/2007: dimensioni minime sezione",
        "e copriferri minimi in funzione di classe R.",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={
            "required_class": fire_cfg.required_fire_resistance_class,
            "exposed_sides": fire_cfg.exposed_sides,
            "implementation_status": "TODO",
        },
        messages_it=messages_it,
        limit_state="FIRE",
        norm_references=[_FIRE_NORM_REF],
    )


def check_fire_resistance_slab_rc(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Verifica di resistenza al fuoco di un solaio/piastra in c.a.

    NormReference: DM 9/3/2007, DM 16/2/2007, EC2 Parte 1-2

    TODO: implementare metodo tabellare per solai
    (spessore minimo, copriferro minimo, tipo di solaio).
    """
    fire_cfg = _extract_fire_config(calc_input, template)

    if fire_cfg is None or not fire_cfg.required_fire_resistance_class:
        return SingleCheckResult(
            template_id=template.template_id,
            ok=False,
            utilisation=None,
            details={"implementation_status": "missing_config"},
            messages_it=[
                "Configurazione incendio non specificata.",
                "Impostare required_fire_resistance_class in fire_config.",
            ],
            limit_state="FIRE",
            norm_references=[_FIRE_NORM_REF],
        )

    messages_it = [
        "Verifica resistenza al fuoco: SOLAIO C.A.",
        f"Classe richiesta: {fire_cfg.required_fire_resistance_class}",
        f"Lati esposti: {fire_cfg.exposed_sides}",
        f"Metodo: {fire_cfg.design_method}",
        "",
        "TODO: implementazione metodo tabellare per solai.",
        "Richiede tabelle DM 9/3/2007: spessore minimo solaio",
        "e copriferro minimo in funzione di classe R.",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={
            "required_class": fire_cfg.required_fire_resistance_class,
            "implementation_status": "TODO",
        },
        messages_it=messages_it,
        limit_state="FIRE",
        norm_references=[_FIRE_NORM_REF],
    )


def check_fire_resistance_beam_cap(calc_input: CalcInput, template: VerificationTemplate) -> SingleCheckResult:
    """Gancio per verifica resistenza al fuoco di trave in c.a.p.

    In futuro dovra:
    - leggere PrecompressionData (quando integrata in CalcInput)
    - considerare riduzioni di resistenza a caldo per calcestruzzo e acciaio
      da precompressione
    - considerare perdite aggiuntive per effetto temperatura
    - utilizzare temperature critiche specifiche per acciaio da precompressione
      (tipicamente piu basse rispetto ad acciaio ordinario)

    NormReference: DM 9/3/2007, DM 16/2/2007, DM 9/1/1996, EC2 Parte 1-2

    TODO: implementazione completa. Per acciai da precompressione le temperature
    critiche sono generalmente piu basse (350-400 gradi C vs 500 gradi C per acciaio
    ordinario). Verificare con DM 9/3/2007 e EC2 Parte 1-2.
    """
    messages_it = [
        "Verifica resistenza al fuoco: TRAVE C.A.P. (precompresso)",
        "",
        "GANCIO: implementazione da completare.",
        "",
        "TODO: richiede integrazione PrecompressionData in CalcInput.",
        "Aspetti da implementare:",
        "  - riduzione resistenza calcestruzzo a caldo",
        "  - riduzione resistenza acciaio da precompressione a caldo",
        "  - temperature critiche acciaio da precompressione",
        "    (tipicamente 350-400 gradi C, inferiori ad acciaio ordinario)",
        "  - perdite aggiuntive per effetto temperatura",
        "  - copriferro minimo per cavi di precompressione",
        "",
        "NormReference: DM 9/3/2007, DM 16/2/2007, EC2 Parte 1-2",
    ]

    return SingleCheckResult(
        template_id=template.template_id,
        ok=False,
        utilisation=None,
        details={"implementation_status": "TODO"},
        messages_it=messages_it,
        limit_state="FIRE",
        norm_references=[_FIRE_NORM_REF],
    )
