"""
material_sources.py - Gestione delle fonti normative per i materiali strutturali.

Questo modulo implementa:
1. Il modello `MaterialSource` per rappresentare una fonte normativa
2. La classe `MaterialSourceLibrary` per gestire l'elenco delle fonti
3. La funzione `get_default_values_for_source()` per calcolare i valori predefiniti

AVVERTENZA IMPORTANTE:
======================
I valori e le formule implementati in questo modulo sono da considerarsi
DI ESEMPIO e devono essere VALIDATI da un ingegnere strutturista qualificato
prima di essere utilizzati per calcoli reali di progettazione o verifica.

Le formule sono state ricavate da fonti pubbliche e dalla documentazione
delle norme tecniche italiane, ma potrebbero contenere errori o semplificazioni.

Unità di misura: tutte le tensioni/pressioni in kg/cm² (storico),
                 geometrie in cm, moduli in kg/cm².

Autore: Assistente AI
Data: 2026-02
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# MODELLO FONTE NORMATIVA
# =============================================================================

class CalculationMethod(str, Enum):
    """Metodo di calcolo/verifica associato alla fonte."""
    TENSIONI_AMMISSIBILI = "TA"      # Metodo alle tensioni ammissibili
    STATI_LIMITE = "SL"              # Metodo agli stati limite
    SEMIPROBABILISTICO = "SP"        # Metodo semiprobabilistico
    SPERIMENTALE = "SPER"            # Dati da prove di laboratorio


@dataclass
class MaterialSource:
    """Rappresenta una fonte normativa per i materiali strutturali.

    Attributi:
        id: Identificativo univoco (es. "RD2229", "NTC2018")
        name: Nome descrittivo leggibile (es. "RD 2229/1939")
        description: Descrizione estesa della norma
        year: Anno di riferimento della norma
        calculation_method: Metodo di calcolo (TA, SL, SP, SPER)
        is_historical: True se norma storica (non più in vigore)
        is_user_defined: True se fonte creata dall'utente
        reference: Riferimento normativo completo (es. "Regio Decreto 16/11/1939 n. 2229")
        notes: Note aggiuntive
    """
    id: str
    name: str
    description: str = ""
    year: Optional[int] = None
    calculation_method: CalculationMethod = CalculationMethod.TENSIONI_AMMISSIBILI
    is_historical: bool = False
    is_user_defined: bool = False
    reference: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        """Serializza in dizionario per JSON."""
        d = asdict(self)
        d["calculation_method"] = self.calculation_method.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "MaterialSource":
        """Deserializza da dizionario."""
        method = d.get("calculation_method", "TA")
        if isinstance(method, str):
            try:
                method = CalculationMethod(method)
            except ValueError:
                method = CalculationMethod.TENSIONI_AMMISSIBILI
        return MaterialSource(
            id=d.get("id", str(uuid4())),
            name=d.get("name", ""),
            description=d.get("description", ""),
            year=d.get("year"),
            calculation_method=method,
            is_historical=d.get("is_historical", False),
            is_user_defined=d.get("is_user_defined", False),
            reference=d.get("reference", ""),
            notes=d.get("notes", ""),
        )


# =============================================================================
# FONTI PREDEFINITE
# =============================================================================

def _get_default_sources() -> List[MaterialSource]:
    """Restituisce l'elenco delle fonti normative predefinite."""
    return [
        MaterialSource(
            id="RD2229",
            name="RD 2229/1939",
            description="Regio Decreto 16 novembre 1939 - Norme per l'esecuzione delle opere in conglomerato cementizio",
            year=1939,
            calculation_method=CalculationMethod.TENSIONI_AMMISSIBILI,
            is_historical=True,
            reference="R.D. 16/11/1939 n. 2229",
            notes="Prima norma italiana organica sul cemento armato. Metodo n (tensioni ammissibili)."
        ),
        MaterialSource(
            id="DM72",
            name="DM 30/05/1972",
            description="Decreto Ministeriale 30 maggio 1972 - Norme tecniche per le costruzioni in cemento armato",
            year=1972,
            calculation_method=CalculationMethod.TENSIONI_AMMISSIBILI,
            is_historical=True,
            reference="D.M. 30/05/1972",
            notes="Aggiornamento delle norme RD 2229/39. Ancora tensioni ammissibili."
        ),
        MaterialSource(
            id="DM92",
            name="DM 14/02/1992",
            description="Decreto Ministeriale 14 febbraio 1992 - Norme tecniche per le costruzioni in zona sismica",
            year=1992,
            calculation_method=CalculationMethod.TENSIONI_AMMISSIBILI,
            is_historical=True,
            reference="D.M. 14/02/1992",
            notes="Introduce requisiti antisismici. Metodo TA con coefficienti sismici."
        ),
        MaterialSource(
            id="DM96",
            name="DM 09/01/1996",
            description="Decreto Ministeriale 9 gennaio 1996 - Norme tecniche per il calcolo, l'esecuzione ed il collaudo delle strutture in cemento armato",
            year=1996,
            calculation_method=CalculationMethod.SEMIPROBABILISTICO,
            is_historical=True,
            reference="D.M. 09/01/1996",
            notes="Introduce il metodo semiprobabilistico agli stati limite come alternativa alle TA."
        ),
        MaterialSource(
            id="OPCM3274",
            name="OPCM 3274/2003",
            description="Ordinanza PCM 20 marzo 2003 n. 3274 - Primi elementi in materia di criteri generali per la classificazione sismica",
            year=2003,
            calculation_method=CalculationMethod.STATI_LIMITE,
            is_historical=True,
            reference="O.P.C.M. 20/03/2003 n. 3274",
            notes="Introduce nuova classificazione sismica e metodo agli stati limite."
        ),
        MaterialSource(
            id="NTC2008",
            name="NTC 2008",
            description="Norme Tecniche per le Costruzioni - DM 14 gennaio 2008",
            year=2008,
            calculation_method=CalculationMethod.STATI_LIMITE,
            is_historical=True,
            reference="D.M. 14/01/2008",
            notes="Prima versione delle NTC. Metodo SL obbligatorio, TA ammesse solo per strutture semplici."
        ),
        MaterialSource(
            id="NTC2018",
            name="NTC 2018",
            description="Norme Tecniche per le Costruzioni - DM 17 gennaio 2018",
            year=2018,
            calculation_method=CalculationMethod.STATI_LIMITE,
            is_historical=False,
            reference="D.M. 17/01/2018",
            notes="Norma vigente. Metodo agli stati limite. Circolare applicativa n. 7/2019."
        ),
        MaterialSource(
            id="LAB_TEST",
            name="Prove di laboratorio",
            description="Valori derivati da prove sperimentali di laboratorio",
            year=None,
            calculation_method=CalculationMethod.SPERIMENTALE,
            is_historical=False,
            is_user_defined=False,
            reference="Certificati di prova",
            notes="Utilizzare per materiali con caratteristiche determinate sperimentalmente."
        ),
        MaterialSource(
            id="CUSTOM",
            name="Fonte libera",
            description="Fonte definita dall'utente",
            year=None,
            calculation_method=CalculationMethod.TENSIONI_AMMISSIBILI,
            is_historical=False,
            is_user_defined=True,
            reference="",
            notes="Fonte personalizzabile. Inserire manualmente i valori dei parametri."
        ),
    ]


