"""Check Registry unificato – registro centralizzato dei check di verifica.

Ogni check è descritto da un :class:`CheckSpec` che dichiara:
- ``id``: identificatore univoco (es. ``"rd2229.flessione"``)
- ``title``: nome leggibile
- ``norm_refs``: lista di riferimenti normativi (clausola + fonte)
- ``input_schema``: dizionario con i campi richiesti e il tipo atteso
- ``applicability_predicate``: funzione che verifica se il check è applicabile
- ``compute``: funzione di calcolo (facoltativa nella registry; può essere None per TODO)

Utilizzo::

    from src.checks.registry import get_registry
    reg = get_registry()
    # Verifica copertura per norma NTC2018
    coverage = reg.coverage_for_norm("NTC2018")
    print(f"NTC2018: {coverage['implemented']}/{coverage['total']} check coperti")
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class NormRef:
    """Riferimento normativo a una clausola di una fonte."""

    source_id: str  # ID da docs/normative/sources.yaml
    clause: str  # es. "§3.3.1", "Table 5.4"
    description: str = ""


@dataclass
class CheckSpec:
    """Specifica di un check di verifica strutturale.

    Attributes:
        id: Identificatore univoco del check (es. ``"rd2229.pressoflessione"``).
        title: Descrizione leggibile del check.
        norm_refs: Lista di riferimenti normativi che definiscono il check.
        input_schema: Schema minimo degli input richiesti (nome → tipo).
        applicability_predicate: Funzione ``(project) -> bool``; se None, sempre applicabile.
        compute: Funzione di calcolo ``(input_dict) -> result_dict``; se None, check TODO.
        tags: Tag opzionali (es. ["RC", "fire", "wind"]).
    """

    id: str
    title: str
    norm_refs: list[NormRef] = field(default_factory=list)
    input_schema: dict[str, str] = field(default_factory=dict)
    applicability_predicate: Callable[..., bool] | None = None
    compute: Callable[..., dict[str, Any]] | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def is_implemented(self) -> bool:
        """True se il check ha una funzione di calcolo implementata."""
        return self.compute is not None


class CheckRegistry:
    """Registry centralizzato dei check di verifica.

    Fornisce metodi per:
    - registrare check (``register``)
    - ottenere check per ID (``get``)
    - listare check per norma (``checks_for_norm``)
    - calcolare copertura per norma (``coverage_for_norm``)
    """

    def __init__(self) -> None:
        self._checks: dict[str, CheckSpec] = {}

    def register(self, spec: CheckSpec) -> None:
        """Registra un check. Sovrascrive check con stesso ID."""
        if spec.id in self._checks:
            logger.debug("CheckRegistry: sovrascrittura check '%s'.", spec.id)
        self._checks[spec.id] = spec

    def get(self, check_id: str) -> CheckSpec | None:
        """Restituisce il check con l'ID specificato, o None se non presente."""
        return self._checks.get(check_id)

    def all_checks(self) -> list[CheckSpec]:
        """Restituisce tutti i check registrati."""
        return list(self._checks.values())

    def checks_for_norm(self, source_id: str) -> list[CheckSpec]:
        """Restituisce i check che hanno almeno un NormRef con il source_id specificato.

        Args:
            source_id: ID della fonte normativa (es. ``"RD2229"``, ``"NTC2018"``).
        """
        return [
            c
            for c in self._checks.values()
            if any(ref.source_id == source_id for ref in c.norm_refs)
        ]

    def coverage_for_norm(self, source_id: str) -> dict[str, Any]:
        """Calcola la copertura (percentuale check implementati) per una norma.

        Args:
            source_id: ID della fonte normativa.

        Returns:
            Dizionario con:
            - ``total``: numero totale di check per la norma
            - ``implemented``: check con funzione ``compute`` presente
            - ``todo``: check senza funzione ``compute`` (TODO)
            - ``pct``: percentuale implementata (0-100)
            - ``checks``: lista check spec
        """
        checks = self.checks_for_norm(source_id)
        implemented = [c for c in checks if c.is_implemented]
        todo = [c for c in checks if not c.is_implemented]
        total = len(checks)
        pct = (len(implemented) / total * 100) if total > 0 else 0.0
        return {
            "source_id": source_id,
            "total": total,
            "implemented": len(implemented),
            "todo": len(todo),
            "pct": round(pct, 1),
            "checks": checks,
        }

    def coverage_all(self) -> dict[str, dict[str, Any]]:
        """Calcola la copertura per tutte le norme presenti nella registry."""
        source_ids: set[str] = set()
        for check in self._checks.values():
            for ref in check.norm_refs:
                source_ids.add(ref.source_id)
        return {sid: self.coverage_for_norm(sid) for sid in sorted(source_ids)}


