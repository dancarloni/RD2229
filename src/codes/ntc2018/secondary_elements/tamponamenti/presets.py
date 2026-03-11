"""
Preset e caricamento configurazioni per tamponamenti secondari (Fase S1).

Gestisce:
- Caricamento di preset da file JSON (data/tamponamenti_presets.json)
- Creazione di tamponamenti predefiniti per rapid input
- Validazione e fallback a default
"""

import json
from pathlib import Path

from .models import SpecAncoraggio, TamponamentoSpec, TipoAncoraggio, TipoVincolo

# Percorso ai preset
PRESETS_PATH = (
    Path(__file__).parent.parent.parent.parent.parent.parent / "data" / "tamponamenti_presets.json"
)


def carica_presets_da_json(filepath: Path | None = None) -> dict:
    """
    Carica preset di tamponamenti da file JSON.

    Struttura JSON attesa:
    {
        "muratura_tradizionale": {
            "nome": "Muratura in laterizio portante",
            "parametri": { ... },
            "ancoraggi": [ ... ]
        },
        ...
    }

    Ritorna: dict con chiave → specifica di preset
    """
    if filepath is None:
        filepath = PRESETS_PATH

    if not filepath.exists():
        print(f"Avviso: file preset non trovato in {filepath}")
        return {}

    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Errore nel caricamento preset: {e}")
        return {}


def crea_spec_da_preset(preset_data: dict) -> TamponamentoSpec:
    """
    Costruisce TamponamentoSpec partendo da dict di preset.
    """

    # Estrai parametri geometrici
    geo = preset_data.get("geometria", {})

    # Estrai ancoraggi
    ancoraggi_list = []
    for ank_data in preset_data.get("ancoraggi", []):
        tipo_str = ank_data.get("tipo", "vite_metallo")
        tipo_enum = {
            "vite_metallo": TipoAncoraggio.VITE_METALLO,
            "tassello_chimico": TipoAncoraggio.TASSELLO_CHIMICO,
            "tassello_meccanico": TipoAncoraggio.TASSELLO_MECCANICO,
            "saldatura": TipoAncoraggio.SALDATURA,
        }.get(tipo_str, TipoAncoraggio.VITE_METALLO)

        anc = SpecAncoraggio(
            tipo=tipo_enum,
            diametro_mm=ank_data.get("diametro_mm", 10.0),
            materiale=ank_data.get("materiale", "acciaio C45"),
            resistenza_trazione_mpa=ank_data.get("resistenza_trazione_mpa", 400.0),
            resistenza_taglio_mpa=ank_data.get("resistenza_taglio_mpa", 250.0),
            numero_fissaggi=ank_data.get("numero_fissaggi", 4),
            interasse_mm=ank_data.get("interasse_mm"),
            profondita_ancoraggio_mm=ank_data.get("profondita_ancoraggio_mm"),
            spessore_acciaio_mm=ank_data.get("spessore_acciaio_mm"),
        )
        ancoraggi_list.append(anc)

    # Estrai vincoli
    vincolo_sup_str = preset_data.get("vincolo_superiore", "incastro_perfetto")
    vincolo_inf_str = preset_data.get("vincolo_inferiore", "incastro_perfetto")

    vincolo_sup = {
        "incastro_perfetto": TipoVincolo.INCASTRO,
        "cerniera_orizzontale": TipoVincolo.CERNIERA_ORIZZONTALE,
        "appoggio_libero": TipoVincolo.APPOGGIO_LIBERO,
        "controvento_elastico_laterale": TipoVincolo.CONTROVENTO_ELASTICO,
    }.get(vincolo_sup_str, TipoVincolo.INCASTRO)

    vincolo_inf = {
        "incastro_perfetto": TipoVincolo.INCASTRO,
        "cerniera_orizzontale": TipoVincolo.CERNIERA_ORIZZONTALE,
        "appoggio_libero": TipoVincolo.APPOGGIO_LIBERO,
        "controvento_elastico_laterale": TipoVincolo.CONTROVENTO_ELASTICO,
    }.get(vincolo_inf_str, TipoVincolo.INCASTRO)

    return TamponamentoSpec(
        altezza_cm=geo.get("altezza_cm", 250.0),
        larghezza_cm=geo.get("larghezza_cm", 300.0),
        spessore_cm=geo.get("spessore_cm", 12.0),
        massa_superficiale_kg_m2=preset_data.get("massa_superficiale_kg_m2", 250.0),
        tipologia=preset_data.get("tipologia", "muratura tradizionale"),
        resistenza_compressione_mpa=preset_data.get("resistenza_compressione_mpa"),
        resistenza_taglio_mpa=preset_data.get("resistenza_taglio_mpa"),
        vincolo_superiore=vincolo_sup,
        vincolo_inferiore=vincolo_inf,
        controvento_laterale=preset_data.get("controvento_laterale", False),
        rigidezza_controvento_elastico_kg_cm=preset_data.get(
            "rigidezza_controvento_elastico_kg_cm"
        ),
        ancoraggi=ancoraggi_list,
        drift_capacita_perc=preset_data.get("drift_capacita_perc", 1.5),
        area_aperture_cm2=preset_data.get("area_aperture_cm2", 0.0),
        numero_aperture=preset_data.get("numero_aperture", 0),
        note_decisionali=preset_data.get("note_decisionali", ""),
    )


