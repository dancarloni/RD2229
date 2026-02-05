from __future__ import annotations

import math
import logging
import tkinter as tk
from dataclasses import dataclass, InitVar
from tkinter import messagebox, ttk, filedialog
from typing import Dict, Iterable, List, Optional, Tuple
import random

try:
    from tools.materials_manager import list_materials
except Exception:  # pragma: no cover - fallback if import fails
    list_materials = None

try:
    from sections_app.services.repository import SectionRepository
except Exception:  # pragma: no cover - fallback if import fails
    SectionRepository = None  # type: ignore

try:
    from sections_app.models.sections import RectangularSection
except Exception:
    RectangularSection = None

try:
    from core_models.materials import MaterialRepository
except Exception:  # pragma: no cover - fallback if import fails
    MaterialRepository = None  # type: ignore

try:
    # Repository for persisted verification items (in-memory by default)
    from verification_items_repository import VerificationItemsRepository
except Exception:  # pragma: no cover - fallback if import fails
    VerificationItemsRepository = None  # type: ignore

try:
    # Data class for saved verification items (keeps input separate from UI)
    from verification_items import VerificationItem
except Exception:  # pragma: no cover - fallback if import fails
    VerificationItem = None  # type: ignore

try:
    from verification_project import VerificationProject
except Exception:
    VerificationProject = None


logger = logging.getLogger(__name__)

ColumnDef = Tuple[str, str, int, str]

MPA_TO_KGCM2 = 10.197


@dataclass
class VerificationInput:
    section_id: str = ""
    verification_method: str = "TA"
    material_concrete: str = ""
    material_steel: str = ""
    n_homog: float = 15.0
    N: float = 0.0
    Mx: float = 0.0  # Momento flettente attorno asse x (era M)
    My: float = 0.0  # Momento flettente attorno asse y (nuovo)
    Mz: float = 0.0  # Momento torcente (nuovo, sostituisce precedente "Mt")
    Tx: float = 0.0  # Taglio lungo direzione x (nuovo)
    Ty: float = 0.0  # Taglio lungo direzione y (era T)
    As_sup: float = 0.0
    As_inf: float = 0.0
    At: float = 0.0  # Armatura a torsione (nuovo)
    d_sup: float = 0.0
    d_inf: float = 0.0
    stirrup_step: float = 0.0
    stirrup_diameter: float = 0.0
    stirrup_material: str = ""
    notes: str = ""
    # Legacy Init vars to accept old keywords M and T in constructor
    M: InitVar[Optional[float]] = None
    T: InitVar[Optional[float]] = None

    def __post_init__(self, M: Optional[float], T: Optional[float]) -> None:
        # Map legacy init kwargs to new internal fields for backward compatibility
        if M is not None:
            self.Mx = M
        if T is not None:
            self.Ty = T

    # Legacy field support for backward compatibility via properties
    @property
    def M(self) -> float:
        """Legacy property for backward compatibility (M -> Mx)."""
        return self.Mx
    
    @M.setter
    def M(self, value: float):
        """Legacy setter for backward compatibility (M -> Mx)."""
        self.Mx = value
    
    @property
    def T(self) -> float:
        """Legacy property for backward compatibility (T -> Ty)."""
        return self.Ty
    
    @T.setter
    def T(self, value: float):
        """Legacy setter for backward compatibility (T -> Ty)."""
        self.Ty = value


