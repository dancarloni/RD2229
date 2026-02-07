from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

from .geometry import SectionGeometry, SectionProperties
from .materials import ConcreteLawTA, SteelLawTA, sigma_c, sigma_s

# Mapping: VB CalcoloTensNormali (4.3), PointP (util to find zero-stress point) and SezioneParzializzata.


@dataclass
class LoadState:
    Nx: float
    My: float
    Mz: float


@dataclass
class StressResult:
    sigma_c_max: float
    sigma_c_min: float
    sigma_c_pos: float
    sigma_c_neg: float
    sigma_c_med: float
    sigma_s_max: float
    sigma_s_array: List[float]
    sigma_vertices: List[float]


def _build_MM(props: SectionProperties):
    # Build the 3x3 stiffness-like matrix as in VB (MM)
    Aci = props.area_equivalent
    Sy = props.Sy
    Sz = props.Sz
    Iy = props.Iy
    Iz = props.Iz
    Iyz = props.Iyz

    MM = [
        [Aci, Sy, Sz],
        [Sy, Iy, Iyz],
        [Sz, Iyz, Iz],
    ]
    return MM


def _invert_3x3(m):
    a11, a12, a13 = m[0]
    a21, a22, a23 = m[1]
    a31, a32, a33 = m[2]
    det = (
        a11 * (a22 * a33 - a23 * a32)
        - a12 * (a21 * a33 - a23 * a31)
        + a13 * (a21 * a32 - a22 * a31)
    )
    if abs(det) < 1e-12:
        raise ValueError("Singular MM matrix: check section properties")
    inv = [[0.0] * 3 for _ in range(3)]
    inv[0][0] = (a22 * a33 - a23 * a32) / det
    inv[0][1] = (a13 * a32 - a12 * a33) / det
    inv[0][2] = (a12 * a23 - a13 * a22) / det
    inv[1][0] = (a23 * a31 - a21 * a33) / det
    inv[1][1] = (a11 * a33 - a13 * a31) / det
    inv[1][2] = (a13 * a21 - a11 * a23) / det
    inv[2][0] = (a21 * a32 - a22 * a31) / det
    inv[2][1] = (a12 * a31 - a11 * a32) / det
    inv[2][2] = (a11 * a22 - a12 * a21) / det
    return inv