# =============================================================================
# LIBRERIA FONTI
# =============================================================================

class MaterialSourceLibrary:
    """Gestisce l'elenco delle fonti normative.

    Carica/salva le fonti da/su file JSON, permettendo all'utente
    di aggiungere, modificare o eliminare fonti personalizzate.
    """

    DEFAULT_FILE = "data/material_sources.json"

    def __init__(self, path: str | Path | None = None):
        self._file_path = Path(path or self.DEFAULT_FILE)
        self._sources: List[MaterialSource] = []
        self._load_or_create_defaults()

    def _load_or_create_defaults(self) -> None:
        """Carica le fonti da file o crea i default se non esiste."""
        if self._file_path.exists():
            try:
                self.load_from_file()
                return
            except Exception:
                logger.exception("Errore caricamento fonti da %s, ricreo default", self._file_path)

        # Crea fonti predefinite
        self._sources = _get_default_sources()
        self.save_to_file()
        logger.info("Create fonti predefinite in %s", self._file_path)

    def load_from_file(self) -> None:
        """Carica le fonti dal file JSON."""
        self._sources.clear()
        with self._file_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, list):
            for item in raw:
                try:
                    self._sources.append(MaterialSource.from_dict(item))
                except Exception:
                    logger.exception("Errore parsing fonte: %s", item)

    def save_to_file(self) -> None:
        """Salva le fonti su file JSON."""
        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._file_path.with_suffix(".json.tmp")
            with tmp.open("w", encoding="utf-8") as f:
                json.dump([s.to_dict() for s in self._sources], f, indent=2, ensure_ascii=False)
            tmp.replace(self._file_path)
        except Exception:
            logger.exception("Errore salvataggio fonti in %s", self._file_path)

    def get_all(self) -> List[MaterialSource]:
        """Restituisce tutte le fonti."""
        return list(self._sources)

    def get_by_id(self, source_id: str) -> Optional[MaterialSource]:
        """Trova una fonte per ID."""
        for s in self._sources:
            if s.id == source_id:
                return s
        return None

    def add(self, source: MaterialSource) -> None:
        """Aggiunge o aggiorna una fonte."""
        existing = self.get_by_id(source.id)
        if existing:
            self._sources = [s for s in self._sources if s.id != source.id]
        self._sources.append(source)
        self.save_to_file()

    def delete(self, source_id: str) -> bool:
        """Elimina una fonte. Restituisce True se eliminata."""
        before = len(self._sources)
        self._sources = [s for s in self._sources if s.id != source_id]
        if len(self._sources) < before:
            self.save_to_file()
            return True
        return False

    def get_source_names_for_combo(self) -> List[str]:
        """Restituisce lista di nomi per ComboBox UI."""
        return [s.name for s in self._sources]

    def get_source_ids(self) -> List[str]:
        """Restituisce lista di ID."""
        return [s.id for s in self._sources]

    def find_by_name(self, name: str) -> Optional[MaterialSource]:
        """Trova una fonte per nome."""
        for s in self._sources:
            if s.name == name:
                return s
        return None