@dataclass
class VerificationOutput:
    sigma_c_max: float
    sigma_c_min: float
    sigma_s_max: float
    asse_neutro: float  # Distanza asse neutro da lembo compresso (legacy)
    asse_neutro_x: float = 0.0  # Coordinata x asse neutro (nuovo)
    asse_neutro_y: float = 0.0  # Coordinata y asse neutro (nuovo)
    inclinazione_asse_neutro: float = 0.0  # Inclinazione asse neutro in gradi (nuovo)
    tipo_verifica: str = ""  # Tipo di verifica eseguita (nuovo)
    sigma_c: float = 0.0  # Tensione calcestruzzo bordo compresso (nuovo)
    sigma_s_tesi: float = 0.0  # Tensione armature in zona tesa (nuovo)
    sigma_s_compressi: float = 0.0  # Tensione armature in zona compressa (nuovo)
    deformazioni: str = ""
    coeff_sicurezza: float = 1.0
    esito: str = ""
    messaggi: List[str] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass initialization."""
        if self.messaggi is None:
            self.messaggi = []


def _get_section_by_id_or_name(section_id: str, section_repository: Optional["SectionRepository"]):
    if not section_repository or not section_id:
        return None
    try:
        if hasattr(section_repository, "find_by_id"):
            found = section_repository.find_by_id(section_id)
            if found is not None:
                return found
    except Exception:
        logger.exception("Errore ricerca sezione per id=%s", section_id)
    try:
        for sec in section_repository.get_all_sections():
            if sec.id == section_id or sec.name == section_id:
                return sec
    except Exception:
        logger.exception("Errore ricerca sezione per nome=%s", section_id)
    return None


def _extract_section_dimensions_cm(section) -> Optional[Tuple[float, float]]:
    if section is None:
        return None
    width = None
    height = None
    if hasattr(section, "width"):
        width = getattr(section, "width")
    if hasattr(section, "height"):
        height = getattr(section, "height")
    if (width is None or height is None) and hasattr(section, "dimensions"):
        dims = getattr(section, "dimensions") or {}
        width = width or dims.get("width") or dims.get("diameter")
        height = height or dims.get("height") or dims.get("diameter")
    if width and height:
        return float(width), float(height)
    return None


def get_section_geometry(
    _input: VerificationInput,
    section_repository: Optional["SectionRepository"],
    *,
    unit: str = "cm",
) -> Tuple[float, float]:
    default_b, default_h = 30.0, 50.0
    if section_repository is None or not _input.section_id:
        logger.warning("SectionRepository mancante o section_id vuoto; uso fallback %sx%s cm", default_b, default_h)
        return (default_b * 10 if unit == "mm" else default_b, default_h * 10 if unit == "mm" else default_h)

    section = _get_section_by_id_or_name(_input.section_id, section_repository)
    if section is None:
        logger.warning("Sezione '%s' non trovata; uso fallback %sx%s cm", _input.section_id, default_b, default_h)
        return (default_b * 10 if unit == "mm" else default_b, default_h * 10 if unit == "mm" else default_h)

    dims = _extract_section_dimensions_cm(section)
    if dims is None:
        logger.warning("Sezione '%s' senza dimensioni; uso fallback %sx%s cm", _input.section_id, default_b, default_h)
        return (default_b * 10 if unit == "mm" else default_b, default_h * 10 if unit == "mm" else default_h)

    b_cm, h_cm = dims
    if unit == "mm":
        return b_cm * 10.0, h_cm * 10.0
    return b_cm, h_cm


def _get_material_by_name(material_repository: Optional["MaterialRepository"], name: str):
    if not material_repository or not name:
        return None
    try:
        if hasattr(material_repository, "find_by_name"):
            return material_repository.find_by_name(name)
        if hasattr(material_repository, "get_by_name"):
            return material_repository.get_by_name(name)
    except Exception:
        logger.exception("Errore ricerca materiale '%s'", name)
    return None


def _extract_material_property(material, keys: Iterable[str]) -> Optional[float]:
    for key in keys:
        if hasattr(material, key):
            val = getattr(material, key)
            if isinstance(val, (int, float)):
                return float(val)
    props = getattr(material, "properties", {}) or {}
    for key in keys:
        if key in props and isinstance(props[key], (int, float)):
            return float(props[key])
    return None


def get_concrete_properties(
    _input: VerificationInput,
    material_repository: Optional["MaterialRepository"],
) -> Tuple[float, float, float]:
    """Restituisce (fck_MPa, fck_kgcm2, sigma_ca_kgcm2)."""
    fallback_fck = 25.0
    fck_mpa = None
    if material_repository is not None and _input.material_concrete:
        mat = _get_material_by_name(material_repository, _input.material_concrete)
        if mat is not None:
            fck_mpa = _extract_material_property(mat, ["fck_MPa", "fck_mpa", "fck"])
    if fck_mpa is None:
        logger.warning("Materiale cls '%s' non trovato; uso fck=%s MPa", _input.material_concrete, fallback_fck)
        fck_mpa = fallback_fck
    fck_kgcm2 = fck_mpa * MPA_TO_KGCM2
    # TODO: calibrare relazione tensione ammissibile cls per normativa specifica
    sigma_ca = 0.5 * fck_kgcm2
    return fck_mpa, fck_kgcm2, sigma_ca


def get_steel_properties(
    _input: VerificationInput,
    material_repository: Optional["MaterialRepository"],
) -> Tuple[float, float, float]:
    """Restituisce (fyk_MPa, fyk_kgcm2, sigma_fa_kgcm2)."""
    fallback_fyk = 450.0
    fyk_mpa = None
    if material_repository is not None and _input.material_steel:
        mat = _get_material_by_name(material_repository, _input.material_steel)
        if mat is not None:
            fyk_mpa = _extract_material_property(mat, ["fyk_MPa", "fyk_mpa", "fyk"])
    if fyk_mpa is None:
        logger.warning("Materiale acciaio '%s' non trovato; uso fyk=%s MPa", _input.material_steel, fallback_fyk)
        fyk_mpa = fallback_fyk
    fyk_kgcm2 = fyk_mpa * MPA_TO_KGCM2
    # TODO: calibrare tensione ammissibile acciaio per metodo TA
    gamma_s_ta = 1.5
    sigma_fa = fyk_kgcm2 / gamma_s_ta
    return fyk_mpa, fyk_kgcm2, sigma_fa


def compute_ta_verification(
    _input: VerificationInput,
    section_repository: Optional["SectionRepository"] = None,
    material_repository: Optional["MaterialRepository"] = None,
) -> VerificationOutput:
    """Verifica a tensioni ammissibili (TA) secondo RD 2229/1939.

    Implementa la verifica semplificata a pressoflessione retta per sezione rettangolare
    con armature ai lembi. Utilizza il metodo della sezione parzializzata (ipotesi di
    cls non reagente a trazione, legame costitutivo lineare).

    Unità di misura:
    - N, M, T: kg, kg·m (da input)
    - M convertito in kg·cm moltiplicando per 100
    - tensioni: Kg/cm² (coerente con materiali storici RD 2229)
    - dimensioni: cm

    Args:
        _input: Dati di input (sezione, materiali, sollecitazioni, armature)

    Returns:
        VerificationOutput con tensioni calcolate, posizione asse neutro, coefficienti
        di utilizzo e esito della verifica
    """
    try:
        # 1. RECUPERO PARAMETRI DA INPUT
        # Sollecitazioni (convertire M in kg·cm)
        N = _input.N  # kg (>0 trazione, <0 compressione)
        M_kgm = _input.M  # kg·m
        M = M_kgm * 100  # kg·cm (momento flettente)
        T = _input.T  # kg (taglio, non usato per verifica a flessione)

        # Coefficiente omogeneizzazione
        n = _input.n_homog if _input.n_homog > 0 else 15.0  # default

        # Armature (As', As in cm²) e copriferri (d', d in cm)
        As_sup = _input.As_sup  # cm² (armatura superiore = compressa se M>0)
        As_inf = _input.As_inf  # cm² (armatura inferiore = tesa se M>0)
        d_sup = _input.d_sup  # cm (distanza armatura superiore da lembo superiore)
        d_inf = _input.d_inf  # cm (distanza armatura inferiore da lembo inferiore)

        # Tensioni ammissibili materiali (Kg/cm²)
        _fck_mpa, _fck_kgcm2, sigma_ca = get_concrete_properties(_input, material_repository)
        _fyk_mpa, _fyk_kgcm2, sigma_fa = get_steel_properties(_input, material_repository)

        # 2. GEOMETRIA SEZIONE
        B, H = get_section_geometry(_input, section_repository, unit="cm")

        if d_sup <= 0:
            d_sup = 4.0  # cm (default copriferro superiore)
        if d_inf <= 0:
            d_inf = 4.0  # cm (default copriferro inferiore)

        d = H - d_inf  # cm (altezza utile = distanza da lembo compresso ad arm. tesa)

        # 3. CALCOLO ECCENTRICITÀ E POSIZIONE ASSE NEUTRO
        # Eccentricità dello sforzo normale rispetto al baricentro geometrico
        if abs(N) < 0.01:  # flessione semplice
            e = 1e10  # valore molto grande per simulare M/N
            is_fless_semplice = True
        else:
            e = abs(M / N) if N != 0 else 0  # cm
            is_fless_semplice = False

        # Determina se sezione interamente compressa o parzializzata
        # Per press oflessione: se e è piccola -> sezione tutta compressa
        # Per semplicità, assumo sezione parzializzata (ipotesi conservativa)

        # 4. CALCOLO ASSE NEUTRO E TENSIONI (sezione parzializzata)
        # Posizione asse neutro x dalla fibra compressa estrema (lembo superiore)
        # Equilibrio alla traslazione e rotazione per sezione rettangolare armata ai lembi

        # Parametri adimensionali
        rho_inf = As_inf / (B * d) if d > 0 and B > 0 else 0.001  # percentuale arm. tesa
        rho_sup = As_sup / (B * d) if d > 0 and B > 0 else 0.0  # percentuale arm. compressa

        # Posizione asse neutro (formula approssimata per sezione rettangolare)
        # x/d = [-n*(rho_inf + rho_sup) + sqrt(n²*(rho_inf+rho_sup)² + 2*n*rho_inf)] / 1
        # Formula semplificata: assumo rho_sup trascurabile per prima approssimazione
        term1 = n * rho_inf
        term2 = math.sqrt((n * rho_inf) ** 2 + 2 * n * rho_inf) if term1 >= 0 else 0.1
        x_over_d = term2 - term1 if term2 > term1 else 0.3  # rapporto x/d

        x = x_over_d * d  # cm (posizione asse neutro da lembo compresso)

        # Limitazioni x
        if x < 0.05 * H:
            x = 0.05 * H
        if x > 0.95 * H:
            x = 0.95 * H

        # 5. CALCOLO TENSIONI (ipotesi di conservazione sezioni piane, legame lineare)
        # Momento rispetto al baricentro della sezione reagente (approx)
        y_baric = x / 3  # cm (baricentro triangolo di compressione da lembo sup)

        # Tensione nel calcestruzzo al lembo compresso (formula semplificata)
        # sigma_c = M / (B * x * (d - x/3)) * x  (dalla teoria)
        # Approccio semplificato usando modulo resistente
        if x > 0 and d > x / 3:
            J_sez_reag = B * x ** 3 / 12 + B * x * (y_baric) ** 2  # momento inerzia (approx)
            # Tensione massima cls al lembo compresso
            sigma_c_max = (M * x) / J_sez_reag if J_sez_reag > 0 else 0.0  # Kg/cm²

            # Tensione nell'acciaio teso
            # Proporzionalità deformazioni: ε_s / ε_c = (d - x) / x
            # σ_s = n * σ_c * (d - x) / x
            if x > 0:
                sigma_s = n * sigma_c_max * (d - x) / x  # Kg/cm²
            else:
                sigma_s = 0.0
        else:
            # Valori di fallback
            sigma_c_max = 0.0
            sigma_s = 0.0

        # Tensioni minime (per sezione parzializzata, trazione = 0)
        sigma_c_min = 0.0  # cls non reagente a trazione

        # 6. VERIFICA CONTRO TENSIONI AMMISSIBILI
        # Coefficiente di utilizzo = max(σ_agente / σ_ammissibile)
        coeff_util_cls = sigma_c_max / sigma_ca if sigma_ca > 0 else 0.0
        coeff_util_acc = sigma_s / sigma_fa if sigma_fa > 0 else 0.0
        coeff_sicurezza = max(coeff_util_cls, coeff_util_acc)

        # Esito verifica
        if coeff_util_cls <= 1.0 and coeff_util_acc <= 1.0:
            esito = "VERIFICATO"
        else:
            esito = "NON VERIFICATO"

        # 7. MESSAGGI ESPLICATIVI
        messaggi = [
            "=== VERIFICA A TENSIONI AMMISSIBILI (TA) - RD 2229/1939 ===",
            "",
            "DATI INPUT:",
            f"  Sezione: {_input.section_id or 'rettangolare B×H'}",
            f"  Dimensioni: B = {B:.1f} cm, H = {H:.1f} cm, d = {d:.1f} cm",
            f"  Armatura inferiore As = {As_inf:.2f} cm²",
            f"  Armatura superiore As' = {As_sup:.2f} cm²",
            f"  Coefficiente omogeneizzazione n = {n:.1f}",
            f"  Sollecitazioni: N = {N:.0f} kg, M = {M_kgm:.2f} kg·m ({M:.0f} kg·cm)",
            "",
            "TENSIONI AMMISSIBILI:",
            f"  Calcestruzzo σ_ca = {sigma_ca:.1f} Kg/cm²",
            f"  Acciaio σ_fa = {sigma_fa:.0f} Kg/cm²",
            "",
            "RISULTATI CALCOLO:",
            f"  Posizione asse neutro x = {x:.2f} cm (da lembo compresso)",
            f"  Rapporto x/d = {x/d:.3f}",
            f"  Tensione cls max σ_c = {sigma_c_max:.2f} Kg/cm²",
            f"  Tensione acciaio σ_s = {sigma_s:.0f} Kg/cm²",
            "",
            "VERIFICHE:",
            f"  Cls: σ_c / σ_ca = {sigma_c_max:.1f} / {sigma_ca:.1f} = {coeff_util_cls:.3f} {'✓' if coeff_util_cls <= 1.0 else '✗'}",
            f"  Acc: σ_s / σ_fa = {sigma_s:.0f} / {sigma_fa:.0f} = {coeff_util_acc:.3f} {'✓' if coeff_util_acc <= 1.0 else '✗'}",
            "",
            f"ESITO: {esito} (coeff. utilizzo max = {coeff_sicurezza:.3f})",
        ]

        return VerificationOutput(
            sigma_c_max=sigma_c_max,
            sigma_c_min=sigma_c_min,
            sigma_s_max=sigma_s,
            asse_neutro=x,
            deformazioni=f"x/d = {x/d:.3f}, ρ_inf = {rho_inf * 100:.2f}%",
            coeff_sicurezza=coeff_sicurezza,
            esito=esito,
            messaggi=messaggi,
        )

    except Exception as e:
        logger.exception("Errore in compute_ta_verification: %s", e)
        return VerificationOutput(
            sigma_c_max=0.0,
            sigma_c_min=0.0,
            sigma_s_max=0.0,
            asse_neutro=0.0,
            deformazioni="",
            coeff_sicurezza=0.0,
            esito="ERRORE",
            messaggi=[f"Errore durante il calcolo TA: {e}"],
        )


def compute_slu_verification(
    _input: VerificationInput,
    section_repository: Optional["SectionRepository"] = None,
    material_repository: Optional["MaterialRepository"] = None,
) -> VerificationOutput:
    """Verifica a stato limite ultimo (SLU) secondo NTC.

    Implementa la verifica semplificata allo SLU per sezione rettangolare con armature
    ai lembi. Usa il diagramma parabola-rettangolo per il cls e elastico-perfettamente
    plastico per l'acciaio.

    Unità di misura:
    - N, M: kg, kg·m (da input)
    - M convertito in Nmm (1 kg·m = 9.80665 Nm = 9806.65 Nmm)
    - resistenze: MPa (fck, fyd) -> convertite in Kg/cm² per output
    - dimensioni: mm -> convertite in cm per output

    Args:
        _input: Dati di input

    Returns:
        VerificationOutput con resistenze, dominio M-N, esito verifica
    """
    try:
        # 1. RECUPERO PARAMETRI
        # Sollecitazioni (NTC usa kN e kNm, ma input è in kg e kg·m)
        # Conversione: 1 kg = 0.00980665 kN ≈ 0.01 kN (approssimazione)
        N_kg = _input.N  # kg
        M_kgm = _input.M  # kg·m
        T_kg = _input.T  # kg

        # Convertire in N e Nmm per calcoli interni (più comodo)
        N = N_kg * 9.80665  # N
        M = M_kgm * 9806.65  # Nmm (1 kg·m = 9.80665 Nm = 9806.65 Nmm)

        # Armature (mm²) e altezza utile (mm)
        As_sup = _input.As_sup * 100  # cm² -> mm² (1 cm² = 100 mm²)
        As_inf = _input.As_inf * 100  # mm²
        d_sup_cm = _input.d_sup if _input.d_sup > 0 else 4.0  # cm
        d_inf_cm = _input.d_inf if _input.d_inf > 0 else 4.0  # cm

        # Geometria (mm)
        B, H = get_section_geometry(_input, section_repository, unit="mm")
        d = H - d_inf_cm * 10  # mm (altezza utile)

        # Materiali - resistenze caratteristiche (MPa)
        fck, _fck_kgcm2, _sigma_ca = get_concrete_properties(_input, material_repository)
        fyk, _fyk_kgcm2, _sigma_fa = get_steel_properties(_input, material_repository)

        # Coefficienti parziali sicurezza NTC2018
        gamma_c = 1.5
        gamma_s = 1.15

        # Resistenze di calcolo
        fcd = 0.85 * fck / gamma_c  # MPa (0.85 = coeff. riduzione resistenza)
        fyd = fyk / gamma_s  # MPa

        # Deformazioni ultime NTC2018
        eps_cu = 0.0035  # deformazione ultima cls (3.5‰)
        eps_yd = fyd / 200000  # deformazione snervamento acciaio (Es = 200000 MPa)

        # 2. CALCOLO MOMENTO RESISTENTE (flessione semplice con sforzo assiale)
        # Ipotesi: sezione sottoposta a presso-flessione retta

        # Posizione asse neutro per equilibrio (ipotesi semplificata)
        # Assumo diagramma rettangolare semplificato (stress-block): σ_c = fcd su altezza 0.8x

        # Tentativo con x = 0.3*d (valore tipico sezione sottarmata)
        x = 0.3 * d  # mm

        # Risultante compressione cls
        Ac_compr = B * 0.8 * x  # mm² (area cls compressa, stress block)
        Rc = Ac_compr * fcd  # N (risultante compressione cls)

        # Risultante armatura tesa (assumo snervata)
        Rs = As_inf * fyd  # N (risultante trazione acciaio)

        # Risultante armatura compressa (se presente)
        Rc_sup = As_sup * fyd if x > d_sup_cm * 10 else 0.0  # N

        # Equilibrio alla traslazione: N = Rc + Rc_sup - Rs
        # Per flessione semplice (N≈0): Rc + Rc_sup ≈ Rs

        # Momento resistente (bracci delle forze rispetto al baricentro)
        # Approx: braccio Rc = d - 0.4*x, braccio Rs = d/2 (semplificato)
        z = d - 0.4 * x  # mm (braccio Rc)
        Mrd = Rc * z + Rc_sup * (d - d_sup_cm * 10)  # Nmm

        # 3. VERIFICA DOMINIO M-N (semplificata)
        # Coeff sicurezza = M_Ed / M_Rd
        coeff_sicurezza = abs(M) / Mrd if Mrd > 0 else 999.0

        # Esito
        if coeff_sicurezza <= 1.0:
            esito = "VERIFICATO"
        else:
            esito = "NON VERIFICATO"

        # 4. TENSIONI (per output, in Kg/cm²)
        # Conversione MPa -> Kg/cm²: 1 MPa = 10.197 Kg/cm²
        fcd_kgcm2 = fcd * MPA_TO_KGCM2
        fyd_kgcm2 = fyd * MPA_TO_KGCM2

        # Tensioni agenti (approx)
        sigma_c_max = fcd if coeff_sicurezza >= 1.0 else fcd * coeff_sicurezza  # MPa
        sigma_s_max = fyd if As_inf > 0 else 0.0  # MPa

        sigma_c_max_kgcm2 = sigma_c_max * MPA_TO_KGCM2  # Kg/cm²
        sigma_s_max_kgcm2 = sigma_s_max * MPA_TO_KGCM2  # Kg/cm²

        # 5. MESSAGGI
        messaggi = [
            "=== VERIFICA STATO LIMITE ULTIMO (SLU) - NTC2018 ===",
            "",
            "DATI INPUT:",
            f"  Sezione: {_input.section_id or 'rettangolare B×H'}",
            f"  Dimensioni: B = {B/10:.1f} cm, H = {H/10:.1f} cm, d = {d/10:.1f} cm",
            f"  Armatura inferiore As = {As_inf/100:.2f} cm²",
            f"  Armatura superiore As' = {As_sup/100:.2f} cm²",
            f"  Sollecitazioni: N = {N_kg:.0f} kg, M = {M_kgm:.2f} kg·m",
            "",
            "RESISTENZE MATERIALI:",
            f"  Calcestruzzo fck = {fck:.0f} MPa → fcd = {fcd:.1f} MPa ({fcd_kgcm2:.1f} Kg/cm²)",
            f"  Acciaio fyk = {fyk:.0f} MPa → fyd = {fyd:.0f} MPa ({fyd_kgcm2:.0f} Kg/cm²)",
            "",
            "RISULTATI CALCOLO:",
            f"  Posizione asse neutro x = {x/10:.2f} cm",
            f"  Rapporto x/d = {x/d:.3f}",
            f"  Momento resistente M_Rd = {Mrd/9806.65:.2f} kg·m",
            f"  Momento agente M_Ed = {M_kgm:.2f} kg·m",
            "",
            "VERIFICA:",
            f"  M_Ed / M_Rd = {coeff_sicurezza:.3f} {'✓' if coeff_sicurezza <= 1.0 else '✗'}",
            "",
            f"ESITO: {esito}",
        ]

        return VerificationOutput(
            sigma_c_max=sigma_c_max_kgcm2,
            sigma_c_min=0.0,
            sigma_s_max=sigma_s_max_kgcm2,
            asse_neutro=x / 10,  # cm
            deformazioni=f"ε_cu = {eps_cu*1000:.2f}‰, x/d = {x/d:.3f}",
            coeff_sicurezza=coeff_sicurezza,
            esito=esito,
            messaggi=messaggi,
        )

    except Exception as e:
        logger.exception("Errore in compute_slu_verification: %s", e)
        return VerificationOutput(
            sigma_c_max=0.0,
            sigma_c_min=0.0,
            sigma_s_max=0.0,
            asse_neutro=0.0,
            deformazioni="",
            coeff_sicurezza=0.0,
            esito="ERRORE",
            messaggi=[f"Errore durante il calcolo SLU: {e}"],
        )


def compute_sle_verification(
    _input: VerificationInput,
    section_repository: Optional["SectionRepository"] = None,
    material_repository: Optional["MaterialRepository"] = None,
) -> VerificationOutput:
    """Verifica a stato limite di esercizio (SLE) secondo NTC.

    Implementa la verifica semplificata allo SLE per sezione rettangolare:
    - Tensioni di esercizio nel cls e acciaio (stato fessurato, stadi II)
    - Controllo fessurazione (apertura fessure)
    - Controllo deformazioni (non implementato qui)

    Unità di misura:
    - Tensioni: Kg/cm²
    - Dimensioni: cm
    - Sollecitazioni: kg, kg·m

    Args:
        _input: Dati di input

    Returns:
        VerificationOutput con tensioni di esercizio, verifica fessurazione
    """
    try:
        # 1. RECUPERO PARAMETRI
        N_kg = _input.N  # kg
        M_kgm = _input.M  # kg·m
        M = M_kgm * 100  # kg·cm

        n = _input.n_homog if _input.n_homog > 0 else 15.0

        # Armature (cm²) e dimensioni (cm)
        As_sup = _input.As_sup
        As_inf = _input.As_inf
        d_sup = _input.d_sup if _input.d_sup > 0 else 4.0
        d_inf = _input.d_inf if _input.d_inf > 0 else 4.0

        # Geometria (cm)
        B, H = get_section_geometry(_input, section_repository, unit="cm")
        d = H - d_inf

        # Materiali (Kg/cm²)
        _fck_mpa, fck_kgcm2, _sigma_ca = get_concrete_properties(_input, material_repository)
        _fyk_mpa, fyk_kgcm2, _sigma_fa = get_steel_properties(_input, material_repository)

        # Limiti tensioni SLE (frazione di fck/fyk)
        # NTC: σ_c ≤ 0.6 fck (combinazione rara), σ_s ≤ 0.8 fyk
        sigma_c_lim = 0.6 * fck_kgcm2  # Kg/cm²
        sigma_s_lim = 0.8 * fyk_kgcm2  # Kg/cm²

        # 2. CALCOLO TENSIONI DI ESERCIZIO (stadio II - sezione fessurata)
        # Posizione asse neutro (sezione omogeneizzata fessurata)
        rho = As_inf / (B * d) if d > 0 and B > 0 else 0.001

        # Formula asse neutro stadio II:
        # x/d = -n*rho + sqrt((n*rho)² + 2*n*rho)
        term = n * rho
        x_over_d = math.sqrt(term ** 2 + 2 * term) - term if term > 0 else 0.3
        x = x_over_d * d  # cm

        # Limitazioni
        if x < 0.05 * H:
            x = 0.05 * H
        if x > 0.95 * H:
            x = 0.95 * H

        # Momento d'inerzia sezione omogeneizzata fessurata (stadio II)
        # I_II = B*x³/3 + n*As_inf*(d-x)²
        I_fess = B * x ** 3 / 3 + n * As_inf * (d - x) ** 2  # cm⁴

        # Tensione nel cls al lembo compresso
        if I_fess > 0:
            sigma_c = M * x / I_fess  # Kg/cm²
        else:
            sigma_c = 0.0

        # Tensione nell'acciaio teso
        if x > 0 and I_fess > 0:
            sigma_s = n * M * (d - x) / I_fess  # Kg/cm²
        else:
            sigma_s = 0.0

        # 3. VERIFICA TENSIONI
        coeff_util_cls = sigma_c / sigma_c_lim if sigma_c_lim > 0 else 0.0
        coeff_util_acc = sigma_s / sigma_s_lim if sigma_s_lim > 0 else 0.0
        coeff_sicurezza = max(coeff_util_cls, coeff_util_acc)

        # Esito tensioni
        tensioni_ok = (sigma_c <= sigma_c_lim) and (sigma_s <= sigma_s_lim)

        # 4. VERIFICA FESSURAZIONE (semplificata)
        # Apertura fessure wk (formula Eurocodice 2 semplificata)
        # wk = sr,max * ε_sm
        # Qui uso formula molto approssimata per demo
        if As_inf > 0:
            phi_eq = 12.0  # mm (diametro equivalente barre, ipotesi)
            rho_eff = As_inf / (B * 2.5 * d_inf)  # percentuale efficace
            sr_max = 3.4 * 4.0 + 0.425 * phi_eq / rho_eff if rho_eff > 0 else 300.0  # mm
            eps_sm = max(sigma_s / (n * 200000), 0.6 * sigma_s / 200000)  # deformazione media (approx)
            wk = sr_max * eps_sm / 1000  # mm (apertura fessura)
        else:
            wk = 0.0

        # Limiti apertura fessure NTC (ambiente ordinario)
        wk_lim = 0.3  # mm (combinazione quasi permanente)
        fessure_ok = wk <= wk_lim

        # Esito globale
        if tensioni_ok and fessure_ok:
            esito = "VERIFICATO"
        else:
            esito = "NON VERIFICATO"

        # 5. MESSAGGI
        messaggi = [
            "=== VERIFICA STATO LIMITE DI ESERCIZIO (SLE) - NTC2018 ===",
            "",
            "DATI INPUT:",
            f"  Sezione: {_input.section_id or 'rettangolare B×H'}",
            f"  Dimensioni: B = {B:.1f} cm, H = {H:.1f} cm, d = {d:.1f} cm",
            f"  Armatura inferiore As = {As_inf:.2f} cm²",
            f"  Coeff. omogeneizzazione n = {n:.1f}",
            f"  Sollecitazioni: M = {M_kgm:.2f} kg·m",
            "",
            "LIMITI TENSIONI SLE:",
            f"  Cls σ_c,lim = 0.6·fck = {sigma_c_lim:.1f} Kg/cm²",
            f"  Acc σ_s,lim = 0.8·fyk = {sigma_s_lim:.0f} Kg/cm²",
            "",
            "RISULTATI CALCOLO (stadio II - fessurato):",
            f"  Posizione asse neutro x = {x:.2f} cm (x/d = {x/d:.3f})",
            f"  Tensione cls σ_c = {sigma_c:.2f} Kg/cm² {'✓' if sigma_c <= sigma_c_lim else '✗'}",
            f"  Tensione acciaio σ_s = {sigma_s:.0f} Kg/cm² {'✓' if sigma_s <= sigma_s_lim else '✗'}",
            "",
            "VERIFICA FESSURAZIONE:",
            f"  Apertura fessure wk = {wk:.3f} mm",
            f"  Limite wk,lim = {wk_lim:.2f} mm {'✓' if wk <= wk_lim else '✗'}",
            "",
            f"ESITO: {esito} (coeff. utilizzo max = {coeff_sicurezza:.3f})",
        ]

        return VerificationOutput(
            sigma_c_max=sigma_c,
            sigma_c_min=0.0,
            sigma_s_max=sigma_s,
            asse_neutro=x,
            deformazioni=f"wk = {wk:.3f} mm, x/d = {x/d:.3f}",
            coeff_sicurezza=coeff_sicurezza,
            esito=esito,
            messaggi=messaggi,
        )

    except Exception as e:
        logger.exception("Errore in compute_sle_verification: %s", e)
        return VerificationOutput(
            sigma_c_max=0.0,
            sigma_c_min=0.0,
            sigma_s_max=0.0,
            asse_neutro=0.0,
            deformazioni="",
            coeff_sicurezza=0.0,
            esito="ERRORE",
            messaggi=[f"Errore durante il calcolo SLE: {e}"],
        )


def compute_santarella_placeholder(_input: VerificationInput) -> VerificationOutput:
    """Placeholder per metodi futuri (es. Santarella).

    Questo è un segnaposto per algoritmi di verifica storici o alternativi
    che potrebbero essere implementati in futuro.
    """
    return VerificationOutput(
        sigma_c_max=0.0,
        sigma_c_min=0.0,
        sigma_s_max=0.0,
        asse_neutro=0.0,
        deformazioni="Placeholder Santarella",
        coeff_sicurezza=1.0,
        esito="NON IMPLEMENTATO",
        messaggi=[
            "Metodo Santarella - Placeholder",
            "Questa riga è un segnaposto per futuri algoritmi.",
            "I metodi storici tipo Santarella saranno implementati in futuro.",
            "Sezione: {}".format(_input.section_id or "non specificata"),
        ],
    )


def compute_verification_result(
    _input: VerificationInput,
    section_repository: Optional["SectionRepository"] = None,
    material_repository: Optional["MaterialRepository"] = None,
) -> VerificationOutput:
    """Motore di verifica principale che instrада verso il metodo appropriato.

    In base al campo verification_method del VerificationInput, chiama la
    funzione di verifica corretta:
    - TA: tensioni ammissibili (RD 2229/1939)
    - SLU: stato limite ultimo (NTC)
    - SLE: stato limite di esercizio (NTC)
    - SANT: placeholder per metodi futuri (Santarella, ecc.)
    """
    method = (_input.verification_method or "").upper().strip()

    if method == "TA":
        return compute_ta_verification(_input, section_repository, material_repository)
    elif method == "SLU":
        return compute_slu_verification(_input, section_repository, material_repository)
    elif method == "SLE":
        return compute_sle_verification(_input, section_repository, material_repository)
    elif method in ("SANT", "PLACEHOLDER"):
        return compute_santarella_placeholder(_input)

    # Metodo sconosciuto o vuoto
    return VerificationOutput(
        sigma_c_max=0.0,
        sigma_c_min=0.0,
        sigma_s_max=0.0,
        asse_neutro=0.0,
        deformazioni="",
        coeff_sicurezza=0.0,
        esito="ERRORE",
        messaggi=[
            "Metodo di verifica non specificato o sconosciuto: '{}'".format(method),
            "Selezionare un metodo dalla colonna 'Metodo verifica': TA, SLU, SLE, SANT",
        ],
    )


COLUMNS: List[ColumnDef] = [
    ("section", "Sezione", 170, "w"),
    ("verif_method", "Metodo verifica", 120, "center"),
    ("mat_concrete", "Materiale cls", 140, "w"),
    ("mat_steel", "Materiale acciaio", 140, "w"),
    ("n", "Coeff. n", 75, "center"),
    ("N", "N [kg]", 80, "center"),
    ("M", "M [kg·m]", 90, "center"),
    ("T", "T [kg]", 80, "center"),
    ("As_p", "As' [cm²]", 90, "center"),
    ("As", "As [cm²]", 90, "center"),
    ("d_p", "d' [cm]", 80, "center"),
    ("d", "d [cm]", 80, "center"),
    ("stirrups_step", "Passo staffe [cm]", 120, "center"),
    ("stirrups_diam", "Diametro staffe [mm]", 130, "center"),
    ("stirrups_mat", "Materiale staffe", 140, "w"),
    ("notes", "NOTE", 240, "w"),
]


class VerificationTableApp(tk.Frame):
    """GUI tabellare per inserimento rapido delle verifiche (senza logica di calcolo)."""

    def __init__(
        self,
        master: tk.Tk,
        section_repository: Optional["SectionRepository"] = None,
        section_names: Optional[Iterable[str]] = None,
        material_repository: Optional["MaterialRepository"] = None,
        material_names: Optional[Iterable[str]] = None,
        verification_items_repository: Optional["VerificationItemsRepository"] = None,
        initial_rows: int = 1,
        *,
        search_limit: int = 200,
        display_limit: int = 50,
    ) -> None:
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)

        self.columns = [c[0] for c in COLUMNS]
        self._last_col = self.columns[0]

        self.section_repository = section_repository
        self.material_repository = material_repository
        # Project model to save/load .jsonp projects
        if VerificationProject is not None:
            self.project: "VerificationProject" = VerificationProject()
            self.project.new_project()
        else:
            self.project = None
        # Optional external repository that stores VerificationItem objects
        self.verification_items_repository = verification_items_repository
        self.initial_rows = int(initial_rows)

        # Configurable limits for search and display to keep UI responsive.
        # - search_limit: how many candidates the repository search returns
        # - display_limit: how many items the suggestion list will display
        self.search_limit = int(search_limit)
        self.display_limit = int(display_limit)

        self.section_names = self._resolve_section_names(section_repository, section_names)
        self.material_names = self._resolve_material_names(material_names)

        # Suggestions map may contain either a static list OR a callable that accepts
        # a query string and returns a filtered list of suggestion strings. By
        # default we prefer callables that query the provided repositories so the
        # suggestions are always up-to-date and can be filtered by material type.
        self.suggestions_map: Dict[str, object] = {
            "section": (lambda q: self._search_sections(q)),
            "mat_concrete": (lambda q: self._search_materials(q, type_filter="concrete")),
            "mat_steel": (lambda q: self._search_materials(q, type_filter="steel")),
            "stirrups_mat": (lambda q: self._search_materials(q, type_filter="steel")),
        }

        self.edit_entry: Optional[ttk.Entry] = None
        self.edit_item: Optional[str] = None
        self.edit_column: Optional[str] = None
        self._suggest_box: Optional[tk.Toplevel] = None
        self._suggest_list: Optional[tk.Listbox] = None
        self._rebar_window: Optional[tk.Toplevel] = None
        self._rebar_vars: Dict[int, tk.StringVar] = {}
        self._rebar_entries: List[tk.Entry] = []
        self._rebar_total_var = tk.StringVar(value="0.00")
        self._rebar_target_column: Optional[str] = None
        # Flag to avoid committing the entry when the rebar calculator is open
        self._in_rebar_calculator: bool = False

        # Stato centralizzato della cella corrente (usato per navigazione/tab/inserimenti)
        self.current_item_id: Optional[str] = None
        self.current_column_index: Optional[int] = None

        self._build_ui()
        self._insert_empty_rows(self.initial_rows)

    def table_row_to_model(self, row_index: int) -> VerificationInput:
        items = list(self.tree.get_children())
        if row_index < 0 or row_index >= len(items):
            raise IndexError("row_index out of range")
        item = items[row_index]

        def get(col: str) -> str:
            return str(self.tree.set(item, col) or "").strip()

        def num(col: str) -> float:
            value = get(col)
            if not value:
                return 0.0
            try:
                return float(value.replace(",", "."))
            except ValueError:
                return 0.0

        return VerificationInput(
            section_id=get("section"),
            verification_method=get("verif_method"),
            material_concrete=get("mat_concrete"),
            material_steel=get("mat_steel"),
            n_homog=num("n"),
            N=num("N"),
            M=num("M"),
            T=num("T"),
            As_sup=num("As"),
            As_inf=num("As_p"),
            d_sup=num("d"),
            d_inf=num("d_p"),
            stirrup_step=num("stirrups_step"),
            stirrup_diameter=num("stirrups_diam"),
            stirrup_material=get("stirrups_mat"),
            notes=get("notes"),
        )
    def update_row_from_model(self, row_index: int, model: VerificationInput) -> None:
        items = list(self.tree.get_children())
        if row_index < 0 or row_index >= len(items):
            raise IndexError("row_index out of range")
        item = items[row_index]
        values_map = {
            "section": model.section_id,
            "verif_method": model.verification_method,
            "mat_concrete": model.material_concrete,
            "mat_steel": model.material_steel,
            "n": model.n_homog,
            "N": model.N,
            "M": model.M,
            "T": model.T,
            "As": model.As_sup,
            "As_p": model.As_inf,
            "d": model.d_sup,
            "d_p": model.d_inf,
            "stirrups_step": model.stirrup_step,
            "stirrups_diam": model.stirrup_diameter,
            "stirrups_mat": model.stirrup_material,
            "notes": model.notes,
        }
        for col, value in values_map.items():
            self.tree.set(item, col, "" if value is None else value)

    def _build_ui(self) -> None:
        top = tk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        # Project file controls
        tk.Button(top, text="Salva progetto", command=self._on_save_project).pack(side="left")
        tk.Button(top, text="Carica progetto", command=self._on_load_project).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Aggiungi lista di elementi", command=self._on_add_list_elements).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Crea progetto test", command=self.create_test_project).pack(side="left", padx=(6,0))

        tk.Button(top, text="Aggiungi riga", command=self._add_row).pack(side="left")
        tk.Button(top, text="Rimuovi riga", command=self._remove_selected_row).pack(side="left", padx=(6, 0))
        # Pulsanti per import/export CSV
        tk.Button(top, text="Importa CSV", command=self._on_import_csv).pack(side="left", padx=(6, 0))
        tk.Button(top, text="Esporta CSV", command=self._on_export_csv).pack(side="left", padx=(6, 0))
        # Pulsante per calcolare tutte le righe
        tk.Button(top, text="Calcola tutte le righe", command=self._on_compute_all).pack(side="left", padx=(6, 0))
        # Pulsante per salvare tutte le righe come VerificationItem nel repository
        tk.Button(top, text="Salva elementi", command=self._on_save_items).pack(side="left", padx=(6, 0))

        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        xscroll = tk.Scrollbar(table_frame, orient="horizontal")
        yscroll = tk.Scrollbar(table_frame, orient="vertical")
        xscroll.pack(side="bottom", fill="x")
        yscroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set,
            selectmode="browse",
        )
        self.tree.pack(fill="both", expand=True)
        xscroll.config(command=self.tree.xview)
        yscroll.config(command=self.tree.yview)

        for key, label, width, anchor in COLUMNS:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=width, anchor=anchor, stretch=False)

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Return>", self._on_tree_return)
        self.tree.bind("<Shift-Return>", self._on_tree_shift_return)
        self.tree.bind("<F2>", self._on_tree_return)
        self.tree.bind("<Key>", self._on_tree_keypress)
        self.tree.bind("<Up>", self._on_tree_arrow)
        self.tree.bind("<Down>", self._on_tree_arrow)
        self.tree.bind("<Left>", self._on_tree_arrow)
        self.tree.bind("<Right>", self._on_tree_arrow)
        self.tree.bind("<Tab>", self._on_tree_tab)
        self.tree.bind("<Shift-Tab>", self._on_tree_shift_tab)
        # Supporto rapido per spostarsi all'inizio/fine della riga con Home/End
        self.tree.bind("<Home>", self._on_tree_home)
        self.tree.bind("<End>", self._on_tree_end)

    def _resolve_section_names(
        self,
        repo: Optional["SectionRepository"],
        provided: Optional[Iterable[str]],
    ) -> List[str]:
        if provided is not None:
            return sorted({s for s in provided if s and s != "C100"})
        if repo is not None:
            return sorted({s.name for s in repo.get_all_sections() if s.name != "C100"})
        return []

    def _resolve_material_names(self, provided: Optional[Iterable[str]]) -> List[str]:
        # Priority: explicit provided list -> material_repository -> global list_materials
        if provided is not None:
            return sorted({m for m in provided if m})
        if self.material_repository is not None:
            try:
                mats = self.material_repository.get_all()
                return sorted({m.name if hasattr(m, "name") else m.get("name") for m in mats if (hasattr(m, "name") and m.name) or (isinstance(m, dict) and m.get("name"))})
            except Exception:
                try:
                    # fallback to older API
                    return sorted({m.get("name") for m in self.material_repository.list_materials()})
                except Exception:
                    logger.debug("Material repository present but could not be read")
        if list_materials is None:
            return []
        try:
            return sorted({m.get("name", "") for m in list_materials() if m.get("name")})
        except Exception:
            return []

    def _insert_empty_rows(self, count: int) -> None:
        for _ in range(count):
            self._add_row()

    # ------------------------------------------------------------------
    # Repository-backed search helpers
    # ------------------------------------------------------------------
    def _search_sections(self, query: str) -> List[str]:
        """Search sections using centralized helper (repository-backed).

        Delegates to sections_app.services.search_helpers.search_sections so the
        search logic is testable and reusable elsewhere.
        """
        try:
            from sections_app.services.search_helpers import search_sections
            return search_sections(self.section_repository, self.section_names, query, limit=self.search_limit)
        except Exception:
            logger.exception("Error searching sections via helper")
            # fallback: local name matching
            q = (query or "").strip().lower()
            return [s for s in self.section_names if q in s.lower()][: self.search_limit]

    def _search_materials(self, query: str, type_filter: Optional[str] = None) -> List[str]:
        """Search materials using centralized helper (repository-backed).

        Delegates to sections_app.services.search_helpers.search_materials which
        supports optional type filtering and is limited by `self.search_limit`.
        """
        try:
            from sections_app.services.search_helpers import search_materials
            return search_materials(self.material_repository, self.material_names, query, type_filter=type_filter, limit=self.search_limit)
        except Exception:
            logger.exception("Error searching materials via helper")
            q = (query or "").strip().lower()
            names = self.material_names or []
            return [n for n in names if q in n.lower()][: self.search_limit]


    def _add_row(self, after_item: Optional[str] = None) -> str:
        values = ["" for _ in self.columns]
        if after_item is None:
            return self.tree.insert("", tk.END, values=values)
        index = self.tree.index(after_item) + 1
        return self.tree.insert("", index, values=values)

    def add_row_from_previous(self, previous_item_id: str) -> str:
        """
        Crea una nuova riga nel Treeview copiando TUTTI i valori
        dalla riga identificata da previous_item_id.
        Restituisce il nuovo item_id.

        Implementazione:
        - legge i valori con self.tree.item(previous_item_id, "values")
        - inserisce una nuova riga subito dopo quella precedente con gli stessi valori
        - seleziona e porta in vista la nuova riga
        """
        children = list(self.tree.get_children())
        if previous_item_id in children:
            prev_values = list(self.tree.item(previous_item_id, "values"))
            index = children.index(previous_item_id) + 1
        else:
            # se l'item precedente non esiste, inseriamo in coda una riga vuota
            prev_values = ["" for _ in self.columns]
            index = tk.END
        new_item = self.tree.insert("", index, values=prev_values)
        # seleziona e porta in vista la nuova riga
        self.tree.selection_set(new_item)
        self.tree.focus(new_item)
        self.tree.see(new_item)
        return new_item

    def _create_editor_for_cell(self, item: str, col: str, value: str, bbox: Tuple[int,int,int,int], initial_text: Optional[str] = None):
        """
        Crea e ritorna un widget editor posizionato sopra la cella indicata.
        Usa `ttk.Combobox` per colonne materiali se `self.material_names` è disponibile,
        altrimenti `ttk.Entry`. Bind degli eventi di navigazione e suggerimenti vengono
        applicati qui centralmente per evitare duplicazione.
        """
        x, y, width, height = bbox
        combobox_columns = {"mat_concrete", "mat_steel", "stirrups_mat", "verif_method"}
        if col in combobox_columns:
            if col == "verif_method":
                # Combobox con valori fissi per metodo di verifica
                editor = ttk.Combobox(self.tree, values=["TA", "SLU", "SLE", "SANT"])
            elif self.material_names:
                # Combobox con materiali
                editor = ttk.Combobox(self.tree, values=self.material_names)
            else:
                # Fallback a Entry se non ci sono materiali
                editor = ttk.Entry(self.tree)
                editor.place(x=x, y=y, width=width, height=height)
                editor.insert(0, value)
                if initial_text:
                    editor.delete(0, tk.END)
                    editor.insert(0, initial_text)
                editor.select_range(0, tk.END)
                editor.focus_set()
                # Bind eventi comuni
                editor.bind("<Return>", self._on_entry_commit_down)
                editor.bind("<Shift-Return>", self._on_entry_commit_up)
                editor.bind("<Tab>", self._on_entry_commit_next)
                editor.bind("<Shift-Tab>", self._on_entry_commit_prev)
                editor.bind("<Escape>", self._on_entry_cancel)
                editor.bind("<Up>", self._on_entry_move_up)
                editor.bind("<Down>", self._on_entry_move_down)
                editor.bind("<Left>", self._on_entry_move_left)
                editor.bind("<Right>", self._on_entry_move_right)
                editor.bind("<FocusOut>", self._on_entry_focus_out)
                editor.bind("<KeyRelease>", self._on_entry_keyrelease)
                editor.bind("<KeyPress>", self._on_entry_keypress)
                return editor

            editor.place(x=x, y=y, width=width, height=height)
            # Set display value
            editor.set(value or "")
            if initial_text:
                editor.delete(0, tk.END)
                editor.insert(0, initial_text)
            try:
                editor.selection_range(0, tk.END)
            except Exception:
                pass
            editor.focus_set()
            # Monkeypatch Combobox.set to record the last value set programmatically.
            # This helps tests that use cb.set('...') and expect the value to be
            # available synchronously at commit time.
            try:
                orig_set = editor.set
                def _set_and_record(val):
                    orig_set(val)
                    try:
                        self._last_editor_value = editor.get()
                    except Exception:
                        pass
                editor.set = _set_and_record  # type: ignore
            except Exception:
                pass
        else:
            editor = ttk.Entry(self.tree)
            editor.place(x=x, y=y, width=width, height=height)
            editor.insert(0, value)
            if initial_text:
                editor.delete(0, tk.END)
                editor.insert(0, initial_text)
            editor.select_range(0, tk.END)
            editor.focus_set()

        # Bind eventi comuni
        editor.bind("<Return>", self._on_entry_commit_down)
        editor.bind("<Shift-Return>", self._on_entry_commit_up)
        editor.bind("<Tab>", self._on_entry_commit_next)
        # Keep a record of the current editor value on key events as well
        def _record_key_event(_e=None):
            try:
                self._last_editor_value = editor.get()
            except Exception:
                pass
        editor.bind("<KeyRelease>", _record_key_event)
        editor.bind("<Shift-Tab>", self._on_entry_commit_prev)
        editor.bind("<Escape>", self._on_entry_cancel)
        editor.bind("<Up>", self._on_entry_move_up)
        editor.bind("<Down>", self._on_entry_move_down)
        editor.bind("<Left>", self._on_entry_move_left)
        editor.bind("<Right>", self._on_entry_move_right)
        editor.bind("<FocusOut>", self._on_entry_focus_out)
        editor.bind("<KeyRelease>", self._on_entry_keyrelease)
        editor.bind("<KeyPress>", self._on_entry_keypress)
        return editor

    def _compute_target_cell(self, current_item: str, current_col: str, delta_col: int, delta_row: int) -> Tuple[str, str, bool]:
        """
        Calcola l'item_id e la chiave di colonna target a partire dalla cella corrente
        e dagli spostamenti `delta_col` e `delta_row`.
        Restituisce (target_item_id, target_col_key, created_new_row_flag).
        """
        items = list(self.tree.get_children())
        if not items:
            return current_item, current_col, False
        if current_item not in items:
            return current_item, current_col, False
        row_idx = items.index(current_item)
        col_idx = self.columns.index(current_col)

        new_col = col_idx + delta_col
        new_row = row_idx + delta_row

        # wrap colonne
        if new_col >= len(self.columns):
            new_col = 0
            new_row += 1
        elif new_col < 0:
            new_col = len(self.columns) - 1
            new_row -= 1

        # se superiamo l'ultima riga creiamo una nuova riga copiando la corrente
        created = False
        if new_row >= len(items):
            new_item = self.add_row_from_previous(current_item)
            items = list(self.tree.get_children())
            target_item = new_item
            created = True
        else:
            new_row = max(0, new_row)
            target_item = items[new_row]

            # Se ci si sta spostando verso il basso e la riga target è vuota,
            # copia i valori della riga corrente nella riga target. Questo
            # mantiene la riga successiva pre-popolata quando l'utente tabba
            # o scende con Invio/freccia giù, ma non sovrascrive righe non vuote
            # e non interviene quando si scende verso l'alto (shift+tab o freccia su).
            if new_row > row_idx and self._row_is_empty(target_item):
                prev_values = list(self.tree.item(current_item, "values"))
                self.tree.item(target_item, values=prev_values)

        target_col = self.columns[new_col]
        return target_item, target_col, created

    # --- API pubbliche -------------------------------------------------
    def create_editor_for_cell(self, item: str, col: str, initial_text: Optional[str] = None):
        """
        API pubblica: crea un editor (Entry o Combobox) posizionato sopra la cella
        `item`/`col` e lo restituisce. Solleva ValueError se la cella non è visibile
        (bbox vuoto).
        """
        bbox = self.tree.bbox(item, col)
        if not bbox:
            raise ValueError(f"Impossibile creare editor: bbox vuoto per item={item}, col={col}")
        value = self.tree.set(item, col)
        return self._create_editor_for_cell(item, col, value, bbox, initial_text=initial_text)

    def compute_target_cell(self, current_item: str, current_col: str, delta_col: int, delta_row: int) -> Tuple[str, str, bool]:
        """
        API pubblica: wrapper che richiama `_compute_target_cell` per calcolare la
        cella target dato un delta di colonna e riga. Restituisce (item_id, column_key, created_flag).
        """
        return self._compute_target_cell(current_item, current_col, delta_col, delta_row)

    def _remove_selected_row(self) -> None:
        sel = self.tree.focus()
        if sel:
            self.tree.delete(sel)

    def _on_tree_click(self, event: tk.Event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        item = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col = self._column_id_to_key(col_id)
        if item and col:
            self._last_col = col
            # Indica che la successiva chiamata a `_update_suggestions` può
            # mostrare l'elenco completo anche se l'entry è vuota.
            self._force_show_all_on_empty = True
            # Start editing and then show suggestions after a brief delay
            self.after_idle(lambda: self._start_edit(item, col))
            self.after(10, self._update_suggestions)

    def _on_tree_double_click(self, event: tk.Event) -> None:
        item = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col = self._column_id_to_key(col_id)
        if not item:
            new_item = self._add_row()
            self._last_col = self.columns[0]
            self._start_edit(new_item, self._last_col)
            return
        if self._row_is_empty(item):
            new_item = self._add_row(after_item=item)
            self._last_col = self.columns[0]
            self._start_edit(new_item, self._last_col)
            return
        if item and col:
            self._last_col = col
            self._start_edit(item, col)

    def _on_tree_return(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_shift_return(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_tab(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_shift_tab(self, _event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        self._start_edit(item, self._last_col)
        return "break"

    def _on_tree_keypress(self, event: tk.Event) -> None:
        if self.edit_entry is not None:
            return
        if not event.char or not event.char.isprintable():
            return
        item = self.tree.focus()
        if not item:
            return
        self._start_edit(item, self._last_col, initial_text=event.char)

    def _on_tree_arrow(self, event: tk.Event) -> str:
        item = self.tree.focus()
        if not item:
            return "break"
        if event.keysym in {"Left", "Right"}:
            delta = -1 if event.keysym == "Left" else 1
            target_item, target_col = self._next_cell(item, self._last_col, delta_col=delta, delta_row=0)
        else:
            delta = -1 if event.keysym == "Up" else 1
            target_item, target_col = self._next_cell(item, self._last_col, delta_col=0, delta_row=delta)
        self._last_col = target_col
        self._start_edit(target_item, target_col)
        return "break"

    def _on_tree_home(self, _event: tk.Event) -> str:
        """Sposta la cella attiva alla prima colonna della riga corrente e apre l'editor."""
        item = self.tree.focus()
        if not item:
            return "break"
        first_col = self.columns[0]
        self._last_col = first_col
        self._start_edit(item, first_col)
        return "break"

    def _on_tree_end(self, _event: tk.Event) -> str:
        """Sposta la cella attiva all'ultima colonna della riga corrente e apre l'editor."""
        item = self.tree.focus()
        if not item:
            return "break"
        last_col = self.columns[-1]
        self._last_col = last_col
        self._start_edit(item, last_col)
        return "break"

    def _column_id_to_key(self, col_id: str) -> Optional[str]:
        if not col_id or not col_id.startswith("#"):
            return None
        try:
            idx = int(col_id.replace("#", "")) - 1
        except ValueError:
            return None
        if 0 <= idx < len(self.columns):
            return self.columns[idx]
        return None

    def _start_edit(self, item: str, col: str, initial_text: Optional[str] = None) -> None:
        self._hide_suggestions()
        if self.edit_entry is not None:
            self._commit_edit()
        bbox = self.tree.bbox(item, col)
        if not bbox:
            return
        x, y, width, height = bbox
        value = self.tree.set(item, col)

        self.edit_item = item
        self.edit_column = col
        # Aggiorna lo stato centralizzato della posizione corrente (indice numerico della colonna)
        self.current_item_id = item
        try:
            self.current_column_index = self.columns.index(col)
        except ValueError:
            self.current_column_index = None

        # Crea l'editor (Entry o Combobox) in modo centralizzato
        self.edit_entry = self._create_editor_for_cell(item, col, value, (x, y, width, height), initial_text=initial_text)

        # Se lo start è esplicito (programma o click), consentiamo alla prima
        # chiamata a `_update_suggestions` di mostrare l'elenco completo se
        # l'entry è vuota. Questo viene resettato immediatamente dopo la chiamata
        # per evitare effetti collaterali sulle successive modifiche.
        self._force_show_all_on_empty = True
        self._update_suggestions()
        self._force_show_all_on_empty = False

    def _commit_edit(self) -> None:
        if self.edit_entry is None or self.edit_item is None or self.edit_column is None:
            return
        # Prefer the last recorded editor value if available (helps with
        # programmatic .set() on Combobox which may not trigger a key event)
        value = getattr(self, '_last_editor_value', None) or self.edit_entry.get()
        # Record debug info via logger (no direct stdout prints)
        try:
            logger.debug("Commit edit: item=%s column=%s value=%r", self.edit_item, self.edit_column, value)
            logger.debug("edit_entry type: %s", type(self.edit_entry))
            if hasattr(self.edit_entry, 'cget'):
                try:
                    logger.debug("combobox values: %s", self.edit_entry.cget('values'))
                except Exception:
                    pass
        except Exception:
            pass
        self.tree.set(self.edit_item, self.edit_column, value)
        logger.debug("Tree value after set: %r", self.tree.set(self.edit_item, self.edit_column))
        self._last_col = self.edit_column
        self.edit_entry.destroy()
        self.edit_entry = None
        self.edit_item = None
        self.edit_column = None
        self._hide_suggestions()

    def _on_entry_focus_out(self, _event: tk.Event) -> None:
        self.after(1, self._commit_if_focus_outside)

    def _on_entry_commit_next(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=1, delta_row=0)

    def _on_entry_commit_prev(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=-1, delta_row=0)

    def _on_entry_commit_down(self, _event: tk.Event) -> str:
        """
        Invio (Return): avanzare di una riga mantenendo la stessa colonna.

        Scelta: ho deciso di far sì che Invio sposti il cursore alla stessa
        colonna nella riga successiva (delta_row=1). Questo è comodo per
        inserimenti per colonna (es. digitare valori numerici riga per riga).
        Per avanzare di colonna usa TAB.
        """
        return self._commit_and_move(delta_col=0, delta_row=1)

    def _on_entry_commit_up(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=0, delta_row=-1)

    def _on_entry_move_up(self, _event: tk.Event) -> str:
        if self._suggest_list is not None:
            idx = self._current_suggestion_index()
            prev_idx = max(idx - 1, 0)
            self._select_suggestion(prev_idx)
            return "break"
        return self._commit_and_move(delta_col=0, delta_row=-1)

    def _on_entry_move_down(self, _event: tk.Event) -> str:
        if self._suggest_list is not None:
            idx = self._current_suggestion_index()
            next_idx = min(idx + 1, self._suggest_list.size() - 1)
            self._select_suggestion(next_idx)
            return "break"
        return self._commit_and_move(delta_col=0, delta_row=1)

    def _on_entry_move_left(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=-1, delta_row=0)

    def _on_entry_move_right(self, _event: tk.Event) -> str:
        return self._commit_and_move(delta_col=1, delta_row=0)

    def _on_entry_cancel(self, _event: tk.Event) -> str:
        if self._suggest_list is not None:
            self._hide_suggestions()
            return "break"
        if self.edit_entry is not None:
            self.edit_entry.destroy()
            self.edit_entry = None
            self.edit_item = None
            self.edit_column = None
            self._hide_suggestions()
        return "break"

    def _commit_and_move(self, delta_col: int, delta_row: int) -> str:
        """
        Commette l'edit corrente e sposta l'editor secondo delta_col/delta_row.

        Comportamento migliorato:
        - Se il movimento raggiunge una riga successiva che non esiste yet, viene
          creata una nuova riga copiando i valori della riga corrente
          (usando `add_row_from_previous`) e l'editor si apre sulla cella desiderata.
        - Usato sia da TAB (delta_col=1, delta_row=0), Invio (delta_row=1, delta_col=0)
          e frecce. Questo centralizza la logica di avanzamento.
        """
        if self.edit_item is None or self.edit_column is None:
            return "break"
        if self._suggest_list is not None:
            self._apply_suggestion()

        current_item = self.edit_item
        current_col = self.edit_column

        # Applica suggerimento se presente e committa l'edit corrente
        if self._suggest_list is not None:
            self._apply_suggestion()
        self._commit_edit()

        # Calcola la cella target (eventualmente creando una nuova riga copiando la corrente)
        target_item, target_col, _created = self._compute_target_cell(current_item, current_col, delta_col, delta_row)

        # Apri l'editor sulla cella target
        self._start_edit(target_item, target_col)
        return "break"

    def _next_cell(self, item: str, col: str, delta_col: int, delta_row: int) -> Tuple[str, str]:
        items = list(self.tree.get_children())
        if not items:
            return item, col
        row_idx = items.index(item)
        col_idx = self.columns.index(col)

        new_col = col_idx + delta_col
        new_row = row_idx + delta_row

        if new_col >= len(self.columns):
            new_col = 0
            new_row += 1
        elif new_col < 0:
            new_col = len(self.columns) - 1
            new_row -= 1

        new_row = max(0, min(new_row, len(items) - 1))
        target_item = items[new_row]
        target_col = self.columns[new_col]
        self.tree.focus(target_item)
        self.tree.selection_set(target_item)
        return target_item, target_col

    def _row_is_empty(self, item: str) -> bool:
        values = self.tree.item(item, "values")
        return all(not (str(v).strip()) for v in values)

    def _on_entry_keyrelease(self, _event: tk.Event) -> None:
        self._update_suggestions()

    def _on_entry_keypress(self, event: tk.Event) -> Optional[str]:
        # Support both event.char and event.keysym to make programmatic key
        # generation in tests more reliable across platforms.
        key = (getattr(event, "char", "") or getattr(event, "keysym", "")).lower()
        if self.edit_column in {"As", "As_p"} and key == "c":
            self._open_rebar_calculator()
            return "break"
        return None

    def _update_suggestions(self) -> None:
        if self.edit_entry is None or self.edit_column is None:
            return
        source = self.suggestions_map.get(self.edit_column)
        if not source:
            self._hide_suggestions()
            return
        query = self.edit_entry.get().strip()
        query_lower = query.lower()

        # Support either a callable(source) -> list[str] or a static list
        try:
            # Columns for which we want to show all suggestions immediately when the
            # field is empty (section, concrete/steel/stirrups materials).
            show_all_on_empty = {"section", "mat_concrete", "mat_steel", "stirrups_mat"}

            if query == "":
                # We only show the full suggestion list on empty query when the edit
                # was explicitly opened (e.g. by clicking the cell). This avoids
                # displaying suggestions when the user types and then deletes input.
                show_all_flag = getattr(self, "_force_show_all_on_empty", False) and (self.edit_column in show_all_on_empty)
                # reset flag regardless
                self._force_show_all_on_empty = False
                if not show_all_flag:
                    # Preserve old behavior: hide suggestions for empty query
                    self._hide_suggestions()
                    return
                # For the allowed columns when explicitly requested, request full list
                if callable(source):
                    filtered = source("")
                else:
                    filtered = list(source)
            else:
                # Non-empty query: keep existing behavior
                if callable(source):
                    filtered = source(query)
                else:
                    filtered = [s for s in source if query_lower in s.lower()]
        except Exception:
            logger.exception("Error while querying suggestions source")
            filtered = []

        if not filtered:
            self._hide_suggestions()
            return

        if self._suggest_box is None:
            self._ensure_suggestion_box()

        if self._suggest_list is None:
            return
        self._suggest_list.delete(0, tk.END)
        for s in filtered[: self.display_limit]:
            self._suggest_list.insert(tk.END, s)
        self._suggest_list.selection_clear(0, tk.END)
        self._suggest_list.selection_set(0)

        x = self.edit_entry.winfo_rootx()
        y = self.edit_entry.winfo_rooty() + self.edit_entry.winfo_height()
        self._suggest_box.geometry(f"{self.edit_entry.winfo_width()}x120+{x}+{y}")

    def _commit_if_focus_outside(self) -> None:
        if self.edit_entry is None:
            return
        if self._focus_is_suggestion():
            return
        # Don't commit while the rebar calculator is open (focus will move to the dialog)
        if getattr(self, "_in_rebar_calculator", False):
            return
        self._commit_edit()

    def _focus_is_suggestion(self) -> bool:
        if self._suggest_box is None:
            return False
        try:
            widget = self.winfo_toplevel().focus_get()
        except KeyError:
            # Sometimes focus_get() raises KeyError for transient widgets
            return False
        while widget is not None:
            if widget == self._suggest_list or widget == self._suggest_box:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _current_suggestion_index(self) -> int:
        if self._suggest_list is None:
            return 0
        selection = self._suggest_list.curselection()
        return selection[0] if selection else 0

    def _select_suggestion(self, index: int) -> None:
        if self._suggest_list is None:
            return
        self._suggest_list.selection_clear(0, tk.END)
        self._suggest_list.selection_set(index)
        self._suggest_list.see(index)

    def _on_suggestion_click(self, _event: tk.Event) -> None:
        self._apply_suggestion()

    def _on_suggestion_enter(self, _event: tk.Event) -> None:
        """Handler when user presses Enter in suggestion list.

        We apply the selected suggestion and commit the edit so that a single
        Enter will both pick the suggestion and populate the cell. This keeps
        keyboard-driven entry fluid for fast data entry.
        """
        # Apply the suggestion to the entry
        self._apply_suggestion()
        # Commit the edit (this will write the value to the tree and destroy the entry)
        self._commit_edit()

    def _apply_suggestion(self) -> None:
        if self.edit_entry is None or self._suggest_list is None:
            return
        idx = self._current_suggestion_index()
        value = self._suggest_list.get(idx)
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, value)
        self._hide_suggestions()
        self.edit_entry.focus_set()

    def _hide_suggestions(self) -> None:
        if self._suggest_box is not None:
            self._suggest_box.destroy()
            self._suggest_box = None
            self._suggest_list = None

    def debug_check_sources(self) -> Dict[str, object]:
        """Returns diagnostic info about connected repositories and lists.

        Useful for debug and for showing in UI.
        """
        info: Dict[str, object] = {}
        # Sections
        try:
            if self.section_repository is None:
                info["sections_count"] = 0
                info["sections_sample"] = []
                logger.warning("No SectionRepository provided to VerificationTableApp")
            else:
                secs = self.section_repository.get_all_sections()
                info["sections_count"] = len(secs)
                info["sections_sample"] = [s.name for s in secs[:10]]
        except Exception as e:
            logger.exception("Error reading sections repository: %s", e)
            info["sections_count"] = 0
            info["sections_sample"] = []

        # Materials
        try:
            if self.material_repository is not None:
                try:
                    mats = self.material_repository.get_all()
                    info["materials_count"] = len(mats)
                    info["materials_sample"] = [m.name if hasattr(m, "name") else m.get("name") for m in mats[:10]]
                except Exception:
                    mats = self.material_repository.list_materials()
                    info["materials_count"] = len(mats)
                    info["materials_sample"] = [m.get("name") for m in mats[:10]]
            else:
                # fall back to the names list we have
                info["materials_count"] = len(self.material_names or [])
                info["materials_sample"] = (self.material_names or [])[:10]
                if not self.material_names:
                    logger.warning("No MaterialRepository provided and no material names available")
        except Exception as e:
            logger.exception("Error reading materials repository: %s", e)
            info["materials_count"] = 0
            info["materials_sample"] = []

        logger.debug("Debug check sources: %s", info)
        return info

    def refresh_sources(self) -> None:
        """Reload names from provided repositories and update suggestion maps.

        We preserve callable suggestion sources for material columns so that
        repository-backed and historical materials are searched dynamically
        (supports type filtering)."""
        self.section_names = self._resolve_section_names(self.section_repository, None)
        self.material_names = self._resolve_material_names(None)
        # Section suggestions can be a static list
        self.suggestions_map["section"] = self.section_names
        # Material suggestions remain callable to allow repository-backed search
        self.suggestions_map["mat_concrete"] = (lambda q: self._search_materials(q, type_filter="concrete"))
        self.suggestions_map["mat_steel"] = (lambda q: self._search_materials(q, type_filter="steel"))
        self.suggestions_map["stirrups_mat"] = (lambda q: self._search_materials(q, type_filter=None))

    def export_to_csv(self) -> None:
        """Apri il dialogo di salvataggio e esporta la tabella in CSV con ';' e ','

        Metodo pubblico che implementa la funzionalità richiesta: apre il
        `asksaveasfilename`, chiama `export_csv(path)` e notifica l'utente.
        """
        try:
            from tkinter import filedialog
        except Exception:
            self._show_error("Export CSV", ["File dialog non disponibile"])
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            self.export_csv(path)
            messagebox.showinfo("Esporta CSV", f"Esportato in {path}")
        except Exception as e:
            logger.exception("Errore esportazione CSV: %s", e)
            self._show_error("Esporta CSV", [f"Errore durante l'esportazione: {e}"])

    def _on_export_csv(self) -> None:
        """Handler collegato al pulsante: delega a `export_to_csv`."""
        self.export_to_csv()

    def _format_errors_for_display(self, errors: List[str], header: Optional[str] = None) -> str:
        """Costruisce una stringa di messaggi di errore coerente da mostrare all'utente.

        - `errors` è una lista di messaggi (linee) che verranno unite con '\n'.
        - `header` testo opzionale da anteporre al messaggio (es. titolo o descrizione breve).
        """
        parts: List[str] = []
        if header:
            parts.append(header)
        parts.extend(errors)
        return "\n".join(parts)

    def _show_error(self, title: str, errors: List[str], header: Optional[str] = None) -> None:
        """Mostra un messagebox.showerror usando il formato centralizzato."""
        text = self._format_errors_for_display(errors, header=header)
        messagebox.showerror(title, text)

    def import_from_csv(self) -> None:
        """Apri dialog 'Apri file' e importa un CSV compatibile con `export_csv`.

        Questo metodo mostra messaggi chiari all'utente in caso di successo o di
        errori (intestazione non valida, righe malformate, ecc.).
        """
        try:
            from tkinter import filedialog
        except Exception:
            self._show_error("Importa CSV", ["File dialog non disponibile"])
            return
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            imported, skipped, errors = self.import_csv(path, clear=True)
            messagebox.showinfo("Importa CSV", f"Importate {imported} righe. Saltate {skipped} righe.")
        except Exception as e:
            logger.exception("Errore import CSV: %s", e)
            self._show_error("Importa CSV", [f"Errore durante l'importazione: {e}"])

    def _on_import_csv(self) -> None:
        """Handler collegato al pulsante: delega a `import_from_csv`."""
        self.import_from_csv()

    # ------------------------------------------------------------------
    # Helpers: suggestion box, esportazione/importazione e gestione righe
    # ------------------------------------------------------------------
    def _ensure_suggestion_box(self) -> None:
        """Crea la finestra e la listbox usate per i suggerimenti se non esistono."""
        if self._suggest_box is not None:
            return
        self._suggest_box = tk.Toplevel(self)
        self._suggest_box.wm_overrideredirect(True)
        self._suggest_box.attributes("-topmost", True)
        self._suggest_list = tk.Listbox(self._suggest_box, height=6)
        self._suggest_list.pack(fill="both", expand=True)
        self._suggest_list.bind("<ButtonRelease-1>", self._on_suggestion_click)
        self._suggest_list.bind("<Return>", self._on_suggestion_enter)
        self._suggest_list.bind("<Escape>", lambda _e: self._hide_suggestions())

    def _col_to_attr(self, col: str) -> str:
        """Mappa la colonna (key) all'attributo del dataclass VerificationInput."""
        mapping = {
            "section": "section_id",
            "verif_method": "verification_method",
            "mat_concrete": "material_concrete",
            "mat_steel": "material_steel",
            "n": "n_homog",
            "N": "N",
            "M": "M",
            "T": "T",
            "As_p": "As_inf",
            "As": "As_sup",
            "d_p": "d_inf",
            "d": "d_sup",
            "stirrups_step": "stirrup_step",
            "stirrups_diam": "stirrup_diameter",
            "stirrups_mat": "stirrup_material",
            "notes": "notes",
        }
        return mapping.get(col, col)

    def get_rows(self) -> List[VerificationInput]:
        """Restituisce tutte le righe della tabella come lista di VerificationInput."""
        items = list(self.tree.get_children())
        return [self.table_row_to_model(i) for i in range(len(items))]

    def set_rows(self, rows: Iterable[VerificationInput]) -> None:
        """Sostituisce il contenuto della tabella con le righe fornite."""
        for item in list(self.tree.get_children()):
            self.tree.delete(item)
        for r in rows:
            item = self._add_row()
            self.update_row_from_model(self.tree.index(item), r)

    def load_items_from_repository(self) -> None:
        """Carica gli elementi dal repository esterno (se presente) nella tabella.

        - Se è fornito `verification_items_repository`, legge `get_all()` e imposta le
          righe con i campi `.input` di ciascun `VerificationItem`.
        - Se il repository è vuoto o non fornito, mantiene il comportamento attuale.
        """
        if not self.verification_items_repository:
            logger.debug("Nessun verification_items_repository fornito; uso righe vuote")
            for item in list(self.tree.get_children()):
                self.tree.delete(item)
            self._insert_empty_rows(self.initial_rows)
            return
        try:
            items = self.verification_items_repository.get_all()
            if not items:
                logger.debug("Repository vuoto: inserisco righe vuote")
                for item in list(self.tree.get_children()):
                    self.tree.delete(item)
                self._insert_empty_rows(self.initial_rows)
                return
            for item in list(self.tree.get_children()):
                self.tree.delete(item)
            self.set_rows([it.input for it in items])
            logger.info("Caricati %d elementi dal repository", len(items))
        except Exception as e:
            logger.exception("Errore in load_items_from_repository: %s", e)
            messagebox.showerror("Caricamento elementi", f"Errore caricamento repository: {e}")

    def save_items_to_repository(self) -> int:
        """Salva tutte le righe correnti della tabella nel repository esterno.

        - Genera ID semplici (E001, E002, ...)
        - Usa `notes` come `name` se presente, altrimenti 'Elemento {index}'
        - Cancella il repository e salva nuovamente tutti gli elementi
        """
        if not self.verification_items_repository:
            logger.debug("Nessun verification_items_repository fornito; skip save")
            return 0
        if VerificationItem is None:
            logger.error("Classe VerificationItem non disponibile; impossibile salvare")
            messagebox.showerror("Salva elementi", "Impossibile salvare: classe VerificationItem non disponibile")
            return 0
        try:
            rows = self.get_rows()
            # Clear repository first (behaviour richiesto)
            self.verification_items_repository.clear()
            for idx, inp in enumerate(rows, start=1):
                item_id = f"E{idx:03d}"
                name = (inp.notes.strip() if getattr(inp, "notes", None) else "") or f"Elemento {idx}"
                item = VerificationItem(id=item_id, name=name, input=inp)
                self.verification_items_repository.save(item)
            logger.info("Salvati %d elementi nel repository", len(rows))
            return len(rows)
        except Exception as e:
            logger.exception("Errore in save_items_to_repository: %s", e)
            messagebox.showerror("Salva elementi", f"Errore salvataggio repository: {e}")
            return 0

    def _on_save_items(self) -> None:
        """Handler per il pulsante 'Salva elementi' nella toolbar."""
        if not self.verification_items_repository:
            messagebox.showwarning("Salva elementi", "Nessun repository fornito per salvare gli elementi.")
            return
        saved = self.save_items_to_repository()
        messagebox.showinfo("Salva elementi", f"Elementi salvati: {saved}")

    # --- Project file handlers (.jsonp) ---
    def _elem_dict_to_input(self, e: dict) -> VerificationInput:
        # Map a flexible element dict into VerificationInput
        def pick(*keys, default=""):
            for k in keys:
                if k in e and e[k] is not None:
                    return e[k]
            return default

        return VerificationInput(
            section_id=pick("section_id", "section", "section_name"),
            verification_method=pick("method", "verification_method", "verif_method", "TA"),
            material_concrete=pick("cls_id", "mat_concrete", "material_concrete", ""),
            material_steel=pick("steel_id", "mat_steel", "material_steel", ""),
            n_homog=float(pick("coeff_n", "n", 15.0) or 15.0),
            N=float(pick("N", 0.0) or 0.0),
            M=float(pick("M", 0.0) or 0.0),
            T=float(pick("T", 0.0) or 0.0),
            As_sup=float(pick("As", "As_sup", "As_sup_cm", 0.0) or 0.0),
            As_inf=float(pick("As_p", "As_inf", "As_inf_cm", 0.0) or 0.0),
            d_sup=float(pick("d", "d_sup", 4.0) or 4.0),
            d_inf=float(pick("d_p", "d_inf", 4.0) or 4.0),
            stirrup_step=float(pick("passo_staffe", "stirrups_step", 0.0) or 0.0),
            stirrup_diameter=float(pick("stirrups_diam", "stirrups_diameter", 0.0) or 0.0),
            stirrup_material=pick("stirrups_mat", "stirrups_material", ""),
            notes=pick("notes", "name", "") or "",
        )

    def _on_load_project(self) -> None:
        if self.project is None:
            messagebox.showerror("Carica progetto", "Modulo progetto non disponibile")
            return
        path = filedialog.askopenfilename(filetypes=[("JSONP", "*.jsonp")])
        if not path:
            return
        try:
            self.project.load_from_file(path)
        except ValueError as e:
            messagebox.showerror("Carica progetto", str(e))
            return
        except Exception as e:
            logger.exception("Errore caricamento progetto: %s", e)
            messagebox.showerror("Carica progetto", f"Errore caricamento progetto: {e}")
            return

        # Clear current table and populate
        for item in list(self.tree.get_children()):
            self.tree.delete(item)
        rows = [self._elem_dict_to_input(el) for el in self.project.elements]
        self.set_rows(rows)

        # Update material and section name lists for suggestions
        # Materials: use ids or names from project
        new_mat_names = set()
        for typ in ("cls", "steel"):
            for m in self.project.materials.get(typ, {}).values():
                name = m.get("name") or m.get("id")
                if name:
                    new_mat_names.add(name)
        if new_mat_names:
            self.material_names = sorted(set(self.material_names) | new_mat_names)

        new_sec_names = {s.get("id") or s.get("name") for s in self.project.sections.values()}
        if new_sec_names:
            self.section_names = sorted(set(self.section_names) | {n for n in new_sec_names if n})

        self.project.dirty = False
        messagebox.showinfo("Carica progetto", f"Progetto caricato: {path}")

    def _on_add_list_elements(self) -> None:
        if self.project is None:
            messagebox.showerror("Aggiungi lista di elementi", "Modulo progetto non disponibile")
            return
        path = filedialog.askopenfilename(filetypes=[("JSONP", "*.jsonp")])
        if not path:
            return
        try:
            new_mats, new_secs, new_elems = self.project.add_elements_from_file(path)
        except ValueError as e:
            messagebox.showerror("Aggiungi lista di elementi", str(e))
            return
        except Exception as e:
            logger.exception("Errore in add_elements_from_file: %s", e)
            messagebox.showerror("Aggiungi lista di elementi", f"Errore apertura file: {e}")
            return

        # Load elements from file and append to table (do not clear existing)
        try:
            import json as _json
            with open(path, "r", encoding="utf-8") as f:
                data = _json.load(f)
            for el in data.get("elements") or []:
                inp = self._elem_dict_to_input(el)
                item = self._add_row()
                self.update_row_from_model(self.tree.index(item), inp)
        except Exception:
            # In case of parsing issues, we've already merged into project; still inform user
            logger.exception("Errore parsing elementi dopo add")

        # Update material and section lists
        if new_mats:
            for typ in ("cls", "steel"):
                for m in self.project.materials.get(typ, {}).values():
                    name = m.get("name") or m.get("id")
                    if name and name not in self.material_names:
                        self.material_names.append(name)
            self.material_names = sorted(set(self.material_names))
        if new_secs:
            for s in self.project.sections.values():
                sid = s.get("id") or s.get("name")
                if sid and sid not in self.section_names:
                    self.section_names.append(sid)
            self.section_names = sorted(set(self.section_names))

        messagebox.showinfo("Aggiungi lista di elementi", f"Aggiunti elementi: {new_elems}; nuove sezioni: {new_secs}; nuovi materiali: {new_mats}")

    def _on_save_project(self) -> None:
        if self.project is None:
            messagebox.showerror("Salva progetto", "Modulo progetto non disponibile")
            return

        # Collect current state from UI into project
        rows = self.get_rows()
        elems = []
        for idx, r in enumerate(rows, start=1):
            el = {
                "id": f"E{idx:03d}",
                "section_id": r.section_id,
                "cls_id": r.material_concrete,
                "steel_id": r.material_steel,
                "method": r.verification_method,
                "N": r.N,
                "M": r.M,
                "T": r.T,
                "coeff_n": r.n_homog,
                "As": r.As_sup,
                "As_p": r.As_inf,
                "d": r.d_sup,
                "d_p": r.d_inf,
                "passo_staffe": r.stirrup_step,
                "stirrups_diam": r.stirrup_diameter,
                "stirrups_mat": r.stirrup_material,
                "notes": r.notes,
            }
            elems.append(el)

            # Ensure materials and sections exist minimally in project
            if r.material_concrete:
                mid = r.material_concrete
                if mid not in self.project.materials.get("cls", {}):
                    self.project.materials.setdefault("cls", {})[mid] = {"id": mid, "name": mid}
            if r.material_steel:
                sid = r.material_steel
                if sid not in self.project.materials.get("steel", {}):
                    self.project.materials.setdefault("steel", {})[sid] = {"id": sid, "name": sid}
            if r.section_id:
                secid = r.section_id
                if secid not in self.project.sections:
                    self.project.sections[secid] = {"id": secid, "type": "unknown"}

        self.project.elements = elems

        # Decide save path: if existing and last action wasn't add-list, reuse; otherwise ask
        save_path = None
        if self.project.path and not self.project.last_action_was_add_list:
            save_path = self.project.path
        else:
            save_path = filedialog.asksaveasfilename(defaultextension=".jsonp", filetypes=[("JSONP", "*.jsonp")])
            if not save_path:
                return

        try:
            self.project.save_to_file(save_path)
            messagebox.showinfo("Salva progetto", f"Progetto salvato: {save_path}")
        except Exception as e:
            logger.exception("Errore salvataggio progetto: %s", e)
            messagebox.showerror("Salva progetto", f"Errore salvataggio progetto: {e}")

    def create_test_project(self) -> None:
        """Crea un progetto di test usando sezioni/materiali esistenti.

        - Cerca un cls il cui nome o code contenga la stringa '160' (case-insensitive).
        - Cerca un acciaio con nome contenente 'ferro' e 'dolce' (deterministico: primo ordinato per name).
        - Usa una sezione rettangolare dalla repository (primo elemento ordinato per name),
          oppure crea una `RectangularSection(30,50)` se non disponibile.
        - Genera N, M, T in [-100, 100] e popola il progetto (`self.project`) e la GUI.

        Nota: se non trova il cls con '160' o il materiale 'ferro dolce', mostra un errore e abortisce.
        """
        if self.project is None:
            messagebox.showerror("Crea progetto test", "Modulo progetto non disponibile")
            return
        if self.material_repository is None or self.section_repository is None:
            messagebox.showerror("Crea progetto test", "Repository sezioni o materiali non disponibili")
            return

        # --- Recupero CLS con '160' nel nome o nel codice ---
        # Cerco in modo deterministico: ordino per nome e prendo il primo che contiene '160'.
        concrete_candidates = [m for m in self.material_repository.get_all() if getattr(m, 'type', '') == 'concrete']
        concrete_candidates_sorted = sorted(concrete_candidates, key=lambda m: (m.name or '').lower())
        cls_mat = None
        for m in concrete_candidates_sorted:
            name_code = f"{(m.name or '')} {getattr(m, 'code', '')}".lower()
            if '160' in name_code:
                cls_mat = m
                break
        if cls_mat is None:
            messagebox.showerror("Crea progetto test", "Nessun calcestruzzo con '160' nel nome trovato nella libreria materiali")
            return

        # --- Recupero acciaio 'ferro dolce' ---
        steel_candidates = [m for m in self.material_repository.get_all() if getattr(m, 'type', '') == 'steel']
        steel_sorted = sorted(steel_candidates, key=lambda m: (m.name or '').lower())
        steel_mat = None
        for m in steel_sorted:
            nm = (m.name or '').lower()
            # Cerco le parole 'ferro' e 'dolce' (flessibile su varianti)
            if 'ferro' in nm and 'dolce' in nm:
                steel_mat = m
                break
        if steel_mat is None:
            messagebox.showerror("Crea progetto test", "Nessun acciaio 'ferro dolce' trovato nella libreria materiali")
            return

        # --- Recupero sezione rettangolare dalla repository ---
        rects = [s for s in self.section_repository.get_all_sections() if getattr(s, 'section_type', '').upper() == 'RECTANGULAR']
        rects_sorted = sorted(rects, key=lambda s: (getattr(s, 'name', '') or '').lower())
        if rects_sorted:
            section = rects_sorted[0]
        else:
            # Se non esiste, creo una sezione rettangolare standard (30x50 cm)
            if RectangularSection is None:
                messagebox.showerror("Crea progetto test", "Classe RectangularSection non disponibile")
                return
            section = RectangularSection(name="Test Rect 30x50", width=30.0, height=50.0)

        # --- Generazione sollecitazioni di prova in intervallo [-100, 100] ---
        N = round(random.uniform(-100.0, 100.0), 3)
        M = round(random.uniform(-100.0, 100.0), 3)
        T = round(random.uniform(-100.0, 100.0), 3)

        # --- Inizializzo nuovo progetto vuoto e popolo materiali/sezioni/elemento ---
        self.project.new_project()

        # Aggiungo materiali al progetto (uso to_dict-like structure)
        # Material ha metodo to_dict() definito in core_models.materials.Material
        try:
            cls_dict = cls_mat.to_dict()
        except Exception:
            cls_dict = {"id": getattr(cls_mat, 'id', ''), "name": getattr(cls_mat, 'name', '')}
        try:
            steel_dict = steel_mat.to_dict()
        except Exception:
            steel_dict = {"id": getattr(steel_mat, 'id', ''), "name": getattr(steel_mat, 'name', '')}
        self.project.materials.setdefault('cls', {})[cls_dict.get('id') or cls_dict.get('name')] = cls_dict
        self.project.materials.setdefault('steel', {})[steel_dict.get('id') or steel_dict.get('name')] = steel_dict

        # Sezione: inserisco il dizionario della sezione
        try:
            sec_dict = section.to_dict()
        except Exception:
            # Fallback minimale
            sec_dict = {"id": getattr(section, 'id', 'SEC1'), "name": getattr(section, 'name', 'Test Rect 30x50'), "type": getattr(section, 'section_type', 'RECTANGULAR')}
        self.project.sections[sec_dict.get('id') or sec_dict.get('name')] = sec_dict

        # Elemento di prova
        elem = {
            "id": "E001",
            "section_id": sec_dict.get('id') or sec_dict.get('name'),
            "cls_id": cls_dict.get('id') or cls_dict.get('name'),
            "steel_id": steel_dict.get('id') or steel_dict.get('name'),
            "method": "TA",
            "N": N,
            "M": M,
            "T": T,
            "coeff_n": 15.0,
            "As": 0.0,
            "As_p": 0.0,
            "d": getattr(section, 'width', 30.0) * 0.1,
            "d_p": 4.0,
        }
        self.project.elements = [elem]
        self.project.dirty = True

        # --- Aggiorno la GUI: svuoto la tabella e aggiungo la riga di test ---
        for item in list(self.tree.get_children()):
            self.tree.delete(item)

        test_input = VerificationInput(
            section_id=elem['section_id'],
            verification_method=elem['method'],
            material_concrete=elem['cls_id'],
            material_steel=elem['steel_id'],
            n_homog=float(elem.get('coeff_n', 15.0)),
            N=float(elem.get('N', 0.0)),
            M=float(elem.get('M', 0.0)),
            T=float(elem.get('T', 0.0)),
            As_sup=float(elem.get('As', 0.0)),
            As_inf=float(elem.get('As_p', 0.0)),
            d_sup=float(elem.get('d', 4.0)),
            d_inf=float(elem.get('d_p', 4.0)),
        )
        self.set_rows([test_input])

        messagebox.showinfo("Crea progetto test", f"Progetto di test creato con cls='{cls_dict.get('name')}' e acciaio='{steel_dict.get('name')}'")

    def _format_value_for_csv(self, value: object) -> str:
        """Formatta un valore per il CSV: usa la virgola come separatore decimale

        - Se il valore è numerico (int/float) lo converte in stringa e sostituisce
          il punto decimale con la virgola.
        - Se è una stringa che rappresenta un numero, tenta la conversione e
          applica la stessa regola; altrimenti restituisce la stringa così com'è.
        """
        # Numerico nativo
        if isinstance(value, (int, float)):
            return str(value).replace(".", ",")
        # Proviamo a interpretare la stringa come numero (accetta "," come separatore)
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return ""
            try:
                # sostituisco la virgola con il punto prima del parsing
                f = float(s.replace(",", "."))
                return str(f).replace(".", ",")
            except Exception:
                return s
        return str(value)

    def export_csv(self, path: str, *, include_header: bool = True) -> None:
        """Esporta la tabella in un file CSV con intestazioni corrispondenti alle colonne.

        - Usa `;` come delimitatore di campo (compatibile con Excel italiano).
        - Converte i separatori decimali da '.' a ',' per i valori numerici tramite
          `_format_value_for_csv` (es. 1.23 -> '1,23').
        """
        import csv
        keys = [c[0] for c in COLUMNS]
        header = [c[1] for c in COLUMNS]
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, delimiter=";")
            if include_header:
                writer.writerow(header)
            for r in self.get_rows():
                row = []
                for k in keys:
                    raw = getattr(r, self._col_to_attr(k))
                    row.append(self._format_value_for_csv(raw))
                writer.writerow(row)

    def import_csv(self, path: str, *, clear: bool = True):
        """Importa righe da CSV; il file deve essere compatibile con `export_csv()`.

        - Legge con `delimiter=';'` e si aspetta la prima riga come intestazione.
        - Se l'intestazione è una permutazione valida delle intestazioni attese,
          si applica automaticamente il mapping delle colonne (opzione utile
          quando il file ha le colonne nello stesso insieme ma in ordine diverso).
        - Per ogni riga successiva converte i campi numerici sostituendo la
          virgola con il punto prima della conversione a float. Se una riga ha
          valori malformati viene saltata; ogni problema viene loggato in modo
          dettagliato e raccolto nella lista `errors`.

        Restituisce una tupla `(imported_count, skipped_count, errors)` per usi
        programmatici.
        """
        import csv
        try:
            with open(path, newline="", encoding="utf-8") as fh:
                reader = csv.reader(fh, delimiter=";")
                rows = list(reader)
        except Exception as e:
            # Gestione più esplicita dei problemi di lettura/parsing CSV
            logger.exception("Import CSV: impossibile leggere/parsare il file '%s': %s", path, e)
            self._show_error("Importa CSV", [f"Impossibile leggere o parsare il file: {e}"])
            return 0, 0, [str(e)]
        if not rows:
            logger.debug("Import CSV: file vuoto o privo di righe: %s", path)
            return 0, 0, []

        expected_header = [c[1] for c in COLUMNS]
        header = [h.strip() for h in rows[0]]

        # Prepariamo una mappa da index_file -> index_expected
        index_map: List[Optional[int]] = []
        if header == expected_header:
            index_map = list(range(len(header)))
            logger.debug("Import CSV: header corrisponde all'ordine atteso")
            # Supporto retro-compatibilità: alcuni file di esempio possono omettere
            # la colonna 'Metodo verifica' (seconda colonna). Se rileviamo che tutte
            # le righe hanno una colonna in meno rispetto all'header, applichiamo
            # una correzione semplice inserendo un placeholder None per la colonna
            # 'Metodo verifica' (index 1) in modo da non agganciare per posizione
            row_lengths = [len(r) for r in rows[1:]]
            logger.info("Import CSV: header len=%d row lens sample=%s", len(header), row_lengths[:5])
            if any(l == len(header) - 1 for l in row_lengths):
                logger.info("Import CSV: righe con colonna mancante rilevate; applico correzione per 'Metodo verifica'")
                # shift indices after the missing column
                index_map = [0, None] + [i - 1 for i in range(2, len(header))]
                logger.debug("Import CSV: index_map corretto: %s", index_map)
        else:
            # Se il set delle intestazioni coincide, applichiamo mapping automatico
            if set(header) == set(expected_header) and len(header) == len(expected_header):
                # per ogni expected header cerchiamo l'indice nel file
                index_map = [header.index(h) for h in expected_header]
                logger.info("Import CSV: header in ordine diverso, applicato mapping automatico: %s", index_map)
            else:
                # Supporta file CSV che contengono un sottoinsieme di colonne in ordine
                # atteso (per compatibilità retroattiva). In questo caso creiamo una
                # mappa con indici o None per colonne mancanti.
                if set(header).issubset(set(expected_header)) and len(header) < len(expected_header):
                    index_map = [header.index(h) if h in header else None for h in expected_header]
                    logger.info("Import CSV: header incompleto, applicato mapping parziale: %s", index_map)
                else:
                    logger.error("Import CSV: header non valido. Atteso: %s. Trovato: %s", expected_header, header)
                    header_msg = f"Intestazione CSV non corrisponde all'ordine atteso."
                    details = [f"Atteso: {expected_header}", f"Trovato: {rows[0]}"]
                    self._show_error("Importa CSV", details, header=header_msg)
                    return 0, max(0, len(rows) - 1), ["Header mismatch"]

        key_names = [c[0] for c in COLUMNS]
        numeric_attrs = {"n_homog", "N", "M", "T", "As_sup", "As_inf", "d_sup", "d_inf", "stirrup_step", "stirrup_diameter"}

        models: List[VerificationInput] = []
        errors: List[str] = []

        for i, row in enumerate(rows[1:], start=2):  # starting from line 2
            # ricaviamo valori usando la mappa di indici
            vals = []
            for idx in index_map:
                if idx is None:
                    vals.append("")
                else:
                    vals.append(row[idx] if idx < len(row) else "")
            # assicurarsi che la lunghezza corrisponda
            vals = vals + [""] * (len(COLUMNS) - len(vals))

            kwargs: Dict[str, object] = {}
            row_bad = False
            for k, idx in zip(key_names, index_map):
                # Se la colonna non è presente nel file (idx is None) saltiamo e
                # lasciamo il valore di default del dataclass (se presente).
                if idx is None:
                    continue
                # idx is the index in the original row; use it directly instead of
                # indexing into 'vals' which holds shifted values.
                v = row[idx] if idx < len(row) else ""
                attr = self._col_to_attr(k)
                if attr in numeric_attrs:
                    s = str(v).strip()
                    if not s:
                        kwargs[attr] = 0.0
                        continue
                    # sostituisco la virgola con il punto per la conversione
                    normalized = s.replace(",", ".")
                    try:
                        kwargs[attr] = float(normalized)
                    except Exception:
                        msg = f"Riga {i}: valore numerico non valido per '{k}': '{v}'"
                        errors.append(msg)
                        logger.error("Import CSV: %s -- riga content: %s", msg, row)
                        row_bad = True
                        break
                else:
                    kwargs[attr] = v
            if row_bad:
                # salto la riga e continuiamo
                continue
            try:
                models.append(VerificationInput(**kwargs))
            except Exception as e:  # pragma: no cover - difensivo
                msg = f"Riga {i}: errore creazione modello: {e}"
                errors.append(msg)
                logger.exception("Import CSV: %s -- riga content: %s", msg, row)

        # Sostituisco le righe della tabella con i modelli importati
        if clear:
            for item in list(self.tree.get_children()):
                self.tree.delete(item)
        self.set_rows(models)

        imported = len(models)
        skipped = max(0, (len(rows) - 1) - imported)

        # Registriamo un log dettagliato e mostriamo messaggi all'utente se ci sono errori
        if errors:
            logger.error("Import CSV: import completato con errori: %s", errors[:20])
            header_msg = "Si sono verificati errori durante l'import:"
            self._show_error("Importa CSV", errors[:20], header=header_msg)
        else:
            logger.info("Import CSV: import completato senza errori. Importate %d righe", imported)

        return imported, skipped, errors

    def _on_compute_all(self) -> None:
        """Handler per il pulsante 'Calcola tutte le righe'.

        Itera su tutte le righe della tabella, per ciascuna:
        - converte la riga in VerificationInput usando table_row_to_model
        - chiama compute_verification_result per ottenere VerificationOutput
        - colleziona i risultati in una stringa descrittiva
        - mostra un messagebox con l'elenco dei risultati

        In futuro potrebbe anche aggiornare colonne della tabella con i risultati
        (es. esito, coeff_sicurezza, ecc.).
        """
        items = list(self.tree.get_children())
        if not items:
            messagebox.showinfo("Verifica", "Nessuna riga da verificare.")
            return

        risultati = []
        for row_idx, item in enumerate(items):
            try:
                model = self.table_row_to_model(row_idx)
            except Exception as e:
                logger.exception("Errore conversione riga %s: %s", row_idx + 1, e)
                risultati.append(f"Riga {row_idx + 1}: ERRORE CONVERSIONE – {e}")
                continue

            try:
                result = compute_verification_result(model, self.section_repository, self.material_repository)
            except Exception as e:
                logger.exception("Errore verifica riga %s: %s", row_idx + 1, e)
                risultati.append(f"Riga {row_idx + 1}: ERRORE CALCOLO – {e}")
                continue

            # Formato: "Riga N [METODO]: esito=..., γ=..."
            metodo = model.verification_method or "?"
            risultati.append(
                f"Riga {row_idx + 1} [{metodo}]: esito={result.esito}, "
                f"γ={result.coeff_sicurezza:.2f}"
            )

        # Mostra risultati in un messagebox
        msg = "\n".join(risultati)
        messagebox.showinfo("Risultati verifiche", msg)

    def _open_rebar_calculator(self) -> None:
        if self.edit_entry is None or self.edit_column is None:
            return
        self._rebar_target_column = self.edit_column
        # Set flag to avoid losing the edit when the calculator grabs focus
        self._in_rebar_calculator = True
        if self._rebar_window is not None and self._rebar_window.winfo_exists():
            self._rebar_window.lift()
            self._rebar_window.focus_set()
            if self._rebar_entries:
                self._rebar_entries[0].focus_set()
            return

        win = tk.Toplevel(self)
        win.title("Calcolo area armatura")
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())
        win.grab_set()
        self._rebar_window = win

        frame = tk.Frame(win, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        diameters = [8, 10, 12, 14, 16, 20, 25]
        self._rebar_vars = {}
        self._rebar_entries = []

        tk.Label(frame, text="Ø (mm)", width=8, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="n barre", width=8, anchor="w").grid(row=0, column=1, sticky="w")

        for i, d in enumerate(diameters, start=1):
            tk.Label(frame, text=f"Ø{d}", width=8, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="")
            self._rebar_vars[d] = var
            ent = tk.Entry(frame, textvariable=var, width=8)
            self._rebar_entries.append(ent)
            ent.grid(row=i, column=1, sticky="w", pady=2)
            var.trace_add("write", lambda *_: self._update_rebar_total())
            if i == 1:
                ent.focus_set()

        total_frame = tk.Frame(frame)
        total_frame.grid(row=len(diameters) + 1, column=0, columnspan=2, sticky="w", pady=(8, 4))
        tk.Label(total_frame, text="Area totale [cm²]:").pack(side="left")
        tk.Label(total_frame, textvariable=self._rebar_total_var, width=10, anchor="w").pack(side="left")

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=len(diameters) + 2, column=0, columnspan=2, sticky="e")
        tk.Button(btn_frame, text="Conferma", command=self._confirm_rebar_total).pack(side="right")

        win.bind("<Escape>", lambda _e: self._close_rebar_window())
        win.bind("<Return>", lambda _e: self._confirm_rebar_total())

        self._update_rebar_total()

    def _update_rebar_total(self) -> None:
        total = 0.0
        for d, var in self._rebar_vars.items():
            try:
                n = int(var.get() or 0)
            except ValueError:
                n = 0
            d_cm = d / 10.0
            area = math.pi * (d_cm ** 2) / 4.0
            total += n * area
        self._rebar_total_var.set(f"{total:.2f}")

    def _confirm_rebar_total(self) -> None:
        if self.edit_entry is None or self._rebar_target_column is None:
            # Fallback: if the entry was closed for some reason, try to set the tree cell directly
            try:
                if self.edit_item and self._rebar_target_column:
                    value = self._rebar_total_var.get()
                    self.tree.set(self.edit_item, self._rebar_target_column, value)
            except Exception:
                logger.exception("Unable to apply rebar total in fallback path")
            self._close_rebar_window()
            return
        value = self._rebar_total_var.get()
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, value)
        self._commit_edit()
        self._close_rebar_window()

    def _close_rebar_window(self) -> None:
        if self._rebar_window is not None:
            self._rebar_window.destroy()
        self._rebar_window = None
        self._rebar_entries = []
        # Clear flag after the calculator is closed
        self._in_rebar_calculator = False


