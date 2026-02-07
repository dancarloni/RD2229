"""GUI window to compare verification methods (.bas translation vs TA vs SLU)."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk

import matplotlib

from sections_app.services.notification import notify_error, notify_info, notify_warning

matplotlib.use("Agg")  # Use Agg for headless tests; GUI will embed FigureCanvasTkAgg if available
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from src.core_calculus.core.verification_bas_adapter import bas_torsion_verification
from src.core_calculus.core.verification_core import LoadCase, ReinforcementLayer, SectionGeometry
from src.core_calculus.core.verification_engine import create_verification_engine
from verification_table import (
    VerificationTableApp,
    compute_slu_verification,
    compute_ta_verification,
    get_section_geometry,
)

logger = logging.getLogger(__name__)

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    FigureCanvasTkAgg = None
MATPLOTLIB_TK = FigureCanvasTkAgg is not None


class VerificationComparatorWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, verification_table_app: VerificationTableApp):
        super().__init__(master)
        self.title("Confronto metodi: .bas vs TA vs SLU")
        self.geometry("900x600")
        self.verification_table_app = verification_table_app

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
        self.ax_section = self.fig.add_subplot(121)
        self.ax_section.set_title("Sezione e asse neutro")
        self.ax_section.set_xlim(0, 1)
        self.ax_section.set_ylim(0, 1)
        self.ax_bars = self.fig.add_subplot(122)
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

    # --- Helper geometry utilities ---------------------------------
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
        theta = math.radians(angle_deg)
        vx, vy = math.cos(theta), math.sin(theta)

        candidates = []
        # x = 0
        if abs(vx) > 1e-12:
            t = (0 - px) / vx
            y = py + t * vy
            if -1e-6 <= y <= h + 1e-6:
                candidates.append((0.0, y))
        # x = b
        if abs(vx) > 1e-12:
            t = (b - px) / vx
            y = py + t * vy
            if -1e-6 <= y <= h + 1e-6:
                candidates.append((b, y))
        # y = 0
        if abs(vy) > 1e-12:
            t = (0 - py) / vy
            x = px + t * vx
            if -1e-6 <= x <= b + 1e-6:
                candidates.append((x, 0.0))
        # y = h
        if abs(vy) > 1e-12:
            t = (h - py) / vy
            x = px + t * vx
            if -1e-6 <= x <= b + 1e-6:
                candidates.append((x, h))

        # Remove duplicates (within tol)
        unique = []
        for c in candidates:
            if not any((abs(c[0] - u[0]) < 1e-6 and abs(c[1] - u[1]) < 1e-6) for u in unique):
                unique.append(c)
        if len(unique) >= 2:
            return unique[0], unique[1]
        # Fallback: return two points along the vector clipped to big extents
        return (max(0.0, min(b, px - 10 * vx)), max(0.0, min(h, py - 10 * vy))), (
            max(0.0, min(b, px + 10 * vx)),
            max(0.0, min(h, py + 10 * vy)),
        )

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
        n = len(poly)
        for i in range(n):
            a = poly[i]
            b = poly[(i + 1) % n]
            ax, ay = a
            bx, by = b
            sa = cross(v[0], v[1], ax - p[0], ay - p[1])
            sb = cross(v[0], v[1], bx - p[0], by - p[1])
            if keep_positive:
                inside_a = sa >= -1e-9
                inside_b = sb >= -1e-9
            else:
                inside_a = sa <= 1e-9
                inside_b = sb <= 1e-9
            if inside_a:
                out.append(a)
            if inside_a ^ inside_b:
                # compute intersection
                dx = bx - ax
                dy = by - ay
                denom = v[0] * dy - v[1] * dx
                if abs(denom) > 1e-12:
                    t = (v[0] * (ay - p[1]) - v[1] * (ax - p[0])) / denom
                    ix = ax + dx * t
                    iy = ay + dy * t
                    out.append((ix, iy))
        return out

    @staticmethod
    def _compute_shaded_polygon(
        b: float,
        h: float,
        p: tuple[float, float],
        angle_deg: float,
        pick_side_point: tuple[float, float] = None,
    ) -> list[tuple[float, float]]:
        # Build rectangle polygon
        rect = [(0.0, 0.0), (b, 0.0), (b, h), (0.0, h)]
        import math

        theta = math.radians(angle_deg)
        v = (math.cos(theta), math.sin(theta))
        # If pick_side_point is None, use top-center to define which side is 'above'
        if pick_side_point is None:
            pick_side_point = (b / 2.0, 0.0)

        # Determine sign for pick point
        def cross(vx, vy, wx, wy):
            return vx * wy - vy * wx

        sign = cross(v[0], v[1], pick_side_point[0] - p[0], pick_side_point[1] - p[1])
        keep_positive = sign >= 0
        return VerificationComparatorWindow._clip_polygon_by_halfplane(rect, p, v, keep_positive=keep_positive)

    def on_compare(self):
        # Get selected row
        item = self.verification_table_app.tree.focus()
        if not item:
            notify_warning("Confronto", "Seleziona una riga nella Verification Table")
            return
        row_idx = list(self.verification_table_app.tree.get_children()).index(item)
        inp = self.verification_table_app.table_row_to_model(row_idx)

        # Prepare material and section repositories if present
        sec_repo = self.verification_table_app.section_repository
        mat_repo = self.verification_table_app.material_repository

        # Run TA and SLU
        ta_res = None
        slu_res = None
        try:
            ta_res = compute_ta_verification(inp, sec_repo, mat_repo)
        except Exception as e:
            logger.exception("Errore calcolo TA: %s", e)
        try:
            slu_res = compute_slu_verification(inp, sec_repo, mat_repo)
        except Exception as e:
            logger.exception("Errore calcolo SLU: %s", e)

        # Run .bas (torsion/bending adapted)
        try:
            engine = create_verification_engine((inp.verification_method or "TA").upper())
            mat_props = engine.get_material_properties(
                inp.material_concrete or "", inp.material_steel or "", material_source="RD2229"
            )
            bas_tors = bas_torsion_verification(
                section=SectionGeometry(*get_section_geometry(inp, sec_repo, unit="cm")),
                reinforcement_tensile=ReinforcementLayer(area=inp.As_inf, distance=inp.d_inf),
                reinforcement_compressed=ReinforcementLayer(area=inp.As_sup, distance=inp.d_sup),
                material=mat_props,
                loads=LoadCase(N=inp.N, Mx=inp.Mx, My=inp.My, Mz=inp.Mz, Tx=inp.Tx, Ty=inp.Ty, At=inp.At),
                method=(inp.verification_method or "TA"),
            )
        except Exception:
            bas_tors = {"messages": [".bas adapter error"], "ok": False}

        # Present text summary
        self.txt_results.delete("1.0", tk.END)

        def _summary(res, label):
            if res is None:
                return f"{label}: errore\n"
            if isinstance(res, dict):
                return f"{label}: {res.get('messages', [])} OK={res.get('ok')}\n"
            # assume VerificationOutput-like
            msgs = getattr(res, "messaggi", []) or getattr(res, "messages", []) or []
            details = (
                f"{label}: esito={getattr(res,'esito','')} "
                f"sigma_c_max={getattr(res,'sigma_c_max','')} "
                f"asse_neutro_x={getattr(res,'asse_neutro_x', getattr(res,'asse_neutro',''))} "
                f"inclinazione={getattr(res,'inclinazione_asse_neutro','')}\n"
            )
            return details + (msgs[0] + "\n" if msgs else "")

        self.txt_results.insert(tk.END, _summary(ta_res, "TA"))
        self.txt_results.insert(tk.END, _summary(slu_res, "SLU"))
        self.txt_results.insert(tk.END, _summary(bas_tors, ".bas (Torsione)"))

        self.txt_results.insert(tk.END, "\nNumeric summary:\n")
        self.summary_table.delete(*self.summary_table.get_children())

        # Draw section and neutral axes with shading
        self.ax_section.clear()
        self.ax_bars.clear()
        b, h = get_section_geometry(inp, sec_repo, unit="cm")
        self.ax_section.add_patch(mpatches.Rectangle((0, 0), b, h, fill=False))

        # helper to obtain a point on NA and angle
        def na_point_and_angle(res):
            if res is None:
                return None
            # prefer explicit x,y if provided
            px = getattr(res, "asse_neutro_x", None) or getattr(res, "asse_neutro", None)
            py = getattr(res, "asse_neutro_y", None)
            ang = getattr(res, "inclinazione_asse_neutro", 0.0)
            if isinstance(px, (int, float)) and isinstance(py, (int, float)):
                return (px, py), ang
            if isinstance(px, (int, float)):
                return (b / 2.0, px), ang
            return (b / 2.0, h / 2.0), ang

        def _get_metrics(res):
            if res is None:
                return {
                    "sigma_c_max": 0.0,
                    "sigma_c_min": 0.0,
                    "sigma_s_max": 0.0,
                    "asse_x": None,
                    "angle": None,
                }
            if isinstance(res, dict):
                return {
                    "sigma_c_max": res.get("Taux_max", 0.0),
                    "sigma_c_min": 0.0,
                    "sigma_s_max": 0.0,
                    "asse_x": None,
                    "angle": None,
                }
            return {
                "sigma_c_max": getattr(res, "sigma_c_max", 0.0),
                "sigma_c_min": getattr(res, "sigma_c_min", 0.0),
                "sigma_s_max": getattr(res, "sigma_s_max", 0.0),
                "asse_x": getattr(res, "asse_neutro_x", getattr(res, "asse_neutro", None)),
                "angle": getattr(res, "inclinazione_asse_neutro", None),
            }

        ta_metrics = _get_metrics(ta_res)
        slu_metrics = _get_metrics(slu_res)
        bas_metrics = _get_metrics(bas_tors)

        methods = [("TA", ta_res, "blue", ta_metrics), ("SLU", slu_res, "green", slu_metrics)]
        for label, res, color, metrics in methods:
            out = na_point_and_angle(res)
            if out is None:
                continue
            p, ang = out
            # endpoints
            e1, e2 = self._compute_na_endpoints(b, h, p, ang)
            # decide compression side using stresses (user preference)
            # choose top-center if sigma_c_max dominates, bottom-center otherwise
            pick_point = (b / 2.0, 0.0) if abs(metrics["sigma_c_max"]) >= abs(metrics["sigma_c_min"]) else (b / 2.0, h)
            poly = self._compute_shaded_polygon(b, h, p, ang, pick_side_point=pick_point)
            self.ax_section.plot([e1[0], e2[0]], [e1[1], e2[1]], color=color, linewidth=2, label=f"{label} NA")
            if poly:
                self.ax_section.add_patch(mpatches.Polygon(poly, color=color, alpha=0.12))
            # annotate with coordinate and angle
            try:
                self.ax_section.text(
                    p[0],
                    p[1],
                    f"{label}\n{p[0]:.1f},{ang:.1f}" if isinstance(ang, (int, float)) else label,
                    color=color,
                )
            except Exception:
                self.ax_section.text(p[0], p[1], label, color=color)

        self.ax_section.legend()
        self.ax_section.set_xlim(-0.1 * b, 1.1 * b)
        self.ax_section.set_ylim(h + 0.1 * h, -0.1 * h)

        # Prepare bar chart and numeric table
        def _get_metrics(res):
            if res is None:
                return {"sigma_c_max": 0.0, "sigma_s_max": 0.0, "asse_x": None, "angle": None}
            if isinstance(res, dict):
                return {
                    "sigma_c_max": res.get("Taux_max", 0.0),
                    "sigma_s_max": 0.0,
                    "asse_x": None,
                    "angle": None,
                }
            return {
                "sigma_c_max": getattr(res, "sigma_c_max", 0.0),
                "sigma_s_max": getattr(res, "sigma_s_max", 0.0),
                "asse_x": getattr(res, "asse_neutro_x", getattr(res, "asse_neutro", None)),
                "angle": getattr(res, "inclinazione_asse_neutro", None),
            }

        ta_metrics = _get_metrics(ta_res)
        slu_metrics = _get_metrics(slu_res)
        bas_metrics = _get_metrics(bas_tors)

        # Fill summary table
        rows = [
            (
                "asse_neutro_x (cm)",
                f"{ta_metrics['asse_x']}",
                f"{slu_metrics['asse_x']}",
                f"{bas_metrics['asse_x'] if bas_metrics['asse_x'] is not None else ''}",
            ),
            (
                "inclinazione (deg)",
                f"{ta_metrics['angle']}",
                f"{slu_metrics['angle']}",
                f"{bas_metrics['angle'] if bas_metrics['angle'] is not None else ''}",
            ),
            (
                "sigma_c_max",
                f"{ta_metrics['sigma_c_max']}",
                f"{slu_metrics['sigma_c_max']}",
                f"{bas_metrics['sigma_c_max']}",
            ),
        ]
        for r in rows:
            self.summary_table.insert("", "end", values=r)

        # Bar chart: show sigma_c_max for methods
        labels = ["TA", "SLU", ".bas"]
        values = [ta_metrics["sigma_c_max"], slu_metrics["sigma_c_max"], bas_metrics["sigma_c_max"]]
        self.ax_bars.bar(labels, values, color=["blue", "green", "magenta"])
        self.ax_bars.set_ylabel("sigma_c_max (kg/cm2)")
        if self.canvas:
            self.canvas.draw()

    def _export(self, fmt: str):
        try:
            import csv
            import json
            from tkinter import filedialog

            item = self.verification_table_app.tree.focus()
            if not item:
                notify_warning("Export", "Seleziona prima una riga nella Verification Table")
                return
            row_idx = list(self.verification_table_app.tree.get_children()).index(item)
            inp = self.verification_table_app.table_row_to_model(row_idx)
            sec_repo = self.verification_table_app.section_repository
            mat_repo = self.verification_table_app.material_repository
            ta_res = compute_ta_verification(inp, sec_repo, mat_repo)
            slu_res = compute_slu_verification(inp, sec_repo, mat_repo)
            engine = create_verification_engine((inp.verification_method or "TA").upper())
            mat_props = engine.get_material_properties(
                inp.material_concrete or "", inp.material_steel or "", material_source="RD2229"
            )
            bas_tors = bas_torsion_verification(
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
                path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                if not path:
                    return
                with open(path, "w", newline="", encoding="utf-8") as fh:
                    w = csv.writer(fh)
                    w.writerow(["method", "sigma_c_max", "asse_neutro_x", "angle"])
                    for k, v in comp.items():
                        if v:
                            w.writerow(
                                [
                                    k,
                                    v.get("sigma_c_max", ""),
                                    v.get("asse_neutro_x", ""),
                                    v.get("angle", ""),
                                ]
                            )
                notify_info("Export", f"Exported CSV to {path}")
            elif fmt == "json":
                path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
                if not path:
                    return
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(comp, fh, default=str, indent=2)
                notify_info("Export", f"Exported JSON to {path}")
            else:
                path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
                if not path:
                    return
                with open(path, "w", encoding="utf-8") as fh:
                    for k, v in comp.items():
                        fh.write(f"== {k} ==\n")
                        fh.write(str(v) + "\n")
                notify_info("Export", f"Exported TXT to {path}")
        except Exception as e:
            logger.exception("Export error: %s", e)
            notify_error("Export", f"Errore export: {e}")


def open_comparator_for_table(app: VerificationTableApp):
    try:
        w = VerificationComparatorWindow(app.winfo_toplevel(), app)
        w.transient(app.winfo_toplevel())
        w.grab_set()
    except Exception:
        logger.exception("Unable to open comparator window")