# =============================================================================
# LOGICA DI CALCOLO PER FONTE
# =============================================================================
#
# AVVERTENZA: Le formule seguenti sono state ricavate dalla documentazione
# pubblica delle norme tecniche italiane. DEVONO essere verificate da un
# professionista prima dell'uso in progettazione reale.
#
# TODO: Alcune formule sono semplificate o parziali. Verificare completezza.
#

def _compute_rd2229_concrete(fck: float, cement_type: str = "normal") -> Dict[str, Any]:
    """
    Calcola i parametri del calcestruzzo secondo RD 2229/1939.

    NOTA: fck qui rappresenta σ_c,28 (resistenza cubica a 28 gg) in kg/cm².

    Args:
        fck: Resistenza cubica a 28 giorni [kg/cm²]
        cement_type: Tipo cemento ("normal", "high", "aluminous", "slow")

    Returns:
        Dizionario con i valori calcolati.
    """
    # Tensioni ammissibili secondo RD 2229/39
    # Riferimento: Art. 10-11 del RD 2229/1939
    if cement_type in ("high", "aluminous"):
        sigma_c_simple = 45.0  # sez. semplicemente compresse
        sigma_c_flex = 50.0    # sez. inflesse/presso-inflesse
        tau_c0 = 6.0           # taglio di servizio
        tau_c1 = 16.0          # taglio massimo
        n = 8.0 if cement_type == "high" else 6.0  # coeff. omogeneizzazione
        Ec_conv = 300000.0 if cement_type == "high" else 330000.0
    else:  # normal, slow
        sigma_c_simple = 35.0
        sigma_c_flex = 40.0
        tau_c0 = 4.0
        tau_c1 = 14.0
        n = 10.0
        Ec_conv = 250000.0 if cement_type == "normal" else 200000.0

    # Per conglomerati speciali (σ_c28 > 225 kg/cm²)
    # σ_c = 75 + (σ_c28 - 225) / 9
    if fck > 225:
        sigma_c_flex = 75.0 + (fck - 225.0) / 9.0
        sigma_c_simple = sigma_c_flex - 10.0  # approssimazione

    # Modulo elastico calcolato: E_c = 550000 * σ_c28 / (σ_c28 + 200)
    Ec_calc = 550000.0 * fck / (fck + 200.0)

    return {
        "fcd": sigma_c_simple,       # σ_c ammissibile (semplice)
        "fcd_flex": sigma_c_flex,    # σ_c ammissibile (inflessa)
        "tau_c0": tau_c0,
        "tau_c1": tau_c1,
        "n": n,
        "Ec": Ec_conv,
        "Ec_calc": Ec_calc,
        "gamma_c": round(fck / sigma_c_simple, 2) if sigma_c_simple > 0 else 3.0,
        "calculation_notes": "Valori da RD 2229/1939. Verificare con il testo normativo originale."
    }


