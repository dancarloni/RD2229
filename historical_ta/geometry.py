from __future__ import annotations

from dataclasses import dataclass
from math import pi

# This module corresponds to VB routines: DatiSezioneCA, CalcoloAreaMomStaticiMomInerziaSezReagente,
# SezioneParzializzata (support functions) and CoordBaricentriTondini.
# The functions here are pure and operate on provided data structures (no Excel interaction).

Point = tuple[float, float]  # (y, z)
Bar = tuple[float, float, float]  # (y, z, diameter)


@dataclass
class SectionGeometry:
    """Section geometry data.

    Units:
      - coordinates y,z: [cm]
      - polygons: list of rings, each vertex (y,z) in [cm]
      - bars: list of tuples (y [cm], z [cm], diameter [cm])
      - n_homog: float, Es/Ec (dimensionless)
    """

    # polygons: list of polygon rings (outer followed by holes if any); each polygon is list of (y,z)
    polygons: list[list[Point]]
    bars: list[Bar]
    n_homog: float = 1.0  # n = Es/Ec (homogenization coefficient)


@dataclass
class SectionProperties:
    area_concrete: float
    area_equivalent: float
    yG: float
    zG: float
    Iy: float
    Iz: float
    Iyz: float
    # internal raw values for transparency
    A_contrib: float | None = None
    Sy: float | None = None
    Sz: float | None = None

    """Units:
      - area_concrete, area_equivalent: [cm^2]
      - yG, zG: [cm]
      - Iy, Iz, Iyz: [cm^4]
    """


def _polygon_area_centroid_inertia(polygon: list[Point]):
    """Compute area, centroid (y,z) and second moments for a single polygon ring about origin.

    Uses standard polygon formulas. Returns (A, y_c, z_c, Iy, Iz, Iyz) where Iy is integral y^2 dA etc.
    """
    if len(polygon) < 3:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    A = 0.0
    Cy = 0.0
    Cz = 0.0
    Iy = 0.0
    Iz = 0.0
    Iyz = 0.0

    for i in range(len(polygon)):
        y0, z0 = polygon[i]
        y1, z1 = polygon[(i + 1) % len(polygon)]
        cross = y0 * z1 - y1 * z0
        A += cross
        Cy += (y0 + y1) * cross
        Cz += (z0 + z1) * cross
        Iy += (z0 * z0 + z0 * z1 + z1 * z1) * cross
        Iz += (y0 * y0 + y0 * y1 + y1 * y1) * cross
        Iyz += (y0 * z1 + 2 * y0 * z0 + 2 * y1 * z1 + y1 * z0) * cross

    A *= 0.5
    if abs(A) < 1e-12:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    y_c = Cy / (6 * A)
    z_c = Cz / (6 * A)

    # Moments as per standard polygon integrals
    Iy = Iy / 12.0
    Iz = Iz / 12.0
    Iyz = Iyz / 24.0

    return A, y_c, z_c, Iy, Iz, Iyz


def compute_section_properties(geom: SectionGeometry) -> SectionProperties:
    """Translate VB: DatiSezioneCA + CalcoloAreaMomStaticiMomInerziaSezReagente.

    Given a `SectionGeometry` with polygon rings and bars, compute:
      - Asez (concrete area)
      - Aci (equivalent area = Asez + n * sum(A_bar))
      - baricentro Gr (yG, zG) of the equivalent section
      - moments of inertia Iy, Iz, Iyz of equivalent section

    Returns SectionProperties (values in same conventions as VB, axes y and z).
    """
    # polygon contributions (outer rings positive, holes expected as additional polygons with appropriate orientation)
    Asez = 0.0
    Sy_pr = 0.0
    Sz_pr = 0.0
    Iy_pr = 0.0
    Iz_pr = 0.0
    Iyz_pr = 0.0

    for poly in geom.polygons:
        A, y_c, z_c, Iy_poly, Iz_poly, Iyz_poly = _polygon_area_centroid_inertia(poly)
        # accumulate
        Asez += A
        Sy_pr += A * y_c
        Sz_pr += A * z_c
        Iy_pr += Iy_poly
        Iz_pr += Iz_poly
        Iyz_pr += Iyz_poly

    # bars contributions (converted area = n * A_bar)
    Aft = 0.0
    for yb, zb, d in geom.bars:
        Abar = pi * (d**2) / 4.0
        Aft += Abar
        Sy_pr += geom.n_homog * Abar * yb
        Sz_pr += geom.n_homog * Abar * zb
        Iy_pr += geom.n_homog * Abar * (zb**2)
        Iz_pr += geom.n_homog * Abar * (yb**2)
        Iyz_pr += geom.n_homog * Abar * (yb * zb)

    # Equivalent area
    Aci = Asez + geom.n_homog * Aft

    if Aci == 0:
        yG = 0.0
        zG = 0.0
    else:
        yG = Sy_pr / Aci
        zG = Sz_pr / Aci

    # Steiner: convert second moments from reference origin to axes through centroid G
    Iy = Iy_pr - Aci * (yG**2)
    Iz = Iz_pr - Aci * (zG**2)
    Iyz = Iyz_pr - Aci * yG * zG

    return SectionProperties(
        area_concrete=Asez,
        area_equivalent=Aci,
        yG=yG,
        zG=zG,
        Iy=Iy,
        Iz=Iz,
        Iyz=Iyz,
        A_contrib=Asez,
        Sy=Sy_pr,
        Sz=Sz_pr,
    )