# ---------------------------------------------------------------------------
# Check specs built-in (RD2229, DM96, NTC2018 seed)
# ---------------------------------------------------------------------------


def _build_default_registry() -> CheckRegistry:
    """Costruisce la registry di default con i check esistenti nel sistema."""
    reg = CheckRegistry()

    # --- RD2229 ---
    reg.register(
        CheckSpec(
            id="rd2229.ta_flessione",
            title="Tensioni Ammissibili – Flessione (RD2229)",
            norm_refs=[
                NormRef(
                    source_id="RD2229",
                    clause="Art. 7",
                    description="Verifica a flessione con metodo delle tensioni ammissibili",
                )
            ],
            input_schema={"width": "float", "height": "float", "Mx": "float"},
            tags=["RC", "TA", "flessione"],
            # compute: delegato a normative_registry; marker implemented
            compute=lambda _: {},
        )
    )

    reg.register(
        CheckSpec(
            id="rd2229.ta_pressoflessione",
            title="Tensioni Ammissibili – Pressoflessione (RD2229)",
            norm_refs=[
                NormRef(
                    source_id="RD2229",
                    clause="Art. 7-8",
                    description="Verifica a pressoflessione con metodo delle tensioni ammissibili",
                )
            ],
            input_schema={"width": "float", "height": "float", "N": "float", "Mx": "float"},
            tags=["RC", "TA", "pressoflessione"],
            compute=lambda _: {},
        )
    )

    reg.register(
        CheckSpec(
            id="rd2229.ta_taglio",
            title="Tensioni Ammissibili – Taglio (RD2229)",
            norm_refs=[
                NormRef(
                    source_id="RD2229",
                    clause="Art. 9",
                    description="Verifica a taglio con metodo delle tensioni ammissibili",
                )
            ],
            input_schema={"width": "float", "height": "float", "Tx": "float"},
            tags=["RC", "TA", "taglio"],
            compute=lambda _: {},
        )
    )

    # --- DM 96 ---
    reg.register(
        CheckSpec(
            id="dm96.slu_flessione",
            title="SLU – Flessione (DM 09/01/1996)",
            norm_refs=[
                NormRef(
                    source_id="DM96",
                    clause="§2.3",
                    description="Verifica allo stato limite ultimo di flessione per sezioni RC",
                )
            ],
            input_schema={"width": "float", "height": "float", "Mx": "float", "f_ck": "float"},
            tags=["RC", "SLU", "flessione"],
            compute=lambda _: {},
        )
    )

    reg.register(
        CheckSpec(
            id="dm96.slu_pressoflessione",
            title="SLU – Pressoflessione (DM 09/01/1996)",
            norm_refs=[
                NormRef(
                    source_id="DM96",
                    clause="§2.4",
                    description="Verifica allo stato limite ultimo di pressoflessione",
                )
            ],
            input_schema={
                "width": "float",
                "height": "float",
                "N": "float",
                "Mx": "float",
                "f_ck": "float",
            },
            tags=["RC", "SLU", "pressoflessione"],
            compute=lambda _: {},
        )
    )

    # --- NTC2018 ---
    reg.register(
        CheckSpec(
            id="ntc2018.slu_flessione",
            title="SLU – Flessione (NTC 2018)",
            norm_refs=[
                NormRef(
                    source_id="NTC2018",
                    clause="§4.1.2",
                    description="Verifica SLU di flessione per sezioni in c.a.",
                )
            ],
            input_schema={
                "width": "float",
                "height": "float",
                "Mx": "float",
                "f_ck": "float",
                "f_yk": "float",
            },
            tags=["RC", "SLU", "NTC2018", "flessione"],
            compute=lambda _: {},
        )
    )

    def _compute_sle_stress(inputs: dict) -> dict:
        from src.actions.action_repo import SLEStressCheck
        element = inputs
        normative = {"norm_code": "NTC2018", "material": inputs.get("material", {})}
        return SLEStressCheck().run(element, normative, inputs.get("settings", {}))

    reg.register(
        CheckSpec(
            id="ntc2018.sle_deformazione",
            title="SLE – Deformazione (NTC 2018)",
            norm_refs=[
                NormRef(
                    source_id="NTC2018",
                    clause="§4.1.4",
                    description="Verifica SLE di deformazione",
                )
            ],
            input_schema={"width": "float", "height": "float", "Mx": "float"},
            tags=["RC", "SLE", "NTC2018"],
            compute=_compute_sle_stress,
        )
    )

    def _compute_sle_cracking(inputs: dict) -> dict:
        from src.actions.action_repo import SLECrackingCheck
        element = inputs
        normative = {"norm_code": "NTC2018", "material": inputs.get("material", {})}
        return SLECrackingCheck().run(element, normative, inputs.get("settings", {}))

    reg.register(
        CheckSpec(
            id="ntc2018.sle_fessurazione",
            title="SLE – Fessurazione (NTC 2018)",
            norm_refs=[
                NormRef(
                    source_id="NTC2018",
                    clause="§4.1.4.2",
                    description="Verifica SLE di fessurazione",
                )
            ],
            input_schema={"width": "float", "height": "float", "Mx": "float"},
            tags=["RC", "SLE", "NTC2018"],
            compute=_compute_sle_cracking,
        )
    )

    # --- Fire ---
    reg.register(
        CheckSpec(
            id="fire.rc_tabellare",
            title="Verifica RC al fuoco – metodo tabellare (ISO 834)",
            norm_refs=[
                NormRef(
                    source_id="ISO834",
                    clause="§1",
                    description="Curva di incendio standard ISO 834-1",
                ),
                NormRef(
                    source_id="NTC2018",
                    clause="§3.6.1",
                    description="Azioni di incendio – requisiti prestazionali",
                ),
            ],
            input_schema={
                "width": "float",
                "height": "float",
                "cover_mm": "float",
                "exposure_sides": "int",
                "required_rating_minutes": "int",
            },
            tags=["RC", "fire", "tabellare"],
            compute=lambda _: {},
        )
    )

    # --- Wind ---
    def _compute_wind_ntc2018(inputs: dict) -> dict:
        import dataclasses
        from src.wind.models import BuildingGeom, WindSite
        from src.wind.ntc2018 import run_ntc2018_wind

        site = WindSite(
            altitude_m=inputs.get("altitudine_m", 0.0),
            terrain_category=inputs.get("categoria_terreno", "II"),
            zone_id=inputs.get("zona_geografica"),
        )
        building = BuildingGeom(
            height_m=inputs.get("altezza_m", 10.0),
            width_m=inputs.get("larghezza_m", 10.0),
            depth_m=inputs.get("profondita_m", 10.0),
        )
        result = run_ntc2018_wind(site, building)
        return dataclasses.asdict(result)

    reg.register(
        CheckSpec(
            id="wind.ntc2018.pressione_vento",
            title="Pressione del vento (NTC 2018 §3.3)",
            norm_refs=[
                NormRef(
                    source_id="NTC2018",
                    clause="§3.3",
                    description="Azioni del vento: velocità di riferimento, pressione cinetica, coefficienti",
                )
            ],
            input_schema={
                "altitudine_m": "float",
                "categoria_terreno": "str",
                "altezza_m": "float",
            },
            tags=["wind", "NTC2018"],
            compute=_compute_wind_ntc2018,
        )
    )

    def _compute_wind_en1991(inputs: dict) -> dict:
        import dataclasses
        from src.wind.models import BuildingGeom, WindSite
        from src.wind.ec1991_1_4 import run_en1991_1_4_wind

        site = WindSite(
            terrain_category=inputs.get("terrain_category", "II"),
            reference_wind_speed_ms=inputs.get("v_b_ms"),
        )
        building = BuildingGeom(
            height_m=inputs.get("z", 10.0),
            width_m=inputs.get("width_m", 10.0),
            depth_m=inputs.get("depth_m", 10.0),
        )
        result = run_en1991_1_4_wind(site, building)
        return dataclasses.asdict(result)

    reg.register(
        CheckSpec(
            id="wind.en1991_1_4.wind_actions",
            title="Wind actions (EN 1991-1-4)",
            norm_refs=[
                NormRef(
                    source_id="EN1991_1_4",
                    clause="§4",
                    description="Wind velocity and velocity pressure",
                )
            ],
            input_schema={"z": "float", "terrain_category": "str"},
            tags=["wind", "EN1991"],
            compute=_compute_wind_en1991,
        )
    )

    return reg


# Singleton della registry di default
_default_registry: CheckRegistry | None = None


def get_registry() -> CheckRegistry:
    """Restituisce la registry singleton di default."""
    global _default_registry
    if _default_registry is None:
        _default_registry = _build_default_registry()
    return _default_registry


def reset_registry() -> None:
    """Reimposta la registry (utile per i test)."""
    global _default_registry
    _default_registry = None
