"""
code_registry.py

Questo modulo definisce il REGISTRY NORMATIVO del software.

Funzioni e responsabilità del registry:
---------------------------------------
- Mappare le normative disponibili (es. "NTC2018", "EC2", "EC8").
- Collegare ogni normativa ai suoi:
    - parametri numerici (JSON → params/)
    - clausole, paragrafi, limiti normativi (YAML → clauses/)
- Fornire un punto unico per il recupero di:
    - coefficienti di sicurezza gamma_M
    - coefficienti di combinazione ψ
    - limiti di tensione σ_max
    - parametri di duttilità
- Fornire interfacce unificate per le verifiche
  senza imporre logica normativa all'interno dei moduli di calcolo.

STUB S2:
---------------------------------------
- Struttura completa
- Docstring ricca
- TODO per Copilot Plan
- Implementazioni minime

Unità di misura:
---------------------------------------
- Tutti i parametri normativi devono essere coerenti con:
    - lunghezze: cm
    - tensioni: kg/cm^2
    - densità: kg/m^3
    - moduli: kg/cm^2

I file in params/ contengono parametri numerici,
mentre i file in clauses/ contengono testo strutturato
che descrive limiti normativi, articoli, paragrafi,
utili ai report e alla generazione di messaggi di verifica.

"""

from typing import Dict, Any, Optional
import json
import yaml
import os


# ======================================================================
# REGISTRY PER LE NORMATIVE DISPONIBILI
# ======================================================================

CODE_REGISTRY: Dict[str, Dict[str, Any]] = {}
"""
Struttura prevista:

CODE_REGISTRY = {
    "NTC2018": {
        "params": {...},   # parametri numerici caricati da JSON
        "clauses": {...},  # clausole testuali da YAML
    },
    "EC2": {...},
    "EC8": {...},
}

TODO Copilot:
- Validare struttura JSON/YAML in fase di bootstrap.
- Aggiungere logging.
"""


# ======================================================================
# FUNZIONI DI BOOTSTRAP
# ======================================================================

def load_code_params(name: str, path: str) -> Dict[str, Any]:
    """
    Carica i parametri normativi (JSON) per una data normativa.

    TODO:
    - Validare file esistente.
    - Gestire errori JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_code_clauses(name: str, path: str) -> Dict[str, Any]:
    """
    Carica le clausole normative (YAML) per una normativa.

    TODO:
    - Validare file esistente.
    - Gestire errori YAML.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def register_code(
    code_name: str,
    params: Dict[str, Any],
    clauses: Dict[str, Any]
) -> None:
    """
    Registra una normativa nel registry.

    TODO:
    - Validazioni su parametri e clausole.
    """
    CODE_REGISTRY[code_name] = {
        "params": params,
        "clauses": clauses,
    }


def get_code(code_name: str) -> Optional[Dict[str, Any]]:
    """
    Recupera una normativa dal registry.
    """
    return CODE_REGISTRY.get(code_name)



# ======================================================================
# FUNZIONE DI BOOT GENERALE (stub)
# ======================================================================

def bootstrap_codes(base_path: str) -> None:
    """
    Carica tutte le normative disponibili leggendo le directory:

        base_path/params/
        base_path/clauses/

    Esempio struttura file:
    - params/NTC2018.json
    - clauses/NTC2018.yml

    TODO Copilot:
    - Iterare sui file in params/.
    - Cercare file corrispondente in clauses/.
    - Chiamare register_code() per ogni normativa.
    - Logging di caricamento.
    """
    params_dir = os.path.join(base_path, "params")
    clauses_dir = os.path.join(base_path, "clauses")

    # TODO: implementazione.
    pass



# ======================================================================
# FINE FILE code_registry.py
# ======================================================================