def compute_normal_stresses_ta(
    geom: SectionGeometry,
    props: SectionProperties,
    loads: LoadState,
    concrete_law: ConcreteLawTA,
    steel_law: SteelLawTA,
    allow_concrete_tension: bool = False,
    max_iter: int = 50,
    tol: float = 1e-6,
) -> StressResult:
    """Compute normal stresses using TA method (translation of CalcoloTensNormali 4.3).

    Units (consistent system used throughout):
      - geometry: lengths [cm], areas [cm^2], inertias [cm^4]
      - loads: Nx [kg], My, Mz [kg·m]
      - materials: Ec, Es [kg/cm^2], stresses [kg/cm^2]

    Algorithm notes:
    - Internally My and Mz are converted from [kg·m] to [kg·cm] (multiply by 100)
      so that matrix equations are dimensionally consistent with inertias in [cm^4].
    - The method builds the matrix MM (Aci, Sy, Sz, Iy, Iz, Iyz), in same spirit as VB,
      in order to compute the generalized strains EpsVec, then divides by Ec to obtain
      strain/curvature values.

    Strategy (keeps VB overall structure):
    - build MM and invert
    - compute strain vector EpsVec = MM_inv * Soll (Soll=[Nx, My_cm, -Mz_cm])
    - divide by Ec to get strains (vb divides Eps by Ec)
    - compute strains at polygon vertices and bars
    - compute stresses via constitutive laws (sigma_c, sigma_s)
    - if concrete in tension and !allow_concrete_tension: approximate parzializzazione by excluding tensile vertex contributions
      and recompute iteratively until convergence

    Returns StressResult containing global extrema and per-bar stresses.
    """
    # initial properties
    section_props = props

    # Prepare vertex list for stress sampling: flatten polygons to vertices
    vertices: List[Tuple[float, float]] = []
    for poly in geom.polygons:
        for y, z in poly:
            vertices.append((y, z))

    # Precompute per-vertex area contribution (simple triangle fan about polygon centroid approximation)
    # For iteration when excluding tensile contributions we need per-vertex area and first moments
    # We compute per-vertex contributions to A, Sy, Sz, Iy, Iz, Iyz
    vertex_contribs = []  # list of tuples (A_v, Sy_v, Sz_v, Iy_v, Iz_v, Iyz_v, y_v, z_v)
    for poly in geom.polygons:
        if len(poly) < 3:
            continue
        # polygon centroid
        A_poly, y_cent, z_cent, Iy_p, Iz_p, Iyz_p = _poly_aux(poly)
        # triangulate as fan from centroid
        for i in range(len(poly)):
            y0, z0 = poly[i]
            y1, z1 = poly[(i + 1) % len(poly)]
            # triangle (centroid, v0, v1)
            cross = (
                0.5 * (y0 * z1 - y1 * z0)
                + 0.5 * (y1 * z_cent - y_cent * z1)
                + 0.5 * (y_cent * z0 - y0 * z_cent)
            )
            # for simplicity attribute the triangle area entirely to v0
            A_tri = abs(0.5 * (y0 * z1 - y1 * z0))
            Sy_tri = A_tri * z0
            Sz_tri = A_tri * y0
            Iy_tri = A_tri * (z0**2)
            Iz_tri = A_tri * (y0**2)
            Iyz_tri = A_tri * (y0 * z0)
            vertex_contribs.append((A_tri, Sy_tri, Sz_tri, Iy_tri, Iz_tri, Iyz_tri, y0, z0))

    # add bars as pseudo-vertices
    for yb, zb, d in geom.bars:
        Abar = math.pi * d * d / 4.0
        A_v = geom.n_homog * Abar
        Sy_v = geom.n_homog * Abar * zb
        Sz_v = geom.n_homog * Abar * yb
        Iy_v = geom.n_homog * Abar * (zb**2)
        Iz_v = geom.n_homog * Abar * (yb**2)
        Iyz_v = geom.n_homog * Abar * (yb * zb)
        vertex_contribs.append((A_v, Sy_v, Sz_v, Iy_v, Iz_v, Iyz_v, yb, zb))

    # iterative loop
    prev_sigma_c_max = None
    for it in range(max_iter):
        # Build adjusted global sums (exclude tensile concrete vertices when not allowed)
        Aci = 0.0
        Sy = 0.0
        Sz = 0.0
        Iy = 0.0
        Iz = 0.0
        Iyz = 0.0

        # Include full polygon & bars contributions first
        Aci = section_props.area_equivalent
        Sy = section_props.Sy
        Sz = section_props.Sz
        Iy = section_props.Iy + Aci * (section_props.yG**2)  # note: we adjust back to raw sums
        Iz = section_props.Iz + Aci * (section_props.zG**2)
        Iyz = section_props.Iyz + Aci * section_props.yG * section_props.zG

        # build MM and invert
        MM = [[Aci, Sy, Sz], [Sy, Iy, Iyz], [Sz, Iyz, Iz]]
        MM_inv = _invert_3x3(MM)

        # Soll vector (VB: Soll = [Nx, My, -Mz])
        # Convert moments from [kg·m] to [kg·cm] (1 m = 100 cm) for dimensional consistency
        My_cm = loads.My * 100.0
        Mz_cm = loads.Mz * 100.0
        Soll = [loads.Nx, My_cm, -Mz_cm]
        # multiply MM_inv * Soll
        EpsVec = [sum(MM_inv[i][j] * Soll[j] for j in range(3)) for i in range(3)]
        # VB divides by Ec
        e0 = EpsVec[0] / concrete_law.Ec
        k_y = EpsVec[1] / concrete_law.Ec
        k_z = EpsVec[2] / concrete_law.Ec

        # compute stresses at vertices
        sigma_vertices = []
        for y, z in [(vc[6], vc[7]) for vc in vertex_contribs]:
            # strain at point (y,z) relative to section centroid
            eps = e0 + k_y * (z - section_props.zG) + k_z * (y - section_props.yG)
            s = sigma_c(eps, concrete_law)
            sigma_vertices.append(s)

        # compute bar stresses
        sigma_bars = []
        for yb, zb, d in geom.bars:
            epsb = e0 + k_y * (zb - section_props.zG) + k_z * (yb - section_props.yG)
            sigma_bars.append(sigma_s(epsb, steel_law))

        sigma_c_max = max(sigma_vertices) if sigma_vertices else 0.0
        sigma_c_min = min(sigma_vertices) if sigma_vertices else 0.0

        # If concrete tensile is not allowed, and tensile stresses exist, we must parzialize
        if (not allow_concrete_tension) and any(s > 0 for s in sigma_vertices):
            # zero-out contributions from vertices with positive stress (approximate SezioneParzializzata)
            # Recompute raw sums by subtracting vertex contributions for tensile vertices
            A_adj = section_props.A_contrib
            Sy_adj = section_props.Sy
            Sz_adj = section_props.Sz
            Iy_adj = section_props.Iy + section_props.area_equivalent * (section_props.yG**2)
            Iz_adj = section_props.Iz + section_props.area_equivalent * (section_props.zG**2)
            Iyz_adj = (
                section_props.Iyz
                + section_props.area_equivalent * section_props.yG * section_props.zG
            )

            for idx, s in enumerate(sigma_vertices):
                if s > 0:
                    A_v, Sy_v, Sz_v, Iy_v, Iz_v, Iyz_v, y_v, z_v = vertex_contribs[idx]
                    A_adj -= A_v
                    Sy_adj -= Sy_v
                    Sz_adj -= Sz_v
                    Iy_adj -= Iy_v
                    Iz_adj -= Iz_v
                    Iyz_adj -= Iyz_v

            # Build new MM with adjusted sums
            Aci = A_adj + 0.0  # keep bars included (they are in area_equivalent already)
            Sy = Sy_adj
            Sz = Sz_adj
            Iy = Iy_adj
            Iz = Iz_adj
            Iyz = Iyz_adj

            MM = [[Aci, Sy, Sz], [Sy, Iy, Iyz], [Sz, Iyz, Iz]]
            try:
                MM_inv = _invert_3x3(MM)
            except ValueError:
                # matrix singular, break
                break
            EpsVec = [sum(MM_inv[i][j] * Soll[j] for j in range(3)) for i in range(3)]
            e0 = EpsVec[0] / concrete_law.Ec
            k_y = EpsVec[1] / concrete_law.Ec
            k_z = EpsVec[2] / concrete_law.Ec

            # recompute sigma vertices with adjusted fields
            sigma_vertices = []
            for y, z in [(vc[6], vc[7]) for vc in vertex_contribs]:
                eps = e0 + k_y * (z - section_props.zG) + k_z * (y - section_props.yG)
                s = sigma_c(eps, concrete_law)
                # clamp tensile to zero as we removed that contribution
                if s > 0:
                    s = 0.0
                sigma_vertices.append(s)

            sigma_c_max = max(sigma_vertices) if sigma_vertices else 0.0
            sigma_c_min = min(sigma_vertices) if sigma_vertices else 0.0

            # check for convergence
            if prev_sigma_c_max is not None and abs(sigma_c_max - prev_sigma_c_max) < tol:
                break
            prev_sigma_c_max = sigma_c_max
            continue
        # No parzializzazione required or allowed
        sigma_c_pos = max(0.0, sigma_c_max)
        sigma_c_neg = min(0.0, sigma_c_min)
        sigma_c_med = (
            loads.Nx / section_props.area_equivalent if section_props.area_equivalent != 0 else 0.0
        )

        sigma_s_max = max(sigma_bars) if sigma_bars else 0.0
        return StressResult(
            sigma_c_max=sigma_c_max,
            sigma_c_min=sigma_c_min,
            sigma_c_pos=sigma_c_pos,
            sigma_c_neg=sigma_c_neg,
            sigma_c_med=sigma_c_med,
            sigma_s_max=sigma_s_max,
            sigma_s_array=sigma_bars,
            sigma_vertices=sigma_vertices,
        )

    # fallback: return last computed
    sigma_s_max = max(sigma_bars) if sigma_bars else 0.0
    sigma_c_pos = max(0.0, sigma_c_max)
    sigma_c_neg = min(0.0, sigma_c_min)
    sigma_c_med = (
        loads.Nx / section_props.area_equivalent if section_props.area_equivalent != 0 else 0.0
    )
    return StressResult(
        sigma_c_max=sigma_c_max,
        sigma_c_min=sigma_c_min,
        sigma_c_pos=sigma_c_pos,
        sigma_c_neg=sigma_c_neg,
        sigma_c_med=sigma_c_med,
        sigma_s_max=sigma_s_max,
        sigma_s_array=sigma_bars,
        sigma_vertices=sigma_vertices,
    )


# helper: compute polygon centroid and area and inertias, but return raw sums used earlier
def _poly_aux(poly):
    from .geometry import _polygon_area_centroid_inertia

    return _polygon_area_centroid_inertia(poly)