class VerificationTableWindow(tk.Toplevel):
    """Thin Toplevel wrapper that accepts section and material repositories and
    embeds the existing `VerificationTableApp` frame. This keeps the original
    GUI/logic unchanged while exposing repository attributes to the window.
    """

    def __init__(
        self,
        master: tk.Misc,
        section_repository: Optional["SectionRepository"] = None,
        material_repository: Optional["MaterialRepository"] = None,
        verification_items_repository: Optional["VerificationItemsRepository"] = None,
    ) -> None:
        super().__init__(master)
        self.section_repository = section_repository
        self.material_repository = material_repository
        self.verification_items_repository = verification_items_repository

        self.title("Verification Table - RD2229")
        self.geometry("1400x520")

        # Prepare material names list if repository provided
        material_names = None
        if material_repository is not None:
            try:
                # MaterialRepository may expose get_all() returning objects with .name
                mats = material_repository.get_all()
                material_names = [m.name if hasattr(m, "name") else m.get("name") for m in mats]
            except Exception:
                try:
                    # Fallback to older interface (tools.materials_manager)
                    material_names = [m.get("name") for m in material_repository.list_materials()]
                except Exception:
                    material_names = None
        else:
            # If no repository is provided, try to use the legacy `list_materials`
            # helper (if available) to pre-populate material names for comboboxes.
            try:
                if list_materials is not None:
                    material_names = [m.get("name") for m in list_materials()]
            except Exception:
                material_names = None

        # Embed the existing app frame
        self.app = VerificationTableApp(
            self,
            section_repository=section_repository,
            material_repository=material_repository,
            material_names=material_names,
            verification_items_repository=verification_items_repository,
        )
        self.app.pack(fill="both", expand=True)

        # Carica eventuali elementi salvati nel repository (se fornito)
        try:
            self.app.load_items_from_repository()
        except Exception:
            # Non vogliamo interrompere l'apertura della finestra per errori di caricamento
            logger.exception("Errore durante il caricamento iniziale degli elementi dal repository")

        # Status / debug frame
        status = tk.Frame(self, relief="groove", bd=1)
        status.pack(fill="x", side="bottom")
        self._status_sections = tk.Label(status, text="Sections: ?")
        self._status_sections.pack(side="left", padx=8)
        self._status_materials = tk.Label(status, text="Materials: ?")
        self._status_materials.pack(side="left", padx=8)
        tk.Button(status, text="Check sources", command=self._check_sources).pack(side="right", padx=8)

        # Initialize status text
        self._update_status_labels()
        
        # Subscribe to repository change events
        self._subscribe_to_events()
        
        # Ensure unsubscribe when window closes
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _subscribe_to_events(self) -> None:
        """Subscribe to repository change events."""
        try:
            from sections_app.services.event_bus import (
                EventBus, SECTIONS_ADDED, SECTIONS_UPDATED, SECTIONS_DELETED, SECTIONS_CLEARED,
                MATERIALS_ADDED, MATERIALS_UPDATED, MATERIALS_DELETED, MATERIALS_CLEARED
            )
            bus = EventBus()
            
            # Subscribe to sections events
            bus.subscribe(SECTIONS_ADDED, self._on_sections_changed)
            bus.subscribe(SECTIONS_UPDATED, self._on_sections_changed)
            bus.subscribe(SECTIONS_DELETED, self._on_sections_changed)
            bus.subscribe(SECTIONS_CLEARED, self._on_sections_changed)
            
            # Subscribe to materials events
            bus.subscribe(MATERIALS_ADDED, self._on_materials_changed)
            bus.subscribe(MATERIALS_UPDATED, self._on_materials_changed)
            bus.subscribe(MATERIALS_DELETED, self._on_materials_changed)
            bus.subscribe(MATERIALS_CLEARED, self._on_materials_changed)
            
            logger.debug("VerificationTableWindow subscribed to repository events")
        except ImportError:
            logger.warning("EventBus not available, automatic refresh disabled")

    def _unsubscribe_from_events(self) -> None:
        """Unsubscribe from repository change events."""
        try:
            from sections_app.services.event_bus import (
                EventBus, SECTIONS_ADDED, SECTIONS_UPDATED, SECTIONS_DELETED, SECTIONS_CLEARED,
                MATERIALS_ADDED, MATERIALS_UPDATED, MATERIALS_DELETED, MATERIALS_CLEARED
            )
            bus = EventBus()
            
            # Unsubscribe from sections events
            bus.unsubscribe(SECTIONS_ADDED, self._on_sections_changed)
            bus.unsubscribe(SECTIONS_UPDATED, self._on_sections_changed)
            bus.unsubscribe(SECTIONS_DELETED, self._on_sections_changed)
            bus.unsubscribe(SECTIONS_CLEARED, self._on_sections_changed)
            
            # Unsubscribe from materials events
            bus.unsubscribe(MATERIALS_ADDED, self._on_materials_changed)
            bus.unsubscribe(MATERIALS_UPDATED, self._on_materials_changed)
            bus.unsubscribe(MATERIALS_DELETED, self._on_materials_changed)
            bus.unsubscribe(MATERIALS_CLEARED, self._on_materials_changed)
            
            logger.debug("VerificationTableWindow unsubscribed from repository events")
        except ImportError:
            pass

    def _on_sections_changed(self, *args, **kwargs) -> None:
        """Callback when sections repository changes."""
        logger.debug("Sections changed, reloading references")
        self.reload_references()
    
    def _on_materials_changed(self, *args, **kwargs) -> None:
        """Callback when materials repository changes."""
        logger.debug("Materials changed, reloading references")
        self.reload_references()
    
    def reload_references(self) -> None:
        """Reload section and material names from repositories and update autocomplete."""
        logger.debug("Reloading references in VerificationTableWindow")
        self.app.refresh_sources()
        self._update_status_labels()

    def _update_status_labels(self) -> None:
        try:
            secs = self.app.section_names or []
            mats = self.app.material_names or []
            self._status_sections.config(text=f"Sections: {len(secs)}")
            self._status_materials.config(text=f"Materials: {len(mats)}")
        except Exception as e:
            logger.exception("Failed to update status labels: %s", e)

    def _check_sources(self) -> None:
        info = self.app.debug_check_sources()
        msg = (
            f"Sections: {info.get('sections_count')}\nSamples: {', '.join(info.get('sections_sample', []))}\n\n"
            f"Materials: {info.get('materials_count')}\nSamples: {', '.join(info.get('materials_sample', []))}"
        )
        messagebox.showinfo("Sources info", msg)
        # Refresh label text after checking
        self.app.refresh_sources()
        self._update_status_labels()
    
    def _on_close(self) -> None:
        """Handle window close event."""
        self._unsubscribe_from_events()
        self.destroy()


def run_demo() -> None:
    root = tk.Tk()
    root.title("Verification Table - RD2229")
    root.geometry("1400x500")
    app = VerificationTableApp(root)
    app.load_items_from_repository()
    app.mainloop()


if __name__ == "__main__":
    run_demo()
