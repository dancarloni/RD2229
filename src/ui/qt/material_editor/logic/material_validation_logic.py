"""
MaterialValidationLogic — validazione soft dei materiali per tipologia

Fornisce funzioni per determinare se un materiale è "completo" per la
sua tipologia e per restituire campi mancanti/warnings. Questa validazione
è soft: segnala i problemi ma non blocca il salvataggio.
"""
from typing import Dict, Any, List

# Mappa di campi obbligatori per tipologia. Estendere secondo necessità.
REQUIRED_FIELDS_BY_TYPE: Dict[str, List[str]] = {
    'Calcestruzzi': ['codice', 'descrizione', 'f_ck', 'E', 'rho'],
    'Acciai': ['codice', 'descrizione', 'f_yk', 'E', 'rho'],
    'Legno': ['codice', 'descrizione', 'f_m', 'E'],
    'Muratura': ['codice', 'descrizione', 'f_b'],
    'Compositi': ['codice', 'descrizione'],
    'Terreni': ['codice', 'descrizione', 'rho', 'E'],
    'Generic': ['codice', 'descrizione']
}


def _has_value(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str) and v.strip() == '':
        return False
    return True


def get_required_fields(tipo: str) -> List[str]:
    if not tipo:
        return REQUIRED_FIELDS_BY_TYPE['Generic']
    # try exact match, then case-insensitive match
    if tipo in REQUIRED_FIELDS_BY_TYPE:
        return REQUIRED_FIELDS_BY_TYPE[tipo]
    for k in REQUIRED_FIELDS_BY_TYPE:
        if k.lower() == tipo.lower():
            return REQUIRED_FIELDS_BY_TYPE[k]
    return REQUIRED_FIELDS_BY_TYPE['Generic']


def validate(material: Dict[str, Any]) -> Dict[str, Any]:
    """Valida il materiale e ritorna un dict con:
    - is_complete: bool
    - missing: list[str]
    - warnings: list[str]
    """
    tipo = material.get('tipo') or material.get('norma') or 'Generic'
    required = get_required_fields(tipo)
    missing = []
    for field in required:
        if not _has_value(material.get(field)):
            missing.append(field)
    warnings: List[str] = []
    # Esempio: warn se valori numeric sono fuori range (placeholder)
    # if 'f_ck' in material and isinstance(material.get('f_ck'), (int, float)):
    #     if material['f_ck'] <= 0:
    #         warnings.append('f_ck deve essere positivo')

    return {
        'is_complete': len(missing) == 0,
        'missing': missing,
        'warnings': warnings
    }
