"""Esegui alcuni test numerici di esempio per il package historical_ta.
Fornisce output leggibile per verificare comportamento in condizioni diverse.
"""

from historical_ta.checks import AllowableStresses, check_allowable_stresses_ta
from historical_ta.geometry import SectionGeometry, compute_section_properties
from historical_ta.materials import ConcreteLawTA, SteelLawTA
from historical_ta.stress import LoadState, compute_normal_stresses_ta


def print_case(title, geom, loads, conc, steel, limits=None, allow_tension=False):
    print("\n" + "=" * 80)
    print(title)
    props = compute_section_properties(geom)
    print(f"Asez = {props.area_concrete:.3f} cm^2, Aci = {props.area_equivalent:.3f} cm^2")
    print(f"Centroid (y,z) = ({props.yG:.3f}, {props.zG:.3f}) cm")
    print(f"Iy = {props.Iy:.3f} cm^4, Iz = {props.Iz:.3f} cm^4, Iyz = {props.Iyz:.3f} cm^4")

    res = compute_normal_stresses_ta(geom, props, loads, conc, steel, allow_concrete_tension=allow_tension)
    print(f"sigma_c_max = {res.sigma_c_max:.3f} kg/cm^2, sigma_c_min = {res.sigma_c_min:.3f} kg/cm^2")
    print(f"sigma_c_med = {res.sigma_c_med:.3f} kg/cm^2")
    print(f"sigma_s_max = {res.sigma_s_max:.3f} kg/cm^2")
    if limits:
        chk = check_allowable_stresses_ta(res, limits)
        print("Checks: ", chk.ok, chk.messages)


def main():
    # Materiali tipici
    conc = ConcreteLawTA(fcd=30.0, Ec=30000.0, eps_c2=0.002, eps_c3=0.003, eps_c4=0.004, eps_cu=0.0035)
    steel = SteelLawTA(Es=210000.0, fyd=500.0, eps_yd=0.00238, eps_su=0.1)
    limits = AllowableStresses(sigma_c_allow=30.0, sigma_s_allow=500.0, sigma_c_med_allow=10.0)

    # Caso 1: Rettangolo 30x15, nessun carico
    poly1 = [[(0.0, 0.0), (30.0, 0.0), (30.0, 15.0), (0.0, 15.0)]]
    geom1 = SectionGeometry(polygons=poly1, bars=[], n_homog=10.0)
    loads1 = LoadState(Nx=0.0, My=0.0, Mz=0.0)
    print_case("Caso 1: Rettangolo 30x15, vuoto", geom1, loads1, conc, steel, limits)

    # Caso 2: Rettangolo, puro assiale Nx = -3000 kg (compression moderate)
    loads2 = LoadState(Nx=-3000.0, My=0.0, Mz=0.0)  # Nx in [kg]
    print_case("Caso 2: Rettangolo, sola compressione Axial -3000 kg", geom1, loads2, conc, steel, limits)

    # Caso 3: Rettangolo 30x15, momento My (bending about y) = 1000 kg·m
    loads3 = LoadState(Nx=0.0, My=1000.0, Mz=0.0)
    print_case("Caso 3: Rettangolo, My = 1000 kg·m (~9.81 kNm)", geom1, loads3, conc, steel, limits)

    # Caso 4: Rettangolo + armatura (due barre) con eccentricità -> combinazione
    bars = [(5.0, 2.5, 1.0), (25.0, 12.5, 1.0)]
    geom4 = SectionGeometry(polygons=poly1, bars=bars, n_homog=10.0)
    loads4 = LoadState(Nx=-3000.0, My=500.0, Mz=-200.0)
    print_case("Caso 4: Rettangolo con 2 barre, combinato", geom4, loads4, conc, steel, limits)


if __name__ == "__main__":
    main()
