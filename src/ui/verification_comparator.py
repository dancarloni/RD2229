"""GUI window to compare verification methods (.bas translation vs TA vs SLU)."""

# pylint: disable=import-error

from __future__ import annotations

import logging
import tkinter as tk
from _csv import Writer
from tkinter import ttk
from typing import Any

import matplotlib
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from sections_app.services.notification import notify_error, notify_info, notify_warning
from src.core_calculus.core.verification_bas_adapter import bas_torsion_verification
from src.core_calculus.core.verification_core import (
    LoadCase,
    MaterialProperties,
    ReinforcementLayer,
    SectionGeometry,
)
from src.core_calculus.core.verification_engine import (
    VerificationEngine,
    create_verification_engine,
)
from src.domain.domain.models import VerificationInput, VerificationOutput
from verification_table import (
    VerificationTableApp,
    compute_slu_verification,
    compute_ta_verification,
    get_section_geometry,
)

matplotlib.use("Agg")  # Use Agg for headless tests; GUI will embed FigureCanvasTkAgg if available

logger: logging.Logger = logging.getLogger(__name__)

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception as exc:  # pylint: disable=broad-exception-caught
    logger.exception("Matplotlib tkagg backend import failed: %s", exc)
    FigureCanvasTkAgg = None
MATPLOTLIB_TK: bool = FigureCanvasTkAgg is not None


def _write_csv_comp(comp: dict[str, Any], path: str) -> None:
    import csv

    with open(path, "w", newline="", encoding="utf-8") as fh:
        w: Writer = csv.writer(fh)
        w.writerow(["method", "sigma_c_max", "asse_neutro_x", "angle"])
        for k, v in comp.items():
            if v:
                w.writerow([k, v.get("sigma_c_max", ""), v.get("asse_neutro_x", ""), v.get("angle", "")])


def _write_json_comp(comp: dict[str, Any], path: str) -> None:
    import json

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(comp, fh, default=str, indent=2)