def _compute_rd2229_steel(fyk: float, steel_type: str = "dolce") -> Dict[str, Any]:
    """
    Calcola i parametri dell'acciaio secondo RD 2229/1939.

    Args:
        fyk: Tensione di snervamento [kg/cm²]
        steel_type: Tipo acciaio ("dolce", "semiduro", "duro")

    Returns:
        Dizionario con i valori calcolati.
    """
    # Tensioni ammissibili secondo RD 2229/39
    # σ_s,amm ≤ fyk/2 (non deve superare metà del carico di snervamento)
    if steel_type == "dolce":
        sigma_s = 1400.0
    elif steel_type == "semiduro":
        sigma_s = 1800.0  # 1600 per sez. T, 1800 per sez. rettangolari
    else:  # duro
        sigma_s = 2000.0  # 1800 per sez. T, 2000 per sez. rettangolari

    # Modulo elastico acciaio (costante storica)
    Es = 2100000.0

    return {
        "fyd": sigma_s,
        "Es": Es,
        "gamma_s": 2.0,  # fyk/fyd = 2 (coefficiente di sicurezza storico)
        "calculation_notes": "Valori da RD 2229/1939. σ_s ≤ fyk/2."
    }


def _compute_ntc2018_concrete(fck: float) -> Dict[str, Any]:
    """
    Calcola i parametri del calcestruzzo secondo NTC 2018.

    NOTA: fck è la resistenza caratteristica CILINDRICA [MPa o kg/cm²].
    Per conversione da cubica: fck_cil ≈ 0.83 * Rck

    Args:
        fck: Resistenza caratteristica cilindrica [kg/cm²]

    Returns:
        Dizionario con i valori calcolati.

    TODO: Verificare formule con NTC 2018 e Circolare n. 7/2019.
    """
    # Conversione approssimativa se il valore sembra essere cubico (> 150 kg/cm²)
    # In realtà NTC2018 usa MPa, qui manteniamo kg/cm² per coerenza col progetto
    # 1 MPa = 10.197 kg/cm² ≈ 10 kg/cm²

    # fcd = α_cc * fck / γ_c  (NTC 2018: α_cc = 0.85, γ_c = 1.5)
    alpha_cc = 0.85
    gamma_c = 1.5
    fcd = alpha_cc * fck / gamma_c

    # Modulo elastico: Ecm = 22000 * (fcm/10)^0.3 [MPa]
    # Conversione approssimativa per kg/cm²:
    # Se fck in kg/cm², fcm ≈ fck + 80 (approssimazione)
    fcm = fck + 80.0  # fcm = fck + 8 MPa ≈ fck + 80 kg/cm²
    # Ecm ≈ 220000 * (fcm/100)^0.3 [kg/cm²]
    Ecm = 220000.0 * ((fcm / 100.0) ** 0.3)

    # Resistenza a trazione: fctm = 0.30 * fck^(2/3) [MPa]
    # Conversione per kg/cm²:
    fctm = 0.30 * (fck ** (2.0/3.0)) * 0.1  # fattore 0.1 per unità

    return {
        "fcd": round(fcd, 1),
        "fctm": round(fctm, 2),
        "Ec": round(Ecm, 0),
        "gamma_c": gamma_c,
        "n": 15.0,  # valore tipico NTC
        "calculation_notes": "TODO: Valori da NTC 2018 - VERIFICARE con testo normativo. "
                            "Le unità potrebbero richiedere conversione MPa ↔ kg/cm²."
    }