def get_preset(nome: str, filepath: Path | None = None) -> TamponamentoSpec | None:
    """
    Estrae un preset per nome.

    Se non trovato, ritorna None.
    """
    presets = carica_presets_da_json(filepath)

    if nome not in presets:
        return None

    return crea_spec_da_preset(presets[nome])


def lista_preset_disponibili(filepath: Path | None = None) -> list[str]:
    """Ritorna lista dei preset disponibili."""
    presets = carica_presets_da_json(filepath)
    return list(presets.keys())


# Preset hardcoded di fallback (per quando JSON non è disponibile)
PRESET_MURATURA_TRADIZIONALE = TamponamentoSpec(
    altezza_cm=300.0,
    larghezza_cm=400.0,
    spessore_cm=12.0,
    massa_superficiale_kg_m2=240.0,
    tipologia="muratura in laterizio portante",
    resistenza_compressione_mpa=2.5,
    resistenza_taglio_mpa=0.3,
    vincolo_superiore=TipoVincolo.INCASTRO,
    vincolo_inferiore=TipoVincolo.INCASTRO,
    ancoraggi=[
        SpecAncoraggio(
            tipo=TipoAncoraggio.VITE_METALLO,
            diametro_mm=10.0,
            materiale="acciaio C45",
            resistenza_trazione_mpa=400.0,
            resistenza_taglio_mpa=250.0,
            numero_fissaggi=8,
            interasse_mm=100.0,
        )
    ],
    drift_capacita_perc=1.5,
)

PRESET_CLS_PREFABBRICATO = TamponamentoSpec(
    altezza_cm=280.0,
    larghezza_cm=350.0,
    spessore_cm=15.0,
    massa_superficiale_kg_m2=350.0,
    tipologia="cls prefabbricato leggero",
    resistenza_compressione_mpa=25.0,
    resistenza_taglio_mpa=2.0,
    vincolo_superiore=TipoVincolo.INCASTRO,
    vincolo_inferiore=TipoVincolo.CERNIERA_ORIZZONTALE,
    ancoraggi=[
        SpecAncoraggio(
            tipo=TipoAncoraggio.TASSELLO_CHIMICO,
            diametro_mm=12.0,
            materiale="resina epossidica",
            resistenza_trazione_mpa=350.0,
            resistenza_taglio_mpa=200.0,
            numero_fissaggi=6,
            profondita_ancoraggio_mm=80.0,
        )
    ],
    drift_capacita_perc=2.0,
)

PRESET_FACCIATA_LEGGERA = TamponamentoSpec(
    altezza_cm=250.0,
    larghezza_cm=300.0,
    spessore_cm=8.0,
    massa_superficiale_kg_m2=80.0,
    tipologia="facciata leggera in alluminio",
    resistenza_compressione_mpa=None,
    resistenza_taglio_mpa=None,
    vincolo_superiore=TipoVincolo.INCASTRO,
    vincolo_inferiore=TipoVincolo.APPOGGIO_LIBERO,
    controvento_laterale=True,
    rigidezza_controvento_elastico_kg_cm=5.0,
    ancoraggi=[
        SpecAncoraggio(
            tipo=TipoAncoraggio.VITE_METALLO,
            diametro_mm=8.0,
            materiale="acciaio inox A4",
            resistenza_trazione_mpa=350.0,
            resistenza_taglio_mpa=200.0,
            numero_fissaggi=12,
            interasse_mm=50.0,
        )
    ],
    drift_capacita_perc=2.5,
    note_decisionali="Facciata con controventi laterali elastici; verifica dinamica consigliata.",
)
