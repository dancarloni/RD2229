"""ProjectModel – fonte unica di verità del progetto RD2229.

Schema versioned JSON per persistenza e pipeline di calcolo.
Tutte le sezioni hanno defaults documentati e sono serializzabili in JSON
tramite :func:`dataclasses.asdict`.

Versioning:
    - ``schema_version`` è obbligatorio in ogni file salvato.
    - Formato: ``"MAJOR.MINOR.PATCH"`` (es. ``"1.0.0"``).
    - Migrazioni gestite in :mod:`src.project.repository`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CURRENT_SCHEMA_VERSION = "1.0.0"


@dataclass
class ProjectInfo:
    """Informazioni generali sul progetto."""

    name: str = ""
    description: str = ""
    author: str = ""
    # ISO-8601 timestamp creazione/modifica
    created_at: str = ""
    updated_at: str = ""


@dataclass
class GeometryEntry:
    """Singolo elemento geometrico (sezione, pilastro, trave, …).

    ``id`` univoco all'interno del progetto; ``type`` è una stringa libera
    (es. ``"RECTANGULAR"``, ``"CIRCULAR"``).
    """

    id: str = ""
    type: str = ""
    width: float = 0.0   # cm o mm (unità dipende da code_settings)
    height: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class MaterialEntry:
    """Singolo materiale (calcestruzzo o acciaio).

    ``material_class`` è opzionale (es. ``"C25/30"``).
    """

    id: str = ""
    type: str = ""  # "concrete" | "steel"
    material_class: str = ""
    f_ck: float | None = None   # MPa  (calcestruzzo)
    f_yk: float | None = None   # MPa  (acciaio)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadEntry:
    """Singola combinazione di carico su un elemento."""

    element_id: str = ""
    N: float | None = None    # kN
    Mx: float | None = None   # kNm
    My: float | None = None   # kNm
    Mz: float | None = None   # kNm
    Tx: float | None = None   # kN
    Ty: float | None = None   # kN
    description: str = ""


@dataclass
class SeismicInputs:
    """Parametri sismici NTC2018 (opzionali).

    Popolati dal paste-service di EdiLus-MS se disponibile;
    se assenti la pipeline li ignora con un warning.
    """

    class_of_use: str = ""
    vita_nominale_years: int = 0
    vr_years: int = 0
    site_label: str = ""
    # Dati grezzi del profilo di pericolosità (dizionario serializzabile)
    hazard_profile: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeSettings:
    """Impostazioni del codice normativo e unità di misura."""

    norm_code: str = "RD2229"           # es. "RD2229" | "NTC2018"
    limit_states: list[str] = field(default_factory=lambda: ["TA"])
    units_force: str = "kN"             # "kN" | "kg"
    units_length: str = "cm"            # "cm" | "mm"


@dataclass
class ResultsRef:
    """Riferimento ai risultati di calcolo (metadata).

    Non contiene i valori numerici; questi vengono salvati in un file
    separato puntato da ``results_path``.
    """

    results_path: str = ""
    computed_at: str = ""
    schema_version_input: str = ""
    summary: str = ""


@dataclass
class ProjectModel:
    """Modello dati del progetto RD2229 – fonte unica di verità.

    Tutti i campi hanno defaults sensati per permettere la creazione di
    un progetto minimale senza argomenti obbligatori (tranne
    ``schema_version`` che viene impostato automaticamente al valore
    corrente).

    Serializzazione::

        import dataclasses, json
        data = dataclasses.asdict(project)
        json.dumps(data)
    """

    schema_version: str = field(default=CURRENT_SCHEMA_VERSION)
    project_info: ProjectInfo = field(default_factory=ProjectInfo)
    geometry: list[GeometryEntry] = field(default_factory=list)
    materials: list[MaterialEntry] = field(default_factory=list)
    loads: list[LoadEntry] = field(default_factory=list)
    seismic_inputs: SeismicInputs = field(default_factory=SeismicInputs)
    code_settings: CodeSettings = field(default_factory=CodeSettings)
    results_ref: ResultsRef = field(default_factory=ResultsRef)