def _write_txt_comp(comp: dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for k, v in comp.items():
            fh.write(f"== {k} ==\n")
            fh.write(str(v) + "\n")


# --- Helper geometry utilities ---------------------------------

def _append_if_in_bounds(candidates: list[tuple[float, float]], x: float, y: float, b: float, h: float) -> None:
    if -1e-6 <= x <= b + 1e-6 and -1e-6 <= y <= h + 1e-6:
        candidates.append((x, y))


def _intersections_with_verticals(
    b: float, h: float, px: float, py: float, vx: float, vy: float
) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    if abs(vx) > 1e-12:
        t = (0 - px) / vx
        y = py + t * vy
        _append_if_in_bounds(out, 0.0, y, b, h)
        t = (b - px) / vx
        y = py + t * vy
        _append_if_in_bounds(out, b, y, b, h)
    return out


def _intersections_with_horizontals(
    b: float, h: float, px: float, py: float, vx: float, vy: float
) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    if abs(vy) > 1e-12:
        t = (0 - py) / vy
        x = px + t * vx
        _append_if_in_bounds(out, x, 0.0, b, h)
        t = (h - py) / vy
        x = px + t * vx
        _append_if_in_bounds(out, x, h, b, h)
    return out


def _line_rect_intersections(
    b: float, h: float, px: float, py: float, vx: float, vy: float
) -> list[tuple[float, float]]:
    candidates: list[tuple[float, float]] = []
    candidates.extend(_intersections_with_verticals(b, h, px, py, vx, vy))
    candidates.extend(_intersections_with_horizontals(b, h, px, py, vx, vy))
    return candidates


def _na_point_and_angle(res: Any, b: float, h: float):
    """Return ((px, py), angle) or None for given result (dict or object)."""
    if res is None:
        return None
    if isinstance(res, dict):
        px = res.get("asse_neutro_x", None) or res.get("asse_neutro", None)
        py = res.get("asse_neutro_y", None)
        ang = res.get("inclinazione_asse_neutro", 0.0)
    else:
        px = getattr(res, "asse_neutro_x", None) or getattr(res, "asse_neutro", None)
        py = getattr(res, "asse_neutro_y", None)
        ang = getattr(res, "inclinazione_asse_neutro", 0.0)
    if isinstance(px, (int, float)) and isinstance(py, (int, float)):
        return (px, py), ang
    if isinstance(px, (int, float)):
        return (b / 2.0, px), ang
    return (b / 2.0, h / 2.0), ang


def _metrics_none() -> dict[str, Any]:
    return {
        "sigma_c_max": 0.0,
        "sigma_c_min": 0.0,
        "sigma_s_max": 0.0,
        "asse_x": None,
        "angle": None,
    }


def _metrics_from_dict(res: dict[str, Any]) -> dict[str, Any]:
    return {
        "sigma_c_max": res.get("Taux_max", 0.0),
        "sigma_c_min": 0.0,
        "sigma_s_max": 0.0,
        "asse_x": None,
        "angle": None,
    }


def _metrics_from_obj(res: Any) -> dict[str, Any]:
    return {
        "sigma_c_max": getattr(res, "sigma_c_max", 0.0),
        "sigma_c_min": getattr(res, "sigma_c_min", 0.0),
        "sigma_s_max": getattr(res, "sigma_s_max", 0.0),
        "asse_x": getattr(res, "asse_neutro_x", getattr(res, "asse_neutro", None)),
        "angle": getattr(res, "inclinazione_asse_neutro", None),
    }


def _metrics_of(res: Any) -> dict[str, Any]:
    if res is None:
        return _metrics_none()
    if isinstance(res, dict):
        return _metrics_from_dict(res)
    return _metrics_from_obj(res)


class VerificationComparatorWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, verification_table_app: VerificationTableApp) -> None:
        super().__init__(master)
        self.title("Confronto metodi: .bas vs TA vs SLU")
        self.geometry("900x600")
        self.verification_table_app: VerificationTableApp = verification_table_app

        top = tk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)
        tk.Button(top, text="Confronta riga selezionata", command=self.on_compare).pack(side="left")
        tk.Button(top, text="Chiudi", command=self.destroy).pack(side="right")

        mid = tk.Frame(self)
        mid.pack(fill="both", expand=True, padx=8, pady=6)

        left = tk.Frame(mid)
        left.pack(side="left", fill="both", expand=True)

        self.txt_results = tk.Text(left, width=50)
        self.txt_results.pack(fill="both", expand=True)

        right = tk.Frame(mid)
        right.pack(side="right", fill="both", expand=True)

        # Two subplots: left for section/NA, right for bar chart
        self.fig = Figure(figsize=(6, 4))
        self.ax_section = self.fig.add_subplot(121)  # type: ignore
        self.ax_section.set_title("Sezione e asse neutro")
        self.ax_section.set_xlim(0, 1)
        self.ax_section.set_ylim(0, 1)
        self.ax_bars = self.fig.add_subplot(122)  # type: ignore
        self.ax_bars.set_title("σ (abs) comparison")
        self.canvas = None
        if FigureCanvasTkAgg is not None:
            self.canvas = FigureCanvasTkAgg(self.fig, master=right)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            self.canvas = None

        # Bottom frame for numeric summary and export
        bottom = tk.Frame(self)
        bottom.pack(fill="x", padx=8, pady=(0, 8))
        self.summary_table = ttk.Treeview(bottom, columns=("metric", "TA", "SLU", ".bas"), show="headings", height=4)
        self.summary_table.heading("metric", text="Metric")
        self.summary_table.heading("TA", text="TA")
        self.summary_table.heading("SLU", text="SLU")
        self.summary_table.heading(".bas", text=".bas")
        self.summary_table.column("metric", width=180)
        self.summary_table.pack(side="left", fill="x", expand=True)

        export_frame = tk.Frame(bottom)
        export_frame.pack(side="right")
        tk.Button(export_frame, text="Export CSV", command=lambda: self._export("csv")).pack(side="left", padx=4)
        tk.Button(export_frame, text="Export JSON", command=lambda: self._export("json")).pack(side="left", padx=4)
        tk.Button(export_frame, text="Export TXT", command=lambda: self._export("txt")).pack(side="left", padx=4)

    @staticmethod
    def _compute_na_endpoints(
        b: float, h: float, p: tuple[float, float], angle_deg: float
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Return two endpoints (on rectangle edges) of the infinite line passing through p with direction angle_deg.

        Coordinate system: origin (0,0) is top-left, x rightwards, y downwards.
        angle_deg: angle in degrees measured counterclockwise from +x axis (standard), consistent with Matplotlib axes.
        """
        import math

        px, py = p
        theta: float = math.radians(angle_deg)
        vx, vy = math.cos(theta), math.sin(theta)

        candidates = _line_rect_intersections(b, h, px, py, vx, vy)

        # Remove duplicates (within tol)
        unique = []
        for c in candidates:
            if not any((abs(c[0] - u[0]) < 1e-6 and abs(c[1] - u[1]) < 1e-6) for u in unique):
                unique.append(c)
        if len(unique) >= 2:
            return unique[0], unique[1]
        # Fallback: return two points along the vector clipped to big extents
        return (
            max(0.0, min(b, px - 10 * vx)),
            max(0.0, min(h, py - 10 * vy)),
        ), (max(0.0, min(b, px + 10 * vx)), max(0.0, min(h, py + 10 * vy)))

    @staticmethod
    def _clip_polygon_by_halfplane(
        poly: list[tuple[float, float]],
        p: tuple[float, float],
        v: tuple[float, float],
        keep_positive: bool = True,
    ) -> list[tuple[float, float]]:
        """Clip convex polygon `poly` by half-plane defined by the line passing through p with direction v.

        Keeps points where cross(v, (pt-p)) has sign >=0 if keep_positive True, else <=0.
        Implemented via Sutherland-Hodgman polygon clipping for a single half-plane.
        """

        def cross(vx, vy, wx, wy):
            return vx * wy - vy * wx

        out = []
        n: int = len(poly)
        for i in range(n):
            a: tuple[float, float] = poly[i]
            b: tuple[float, float] = poly[(i + 1) % n]
            ax, ay = a
            bx, by = b
            sa: float = cross(v[0], v[1], ax - p[0], ay - p[1])
            sb: float = cross(v[0], v[1], bx - p[0], by - p[1])
            if keep_positive:
                inside_a: bool = sa >= -1e-9
                inside_b: bool = sb >= -1e-9
            else:
                inside_a: bool = sa <= 1e-9
                inside_b: bool = sb <= 1e-9
            if inside_a:
                out.append(a)
            if inside_a ^ inside_b:
                # compute intersection
                dx: float = bx - ax
                dy: float = by - ay
                denom: float = v[0] * dy - v[1] * dx
                if abs(denom) > 1e-12:
                    t: float = (v[0] * (ay - p[1]) - v[1] * (ax - p[0])) / denom
                    ix: float = ax + dx * t
                    iy: float = ay + dy * t
                    out.append((ix, iy))
        return out

    @staticmethod
    def _compute_shaded_polygon(
        b: float,
        h: float,
        p: tuple[float, float],
        angle_deg: float,
        pick_side_point: tuple[float, float] | None = None,
    ) -> list[tuple[float, float]]:
        # Build rectangle polygon
        rect: list[tuple[float, float]] = [(0.0, 0.0), (b, 0.0), (b, h), (0.0, h)]
        import math

        theta: float = math.radians(angle_deg)
        v: tuple[float, float] = (math.cos(theta), math.sin(theta))
        # If pick_side_point is None, use top-center to define which side is 'above'
        if pick_side_point is None:
            pick_side_point = (b / 2.0, 0.0)

        # Determine sign for pick point
        def cross(vx, vy, wx, wy):
            return vx * wy - vy * wx

        sign: float = cross(v[0], v[1], pick_side_point[0] - p[0], pick_side_point[1] - p[1])
        keep_positive: bool = sign >= 0
        return VerificationComparatorWindow._clip_polygon_by_halfplane(rect, p, v, keep_positive=keep_positive)

    def _present_summary(self, ta_res: Any, slu_res: Any, bas_tors: Any) -> None:
        self.txt_results.delete("1.0", tk.END)

        def _summary(res, label) -> str | Any:
            if res is None:
                return f"{label}: errore\n"
            if isinstance(res, dict):
                return f"{label}: {res.get('messages', [])} OK={res.get('ok')}\n"
            # assume VerificationOutput-like
            msgs: Any | list[Any] = getattr(res, "messaggi", []) or getattr(res, "messages", []) or []
            details: str = (
                f"{label}: esito={getattr(res, 'esito', '')} "
                f"sigma_c_max={getattr(res, 'sigma_c_max', '')} "
                f"asse_neutro_x={getattr(res, 'asse_neutro_x', getattr(res, 'asse_neutro', ''))} "
                f"inclinazione={getattr(res, 'inclinazione_asse_neutro', '')}\n"
            )
            return details + (msgs[0] + "\n" if msgs else "")

        self.txt_results.insert(tk.END, _summary(ta_res, "TA"))
        self.txt_results.insert(tk.END, _summary(slu_res, "SLU"))
        self.txt_results.insert(tk.END, _summary(bas_tors, ".bas (Torsione)"))

        self.txt_results.insert(tk.END, "\nNumeric summary:\n")
        self.summary_table.delete(*self.summary_table.get_children())

    def _compute_all_methods(self, inp: VerificationInput, sec_repo, mat_repo) -> tuple[Any, Any, dict[str, Any]]:
        ta_res = None
        slu_res = None
        try:
            ta_res: VerificationOutput = compute_ta_verification(inp, sec_repo, mat_repo)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Errore calcolo TA: %s", exc)
        try:
            slu_res = compute_slu_verification(inp, sec_repo, mat_repo)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Errore calcolo SLU: %s", exc)
        try:
            engine: VerificationEngine = create_verification_engine((inp.verification_method or "TA").upper())
            mat_props: MaterialProperties = engine.get_material_properties(
                inp.material_concrete or "", inp.material_steel or "", material_source="RD2229"
            )
            bas_tors: dict[str, Any] = bas_torsion_verification(
                section=SectionGeometry(*get_section_geometry(inp, sec_repo, unit="cm")),
                reinforcement_tensile=ReinforcementLayer(area=inp.As_inf, distance=inp.d_inf),
                reinforcement_compressed=ReinforcementLayer(area=inp.As_sup, distance=inp.d_sup),
                material=mat_props,
                loads=LoadCase(N=inp.N, Mx=inp.Mx, My=inp.My, Mz=inp.Mz, Tx=inp.Tx, Ty=inp.Ty, At=inp.At),
                method=(inp.verification_method or "TA"),
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Errore .bas adapter: %s", exc)
            bas_tors = {"messages": [".bas adapter error"], "ok": False}
        return ta_res, slu_res, bas_tors

    def _draw_method_na(self, b: float, h: float, label: str, res: Any, metrics: dict[str, Any], color: str) -> None:
        out = _na_point_and_angle(res, b, h)
        if out is None:
            return
        p, ang = out
        e1, e2 = self._compute_na_endpoints(b, h, p, ang)
        pick_point: tuple[float, float] = (
            (b / 2.0, 0.0) if abs(metrics["sigma_c_max"]) >= abs(metrics["sigma_c_min"]) else (b / 2.0, h)
        )
        poly: list[tuple[float, float]] = self._compute_shaded_polygon(b, h, p, ang, pick_side_point=pick_point)
        self.ax_section.plot([e1[0], e2[0]], [e1[1], e2[1]], color=color, linewidth=2, label=f"{label} NA")
        if poly:
            self.ax_section.add_patch(mpatches.Polygon(poly, color=color, alpha=0.12))
        try:
            self.ax_section.text(
                p[0],
                p[1],
                f"{label}\n{p[0]:.1f},{ang:.1f}" if isinstance(ang, (int, float)) else label,
                color=color,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to annotate NA text: %s", exc)
            self.ax_section.text(p[0], p[1], label, color=color)

    def on_compare(self) -> None:
        # Get selected row
        item: str = self.verification_table_app.tree.focus()
        if not item:
            notify_warning("Confronto", "Seleziona una riga nella Verification Table")
            return
        row_idx: int = list(self.verification_table_app.tree.get_children()).index(item)
        inp: VerificationInput = self.verification_table_app.table_row_to_model(row_idx)

        # Prepare material and section repositories if present
        sec_repo = self.verification_table_app.section_repository
        mat_repo = self.verification_table_app.material_repository

        # Run TA and SLU
        ta_res: VerificationOutput | None = None
        slu_res: VerificationOutput | None = None
        try:
            ta_res = compute_ta_verification(inp, sec_repo, mat_repo)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Errore calcolo TA: %s", exc)
        try:
            slu_res: VerificationOutput = compute_slu_verification(inp, sec_repo, mat_repo)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Errore calcolo SLU: %s", exc)

        # Run .bas (torsion/bending adapted)
        try:
            engine: VerificationEngine = create_verification_engine((inp.verification_method or "TA").upper())
            mat_props: MaterialProperties = engine.get_material_properties(
                inp.material_concrete or "", inp.material_steel or "", material_source="RD2229"
            )
            bas_tors: dict[str, Any] = bas_torsion_verification(
                section=SectionGeometry(*get_section_geometry(inp, sec_repo, unit="cm")),
                reinforcement_tensile=ReinforcementLayer(area=inp.As_inf, distance=inp.d_inf),
                reinforcement_compressed=ReinforcementLayer(area=inp.As_sup, distance=inp.d_sup),
                material=mat_props,
                loads=LoadCase(N=inp.N, Mx=inp.Mx, My=inp.My, Mz=inp.Mz, Tx=inp.Tx, Ty=inp.Ty, At=inp.At),
                method=(inp.verification_method or "TA"),
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Errore .bas adapter: %s", exc)
            bas_tors = {"messages": [".bas adapter error"], "ok": False}

        # Present text summary
        self._present_summary(ta_res, slu_res, bas_tors)

        # Draw section and neutral axes with shading
        self.ax_section.clear()
        self.ax_bars.clear()
        b, h = get_section_geometry(inp, sec_repo, unit="cm")
        self.ax_section.add_patch(mpatches.Rectangle((0, 0), b, h, fill=False))

        ta_metrics = _metrics_of(ta_res)
        slu_metrics = _metrics_of(slu_res)
        bas_metrics = _metrics_of(bas_tors)

        methods = [
            ("TA", ta_res, "blue", ta_metrics),
            ("SLU", slu_res, "green", slu_metrics),
            (".bas", bas_tors, "magenta", bas_metrics),
        ]
        for label, res, color, metrics in methods:
            self._draw_method_na(b, h, label, res, metrics, color)

        self.ax_section.legend()
        self.ax_section.set_xlim(-0.1 * b, 1.1 * b)
        self.ax_section.set_ylim(h + 0.1 * h, -0.1 * h)

        # Prepare bar chart and numeric table — reuse metrics computed above
        self._populate_numeric_and_bars(ta_metrics, slu_metrics, bas_metrics)

    def _populate_numeric_and_bars(
        self,
        ta_metrics: dict[str, Any],
        slu_metrics: dict[str, Any],
        bas_metrics: dict[str, Any],
    ) -> None:
        asse_x_ta = f"{ta_metrics['asse_x']}"
        asse_x_slu = f"{slu_metrics['asse_x']}"
        asse_x_bas = f"{bas_metrics['asse_x'] if bas_metrics['asse_x'] is not None else ''}"

        angle_ta = f"{ta_metrics['angle']}"
        angle_slu = f"{slu_metrics['angle']}"
        angle_bas = f"{bas_metrics['angle'] if bas_metrics['angle'] is not None else ''}"

        sigma_ta = f"{ta_metrics['sigma_c_max']}"
        sigma_slu = f"{slu_metrics['sigma_c_max']}"
        sigma_bas = f"{bas_metrics['sigma_c_max']}"

        rows: list[tuple[str, str, str, str]] = [
            ("asse_neutro_x (cm)", asse_x_ta, asse_x_slu, asse_x_bas),
            ("inclinazione (deg)", angle_ta, angle_slu, angle_bas),
            ("sigma_c_max", sigma_ta, sigma_slu, sigma_bas),
        ]
        for r in rows:
            self.summary_table.insert("", "end", values=r)

        labels: list[str] = ["TA", "SLU", ".bas"]
        values = [ta_metrics["sigma_c_max"], slu_metrics["sigma_c_max"], bas_metrics["sigma_c_max"]]
        self.ax_bars.bar(labels, values, color=["blue", "green", "magenta"])
        self.ax_bars.set_ylabel("sigma_c_max (kg/cm2)")
        if self.canvas:
            self.canvas.draw()

    def _export(self, fmt: str) -> None:
        try:
            from tkinter import filedialog

            item: str = self.verification_table_app.tree.focus()
            if not item:
                notify_warning("Export", "Seleziona prima una riga nella Verification Table")
                return
            row_idx: int = list(self.verification_table_app.tree.get_children()).index(item)
            inp: VerificationInput = self.verification_table_app.table_row_to_model(row_idx)
            sec_repo = self.verification_table_app.section_repository
            mat_repo = self.verification_table_app.material_repository
            ta_res: VerificationOutput = compute_ta_verification(inp, sec_repo, mat_repo)
            slu_res: VerificationOutput = compute_slu_verification(inp, sec_repo, mat_repo)
            engine: VerificationEngine = create_verification_engine((inp.verification_method or "TA").upper())
            mat_props: MaterialProperties = engine.get_material_properties(
                inp.material_concrete or "", inp.material_steel or "", material_source="RD2229"
            )
            bas_tors: dict[str, Any] = bas_torsion_verification(
                section=SectionGeometry(*get_section_geometry(inp, sec_repo, unit="cm")),
                reinforcement_tensile=ReinforcementLayer(area=inp.As_inf, distance=inp.d_inf),
                reinforcement_compressed=ReinforcementLayer(area=inp.As_sup, distance=inp.d_sup),
                material=mat_props,
                loads=LoadCase(N=inp.N, Mx=inp.Mx, My=inp.My, Mz=inp.Mz, Tx=inp.Tx, Ty=inp.Ty, At=inp.At),
                method=(inp.verification_method or "TA"),
            )
            comp = {
                "TA": ta_res
                and {
                    "sigma_c_max": getattr(ta_res, "sigma_c_max", None),
                    "asse_neutro_x": getattr(ta_res, "asse_neutro_x", getattr(ta_res, "asse_neutro", None)),
                    "angle": getattr(ta_res, "inclinazione_asse_neutro", None),
                },
                "SLU": slu_res
                and {
                    "sigma_c_max": getattr(slu_res, "sigma_c_max", None),
                    "asse_neutro_x": getattr(slu_res, "asse_neutro_x", getattr(slu_res, "asse_neutro", None)),
                    "angle": getattr(slu_res, "inclinazione_asse_neutro", None),
                },
                ".bas": bas_tors,
            }
            if fmt == "csv":
                path: str = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                if not path:
                    return
                _write_csv_comp(comp, path)
                notify_info("Export", f"Exported CSV to {path}")
            elif fmt == "json":
                path: str = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
                if not path:
                    return
                _write_json_comp(comp, path)
                notify_info("Export", f"Exported JSON to {path}")
            else:
                path: str = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
                if not path:
                    return
                _write_txt_comp(comp, path)
                notify_info("Export", f"Exported TXT to {path}")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.exception("Export error: %s", exc)
            notify_error("Export", f"Errore export: {exc}")


def open_comparator_for_table(app: VerificationTableApp) -> None:
    try:
        w = VerificationComparatorWindow(app.winfo_toplevel(), app)
        w.transient(app.winfo_toplevel())
        w.grab_set()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception("Unable to open comparator window: %s", exc)