def _compute_ntc2018_steel(fyk: float) -> Dict[str, Any]:
    """
    Calcola i parametri dell'acciaio secondo NTC 2018.

    Args:
        fyk: Tensione caratteristica di snervamento [kg/cm²]

    Returns:
        Dizionario con i valori calcolati.
    """
    # fyd = fyk / γ_s  (NTC 2018: γ_s = 1.15)
    gamma_s = 1.15
    fyd = fyk / gamma_s

    # Modulo elastico acciaio
    Es = 2100000.0  # 210000 MPa = 2100000 kg/cm²

    return {
        "fyd": round(fyd, 1),
        "Es": Es,
        "gamma_s": gamma_s,
        "calculation_notes": "Valori da NTC 2018. fyd = fyk/γ_s con γ_s = 1.15."
    }


def _compute_dm96_concrete(fck: float) -> Dict[str, Any]:
    """
    Calcola i parametri del calcestruzzo secondo DM 09/01/1996.

    TODO: Verificare formule con testo DM 96.
    """
    # DM96 introduce il metodo semiprobabilistico come alternativa
    # Coefficienti parziali: γ_c = 1.6 (combinazioni fondamentali)
    gamma_c = 1.6
    fcd = 0.85 * fck / gamma_c

    # Modulo elastico (formula simile a EC2 pre-NTC)
    Ecm = 9500.0 * ((fck + 80.0) ** (1.0/3.0))

    return {
        "fcd": round(fcd, 1),
        "Ec": round(Ecm, 0),
        "gamma_c": gamma_c,
        "n": 15.0,
        "calculation_notes": "TODO: Valori da DM 09/01/1996 - VERIFICARE con testo normativo."
    }


def _compute_dm96_steel(fyk: float) -> Dict[str, Any]:
    """
    Calcola i parametri dell'acciaio secondo DM 09/01/1996.
    """
    gamma_s = 1.15
    fyd = fyk / gamma_s
    Es = 2100000.0

    return {
        "fyd": round(fyd, 1),
        "Es": Es,
        "gamma_s": gamma_s,
        "calculation_notes": "TODO: Valori da DM 09/01/1996 - VERIFICARE con testo normativo."
    }


# =============================================================================
# FUNZIONE PRINCIPALE DI CALCOLO
# =============================================================================

