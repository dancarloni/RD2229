"""Wind Action Service – orchestrazione multi-norma per il calcolo del vento.

Supporta metodi: "NTC2018", "EN1991_1_4", "CNR_DT207", "hybrid".
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from src.wind.models import BuildingGeom, WindSite
from src.wind.outputs import WindResults

logger = logging.getLogger(__name__)


@dataclass
class WindConfig:
    """Configurazione per il calcolo del vento.

    Attributes:
        method: Metodo normativo ("NTC2018", "EN1991_1_4", "CNR_DT207", "hybrid").
        site: Parametri del sito.
        building: Geometria dell'edificio.
        apply_cnr_dt207: Se True, arricchisce con fattori CNR-DT 207 R1/2018.
    """

    method: str = "NTC2018"
    site: WindSite = field(default_factory=WindSite)
    building: BuildingGeom = field(default_factory=BuildingGeom)
    apply_cnr_dt207: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


class WindActionService:
    """Servizio di calcolo delle azioni del vento.

    Seleziona il metodo normativo in base a ``WindConfig.method`` e
    produce un :class:`WindResults` coerente.

    Uso::

        service = WindActionService()
        config = WindConfig(
            method="NTC2018",
            site=WindSite(altitude_m=100, terrain_category="II"),
            building=BuildingGeom(height_m=20),
        )
        results = service.compute(config)
    """

    def compute(self, config: WindConfig) -> WindResults:
        """Calcola le azioni del vento per la configurazione specificata.

        Args:
            config: Configurazione con metodo, sito e geometria.

        Returns:
            :class:`WindResults` con profilo e pressioni calcolate.

        Note:
            Non solleva eccezioni: in caso di errore, restituisce un
            :class:`WindResults` con status di errore nei warnings.
        """
        method = (config.method or "NTC2018").upper()

        try:
            if method in ("NTC2018",):
                results = self._run_ntc2018(config)
            elif method in ("EN1991_1_4", "EN1991", "EC"):
                results = self._run_en1991(config)
            elif method in ("CNR_DT207", "CNR"):
                # CNR-DT 207 usa NTC2018 come base + arricchimento
                results = self._run_ntc2018(config)
                results = self._apply_cnr(results, config)
            elif method in ("HYBRID",):
                results = self._run_hybrid(config)
            else:
                logger.warning("Metodo vento '%s' non riconosciuto; uso NTC2018.", method)
                results = self._run_ntc2018(config)
                results.warnings.append(f"Metodo '{config.method}' non riconosciuto; usato NTC2018.")

            # Applica arricchimento CNR se richiesto
            if config.apply_cnr_dt207 and method not in ("CNR_DT207", "HYBRID"):
                results = self._apply_cnr(results, config)

        except Exception as exc:
            logger.exception("WindActionService.compute error: %s", exc)
            results = WindResults(
                method=config.method,
                warnings=[f"Errore calcolo vento: {exc}"],
            )

        return results

    def _run_ntc2018(self, config: WindConfig) -> WindResults:
        from src.wind.ntc2018 import run_ntc2018_wind

        return run_ntc2018_wind(config.site, config.building)

    def _run_en1991(self, config: WindConfig) -> WindResults:
        from src.wind.ec1991_1_4 import run_en1991_1_4_wind

        return run_en1991_1_4_wind(config.site, config.building)

    def _apply_cnr(self, results: WindResults, config: WindConfig) -> WindResults:
        from src.wind.cnr_dt207 import enrich_results_with_cnr_dt207

        # z0/z_min: prendi dai params terreno del metodo base
        z0 = config.site.extra.get("z0_m", 0.05)
        z_min = config.site.extra.get("z_min_m", 2.0)
        return enrich_results_with_cnr_dt207(results, config.site, config.building, z0=z0, z_min=z_min)

    def _run_hybrid(self, config: WindConfig) -> WindResults:
        """Metodo ibrido: NTC2018 + EN1991-1-4 + CNR (envelope conservativo)."""
        ntc = self._run_ntc2018(config)
        en = self._run_en1991(config)

        # Prende il profilo più conservativo (max q per quota)
        hybrid_profile = []
        for p_ntc, p_en in zip(ntc.velocity_profile, en.velocity_profile):
            if p_ntc.q_kN_m2 >= p_en.q_kN_m2:
                hybrid_profile.append(p_ntc)
            else:
                hybrid_profile.append(p_en)

        warnings = ntc.warnings + en.warnings
        warnings.append("Metodo ibrido: envelope conservativo tra NTC2018 e EN1991-1-4.")

        import dataclasses

        result = dataclasses.replace(
            ntc,
            method="hybrid",
            velocity_profile=hybrid_profile,
            v_b_ms=max(ntc.v_b_ms, en.v_b_ms),
            q_b_kN_m2=max(ntc.q_b_kN_m2, en.q_b_kN_m2),
            warnings=warnings,
        )
        return self._apply_cnr(result, config)
