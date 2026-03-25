"""Servizi applicativi per GUI moderna RD2229.

Il modulo mantiene le API storiche usate dai test (`ProjectIOService`,
`CalculationService`) e aggiunge un livello operativo con preset eseguibili
da pulsanti GUI.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from .action_report import ActionReport
from .calculation_service import CalculationService
from .project_io_service import ProjectIOService


def _build_demo_project(norm_code: str, limit_states: list[str]) -> Any:
    from src.project.schema import (
        CodeSettings,
        GeometryEntry,
        LoadEntry,
        MaterialEntry,
        ProjectModel,
    )

    return ProjectModel(
        geometry=[GeometryEntry(id="E1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0, f_yk=450.0)],
        loads=[
            LoadEntry(
                element_id="E1",
                N=100.0,
                Mx=55.0,
                Tx=20.0,
                description="preset_ui_modern",
                extra={
                    "As": 12.0,
                    "As_p": 8.0,
                    "d": 45.0,
                    "d_p": 5.0,
                    "staffe_diametro": 8.0,
                    "staffe_num_bracci": 2,
                    "staffe_passo": 20.0,
                },
            )
        ],
        code_settings=CodeSettings(norm_code=norm_code, limit_states=limit_states),
    )


class PresetExecutionService:
    """Preset pronti all'uso per dashboard e wizard della GUI moderna."""

    def __init__(
        self,
        io_service: ProjectIOService | None = None,
        calculation_service: CalculationService | None = None,
    ) -> None:
        self._io = io_service or ProjectIOService()
        self._calc = calculation_service or CalculationService()

    def run_full_pipeline_from_file(
        self,
        project_path: str,
        output_dir: str | None = None,
    ) -> ActionReport:
        from src.reporting.export import export_report_html, export_report_md
        from src.reporting.report_builder import build_report

        project = self._io.open_project(project_path)
        results = self._calc.run(project)
        artifact = build_report(project, results)

        target_dir = Path(output_dir) if output_dir else Path(project_path).parent
        target_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(project_path).stem
        md_path = target_dir / f"{stem}_report.md"
        html_path = target_dir / f"{stem}_report.html"
        export_report_md(artifact, str(md_path))
        export_report_html(artifact, str(html_path))

        return ActionReport(
            name="workflow_completo",
            ok=bool(results.ok),
            summary="Pipeline completa eseguita con export report.",
            details={
                "ok": bool(results.ok),
                "n_elementi": len(getattr(results, "elements", [])),
                "warnings": list(getattr(results, "warnings", [])),
                "report_md": str(md_path),
                "report_html": str(html_path),
            },
        )

    def run_normative_rd2229(self) -> ActionReport:
        project = _build_demo_project("RD2229", ["TA"])
        results = self._calc.run(project)
        first = results.elements[0] if results.elements else None

        return ActionReport(
            name="normativa_rd2229",
            ok=bool(results.ok),
            summary="Verifica normativa RD2229 su modello demo.",
            details={
                "ok": bool(results.ok),
                "n_elementi": len(results.elements),
                "trace_tail": list(results.trace[-5:]),
                "metriche_elemento_1": dict(first.metrics) if first else {},
            },
        )

    def run_secondari_ntc2018(self) -> ActionReport:
        project = _build_demo_project("NTC2018", ["SLU", "SLE"])
        results = self._calc.run(project)

        return ActionReport(
            name="secondari_ntc2018",
            ok=bool(results.ok),
            summary="Preset elementi secondari NTC2018 (SLU/SLE).",
            details={
                "ok": bool(results.ok),
                "n_elementi": len(results.elements),
                "warnings": list(results.warnings),
                "trace_tail": list(results.trace[-5:]),
            },
        )

    def run_wind_ntc2018(self) -> ActionReport:
        from src.wind.models import StructureGeom, WindSite
        from src.wind.service import WindActionService, WindConfig

        service = WindActionService()
        config = WindConfig(
            method="NTC2018",
            site=WindSite(altitude_m=120.0, terrain_category="II"),
            structure=StructureGeom(
                structure_type="BUILDING",
                height_m=18.0,
                width_m=12.0,
                depth_m=10.0,
                roof_angle_deg=15.0,
            ),
            compute_combinations=True,
        )
        results = service.compute(config)

        return ActionReport(
            name="vento_ntc2018",
            ok=len(results.warnings) == 0,
            summary="Calcolo vento NTC2018 completato.",
            details={
                "method": results.method,
                "v_b_ms": results.v_b_ms,
                "q_b_kN_m2": results.q_b_kN_m2,
                "n_quote_profilo": len(results.velocity_profile),
                "n_zone_pressione": len(results.pressure_zones),
                "n_combinazioni": len(results.combinations),
                "warnings": list(results.warnings),
            },
        )

    def run_fem_demo(self) -> ActionReport:
        from src.fem import (
            ApplicatoreBC,
            Assemblatore,
            CaricoDistribuitoUniforme,
            ElementoFEM,
            NodoFEM,
            SolutoreFEMSparso,
            TipoVincolo,
            VincoloNodo,
        )

        nodo_i = NodoFEM(id=0, x=0.0, y=0.0)
        nodo_j = NodoFEM(id=1, x=600.0, y=0.0)
        elem = ElementoFEM.da_nodi(
            0,
            nodo_i,
            nodo_j,
            E=30000.0,
            A=100.0,
            I=10000.0,
            carichi=[CaricoDistribuitoUniforme(intensita=-2.0)],
            etichetta="FEM_UI",
        )
        asm = Assemblatore(nodi=[nodo_i, nodo_j], elementi=[elem])
        K_glob, F_glob = asm.assembla()

        bc = ApplicatoreBC(
            vincoli=[
                VincoloNodo(id_nodo=0, tipo=TipoVincolo.CERNIERA),
                VincoloNodo(id_nodo=1, tipo=TipoVincolo.CERNIERA),
            ]
        )
        K_rid, F_rid, gdl_liberi, _ = bc.applica(K_glob, F_glob)
        solved = SolutoreFEMSparso().risolvi(K_rid, F_rid, gdl_liberi, asm.n_gdl)

        max_disp = float(np.max(np.abs(solved.spostamenti_completi)))
        return ActionReport(
            name="fem_2d",
            ok=math.isfinite(max_disp),
            summary="Preset FEM 2D trave appoggiata risolto.",
            details={
                "n_gdl_totale": solved.n_gdl_totale,
                "n_gdl_liberi": solved.n_gdl_liberi,
                "norma_residuo": solved.norma_residuo,
                "max_spostamento": max_disp,
            },
        )

    def run_cross_pozzati_demo(self) -> ActionReport:
        from src.methods.rd2229.telaio.cross_pozzati import calcola_cross_pozzati
        from src.methods.rd2229.telaio.modello_telaio import (
            AstaTelaio,
            CaricoAsta,
            ModelloTelaio,
            NodoTelaio,
            RilascioEstremita,
            SezioneTelaio,
            TipoAsta,
            TipoCarico,
            TipoRilascioInterno,
            TipoVincoloEsterno,
            VincoloEsterno,
        )

        nodi = [
            NodoTelaio(id=1, x=0, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
            NodoTelaio(id=2, x=400, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.LIBERO)),
            NodoTelaio(id=3, x=700, y=0, vincolo=VincoloEsterno(TipoVincoloEsterno.INCASTRO)),
        ]
        rigido = RilascioEstremita(TipoRilascioInterno.NODO_RIGIDO)
        sezione = SezioneTelaio.rettangolare(30.0, 50.0, E=300000.0)
        aste = [
            AstaTelaio(
                id=1,
                nodo_i=1,
                nodo_j=2,
                tipo=TipoAsta.TRAVE,
                sezione=sezione,
                rilascio_i=rigido,
                rilascio_j=rigido,
                etichetta="AB",
                carichi=[CaricoAsta(TipoCarico.DISTRIBUITO_UNIFORME, valore_sx=2.0)],
            ),
            AstaTelaio(
                id=2,
                nodo_i=2,
                nodo_j=3,
                tipo=TipoAsta.TRAVE,
                sezione=sezione,
                rilascio_i=rigido,
                rilascio_j=rigido,
                etichetta="BC",
                carichi=[CaricoAsta(TipoCarico.DISTRIBUITO_UNIFORME, valore_sx=3.0)],
            ),
        ]
        model = ModelloTelaio(nome="CrossUI", nodi=nodi, aste=aste, piani=[], zona_sismica="none")
        cross = calcola_cross_pozzati(model)

        max_m = 0.0
        for moments in cross.momenti_finali.values():
            max_m = max(max_m, max(abs(moments[0]), abs(moments[1])))

        return ActionReport(
            name="cross_pozzati",
            ok=bool(cross.convergenza),
            summary="Calcolo Cross-Pozzati completato.",
            details={
                "convergenza": cross.convergenza,
                "n_iterazioni": cross.n_iterazioni,
                "errore_residuo": cross.errore_residuo,
                "momento_max_kgcm": max_m,
            },
        )

    def run_solaio_input_demo(self) -> ActionReport:
        from src.core_calculus.solaio_input import parse_solaio_input

        data = {
            "tipologia": "laterocemento",
            "norma": "NTC2018",
            "edificio_esistente": True,
            "unit_system": "auto",
            "geometria": {"luce_cm": 450.0, "interasse_cm": 50.0, "spessore_cm": 20.0},
            "materiali": {"f_ck": 250.0, "f_yk": 4300.0, "E": 300000.0, "rho": 2500.0},
            "carichi": {"G1": 250.0, "G2": 120.0, "Q": 200.0, "categoria": "A"},
            "aperture": [],
            "cerchiature": [],
            "lc_fc": {},
        }
        parsed = parse_solaio_input(data)
        ready = parsed.as_ready_dict()

        return ActionReport(
            name="solai_x1",
            ok=True,
            summary="Parsing e normalizzazione input solaio completati.",
            details={
                "tipologia": ready["meta"]["tipologia"],
                "norma": ready["meta"]["norma"],
                "unit_system_detected": ready["meta"]["unit_system_detected"],
                "luce_m": ready["normalized"]["geometria"]["luce_m"],
                "Q_kN_m2": ready["normalized"]["carichi"]["Q_kN_m2"],
            },
        )

    def run_x8_demo(self) -> ActionReport:
        from src.x8_special_cases import SpecialCaseInput, evaluate_special_case
        from src.x8_special_cases.x8_models import SpecialCaseType

        result = evaluate_special_case(
            SpecialCaseInput(
                case_type=SpecialCaseType.PREDALLES,
                norm_code="NTC2018",
                span_m=5.5,
                gk_kg_m2=250.0,
                qk_kg_m2=200.0,
                height_cm=25.0,
            ),
            strict_blocking=False,
        )

        return ActionReport(
            name="x8_casi_speciali",
            ok=not result.blocked,
            summary="Valutazione caso speciale X8 completata.",
            details={
                "case_type": result.case_type,
                "blocked": result.blocked,
                "warnings": list(result.warnings),
                "benchmark_values": dict(result.benchmark_values),
            },
        )


__all__ = [
    "ActionReport",
    "ProjectIOService",
    "CalculationService",
    "PresetExecutionService",
]