def get_default_values_for_source(
    source_id: str,
    material_type: str,
    base_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calcola i valori predefiniti per un materiale in base alla fonte normativa.

    AVVERTENZA: I valori restituiti sono da considerarsi DI ESEMPIO.
    Devono essere VERIFICATI da un ingegnere strutturista prima dell'uso
    in calcoli reali di progettazione o verifica.

    Args:
        source_id: ID della fonte normativa (es. "RD2229", "NTC2018")
        material_type: Tipo di materiale ("concrete", "steel", "stirrup_steel")
        base_params: Parametri di input, tipicamente:
            - Per calcestruzzo: {"fck": <valore>, "cement_type": "normal"|"high"|...}
            - Per acciaio: {"fyk": <valore>, "steel_type": "dolce"|"semiduro"|"duro"}

    Returns:
        Dizionario con i valori calcolati. Chiavi tipiche:
        - Calcestruzzo: fcd, tau_c0, tau_c1, n, Ec, gamma_c, fctm, ...
        - Acciaio: fyd, Es, gamma_s, ...
        - Sempre presente: "calculation_notes" con avvertenze
    """
    result: Dict[str, Any] = {
        "source_id": source_id,
        "calculation_notes": ""
    }

    # Estrai parametri di input
    fck = base_params.get("fck") or base_params.get("sigma_c28", 0)
    fyk = base_params.get("fyk") or base_params.get("sigma_sn", 0)
    cement_type = base_params.get("cement_type", "normal")
    steel_type = base_params.get("steel_type", "dolce")

    # Seleziona la logica di calcolo in base alla fonte
    if source_id == "RD2229":
        if material_type == "concrete":
            if fck > 0:
                result.update(_compute_rd2229_concrete(fck, cement_type))
        elif material_type in ("steel", "stirrup_steel"):
            if fyk > 0:
                result.update(_compute_rd2229_steel(fyk, steel_type))

    elif source_id == "NTC2018":
        if material_type == "concrete":
            if fck > 0:
                result.update(_compute_ntc2018_concrete(fck))
        elif material_type in ("steel", "stirrup_steel"):
            if fyk > 0:
                result.update(_compute_ntc2018_steel(fyk))

    elif source_id in ("DM96", "DM92"):
        if material_type == "concrete":
            if fck > 0:
                result.update(_compute_dm96_concrete(fck))
        elif material_type in ("steel", "stirrup_steel"):
            if fyk > 0:
                result.update(_compute_dm96_steel(fyk))

    elif source_id == "NTC2008":
        # NTC2008 simile a NTC2018 con piccole differenze
        if material_type == "concrete":
            if fck > 0:
                vals = _compute_ntc2018_concrete(fck)
                vals["calculation_notes"] = "TODO: Valori da NTC 2008 - VERIFICARE. Simili a NTC 2018."
                result.update(vals)
        elif material_type in ("steel", "stirrup_steel"):
            if fyk > 0:
                vals = _compute_ntc2018_steel(fyk)
                vals["calculation_notes"] = "Valori da NTC 2008, simili a NTC 2018."
                result.update(vals)

    elif source_id == "OPCM3274":
        # OPCM3274 introduce SL ma con coefficienti leggermente diversi
        # TODO: Implementare formule specifiche OPCM3274
        result["calculation_notes"] = "TODO: Implementare formule specifiche OPCM 3274/2003."

    elif source_id == "DM72":
        # DM72 simile a RD2229 con piccoli aggiornamenti
        if material_type == "concrete":
            if fck > 0:
                vals = _compute_rd2229_concrete(fck, cement_type)
                vals["calculation_notes"] = "Valori da DM 30/05/1972, simili a RD 2229/39."
                result.update(vals)
        elif material_type in ("steel", "stirrup_steel"):
            if fyk > 0:
                vals = _compute_rd2229_steel(fyk, steel_type)
                vals["calculation_notes"] = "Valori da DM 30/05/1972, simili a RD 2229/39."
                result.update(vals)

    elif source_id == "LAB_TEST":
        # Per prove di laboratorio, non calcolare nulla automaticamente
        result["calculation_notes"] = "Fonte sperimentale: inserire manualmente i valori misurati."

    elif source_id == "CUSTOM":
        # Fonte libera: nessun calcolo automatico
        result["calculation_notes"] = "Fonte personalizzata: inserire manualmente tutti i valori."

    else:
        # Fonte sconosciuta
        result["calculation_notes"] = f"Fonte '{source_id}' non riconosciuta. Nessun calcolo automatico disponibile."

    # Aggiungi avvertenza standard
    if result.get("calculation_notes"):
        result["calculation_notes"] += "\n"
    result["calculation_notes"] += (
        "AVVERTENZA: Valori di esempio. Verificare con normativa originale prima dell'uso."
    )

    return result


# =============================================================================
# ISTANZA GLOBALE (per comodità)
# =============================================================================

# Istanza singleton della libreria fonti (lazy loading)
_source_library: Optional[MaterialSourceLibrary] = None


def get_source_library() -> MaterialSourceLibrary:
    """Restituisce l'istanza globale della libreria fonti."""
    global _source_library
    if _source_library is None:
        _source_library = MaterialSourceLibrary()
    return _source_library


def get_all_source_names() -> List[str]:
    """Shortcut per ottenere i nomi delle fonti per UI."""
    return get_source_library().get_source_names_for_combo()


def get_source_by_name(name: str) -> Optional[MaterialSource]:
    """Shortcut per trovare una fonte per nome."""
    return get_source_library().find_by_name(name)


def get_source_by_id(source_id: str) -> Optional[MaterialSource]:
    """Shortcut per trovare una fonte per ID."""
    return get_source_library().get_by_id(source_id)
