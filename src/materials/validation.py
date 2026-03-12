"""Validazione dei materiali strutturali.

Centralizza i controlli di coerenza sui parametri dei materiali:
- Controlli generici (ID, densità, famiglia)
- Controlli per famiglia (calcestruzzo, acciaio, muratura)
- Controlli sui range fisicamente ammissibili
"""

from __future__ import annotations

from .material_model import Material

_FAMIGLIE_VALIDE = {"calcestruzzo", "acciaio", "muratura", "legno"}


class MaterialValidationError(Exception):
    """Errore di validazione dei materiali."""


def validate_material(material: Material) -> list[str]:
    """Valida un materiale e restituisce la lista di errori riscontrati.

    Non solleva eccezioni: restituisce una lista di messaggi di errore.
    Lista vuota = materiale valido.

    Parametri:
        material: Materiale da validare.

    Restituisce:
        Lista di stringhe con gli errori riscontrati.
    """
    errors: list[str] = []

    # --- Controlli generici ---
    if not material.material_id:
        errors.append("material_id mancante.")

    if material.densita_kg_m3 <= 0:
        errors.append("La densità deve essere positiva (kg/m³).")

    if material.famiglia not in _FAMIGLIE_VALIDE:
        errors.append(
            f"Famiglia '{material.famiglia}' non valida. "
            f"Valori ammessi: {', '.join(sorted(_FAMIGLIE_VALIDE))}."
        )

    if material.E < 0:
        errors.append("Il modulo elastico E non può essere negativo.")

    if not (0.0 <= material.nu <= 0.5):
        errors.append(f"Coefficiente di Poisson ν={material.nu:.3f} fuori range [0.0, 0.5].")

    # --- Controlli per famiglia ---
    if material.famiglia == "calcestruzzo":
        errors.extend(_valida_calcestruzzo(material))
    elif material.famiglia == "acciaio":
        errors.extend(_valida_acciaio(material))
    elif material.famiglia == "muratura":
        errors.extend(_valida_muratura(material))
    elif material.famiglia == "legno":
        errors.extend(_valida_legno(material))

    return errors


def _valida_calcestruzzo(material: Material) -> list[str]:
    """Validazione specifica per calcestruzzo."""
    errors: list[str] = []

    # Per NTC2018 (SL) serve f_ck; per TA servono sigma_c28/sigma_c_adm
    ha_sl = material.f_ck > 0
    ha_ta = material.sigma_c28 > 0 or material.sigma_c_adm > 0

    if not ha_sl and not ha_ta:
        errors.append("Calcestruzzo: serve f_ck > 0 (SL) oppure sigma_c28/sigma_c_adm > 0 (TA).")

    if material.gamma_c <= 0:
        errors.append("Calcestruzzo: gamma_c deve essere > 0.")

    if material.alpha_cc <= 0:
        errors.append("Calcestruzzo: alpha_cc deve essere > 0.")

    return errors


def _valida_acciaio(material: Material) -> list[str]:
    """Validazione specifica per acciaio da armatura."""
    errors: list[str] = []

    ha_sl = material.f_yk > 0
    ha_ta = material.sigma_s_adm > 0

    if not ha_sl and not ha_ta:
        errors.append("Acciaio: serve f_yk > 0 (SL) oppure sigma_s_adm > 0 (TA).")

    if material.gamma_s <= 0:
        errors.append("Acciaio: gamma_s deve essere > 0.")

    return errors


def _valida_muratura(material: Material) -> list[str]:
    """Validazione specifica per muratura."""
    errors: list[str] = []

    if material.f_k <= 0:
        errors.append("Muratura: f_k deve essere > 0.")

    if material.f_vk0 < 0:
        errors.append("Muratura: f_vk0 non può essere negativo.")

    if material.gamma_M <= 0:
        errors.append("Muratura: gamma_M deve essere > 0.")

    return errors


def _valida_legno(material: Material) -> list[str]:
    """Validazione specifica per legno strutturale."""
    errors: list[str] = []

    if material.f_mk <= 0:
        errors.append("Legno: f_mk (resistenza a flessione) deve essere > 0.")

    if material.f_c0k <= 0:
        errors.append("Legno: f_c0k (compressione parallela) deve essere > 0.")

    if material.gamma_M <= 0:
        errors.append("Legno: gamma_M deve essere > 0.")

    if material.classe_servizio not in (1, 2, 3):
        errors.append(
            f"Legno: classe_servizio={material.classe_servizio} non valida. "
            "Valori ammessi: 1, 2, 3."
        )

    return errors
