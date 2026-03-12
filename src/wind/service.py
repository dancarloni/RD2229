"""Wind Action Service – orchestrazione multi-norma per il calcolo del vento.

Supporta metodi: "NTC2018", "EN1991_1_4", "CNR_DT207", "hybrid".

Pipeline completa:
1. Calcolo velocità/pressione base (NTC2018 o EN1991)
2. Topografia (ct)
3. Fattore strutturale cs·cd
4. Coefficienti pressione esterna (cp_e per edifici o strutture speciali)
5. Pressione interna (cp_i)
6. Pressioni nette per zone
7. Forze di attrito
8. Schermatura
9. Forze risultanti
10. Combinazioni (opzionale)
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass, field
from typing import Any

from src.wind.models import BuildingGeom, InternalPressureConfig, StructureGeom, WindSite
from src.wind.outputs import PressureZoneResults, WindResults

logger = logging.getLogger(__name__)


@dataclass
class WindConfig:
    """Configurazione per il calcolo del vento.

    Attributes:
        method: Metodo normativo ("NTC2018", "EN1991_1_4", "CNR_DT207", "hybrid").
        site: Parametri del sito.
        building: Geometria dell'edificio (retrocompatibilità).
        structure: Geometria generalizzata (se specificata, sovrascrive building).
        apply_cnr_dt207: Se True, arricchisce con fattori CNR-DT 207 R1/2018.
        internal_pressure: Configurazione pressione interna.
        compute_combinations: Se True, genera combinazioni SLU/SLE.
        compute_friction: Se True, calcola forze di attrito.
        apply_shielding: Se True, applica fattori di schermatura.
    """

    method: str = "NTC2018"
    site: WindSite = field(default_factory=WindSite)
    building: BuildingGeom = field(default_factory=BuildingGeom)
    structure: StructureGeom | None = None
    apply_cnr_dt207: bool = False
    internal_pressure: InternalPressureConfig | None = None
    compute_combinations: bool = False
    compute_friction: bool = False
    apply_shielding: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def get_building_geom(self) -> BuildingGeom:
        """Restituisce BuildingGeom, convertendo da StructureGeom se necessario."""
        if self.structure is not None:
            return self.structure.to_building_geom()
        return self.building


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

        Pipeline:
        1. Profilo velocità/pressione base
        2. Topografia → applicata al profilo
        3. cs·cd → fattore strutturale
        4-5. Pressioni esterne + interne → zone
        6. Attrito (opzionale)
        7. Schermatura (opzionale)
        8. Forze risultanti
        9. Combinazioni (opzionale)
        """
        method = (config.method or "NTC2018").upper()

        try:
            # Step 1: Profilo base
            if method in ("NTC2018",):
                results = self._run_ntc2018(config)
            elif method in ("EN1991_1_4", "EN1991", "EC"):
                results = self._run_en1991(config)
            elif method in ("CNR_DT207", "CNR"):
                results = self._run_ntc2018(config)
                results = self._apply_cnr(results, config)
            elif method in ("HYBRID",):
                results = self._run_hybrid(config)
            else:
                logger.warning("Metodo vento '%s' non riconosciuto; uso NTC2018.", method)
                results = self._run_ntc2018(config)
                results.warnings.append(
                    f"Metodo '{config.method}' non riconosciuto; usato NTC2018."
                )

            # Applica arricchimento CNR se richiesto
            if config.apply_cnr_dt207 and method not in ("CNR_DT207", "HYBRID"):
                results = self._apply_cnr(results, config)

            # Step 2: Topografia
            results = self._apply_topography(results, config)

            # Step 3: cs·cd
            results = self._apply_structural_factor(results, config)

            # Step 4-5: Pressioni (se struttura specificata)
            if config.structure is not None:
                results = self._compute_pressures(results, config)

            # Step 6: Attrito
            if config.compute_friction:
                results = self._compute_friction(results, config)

            # Step 7-8: Forze risultanti
            if results.pressure_zones:
                results = self._compute_resultant_forces(results, config)

            # Step 9: Combinazioni
            if config.compute_combinations and results.pressure_zones:
                results = self._generate_combinations(results, config)

        except Exception as exc:
            logger.exception("WindActionService.compute error: %s", exc)
            results = WindResults(
                method=config.method,
                warnings=[f"Errore calcolo vento: {exc}"],
            )

        return results

    # ----- Step 1: Metodi base ----- #

    def _run_ntc2018(self, config: WindConfig) -> WindResults:
        from src.wind.ntc2018 import run_ntc2018_wind

        return run_ntc2018_wind(config.site, config.get_building_geom())

    def _run_en1991(self, config: WindConfig) -> WindResults:
        from src.wind.ec1991_1_4 import run_en1991_1_4_wind

        return run_en1991_1_4_wind(config.site, config.get_building_geom())

    def _apply_cnr(self, results: WindResults, config: WindConfig) -> WindResults:
        from src.wind.cnr_dt207 import enrich_results_with_cnr_dt207

        z0 = config.site.extra.get("z0_m", 0.05)
        z_min = config.site.extra.get("z_min_m", 2.0)
        return enrich_results_with_cnr_dt207(
            results, config.site, config.get_building_geom(), z0=z0, z_min=z_min
        )

    def _run_hybrid(self, config: WindConfig) -> WindResults:
        """Metodo ibrido: NTC2018 + EN1991-1-4 + CNR (envelope conservativo)."""
        ntc = self._run_ntc2018(config)
        en = self._run_en1991(config)

        hybrid_profile = []
        for p_ntc, p_en in zip(ntc.velocity_profile, en.velocity_profile):
            if p_ntc.q_kN_m2 >= p_en.q_kN_m2:
                hybrid_profile.append(p_ntc)
            else:
                hybrid_profile.append(p_en)

        warnings = ntc.warnings + en.warnings
        warnings.append("Metodo ibrido: envelope conservativo tra NTC2018 e EN1991-1-4.")

        result = dataclasses.replace(
            ntc,
            method="hybrid",
            velocity_profile=hybrid_profile,
            v_b_ms=max(ntc.v_b_ms, en.v_b_ms),
            q_b_kN_m2=max(ntc.q_b_kN_m2, en.q_b_kN_m2),
            warnings=warnings,
        )
        return self._apply_cnr(result, config)

    # ----- Step 2: Topografia ----- #

    def _apply_topography(self, results: WindResults, config: WindConfig) -> WindResults:
        topo = config.site.topography_params
        if topo is None or topo.topo_type.lower() == "flat":
            return results

        from src.wind.topography import compute_topography_factor

        building = config.get_building_geom()
        ct = compute_topography_factor(building.height_m, topo)

        if ct <= 1.0:
            return results

        # ct amplifica la velocità → pressione scala come ct²
        from src.wind.outputs import WindProfilePoint

        new_profile = []
        for p in results.velocity_profile:
            ct_z = compute_topography_factor(p.z_m, topo)
            v_new = p.v_m_s * ct_z
            from src.wind.ntc2018 import compute_kinetic_pressure

            q_new = compute_kinetic_pressure(v_new)
            new_profile.append(
                WindProfilePoint(
                    z_m=p.z_m,
                    v_m_s=round(v_new, 3),
                    q_kN_m2=round(q_new, 4),
                )
            )

        return dataclasses.replace(
            results,
            velocity_profile=new_profile,
            topography_factor=round(ct, 3),
        )

    # ----- Step 3: cs·cd ----- #

    def _apply_structural_factor(self, results: WindResults, config: WindConfig) -> WindResults:
        from src.wind.cnr_dt207 import compute_structural_factor

        structure = config.structure or config.get_building_geom()
        z0 = config.site.extra.get("z0_m", 0.05)
        z_min = config.site.extra.get("z_min_m", 2.0)

        cscd = compute_structural_factor(
            structure,
            config.site,
            z0=z0,
            z_min=z_min,
            override=config.extra.get("cscd_override"),
        )

        if cscd == 1.0:
            return results

        return dataclasses.replace(
            results,
            structural_factor=cscd,
        )

    # ----- Step 4-5: Pressioni ----- #

    def _compute_pressures(self, results: WindResults, config: WindConfig) -> WindResults:
        structure = config.structure
        if structure is None:
            return results

        # Pressione di picco alla quota di riferimento (sommità)
        q_p = (
            results.velocity_profile[-1].q_kN_m2 if results.velocity_profile else results.q_b_kN_m2
        )
        q_p *= results.structural_factor  # Applica cs·cd

        from src.wind.internal_pressure import get_cpi_values

        cpi_values = get_cpi_values(config.internal_pressure)

        stype = structure.structure_type.upper()

        if stype == "BUILDING":
            return self._pressures_building(results, config, q_p, cpi_values)
        elif stype in ("CANOPY_MONO", "CANOPY_DUO", "CANOPY_TROUGH", "CANOPY_MULTI"):
            return self._pressures_canopy(results, config, q_p)
        elif stype == "SHELTER":
            return self._pressures_shelter(results, config, q_p)
        elif stype in ("SIGN", "SIGN_LATTICE"):
            return self._pressures_sign(results, config, q_p)
        elif stype in ("SOLAR_GROUND", "SOLAR_FLAT_ROOF", "SOLAR_PITCHED_ROOF", "SOLAR_TRACKER"):
            return self._pressures_solar(results, config, q_p)
        elif stype in ("WALL_FREE", "FENCE"):
            return self._pressures_wall(results, config, q_p)
        else:
            results.warnings.append(
                f"Tipo struttura '{stype}' non supportato per calcolo pressioni."
            )
            return results

    def _pressures_building(
        self,
        results: WindResults,
        config: WindConfig,
        q_p: float,
        cpi_values: tuple[float, float],
    ) -> WindResults:
        from src.wind.pressure_coefficients import compute_building_pressure_zones

        structure = config.structure
        overrides = config.extra.get("cpe_overrides", {})

        zones_data = compute_building_pressure_zones(
            structure.height_m,
            structure.width_m,
            structure.depth_m,
            q_p,
            roof_angle_deg=structure.roof_angle_deg,
            cpi_values=cpi_values,
            overrides=overrides,
        )

        zones = []
        for zd in zones_data:
            zones.append(
                PressureZoneResults(
                    zone_id=zd["zone_id"],
                    description=zd["description"],
                    cpe=zd["cpe"],
                    cpi=zd["cpi"],
                    we_kN_m2=zd["we_kN_m2"],
                    wi_kN_m2=zd["wi_kN_m2"],
                    net_kN_m2=zd["net_kN_m2"],
                )
            )

        return dataclasses.replace(results, pressure_zones=zones)

    def _pressures_canopy(
        self,
        results: WindResults,
        config: WindConfig,
        q_p: float,
    ) -> WindResults:
        from src.wind.special_structures import compute_canopy_pressures

        structure = config.structure
        num_bays = config.extra.get("num_bays", 1)
        overrides = config.extra.get("canopy_overrides", {})

        zones_data = compute_canopy_pressures(
            structure.structure_type,
            structure.roof_angle_deg,
            structure.blockage_ratio,
            q_p,
            num_bays=num_bays,
            overrides=overrides,
        )

        zones = []
        for zd in zones_data:
            zones.append(
                PressureZoneResults(
                    zone_id=zd["zone_id"],
                    description=zd["description"],
                    cpe=zd["cp_net_max"],  # Caso più sfavorevole
                    net_kN_m2=zd["w_max_kN_m2"],
                )
            )
            zones.append(
                PressureZoneResults(
                    zone_id=zd["zone_id"] + "_min",
                    description=zd["description"] + " (min)",
                    cpe=zd["cp_net_min"],
                    net_kN_m2=zd["w_min_kN_m2"],
                )
            )

        return dataclasses.replace(results, pressure_zones=zones)

    def _pressures_shelter(
        self,
        results: WindResults,
        config: WindConfig,
        q_p: float,
    ) -> WindResults:
        from src.wind.special_structures import compute_shelter_pressures

        structure = config.structure
        overrides = config.extra.get("shelter_overrides", {})

        zones_data = compute_shelter_pressures(
            structure.roof_angle_deg,
            structure.blockage_ratio,
            q_p,
            overrides=overrides,
        )

        zones = []
        for zd in zones_data:
            zones.append(
                PressureZoneResults(
                    zone_id=zd["zone_id"],
                    description=zd["description"],
                    cpe=zd["cp_net_max"],
                    net_kN_m2=zd["w_max_kN_m2"],
                )
            )

        return dataclasses.replace(results, pressure_zones=zones)

    def _pressures_sign(
        self,
        results: WindResults,
        config: WindConfig,
        q_p: float,
    ) -> WindResults:
        from src.wind.special_structures import compute_sign_force, compute_sign_zone_pressures

        structure = config.structure
        is_lattice = structure.structure_type.upper() == "SIGN_LATTICE"

        # Forza globale (cf complessivo)
        force_data = compute_sign_force(
            structure.width_m,
            structure.height_m,
            q_p,
            solidity_ratio=structure.solidity_ratio,
            ground_clearance_m=structure.ground_clearance_m,
            is_lattice=is_lattice,
            override_cf=config.extra.get("cf_override"),
        )

        # Zone di pressione dettagliate (CNR-DT 207 G.7)
        use_zones = config.extra.get("sign_zone_pressures", False)

        if use_zones and not is_lattice:
            zone_data = compute_sign_zone_pressures(
                structure.width_m,
                structure.height_m,
                q_p,
                solidity_ratio=structure.solidity_ratio,
                ground_clearance_m=structure.ground_clearance_m,
            )
            zones = []
            for zd in zone_data:
                zones.append(
                    PressureZoneResults(
                        zone_id=zd["zone_id"],
                        description=zd["description"],
                        cpe=zd["cpn"],
                        net_kN_m2=zd["w_kN_m2"],
                        area_m2=zd["area_m2"],
                    )
                )
        else:
            zones = [
                PressureZoneResults(
                    zone_id="sign",
                    description=force_data["description"],
                    cpe=force_data["cf"],
                    net_kN_m2=force_data["F_kN"] / max(force_data["area_ref_m2"], 0.01),
                    area_m2=force_data["area_ref_m2"],
                )
            ]

        # Salva eccentricità e punto di applicazione per forze risultanti
        extra = dict(results.extra)
        extra["sign_eccentricity_m"] = force_data.get("eccentricity_m", 0.0)
        extra["sign_application_point_m"] = force_data.get("application_point_m", 0.0)
        extra["sign_global_force_kN"] = force_data.get("F_kN", 0.0)

        return dataclasses.replace(results, pressure_zones=zones, extra=extra)

    def _pressures_solar(
        self,
        results: WindResults,
        config: WindConfig,
        q_p: float,
    ) -> WindResults:
        from src.wind.special_structures import compute_solar_pressures

        structure = config.structure
        overrides = config.extra.get("solar_overrides", {})

        zones_data = compute_solar_pressures(
            structure.structure_type,
            structure.panel_tilt_deg,
            q_p,
            roof_angle_deg=structure.roof_angle_deg,
            num_rows=structure.panel_rows,
            tracking_angle_deg=config.extra.get("tracking_angle_deg", 0.0),
            overrides=overrides,
        )

        zones = []
        for zd in zones_data:
            zones.append(
                PressureZoneResults(
                    zone_id=zd["zone_id"],
                    description=zd["description"],
                    cpe=zd["cp_net_max"],
                    net_kN_m2=zd["w_max_kN_m2"],
                )
            )
            zones.append(
                PressureZoneResults(
                    zone_id=zd["zone_id"] + "_min",
                    description=zd["description"] + " (min)",
                    cpe=zd["cp_net_min"],
                    net_kN_m2=zd["w_min_kN_m2"],
                )
            )

        return dataclasses.replace(results, pressure_zones=zones)

    def _pressures_wall(
        self,
        results: WindResults,
        config: WindConfig,
        q_p: float,
    ) -> WindResults:
        from src.wind.special_structures import get_freestanding_wall_cp

        structure = config.structure

        cp_center = get_freestanding_wall_cp(
            structure.width_m,
            structure.height_m,
            solidity_ratio=structure.solidity_ratio,
        )
        cp_corner = get_freestanding_wall_cp(
            structure.width_m,
            structure.height_m,
            solidity_ratio=structure.solidity_ratio,
            return_corner=True,
        )

        zones = [
            PressureZoneResults(
                zone_id="wall_center",
                description="Muro isolato — zona centrale",
                cpe=cp_center,
                net_kN_m2=round(cp_center * q_p, 4),
            ),
            PressureZoneResults(
                zone_id="wall_corner",
                description="Muro isolato — zona bordo",
                cpe=cp_corner,
                net_kN_m2=round(cp_corner * q_p, 4),
            ),
        ]

        return dataclasses.replace(results, pressure_zones=zones)

    # ----- Step 6: Attrito ----- #

    def _compute_friction(self, results: WindResults, config: WindConfig) -> WindResults:
        from src.wind.friction import compute_building_friction

        building = config.get_building_geom()
        q_p = (
            results.velocity_profile[-1].q_kN_m2 if results.velocity_profile else results.q_b_kN_m2
        )

        friction_class = "SMOOTH"
        if config.structure:
            friction_class = config.structure.friction_class

        forces = compute_building_friction(
            building.height_m,
            building.width_m,
            building.depth_m,
            q_p,
            friction_class=friction_class,
            override_cfr=config.extra.get("cfr_override"),
        )

        if forces:
            return dataclasses.replace(results, friction_forces=forces)
        return results

    # ----- Step 7-8: Forze risultanti ----- #

    def _compute_resultant_forces(self, results: WindResults, config: WindConfig) -> WindResults:
        from src.wind.resultant_forces import compute_resultant_forces

        building = config.get_building_geom()
        default_area = config.extra.get("default_tributary_area_m2", 0.0)

        # Eccentricità per insegne (CNR-DT 207 App. G.7)
        sign_eccentricity = results.extra.get("sign_eccentricity_m", 0.0)
        sign_app_point = results.extra.get("sign_application_point_m", 0.0)

        forces = compute_resultant_forces(
            results.pressure_zones,
            default_area_m2=default_area,
            height_m=building.height_m,
            eccentricity_m=sign_eccentricity,
            force_application_point_m=sign_app_point if sign_app_point > 0 else None,
        )

        return dataclasses.replace(results, resultant_forces=forces)

    # ----- Step 9: Combinazioni ----- #

    def _generate_combinations(self, results: WindResults, config: WindConfig) -> WindResults:
        from src.wind.combinations import generate_wind_combinations

        norm_code = config.method or "NTC2018"
        combos = generate_wind_combinations(
            results.pressure_zones,
            norm_code,
            resultant_forces=results.resultant_forces,
        )

        return dataclasses.replace(results, combinations=combos)
