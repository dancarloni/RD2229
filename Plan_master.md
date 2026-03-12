
# PLAN MASTER — Multi‑Block Implementation

## 0. Instructions to the Agent

- Execute the entire plan inside ONE SINGLE session.
- Never start secondary sessions.
- Never request confirmation.
- Use cloud execution only as continuation of the same session.
- Output ONE pull request containing the entire implementation.

##############################################

# PROMPT PER GITHUB COPILOT PLAN / CLAUDE CODE

# PROGETTO DI RISTRUTTURAZIONE COMPLETA (A1)

# + INTRODUZIONE DI TUTTI I MODULI STRUTTURALI

# + STUB S2 ULTRACOMMENTATI

##############################################

OBIETTIVO PRINCIPALE:
Ricostruire completamente il progetto Python esistente riorganizzandolo in una nuova architettura professionale e modulare, con struttura A1 (migrazione totale), introducendo un package `/src/` come radice e distribuendo l’intera logica in sottopacchetti dedicati:

    src/
        legacy/                <-- tutti i file attuali NON modificati
        softw_components/
        calc/
        materials/
        elements/
        codes/
        actions/
        report/
        config/
        tools/
        tests/

La GUI (se e quando sarà presente) NON deve contenere logica di calcolo.
I calcoli vengono incapsulati nei moduli dedicati.
Le unità di misura devono rispettare lo standard definito dall'utente:

- lunghezze in cm
- aree in cm^2
- inerzie in cm^4
- tensioni in kg/cm^2
- densità in kg/m^3

Il progetto deve introdurre:

- calcolo area a taglio (A_sx, A_sy) per TUTTE le sezioni;
- configuratore degli elementi strutturali;
- sistema parametri normativi con pannelli dedicati;
- repository materiali e sezioni;
- routing normative dinamico;
- rendering dei report (JSON, MD, HTML, PDF);
- test automatici;
- template di report in HTML/MD;
- CLI, strumenti, salvataggi e serializzazione;
- file config (units, app, features, numerics);
- logging;
- indice risultati.

TUTTI i nuovi moduli devono essere generati come STUB **S2**:

- estremamente commentati;
- docstring lunghe esplicative;
- TODO marcati chiaramente per Copilot;
- strutture delle classi ben definite;
- esempi di utilizzo;
- design chiaro, estensibile;
- nessuna logica implementativa profonda: solo interfacce e struttura.

##################################################

# FASI CHE IL PIANO DEVE SEGUIRE DURANTE APPLY

##################################################

FASE 0 — Ricognizione del progetto

- Analizza la repo.
- Conferma che tutti i file attuali siano spostati in src/legacy/.
- Verifica che i nuovi package siano integri.

FASE 1 — Creazione cartelle e **init**.py

FASE 2 — Generazione stub dei moduli:

- calc/shear_area_registry.py
- materials/material_model.py
- materials/validation.py
- materials/material_repo.py
- elements/element_model.py
- elements/element_repo.py
- elements/resolve_inputs.py
- codes/code_registry.py
- codes/params/<normativa>.json (esempi)
- codes/clauses/<normativa>.yml (esempi)
- actions/action_repo.py
- report/renderer_md.py
- report/renderer_html.py
- report/renderer_pdf.py
- config/*.yml
- tools/verify_cli.py
- tools/export_results.py
- tests test per calcolo A_s, routing normative, risoluzione input, repo, reporting

FASE 3 — Aggiornamento import per nuova struttura

FASE 4 — Validazione architettura con i test minimi

FASE 5 — Documentazione README e changelog

############################################################

# REGOLE IMPORTANTI

############################################################

- NON modificare il contenuto dei file in legacy/.
- NON introdurre logica nella GUI.
- NON alterare unità di misura definite dall'utente.
- NON effettuare conversioni implicite.
- Tutte le interfacce devono essere chiare e modulari.
- Ogni file deve avere almeno 2–4 TODO mirati.
- Tutte le funzioni devono avere type hint.

############################################################

# RISULTATO ATTESO

############################################################
Una ristrutturazione completa del progetto in cui:

- il codice attuale vive in src/legacy/
- l’architettura nuova è separata, pulita, estensibile
- i moduli sono pronti per successive implementazioni
- la struttura supporta verifiche strutturali, materiali, sezioni, normative
- i report sono pronti per generare output tecnici professionali
- i test sono pronti per pipeline CI
- Continue e Copilot possono completare automaticamente l’implementazione

############################################################

# FINE BLOCCO 1: PROMPT PLAN

############################################################
############################################################

# BLOCCO 2 / 12

# STRUTTURA COMPLETA DELLA NUOVA ARCHITETTURA /src/

# + NOTE DI MIGRAZIONE (A1)

############################################################

Questo blocco definisce:

1. La nuova struttura del progetto secondo OPZIONE A1.
2. Le linee guida di migrazione completa.
3. L'albero delle cartelle così come dovrà comparire nella repo.
4. I file **init**.py richiesti.
5. Le note operative per Continue / Copilot Plan.

============================================================
SEZIONE 1 — STRUTTURA DELLA NUOVA ARCHITETTURA
============================================================

La ristrutturazione A1 prevede:

- Creazione della cartella radice:
        src/

- Spostamento TOTALE degli script esistenti della root in:
        src/legacy/

- Introduzione dei nuovi package modulari:
        src/softw_components/      (ex section_app)
        src/calc/                  (calcoli e registry)
        src/materials/             (materiali)
        src/elements/              (elementi strutturali)
        src/codes/                 (normative + parametri)
        src/actions/               (azioni di verifica)
        src/report/                (renderer e template)
        src/config/                (yaml di configurazione)
        src/tools/                 (CLI, export, utility)
        src/tests/                 (test minimi)

Tutti questi pacchetti saranno popolati nei blocchi successivi.

============================================================
SEZIONE 2 — ALBERO DIRECTORY COMPLETO
============================================================

Il progetto dovrà apparire così dopo la migrazione:

src/
    **init**.py
    legacy/
        **init**.py
        # -> Qui verranno copiati TUTTI i file esistenti dalla root
        #    originaria del progetto, SENZA ALCUNA MODIFICA.
        #    Esempi:
        #       verification_project.py
        #       verification_items.py
        #       historical_materials.py
        #       materials_repository.py
        #       quantities_registry.py
        #       etc.
    softw_components/
        **init**.py
        # -> Moduli estratti da section_app (ora deprecato)
    calc/
        **init**.py
        shear_area_registry.py
        section_registry.py
    materials/
        **init**.py
        material_model.py
        material_repo.py
        validation.py
    elements/
        **init**.py
        element_model.py
        element_repo.py
        resolve_inputs.py
    codes/
        **init**.py
        code_registry.py
        clauses/
            **init**.py
            # file YAML generati nei blocchi successivi
        params/
            **init**.py
            # file JSON generati nei blocchi successivi
    actions/
        **init**.py
        action_repo.py
    report/
        **init**.py
        renderer_md.py
        renderer_html.py
        renderer_pdf.py
        templates/
            **init**.py
            template.html
            template.md
    config/
        **init**.py
        units.yml
        numerics.yml
        app.yml
        features.yml
    tools/
        **init**.py
        verify_cli.py
        export_results.py
    tests/
        **init**.py
        test_shear_area.py
        test_code_routing.py
        test_resolve_inputs.py
        test_reporting.py
        test_material_repo.py
        test_elements_repo.py

============================================================
SEZIONE 3 — LINEE GUIDA DI MIGRAZIONE (A1)
============================================================

1) CREA la directory:
        src/

2) CREA la directory:
        src/legacy/

3) SPOSTA TUTTI i file attuali del progetto (dalla root originaria)
   dentro:
        src/legacy/

   Esempi tipici:
        verification_project.py
        verification_items.py
        verification_items_repository.py
        materials_repository.py
        historical_materials.py
        quantities_registry.py
        sections.json
        materials.json
        requirements*.txt
        qualsiasi altro .py o .json presente nella root

   NB: NON modificare il contenuto dei file legacy.

4) RIMUOVI cartelle di vecchi moduli come section_app
   se presente, dopo aver verificato che tutto è migrato.

5) CREA tutte le nuove cartelle:
        softw_components/
        calc/
        materials/
        elements/
        codes/
        actions/
        report/
        tools/
        tests/
        config/

6) CREA i file **init**.py per ogni cartella.

7) Aggiorna successivamente gli import (fase gestita dal piano Plan).

============================================================
SEZIONE 4 — FILE **init**.py MINIMI
============================================================

Tutti gli **init**.py saranno minimali, es.:

------------------------------------------------------------

File: src/**init**.py
------------------------------------------------------------

"""
Root package of the restructured engineering verification framework.

This folder contains:

- the legacy code (in src/legacy/)
- the new modular architecture
"""

------------------------------------------------------------

File: src/legacy/**init**.py
------------------------------------------------------------

"""
Legacy code — original project modules preserved unchanged.

DO NOT EDIT FILES IN THIS FOLDER.
"""

------------------------------------------------------------

TUTTI GLI ALTRI **init**.py
------------------------------------------------------------

"""
Package initializer.

This module is part of the restructured architecture.
"""

============================================================
SEZIONE 5 — NOTE OPERATIVE PER CONTINUE / COPILOT PLAN
============================================================

- Dopo l’inserimento del BLOCCO 2:
    → il piano può creare fisicamente la struttura
    → può spostare i file legacy
    → può generare gli stub dei moduli nei blocchi successivi

- La generazione del codice vero e proprio avverrà a partire dal BLOCCO 3.

- Nessun file in legacy deve essere modificato.

- Gli stub verranno forniti nei blocchi successivi, uno per categoria.

============================================================
FINE BLOCCO 2 / 12
============================================================

############################################################

# BLOCCO 3 / 12

# PACKAGE: src/calc/

# CONTENUTO

# - shear_area_registry.py

# - section_registry.py

# - **init**.py già definito nel Blocco 2

#

# TUTTI I FILE SONO STUB S2 (ultra commentati e pronti

# per essere espansi da Copilot Plan / Continue)

############################################################

============================================================
FILE: src/calc/shear_area_registry.py
============================================================

"""
shear_area_registry.py

Questo modulo definisce:

- Il registry per il calcolo dell'area a taglio A_sx e A_sy,
  applicato a TUTTE le sezioni del software.
- Un sistema estensibile per aggiungere strategie di calcolo
  specifiche per tipologia di sezione.
- Fallback universale basato su kappa (metodo Timoshenko).
- Interfaccia coerente per integrarsi con il motore
  elementi → risoluzione input → verifiche strutturali.

UNITÀ di MISURA:

- Tutte le lunghezze devono essere considerate in cm.
- Le aree devono essere restituite in cm^2.
- Nessuna conversione implicita deve essere introdotta
  in questo modulo.

NOTE:

- Questo file è uno STUB S2: contiene docstring esaustive,
  TODO chiari, e struttura definita, ma NON implementazione
  di calcoli complessi.
- Continue / Copilot Plan aggiungerà la logica quando richiesto.
"""

from typing import Callable, Dict, Tuple, Optional, Any

# ======================================================================

# TIPOLOGIE DI ALIAS

# ======================================================================

ShearAreaFunction = Callable[[Any], Tuple[float, float]]
"""
Funzione che accetta un oggetto sezione (Section)
e restituisce una tupla:

    (A_sx_cm2: float, A_sy_cm2: float)

Unità: cm^2.
"""

# ======================================================================

# COSTANTI DI BASE (VALORI CLASSICI PER SEZIONI PIENE)

# ======================================================================

DEFAULT_KAPPA: float = 5.0 / 6.0
"""
Valore kappa classico per sezioni rettangolari piene.

Questo valore è da considerarsi fallback.
ATTENZIONE:

- Non va usato come verità normativa.
- È un valore standard della teoria della trave di Timoshenko.
- Il software può sovrascriverlo tramite config o registry.

TODO Copilot:

- Aggiungere supporto configurazione kappa da file YAML
  (es. src/config/app.yml)
"""

CIRCLE_KAPPA: float = 0.9
"""
Valore classico approssimato per sezioni circolari piene.

TODO Copilot:

- Verificare eventuale ref. interna ai parametri materiali.
"""

# ======================================================================

# REGISTRY DELLE STRATEGIE DI CALCOLO

# ======================================================================

SHEAR_AREA_STRATEGIES: Dict[str, ShearAreaFunction] = {}
"""
Mappa:

    shape_id: str → funzione calcolo A_sx, A_sy

shape_id è l'identificatore univoco di una sezione
nel repository delle sezioni (src/sections o src/elements).

TODO Copilot:

- Riempire il registry in fase di bootstrap
  leggendo dal registry delle sezioni.
"""

# ======================================================================

# FUNZIONI DI UTILITÀ PER REGISTRAZIONE

# ======================================================================

def register_shear_area_strategy(shape_id: str, func: ShearAreaFunction) -> None:
    """
    Registra una strategia di calcolo dell'area a taglio.

    Parametri:
    - shape_id: identificatore univoco della sezione.
    - func: funzione che implementa il calcolo.

    TODO Copilot:
    - Validazioni: shape_id non vuoto, func callable.
    """
    SHEAR_AREA_STRATEGIES[shape_id] = func

# ======================================================================

# STRATEGIE STANDARD (rettangolo & cerchio)

# ======================================================================

def _rectangular_shear_area(section: Any) -> Tuple[float, float]:
    """
    Calcolo A_sx e A_sy per una sezione rettangolare piena.

    Formula classica:
        A_s = kappa * A

    TODO Copilot:
    - Recuperare area reale della sezione.
    - Validare tipo 'rectangle'.
    """
    A = getattr(section, "area_cm2", 0.0)
    As = DEFAULT_KAPPA * A
    return (As, As)

def _circular_shear_area(section: Any) -> Tuple[float, float]:
    """
    Calcolo A_sx e A_sy per sezione circolare piena.

    TODO Copilot:
    - Validare tipo 'circle'.
    """
    A = getattr(section, "area_cm2", 0.0)
    As = CIRCLE_KAPPA * A
    return (As, As)

# ======================================================================

# REGISTRAZIONE DELLE STRATEGIE STANDARD

# ======================================================================

# TODO Copilot

# - In futuro questi id saranno letti dal registry sezione

register_shear_area_strategy("rectangle",_rectangular_shear_area)
register_shear_area_strategy("circle",_circular_shear_area)

# ======================================================================

# FUNZIONE GENERALE DI CALCOLO

# ======================================================================

def compute_shear_area(section: Any) -> Tuple[float, float]:
    """
    Calcola (A_sx, A_sy) in cm^2 per una sezione arbitraria.

    Comportamento:
    - Se esiste una strategia registrata → usarla.
    - Se *NON* esiste strategia → fallback a:
            A_sx = kappa_x * A
            A_sy = kappa_y * A
      dove kappa_x / kappa_y sono attributi opzionali della sezione.
      Se assenti → uso DEFAULT_KAPPA.

    ATTENZIONE:
    - Nessun calcolo normativo avviene qui.
    - Nessuna conversione automatica di unità.
    - Il fallback viene applicato a tutte le sezioni
      non coperte dal registry.

    TODO Copilot:
    - Estrarre kappa_x e kappa_y dalla sezione,
      con fallback DEFAULT_KAPPA.
    - Loggare strategia usata.
    - Integrare con config/numerics.yml se presente.
    """
    shape_id: Optional[str] = getattr(section, "shape_id", None)

    if shape_id in SHEAR_AREA_STRATEGIES:
        func = SHEAR_AREA_STRATEGIES[shape_id]
        return func(section)

    # --- Fallback universale ---
    A = getattr(section, "area_cm2", 0.0)
    kappa_x = getattr(section, "kappa_x", DEFAULT_KAPPA)
    kappa_y = getattr(section, "kappa_y", DEFAULT_KAPPA)

    return (kappa_x * A, kappa_y * A)

# ======================================================================

# FINE FILE

# ======================================================================

============================================================
FILE: src/calc/section_registry.py
============================================================

"""
section_registry.py

Questo modulo gestisce il registry delle sezioni geometriche
(e.g. rettangolo, cerchio, profili vari). Non contiene calcoli,
ma memorizza info di base utili nelle fasi successive.

Utilizzi:

- Copilot Plan potrà popolare automaticamente il registry
  leggendo da un file JSON/CSV (es. sections.json in legacy).
- Il registry faciliterà:
  - selezione sezione nella configurazione elementi
  - reperimento area, inerzia, parametri aggiuntivi
  - collegamento con shear_area_registry

Questo file è uno STUB S2:

- molto commentato
- nessuna implementazione reale

UNITÀ DI MISURA:

- Tutti i valori geometrici memorizzati devono rispettare:
    lunghezze: cm
    aree: cm^2
    inerzie: cm^4
"""

from typing import Dict, Any, Optional

# ======================================================================

# REGISTRY DELLE SEZIONI

# ======================================================================

SECTION_REGISTRY: Dict[str, Any] = {}
"""
Mappa:

    shape_id: str  ->  section_metadata: Dict[str, Any]

La struttura interna section_metadata è a discrezione del progetto:
tipicamente:
{
    "id": "rectangle",
    "description": "...",
    "parameters": {...},
    "area_cm2": float,
    "inertia_cm4": {...},
    "kappa_x": float,
    "kappa_y": float,
    ...
}

TODO Copilot:

- Definire struttura finale leggendo sections.json in legacy.
- Aggiungere validazioni.
"""

# ======================================================================

# FUNZIONI DI REGISTRAZIONE E RECUPERO

# ======================================================================

def register_section(shape_id: str, metadata: Dict[str, Any]) -> None:
    """
    Registra una sezione nel registry.

    TODO:
    - Validare shape_id non vuoto
    - Validare metadata conforme al progetto
    - Aggiungere logging
    """
    SECTION_REGISTRY[shape_id] = metadata

def get_section_metadata(shape_id: str) -> Optional[Dict[str, Any]]:
    """
    Restituisce il metadata associato alla sezione.

    TODO:
    - Gestire eccezioni o shape non trovata
    """
    return SECTION_REGISTRY.get(shape_id)

# ======================================================================

# FUNZIONE DI BOOTSTRAP (stub)

# ======================================================================

def load_sections_from_legacy() -> None:
    """
    Carica le sezioni dal file legacy (ad es. sections.json
    nella cartella src/legacy/).

    TODO Copilot:
    - Leggere src/legacy/sections.json
    - Popolare SECTION_REGISTRY
    - Collegare shape_id al shear_area_registry
    """
    pass

# ======================================================================

# FINE FILE

# ======================================================================

############################################################

# FINE BLOCCO 3 / 12

############################################################
############################################################

# BLOCCO 4 / 12

# PACKAGE: src/materials/

#

# Contenuto

# - material_model.py

# - validation.py

# - material_repo.py

#

# Tutti i file sono STUB S2

# - Estremamente commentati

# - Docstring lunghe

# - Struttura chiara e pronta per espansione con Copilot Plan

############################################################

============================================================
FILE: src/materials/material_model.py
============================================================

"""
material_model.py

Questo modulo definisce il modello dei materiali utilizzati nel
framework di verifica strutturale. È un componente fondamentale
per la gestione di:

- Resistenze caratteristiche (calcestruzzo, acciaio, muratura).
- Moduli elastici.
- Coefficienti parziali di sicurezza.
- Densità (unità in kg/m^3).
- Parametri normativi (collegamento con il package `codes`).
- Parametri storici/legacy (collegamento con src/legacy/historical_materials).

UNITÀ DI MISURA:

- Resistenze (f_ck, f_yk) → kg/cm^2
- Moduli elastici → kg/cm^2
- Densità → kg/m^3

OBIETTIVI DEL MODELLO:

- Rappresentare in modo coerente i materiali.
- Essere serializzabile JSON.
- Essere pronto per la validazione via validation.py.
- Essere integrato nel repo materiali via material_repo.py.

NOTA:
Questo file è uno STUB S2: contiene struttura e TODO ma non logica.

"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class Material:
    """
    Modello di un materiale.

    Attributi fondamentali:
    - material_id: identificatore univoco del materiale.
    - description: descrizione testuale.
    - family: categoria (es. "cls", "steel", "masonry").
    - density_kg_m3: densità (kg/m^3).
    - params: dizionario parametri, tipicamente:
        { "fck": ..., "fyk": ..., "E": ..., ... }

    TODO Copilot:
    - Aggiungere parametri opzionali come gamma_M.
    - Aggiungere metodo to_json() se richiesto dal progetto.
    """

    material_id: str
    description: str
    family: str
    density_kg_m3: float
    params: Dict[str, float] = field(default_factory=dict)

    def get_param(self, name: str) -> Optional[float]:
        """
        Restituisce un parametro del materiale, oppure None se mancante.

        TODO Copilot:
        - Validazione su nome parametro.
        - Logging esteso.
        """
        return self.params.get(name)

# ======================================================================

# FINE FILE material_model.py

# ======================================================================

============================================================
FILE: src/materials/validation.py
============================================================

"""
validation.py

Modulo dedicato alla validazione dei materiali.

Questo modulo centralizza:

- Controlli su densità (valori positivi).
- Controlli su parametri (fck, fyk, E).
- Controlli logici (es. una muratura non deve avere fyk).
- Controlli normativi (da introdurre in blocchi successivi
  tramite il package `codes`).

NOTA:
Questo è uno STUB S2: struttura completa, TODO attivi, niente logica.

"""

from typing import List
from .material_model import Material

class MaterialValidationError(Exception):
    """Errore di validazione dei materiali."""
    pass

def validate_material(material: Material) -> List[str]:
    """
    Valida un materiale e restituisce la lista di errori riscontrati.

    Comportamenti previsti:
    - Nessuna eccezione (eccetto errori interni)
    - Ritorno di una lista di messaggi testuali

    TODO Copilot:
    - Implementare controlli sulle unità di misura.
    - Verificare che E, fck, fyk siano coerenti con family.
    - Integrare controlli con normative tramite codes/code_registry.

    """
    errors: List[str] = []

    # Esempi di controlli minimi da completare
    if material.density_kg_m3 <= 0:
        errors.append("La densità deve essere positiva (kg/m^3).")

    if not material.material_id:
        errors.append("material_id mancante.")

    # TODO Copilot:
    # - Validare parametri in material.params.

    return errors

# ======================================================================

# FINE FILE validation.py

# ======================================================================

============================================================
FILE: src/materials/material_repo.py
============================================================

"""
material_repo.py

Repository dei materiali.

Obiettivi:

- Gestire caricamento materiali da file legacy.
- Gestire caricamento materiali da file JSON/YAML moderni.
- Permettere recupero per material_id.
- Fornire strumenti per validazione automatica.
- Essere integrato con src/elements per assegnare materiali
  agli elementi strutturali.
- Essere integrato con src/codes per coefficienti normativi.

NOTE:
Questo file è uno STUB S2:

- Contiene struttura, docstring, TODO
- Nessuna implementazione completa

"""

from typing import Dict, Optional, List
from .material_model import Material
from .validation import validate_material

class MaterialRepository:
    """
    Repository per i materiali.

    Funzionalità previste:
    - add_material(material)
    - get(material_id)
    - load_from_legacy_json(path)
    - validate_all()
    - list_all()

    TODO Copilot:
    - Implementare caricamento da src/legacy/materials.json.
    - Aggiungere logging.
    - Integrare con config/app.yml per selezione materiali attivi.
    """

    def __init__(self) -> None:
        self._materials: Dict[str, Material] = {}

    # ------------------------------------------------------------------

    def add_material(self, material: Material) -> None:
        """
        Aggiunge un materiale.

        TODO:
        - Validare duplicati.
        """
        self._materials[material.material_id] = material

    # ------------------------------------------------------------------

    def get(self, material_id: str) -> Optional[Material]:
        """
        Restituisce il materiale richiesto.

        TODO:
        - Gestire eccezioni.
        - Logging del materiale recuperato.
        """
        return self._materials.get(material_id)

    # ------------------------------------------------------------------

    def list_all(self) -> List[Material]:
        """
        Restituisce tutti i materiali caricati.
        """
        return list(self._materials.values())

    # ------------------------------------------------------------------

    def validate_all(self) -> Dict[str, List[str]]:
        """
        Valida tutti i materiali nel repository.

        Ritorna:
            { material_id: [lista errori] }

        TODO:
        - Logging per ogni materiale.
        """
        results: Dict[str, List[str]] = {}

        for m in self._materials.values():
            errors = validate_material(m)
            results[m.material_id] = errors

        return results

    # ------------------------------------------------------------------

    def load_from_legacy_json(self, path: str) -> None:
        """
        Carica i materiali da un file JSON legacy.

        TODO Copilot:
        - Implementare lettura JSON.
        - Create Material(...) a partire dai dati caricati.
        - Chiamare add_material().
        - Integrare con validate_all().
        """
        pass

# ======================================================================

# FINE FILE material_repo.py

# ======================================================================

############################################################

# FINE BLOCCO 4 / 12

############################################################
############################################################

# BLOCCO 5 / 12

# PACKAGE: src/elements/

#

# Contenuto

# - element_model.py

# - element_repo.py

# - resolve_inputs.py

#

# Tutto in versione STUB S2

# - Docstring lunghissime

# - Commenti guida per Plan

# - Interfacce pulite e pronte per implementazioni successive

############################################################

============================================================
FILE: src/elements/element_model.py
============================================================

"""
element_model.py

Questo modulo definisce il MODELLO dati degli elementi strutturali
gestiti dal software.

Un elemento strutturale è l’unità tecnica minima su cui si svolgono:

- calcoli antisismici
- verifiche statiche
- assegnazione materiali
- assegnazione sezione
- mapping verso normative e coefficienti
- generazione report

ESEMPI DI ELEMENTI:

- Trave in c.a.
- Pilastro in c.a.
- Parete in c.a.
- Trave acciaio
- Trave legno
- Elemento murario

Questo STUB S2 definisce:

1. Interfaccia principale `Element`.
2. Parametri geometrici essenziali.
3. Collegamento a:
    - materiali/material_repo
    - calc/shear_area_registry
    - codes per parametri normativi
4. Metodi placeholder pronti per essere implementati da Copilot Plan.

UNITÀ DI MISURA:

- Lunghezze → cm
- Aree → cm²
- Inerzie → cm⁴
- Carichi → kg
- Densità → kg/m³

"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..materials.material_model import Material
from ..calc.shear_area_registry import compute_shear_area

@dataclass
class Element:
    """
    Modello base di un elemento strutturale.

    Attributi:
    - element_id: identificatore univoco dell’elemento.
    - type: categoria (es. "beam", "column", "wall", "steel_beam").
    - length_cm: lunghezza in cm.
    - material: oggetto Material assegnato.
    - section: dizionario metadata della sezione (da section_registry).
    - additional_params: parametri variabili (forze, vincoli, etc.)

    TODO Copilot:
    - Aggiungere sistema vincoli (fixed, hinge, ecc.)
    - Collegamento con verifica sezioni (modulo future).
    """

    element_id: str
    type: str
    length_cm: float
    material: Optional[Material] = None
    section: Optional[Dict[str, Any]] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------
    # GEOMETRIA SEZIONE
    # ------------------------------------------------------------
    def get_section_area(self) -> Optional[float]:
        """
        Restituisce l'area della sezione in cm^2.

        TODO Copilot:
        - Validare che section contenga area_cm2.
        """
        if self.section:
            return self.section.get("area_cm2")
        return None

    def get_inertia(self) -> Optional[Dict[str, float]]:
        """
        Restituisce la mappa delle inerzie, es.:

            { "Ix": ..., "Iy": ... }

        TODO:
        - Validare presenza valori.
        """
        if self.section:
            return self.section.get("inertia_cm4")
        return None

    # ------------------------------------------------------------
    # AREA A TAGLIO
    # ------------------------------------------------------------
    def get_shear_area(self):
        """
        Restituisce A_sx e A_sy.

        NOTE:
        - Utilizza compute_shear_area(section_obj-like).
        - Qui la sezione è un dict, non un oggetto → serve bridging.

        TODO Copilot:
        - Implementare un wrapper Section minimal per compatibilità.
        """
        if not self.section:
            return (0.0, 0.0)

        class _Sec:
            """Mini-adapter per compatibilità compute_shear_area."""
            def __init__(self, md):
                self.shape_id = md.get("id")
                self.area_cm2 = md.get("area_cm2")
                self.kappa_x = md.get("kappa_x", None)
                self.kappa_y = md.get("kappa_y", None)

        return compute_shear_area(_Sec(self.section))

    # ------------------------------------------------------------
    # MATERIALI
    # ------------------------------------------------------------
    def get_material_param(self, name: str) -> Optional[float]:
        """
        Recupera il parametro materiale (es. fck, fyk, E).

        TODO:
        - Validare self.material.
        """
        if self.material:
            return self.material.get_param(name)
        return None

    # ------------------------------------------------------------
    # SERIALIZZAZIONE
    # ------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializzazione base, pronta per JSON.

        TODO:
        - Integrare parametri aggiuntivi.
        """
        return {
            "element_id": self.element_id,
            "type": self.type,
            "length_cm": self.length_cm,
            "material": self.material.material_id if self.material else None,
            "section_id": self.section.get("id") if self.section else None,
            "additional_params": self.additional_params,
        }

# ======================================================================

# FINE FILE element_model.py

# ======================================================================

============================================================
FILE: src/elements/element_repo.py
============================================================

"""
element_repo.py

Questo modulo definisce il REPOSITORY degli elementi strutturali.

Responsabilità del repository:

- Creazione e registrazione elementi.
- Caricamento da file JSON/XML/YAML moderni.
- Caricamento da file legacy (se esiste un corrispettivo).
- Collegamento con repository materiali.
- Collegamento con registry sezioni.
- Collegamento con funzioni di risoluzione input (resolve_inputs).

STUB S2:

- Struttura completa
- Docstring lunghe
- TODO per Copilot
"""

from typing import Dict, Optional, List
from .element_model import Element
from ..materials.material_repo import MaterialRepository
from ..calc.section_registry import get_section_metadata

class ElementRepository:
    """
    Repository per la gestione degli elementi strutturali.

    Funzioni previste:
    - add_element()
    - get()
    - list_all()
    - load_from_json()
    - assign_material()
    - assign_section()

    TODO Copilot:
    - Collegare a resolve_inputs.
    """

    def __init__(self) -> None:
        self._elements: Dict[str, Element] = {}

    # --------------------------------------------------------------

    def add_element(self, element: Element) -> None:
        """
        Aggiunge un elemento.

        TODO:
        - Validare duplicati id.
        """
        self._elements[element.element_id] = element

    # --------------------------------------------------------------

    def get(self, element_id: str) -> Optional[Element]:
        """
        Recupera un elemento.
        """
        return self._elements.get(element_id)

    # --------------------------------------------------------------

    def list_all(self) -> List[Element]:
        """
        Restituisce tutti gli elementi.
        """
        return list(self._elements.values())

    # --------------------------------------------------------------

    def assign_material(self, element_id: str, material_id: str, material_repo: MaterialRepository) -> None:
        """
        Assegna un materiale a un elemento, recuperandolo dal repository.

        TODO:
        - Validare esistenza materiale
        - Logging
        """
        el = self.get(element_id)
        mat = material_repo.get(material_id)
        if el and mat:
            el.material = mat

    # --------------------------------------------------------------

    def assign_section(self, element_id: str, section_id: str) -> None:
        """
        Assegna la sezione tramite registry globale.

        TODO:
        - Validare esistenza sezione
        """
        el = self.get(element_id)
        metadata = get_section_metadata(section_id)
        if el and metadata:
            el.section = metadata

    # --------------------------------------------------------------

    def load_from_json(self, path: str, material_repo: MaterialRepository) -> None:
        """
        Carica elementi da file JSON.

        TODO Copilot:
        - Implementare lettura JSON.
        - Creare Element(...).
        - Assegnare materiali e sezioni.
        - Aggiungere logging.
        """
        pass

# ======================================================================

# FINE FILE element_repo.py

# ======================================================================

============================================================
FILE: src/elements/resolve_inputs.py
============================================================

"""
resolve_inputs.py

Questo modulo centralizza la RISOLUZIONE INPUT, cioè la fase in cui
l’utente imposta:

- elementi da verificare
- materiali assegnati
- sezioni assegnate
- parametri strutturali
- parametri normativi
- carichi aggiuntivi
- condizioni di verifica

Tale sistema produce un oggetto strutturato pronto per il motore
di verifica.

Questo modulo è fondamentale perché:

- garantisce consistenza tra materiale/sezione/elemento
- normalizza unità di misura
- effettua controlli di validità
- decide quali attributi passare alle verifiche
- gestisce fallback e default

STUB S2:

- Nessuna implementazione reale
- Struttura, docstring e TODO pronti per essere espansi dal Plan
"""

from typing import Dict, Any
from .element_repo import ElementRepository
from ..materials.material_repo import MaterialRepository

def resolve_verification_inputs(
    element_repo: ElementRepository,
    material_repo: MaterialRepository,
    user_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Risolve gli input dell’utente e costruisce una struttura completa
    per le verifiche.

    Parametri:
    - element_repo: repository elementi (già popolato)
    - material_repo: repository materiali (già popolato)
    - user_config: configurazioni da GUI o file (es. tipo verifica,
                   parametri normativi, carichi, ecc.)

    Output previsto:
    {
        "elements": [...],
        "materials": [...],
        "settings": {...},
        "normative": {...},
        "load_cases": [...],
        "error_list": [...]
    }

    TODO Copilot:
    - Validare integrità materiale/sezione/elemento.
    - Integrare normative (package codes).
    - Implementare conversione unità se necessario.
    - Aggiungere logging e gestione errori.
    - Integrare con config/app.yml.
    """
    resolved: Dict[str, Any] = {
        "elements": [],
        "materials": [],
        "settings": {},
        "normative": {},
        "load_cases": [],
        "error_list": [],
    }

    # TODO Copilot:
    # - Popolare i campi con dati reali provenienti dai repository.
    # - Integrare config numerics.
    # - Validare parametri utente.

    return resolved

# ======================================================================

# FINE FILE resolve_inputs.py

# ======================================================================

############################################################

# FINE BLOCCO 5 / 12

############################################################
############################################################

# BLOCCO 6 / 12

# PACKAGE: src/codes/

#

# Contenuto

# - code_registry.py

# - clauses/<normativa>.yml (stub)

# - params/<normativa>.json (stub)

#

# Tutti i file sono STUB S2

# - Docstring estese

# - Schema pensato per Continue / Copilot Plan

############################################################

============================================================
FILE: src/codes/code_registry.py
============================================================

"""
code_registry.py

Questo modulo definisce il REGISTRY NORMATIVO del software.

Funzioni e responsabilità del registry
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
  senza imporre logica normativa all’interno dei moduli di calcolo.

STUB S2
---------------------------------------

- Struttura completa
- Docstring ricca
- TODO per Copilot Plan
- Implementazioni minime

Unità di misura
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

============================================================
FILE: src/codes/params/NTC2018.json
============================================================

{
    "_comment": "Esempio STUB S2 dei parametri numerici della normativa NTC 2018. I valori sono placeholders e verranno sovrascritti da Copilot Plan.",
    "gamma_c": 1.5,
    "gamma_s": 1.15,
    "psi_0": 0.7,
    "psi_1": 0.5,
    "psi_2": 0.3,
    "E_cm": 300000.0,
    "note": "Tutti i valori riportati sono da validare e aggiornare."
}

============================================================
FILE: src/codes/clauses/NTC2018.yml
============================================================

# Esempio STUB S2 di clausole normative per NTC 2018

# Il testo NON è normativo reale: è solo struttura per supportare

# Copilot Plan nella generazione di report tecnici

general:
  title: "Norme Tecniche per le Costruzioni 2018"
  scope: "Regole generali per progettazione e verifica."

materials:
  concrete:
    limit_states:
      - id: "SLE"
        desc: "Stato Limite di Esercizio."
      - id: "SLU"
        desc: "Stato Limite Ultimo."
    remarks:
      - "Questo testo è un placeholder e va sostituito."

geometry:
  section_limits:
    min_height_cm: 20
    min_width_cm: 20
    note: "Placeholder."

load_combinations:
  ulc:
    desc: "Combinazione allo Stato Limite Ultimo."
    text: "Placeholder per descrizione combinazione ULC."

verification:
  flexure:
    description: "Regole di verifica flessionale."
    formula_ref: "TODO: inserire richiamo normativo reale."

============================================================
FILE: src/codes/params/EC2.json
============================================================

{
    "_comment": "Parametri numerici STUB S2 per Eurocodice 2.",
    "gamma_c": 1.5,
    "gamma_s": 1.15,
    "psi_0": 0.7,
    "E_cm": 310000.0,
    "note": "Placeholder, valori da aggiornare."
}

============================================================
FILE: src/codes/clauses/EC2.yml
============================================================

general:
  title: "Eurocodice 2 - Progettazione delle strutture in calcestruzzo"
  scope: "Strutture in c.a. e c.a.p."
materials:
  concrete:
    limit_states:
      - id: "ULS"
        desc: "Ultimate Limit State."
verification:
  general:
    warning: "Contenuto non normativo reale, da sostituire."
    limits:
      flexure: "Placeholder limite flessionale."
      shear: "Placeholder limite taglio."

============================================================
NOTE FINALI DEL BLOCCO 6
============================================================

- Il pacchetto `codes/` è ora completo per la struttura S2.
- I file JSON/YAML sono placeholders solo per fornire
  uno scheletro per Plan.
- Nei prossimi blocchi i moduli potranno referenziare parametri
  e clausole normative tramite code_registry.

############################################################

# FINE BLOCCO 6 / 12

############################################################
############################################################

# BLOCCO 7 / 12

# PACKAGE: src/actions/

#

# Contenuto

# - action_repo.py

# - infrastruttura generale per azioni di verifica

#

# TUTTI i file in modalità STUB S2

############################################################

============================================================
FILE: src/actions/action_repo.py
============================================================

"""
action_repo.py

Questo modulo definisce l'infrastruttura per la gestione
delle AZIONI DI VERIFICA.

Una “azione di verifica” (VerificationAction) è un oggetto
che incapsula una singola REGOLA DI VERIFICA strutturale,
come ad esempio:

- verifica flessione semplice (R_c > S_c)
- verifica taglio
- verifica pressoflessione
- verifica tensioni
- verifica snellezza
- verifica duttilità
- verifiche combinate secondo normativa
- verifiche allo SLU
- verifiche allo SLE

La finalità del repository è:

1) Raccogliere tutte le azioni disponibili.
2) Collegarle a normative specifiche.
3) Applicarle agli elementi o insiemi di elementi
   all’interno del motore di verifica.

Questo è uno STUB S2:

- NON contiene formule vere.
- Fornisce la struttura per Copilot Plan.
- Usa interfacce pronte per essere ampliate nei blocchi successivi.
"""

from typing import Callable, Dict, List, Any

# ==========================================================

# TIPI E INTERFACCE

# ==========================================================

class VerificationAction:
    """
    Interfaccia base per una singola azione di verifica.

    Ogni azione deve implementare:
        - action_id: identificatore
        - description: breve descrizione
        - run(element, normative, settings) -> Dict[str, Any]

    Esempio output previsto:
    {
        "action_id": "flexure_check",
        "ok": True/False,
        "messages": ["...", "..."],
        "partials": {... valori intermedi ...}
    }

    NOTE:
    - Nessuna formula reale è implementata qui.
    - Questa è una classe di “schema” per future implementazioni.
    """

    action_id: str = "undefined"
    description: str = "Verification Action (stub)."

    def run(self, element: Any, normative: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Esegue la verifica sull’elemento e restituisce un dizionario.

        TODO Copilot:
        - Implementare classe astratta con NotImplementedError.
        - Permettere logging dei valori intermedi.
        """
        raise NotImplementedError("Azione di verifica non implementata.")

# ==========================================================

# REPOSITORY DELLE AZIONI

# ==========================================================

ACTION_REPOSITORY: Dict[str, VerificationAction] = {}
"""
Mappa: action_id → istanza di VerificationAction

TODO Copilot:

- Introdurre factory pattern per creare azioni in base alla normativa.
- Permettere override normative (es. eccezioni speciali).
"""

def register_action(action: VerificationAction) -> None:
    """
    Registra una azione di verifica nel repository.

    TODO:
    - Validazione duplicati.
    - Logging.
    """
    ACTION_REPOSITORY[action.action_id] = action

def get_action(action_id: str) -> VerificationAction:
    """
    Recupera una azione di verifica registrata.

    TODO:
    - Gestire errori se missing.
    """
    return ACTION_REPOSITORY[action_id]

def list_actions() -> List[str]:
    """
    Restituisce la lista di tutte le azioni disponibili.
    """
    return list(ACTION_REPOSITORY.keys())

# ==========================================================

# ESEMPI DI AZIONI (STUB)

# ==========================================================

class FlexureCheck(VerificationAction):
    """
    Verifica flessionale (stub).

    NON implementa formule.
    Serve come modello per Continue / Copilot Plan.

    TODO Copilot:
    - Aggiungere input richiesti: M_ed, resistenze, gamma_M.
    - Integrare normative: normative["params"], normative["clauses"].
    - Integrare sezione: element.section.
    """
    action_id = "flexure_check"
    description = "Verifica flessionale (stub, nessuna formula)."

    def run(self, element: Any, normative: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: implementazione reale
        return {
            "action_id": self.action_id,
            "ok": True,
            "messages": ["Flexure check not implemented (stub)."],
            "partials": {}
        }

class ShearCheck(VerificationAction):
    """
    Verifica taglio (stub).

    TODO:
    - Integrare area a taglio: element.get_shear_area().
    - Inserire parametri normativi.
    """
    action_id = "shear_check"
    description = "Verifica taglio (stub, nessuna formula)."

    def run(self, element: Any, normative: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "ok": True,
            "messages": ["Shear check not implemented (stub)."],
            "partials": {}
        }

# ==========================================================

# REGISTRAZIONE AUTOMATICA DELLE AZIONI DI BASE

# ==========================================================

register_action(FlexureCheck())
register_action(ShearCheck())

# ======================================================================

# FINE FILE action_repo.py

# ======================================================================

############################################################

# FINE BLOCCO 7 / 12

############################################################
############################################################

# BLOCCO 8 / 12

# PACKAGE: src/report/

#

# Contenuto

# - renderer_md.py

# - renderer_html.py

# - renderer_pdf.py (stub)

# - templates/template.md

# - templates/template.html

#

# Tutti i file sono STUB S2

# - Docstring molto dettagliate

# - Struttura pronta per Copilot Plan

# - Nessuna implementazione reale del rendering complesso

############################################################

============================================================
FILE: src/report/renderer_md.py
============================================================

"""
renderer_md.py

Renderer per generare report in formato **Markdown**.

Funzioni del renderer:

- Creare report sintetici o estesi sulle verifiche
- Utilizzare i template MD del progetto (templates/template.md)
- Inserire:
  - dati dell’elemento
  - risultati delle verifiche (ok, non ok, valori parziali)
  - parametri normativi utilizzati
  - informazioni geometriche (A_sx, A_sy, area, inerzia)
- Essere integrato con la pipeline completa del motore di verifica

Questo modulo è uno STUB S2:

- Struttura completa
- Docstring molto dettagliate
- TODO diffusi per permettere a Copilot Plan di completare

Unità di misura da rispettare (nessuna conversione):

- tensioni: kg/cm^2
- lunghezze: cm
- inerzie: cm^4
- aree: cm^2
- densità: kg/m^3
"""

from typing import Dict, Any
import datetime
import os

class MarkdownReportRenderer:
    """
    Renderer per output Markdown.

    Metodo principale:
        render(data: Dict[str, Any]) -> str

    dove "data" contiene:
        {
            "elements": [...],
            "results": [...],
            "normative": {...},
            "settings": {...}
        }

    TODO Copilot:
    - Integrare lettura template dal file template.md
    - Formattare tabelle
    - Aggiungere sezioni opzionali
    """

    def __init__(self, template_path: str) -> None:
        self.template_path = template_path

    def render(self, data: Dict[str, Any]) -> str:
        """
        Restituisce una stringa Markdown del report.

        TODO:
        - Implementare sostituzione placeholder
        - Generare sezioni dinamiche per elemento e verifiche
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        output = [
            f"# Report di Verifica",
            f"**Generato:** {now}",
            "",
            "## Sommario",
            "- Report generato (stub, implementazione mancante).",
            "",
            "## Elementi",
            "I dettagli degli elementi saranno inseriti qui.",
            "",
            "## Risultati",
            "I risultati delle verifiche saranno inseriti qui.",
            "",
            "_(renderer_md.py è uno stub S2)_"
        ]
        return "\n".join(output)

# ======================================================================

# FINE FILE renderer_md.py

# ======================================================================

============================================================
FILE: src/report/renderer_html.py
============================================================

"""
renderer_html.py

Renderer per generare report in formato **HTML**.

Funzioni previste:

- Caricare un template HTML (templates/template.html)
- Inserire contenuti dinamici:
  - intestazione
  - dati elementi
  - risultati verifiche
- Generare sezioni tabulate
- Supportare eventuali CSS inline o allegati
- Integrare riferimenti normativi (da codes/)

Questo è uno STUB S2:

- Non esegue rendering reale
- Struttura pronta per Copilot
"""

from typing import Dict, Any
import datetime
import os

class HTMLReportRenderer:
    """
    Renderer HTML.

    TODO:
    - Aggiungere supporto CSS
    - Integrare template engine semplice (string replace)
    """

    def __init__(self, template_path: str) -> None:
        self.template_path = template_path

    def render(self, data: Dict[str, Any]) -> str:
        """
        Restituisce una stringa HTML completa.

        TODO:
        - Leggere il file template.html
        - Inserire tabelle dinamiche
        - Formattare valori con unità
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Report di Verifica (stub)</title>
</head>
<body>
    <h1>Report di Verifica</h1>
    <p><strong>Generato:</strong> {now}</p>
    <h2>Sommario</h2>
    <p>Report HTML generato come stub S2.</p>
    <h2>Elementi</h2>
    <p>I dettagli degli elementi andranno qui.</p>
    <h2>Risultati</h2>
    <p>I risultati delle verifiche andranno qui.</p>
</body>
</html>
"""
        return html

# ======================================================================

# FINE FILE renderer_html.py

# ======================================================================

============================================================
FILE: src/report/renderer_pdf.py
============================================================

"""
renderer_pdf.py

Renderer PDF (STUB).

Questo modulo definisce l'interfaccia per esportare il report
in formato PDF. L’implementazione reale può essere delegata a:

- ReportLab (raccomandato)
- WeasyPrint (HTML → PDF)
- wkhtmltopdf (se disponibile)
- altre soluzioni basate su template HTML

Tuttavia:

- Questo file NON deve implementare nulla ora.
- Serve solo la struttura per future espansioni.

STUB S2:

- interfaccia render()
- docstring dettagliata
"""

from typing import Dict, Any

class PDFReportRenderer:
    """
    Interfaccia base per generare PDF.

    TODO Copilot:
    - Integrare un motore PDF
    - Riallineare stile ai template HTML/MD
    """

    def __init__(self) -> None:
        pass

    def render(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Genera un PDF in output_path.

        TODO:
        - Implementare tramite ReportLab o HTML→PDF
        """
        raise NotImplementedError("PDF rendering non implementato (stub).")

# ======================================================================

# FINE FILE renderer_pdf.py

# ======================================================================

============================================================
FILE: src/report/templates/template.md
============================================================

# Report di Verifica — Template Markdown

**ATTENZIONE:** questo file è uno STUB S2.
Verrà usato come base da renderer_md.py per generare report reali.

---

## Intestazione

- **Data generazione:** {{generation_date}}
- **Normativa:** {{code_name}}
- **Versione software:** {{software_version}}

---

## Elementi

{{elements_table}}

---

## Risultati

{{results_table}}

---

## Messaggi

{{messages}}

---

_(File template.md, stub S2)_

============================================================
FILE: src/report/templates/template.html
============================================================

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Report di Verifica — Template HTML</title>
</head>

<body>
    <h1>Report di Verifica — Template HTML</h1>

    <p><strong>Generato:</strong> {{generation_date}}</p>
    <p><strong>Normativa:</strong> {{code_name}}</p>
    <p><strong>Versione software:</strong> {{software_version}}</p>

    <h2>Elementi</h2>
    {{elements_table}}

    <h2>Risultati</h2>
    {{results_table}}

    <h2>Messaggi</h2>
    {{messages}}

    <p><em>File template.html — STUB S2</em></p>
</body>
</html>

############################################################

# FINE BLOCCO 8 / 12

############################################################
############################################################

# BLOCCO 9 / 12

# PACKAGE: src/config/

#

# Contenuto

# - units.yml

# - numerics.yml

# - app.yml

# - features.yml

#

# Tutti file serie STUB S2 (commentati, pronti per estensioni)

############################################################

============================================================
FILE: src/config/units.yml
============================================================

# ==========================================================

# units.yml

# ==========================================================

# File di configurazione principale delle unità di misura

#

# ATTENZIONE

# - Il progetto utilizza _solo_ le unità richieste dall’utente

# - Nessuna conversione implicita deve essere fatta nei moduli

#

# FORMATO

# - "unit": stringa descrittiva (ad uso GUI / report)

# - "factor": eventuale fattore di conversione se in futuro

# volessi supportare unità alternative (non implementato ora)

#

# STUB S2 — pronto per essere esteso

# ==========================================================

length:
  base: "cm"
  factor: 1.0      # cm → cm

area:
  base: "cm2"
  factor: 1.0

inertia:
  base: "cm4"
  factor: 1.0

stress:
  base: "kg/cm2"
  factor: 1.0

density:
  base: "kg/m3"
  factor: 1.0

mass:
  base: "kg"
  factor: 1.0

force:
  base: "kg"
  factor: 1.0

# NOTE

# In futuro si potrà estendere con

# - kN, kN·m, MPa, etc

# mantenendo cm e kg come base di calcolo

============================================================
FILE: src/config/numerics.yml
============================================================

# ==========================================================

# numerics.yml

# ==========================================================

# Configurazione per la parte numerica del software

#

# CONTIENE

# - precisioni di arrotondamento

# - tolleranze numeriche

# - parametri utili ai calcoli interni

#

# STUB S2 — nessun valore definitivo

# ==========================================================

rounding:
  default: 4            # decimali di default
  stresses: 3           # tensioni
  geometry: 3           # aree, inerzie

tolerances:
  zero: 1e-9            # tolleranza valore zero
  equality: 1e-6        # tolleranza confronto valori

options:
  enable_debug: false   # debug numerico
  verbose_calculation: false

============================================================
FILE: src/config/app.yml
============================================================

# ==========================================================

# app.yml

# ==========================================================

# Configurazione generale dell'applicazione

#

# CONTIENE

# - Nome software

# - Versione

# - Default normativa utilizzata

# - Percorsi file

# - Impostazioni globali

#

# STUB S2 — da estendere con Copilot Plan

# ==========================================================

application:
  name: "Engineering Verification Framework"
  version: "0.1.0"
  description: "Framework modulare per verifiche strutturali — Stub S2"

defaults:
  normative: "NTC2018"
  report_format: "html"

paths:
  legacy: "src/legacy"
  templates: "src/report/templates"

logging:
  level: "INFO"     # può essere DEBUG, INFO, WARNING, ERROR
  file: "logs/app.log"

ui:
  enable_gui_warnings: true

============================================================
FILE: src/config/features.yml
============================================================

# ==========================================================

# features.yml

# ==========================================================

# File di feature-flag del software

#

# SERVE PER

# - Attivare/disattivare parti opzionali del programma

# - Permettere sviluppo incrementale (strategie Plan)

#

# STUB S2 — da espandere

# ==========================================================

features:

# --------------------------------------------------------

# Elementi e modellazione

# --------------------------------------------------------

  enable_element_restrictions: true
  enable_section_registry: true
  enable_shear_area_fallback: true

# --------------------------------------------------------

# Materiali

# --------------------------------------------------------

  enable_material_validation: true
  enable_material_import_legacy: true

# --------------------------------------------------------

# Normative

# --------------------------------------------------------

  enable_normative_bootstrap: true
  enable_normative_overrides: false

# --------------------------------------------------------

# Report

# --------------------------------------------------------

  enable_html_reports: true
  enable_md_reports: true
  enable_pdf_reports: false     # PDF disabilitato finché non implementato

# --------------------------------------------------------

# Debug e log

# --------------------------------------------------------

  enable_debug_messages: false

############################################################

# FINE BLOCCO 9 / 12

############################################################
############################################################

# BLOCCO 10 / 12

# PACKAGE: src/tools/

#

# Contenuto

# - verify_cli.py

# - export_results.py

#

# Entrambi in versione _STUB S2_

# - Docstring molto estese

# - Commenti guida

# - Struttura per CLI e export

############################################################

============================================================
FILE: src/tools/verify_cli.py
============================================================

"""
verify_cli.py

Strumento CLI (Command Line Interface) per eseguire verifiche
strutturali dalla riga di comando.

OBIETTIVI:

- Permettere l'esecuzione automatica delle verifiche senza GUI.
- Caricare repository materiali, elementi e normative.
- Invocare resolve_inputs() per generare gli input finali.
- Attivare una pipeline di verifiche basata su action_repo.
- Generare un report (HTML/MD) tramite i renderer del package report.

UTILIZZO ATTESO (futuro):
    python verify_cli.py --config config/user_conf.yml

FUNZIONI PRINCIPALI:

- parse_args()
- load_user_config()
- bootstrap_all()
- run_verifications()
- export_report()

Questo file è uno STUB S2:

- Nessuna implementazione reale della pipeline
- Struttura e TODO per Copilot Plan
"""

import argparse
import json
from typing import Dict, Any

from ..elements.element_repo import ElementRepository
from ..materials.material_repo import MaterialRepository
from ..codes.code_registry import bootstrap_codes, get_code
from ..elements.resolve_inputs import resolve_verification_inputs
from ..report.renderer_html import HTMLReportRenderer
from ..report.renderer_md import MarkdownReportRenderer

def parse_args():
    """
    Parsing degli argomenti CLI.

    TODO Copilot:
    - Aggiungere opzioni per:
        --config file.yml
        --output out.html
        --format html/md
    """
    parser = argparse.ArgumentParser(description="CLI verifica strutturale (stub).")
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--format", type=str, default="html")
    return parser.parse_args()

def load_user_config(path: str) -> Dict[str, Any]:
    """
    Carica configurazione utente da file JSON/YAML.

    TODO Copilot:
    - Supportare YAML.
    - Validare dati.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def bootstrap_all() -> Dict[str, Any]:
    """
    Inizializza repository e normative.

    TODO:
    - Caricare materiali da legacy.
    - Caricare sezioni da legacy.
    - Inizializzare registry normative.
    """

    materials = MaterialRepository()
    elements = ElementRepository()

    # Boot normative — path fisso (stub)
    bootstrap_codes("src/codes")

    return {
        "materials": materials,
        "elements": elements,
    }

def run_cli() -> None:
    """
    Entry point CLI.

    TODO Copilot:
    - Implementare pipeline completa.
    """
    args = parse_args()

    # Carica user config
    if args.config:
        user_conf = load_user_config(args.config)
    else:
        user_conf = {}

    # Bootstrap
    repos = bootstrap_all()
    materials = repos["materials"]
    elements = repos["elements"]

    # Risolve input
    resolved = resolve_verification_inputs(elements, materials, user_conf)

    # Report
    if args.format == "html":
        renderer = HTMLReportRenderer("src/report/templates/template.html")
        out = renderer.render(resolved)
        print(out)
    else:
        renderer = MarkdownReportRenderer("src/report/templates/template.md")
        out = renderer.render(resolved)
        print(out)

    print("\n[CLI Stub] Verifica completata (stub).\n")

if **name** == "**main**":
    run_cli()

# ======================================================================

# FINE FILE verify_cli.py

# ======================================================================

============================================================
FILE: src/tools/export_results.py
============================================================

"""
export_results.py

Utility per esportare i risultati delle verifiche in vari formati:

- JSON
- CSV
- TABELLE (per uso interno)
- Integrazione con report HTML / MD / PDF

Il modulo NON effettua verifiche: riceve i dati finali strutturati.
Fa parte della pipeline:

    repo → resolve_inputs → action_repo → report → exporter

Questo file è STUB S2:

- Struttura completa
- Docstring estese
- Nessuna implementazione reale
"""

from typing import Dict, Any
import json
import csv

def export_to_json(data: Dict[str, Any], path: str) -> None:
    """
    Esporta i risultati in JSON.

    TODO Copilot:
    - Validare struttura dati.
    - Aggiungere indentazione configurabile.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def export_to_csv(data: Dict[str, Any], path: str) -> None:
    """
    Esporta i risultati in CSV.

    Il CSV include tipicamente:
    - element_id
    - action_id
    - ok/non ok
    - messaggi principali

    TODO:
    - Validare presenza campi
    - Gestire errori
    """

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["element_id", "action_id", "ok", "message"])

        # TODO Copilot:
        # - Iterare su data["results"]
        # - Scrivere righe pertinenti
        writer.writerow(["stub_element", "stub_action", True, "no data (stub)"])

# ======================================================================

# FINE FILE export_results.py

# ======================================================================

############################################################

# FINE BLOCCO 10 / 12

############################################################
############################################################

# BLOCCO 11 / 12

# PACKAGE: src/tests/

#

# Contiene

# - test_shear_area.py

# - test_code_routing.py

# - test_resolve_inputs.py

# - test_reporting.py

# - test_material_repo.py

# - test_elements_repo.py

#

# Tutti in versione STUB S2

############################################################

============================================================
FILE: src/tests/test_shear_area.py
============================================================

"""
test_shear_area.py

Test minimi per il modulo:
    src/calc/shear_area_registry.py

Gli obiettivi dei test:

- Verificare che il registry funzioni.
- Verificare che compute_shear_area restituisca tuple valide.
- Verificare comportamento fallback.

STUB S2: test semplici, non completi.
"""

import pytest
from src.calc.shear_area_registry import compute_shear_area

class DummyRectSection:
    """Sezione rettangolare dummy per test."""
    def **init**(self):
        self.shape_id = "rectangle"
        self.area_cm2 = 100.0
        self.kappa_x = None
        self.kappa_y = None

class DummyUnknownSection:
    """Sezione sconosciuta → fallback."""
    def **init**(self):
        self.shape_id = "unknown"
        self.area_cm2 = 50.0
        self.kappa_x = 0.8
        self.kappa_y = 0.7

def test_rectangular_shear_area():
    sec = DummyRectSection()
    Asx, Asy = compute_shear_area(sec)
    assert Asx > 0
    assert Asy > 0

def test_fallback_shear_area():
    sec = DummyUnknownSection()
    Asx, Asy = compute_shear_area(sec)
    assert Asx == pytest.approx(0.8 *50.0)
    assert Asy == pytest.approx(0.7* 50.0)

============================================================
FILE: src/tests/test_code_routing.py
============================================================

"""
test_code_routing.py

Test minimi per:
    src/codes/code_registry.py

Verifica che:

- il registry possa registrare una normativa
- la funzione get_code funzioni correttamente
"""

from src.codes.code_registry import register_code, get_code

def test_register_and_get_code():
    params = {"gamma_c": 1.5}
    clauses = {"general": {"title": "Test"}}

    register_code("TESTCODE", params, clauses)
    retrieved = get_code("TESTCODE")

    assert retrieved is not None
    assert retrieved["params"]["gamma_c"] == 1.5
    assert retrieved["clauses"]["general"]["title"] == "Test"

============================================================
FILE: src/tests/test_resolve_inputs.py
============================================================

"""
test_resolve_inputs.py

Test minimi per:
    src/elements/resolve_inputs.py

Controlliamo:

- La struttura base dell’output
- Che non sollevi errori
"""

from src.elements.resolve_inputs import resolve_verification_inputs
from src.elements.element_repo import ElementRepository
from src.materials.material_repo import MaterialRepository

def test_resolve_inputs_structure():
    repo_e = ElementRepository()
    repo_m = MaterialRepository()

    result = resolve_verification_inputs(repo_e, repo_m, {})

    assert isinstance(result, dict)
    assert "elements" in result
    assert "materials" in result
    assert "settings" in result
    assert "normative" in result
    assert "load_cases" in result
    assert "error_list" in result

============================================================
FILE: src/tests/test_reporting.py
============================================================

"""
test_reporting.py

Test minimi dei renderer Markdown e HTML.
"""

from src.report.renderer_md import MarkdownReportRenderer
from src.report.renderer_html import HTMLReportRenderer

def test_md_renderer_basic():
    renderer = MarkdownReportRenderer("src/report/templates/template.md")
    result = renderer.render({"elements": [], "results": []})
    assert isinstance(result, str)
    assert "Report di Verifica" in result

def test_html_renderer_basic():
    renderer = HTMLReportRenderer("src/report/templates/template.html")
    result = renderer.render({"elements": [], "results": []})
    assert "<html>" in result
    assert "</html>" in result

============================================================
FILE: src/tests/test_material_repo.py
============================================================

"""
test_material_repo.py

Test minimi per:
    src/materials/material_repo.py
"""

from src.materials.material_repo import MaterialRepository
from src.materials.material_model import Material

def test_material_repo_add_and_get():
    repo = MaterialRepository()
    m = Material(
        material_id="C25",
        description="Calcestruzzo C25 (stub)",
        family="cls",
        density_kg_m3=2400,
        params={"fck": 250, "E": 300000}
    )
    repo.add_material(m)

    got = repo.get("C25")
    assert got is not None
    assert got.description == "Calcestruzzo C25 (stub)"

============================================================
FILE: src/tests/test_elements_repo.py
============================================================

"""
test_elements_repo.py

Test minimi per il repository degli elementi.
"""

from src.elements.element_repo import ElementRepository
from src.elements.element_model import Element

def test_add_and_get_element():
    repo = ElementRepository()
    e = Element(
        element_id="E1",
        type="beam",
        length_cm=300.0
    )
    repo.add_element(e)

    got = repo.get("E1")
    assert got is not None
    assert got.type == "beam"

############################################################

# FINE BLOCCO 11 / 12

############################################################
############################################################

# BLOCCO 12 / 12

# DOCUMENTAZIONE FINALE DEL PROGETTO

#

# Contenuto

# - README.md (versione completa)

# - NOTE DI MIGRAZIONE

# - CHANGELOG (v0.1.0)

# - eventuale **all** centralizzato (stub)

############################################################

============================================================
FILE: README.md
============================================================

# Engineering Verification Framework

### Architettura modulare per verifiche strutturali

Questo progetto implementa un **framework modulare per verifiche strutturali**, completamente ristrutturato secondo l’architettura definita nella OPZIONE A1.

Tutti i moduli sono stati ricreati secondo standard professionali, con:

- Separazione totale tra moduli
- Nessun calcolo mescolato alla GUI
- Repository per materiali, elementi, normative
- Registry per sezioni e area a taglio
- Resolver centralizzato degli input
- Pipeline completa: repo → resolver → actions → report
- Configurazione tramite file YAML
- Stub S2 pronti per essere ampliati da Copilot Plan

Il progetto include:

```
src/
    legacy/               <-- vecchi moduli invariati
    calc/
    elements/
    materials/
    codes/
    actions/
    report/
    config/
    tools/
    tests/
```

---

## 1. Obiettivi del progetto

- Implementare una struttura modulare, estensibile e professionale.
- Permettere verifiche strutturali in modo scalabile.
- Integrare normative (NTC2018, EC2, EC8) tramite registry.
- Generare report HTML/MD (e PDF in futuro).
- Permettere la creazione di strumenti CLI per automazione.

---

## 2. Filosofia del framework

- **Tutto è un modulo**
- **La GUI non contiene logica tecnica**
- **Unità di misura fisse**:
  - lunghezze → cm
  - aree → cm²
  - inerzie → cm⁴
  - tensioni → kg/cm²
  - densità → kg/m³

- **Calcoli separati per dominio**:
  - area a taglio → `calc/`
  - materiali → `materials/`
  - elementi → `elements/`
  - normative → `codes/`
  - verifiche → `actions/`
  - report → `report/`
  - CLI → `tools/`

---

## 3. Principi di sviluppo

- Ogni modulo ha responsabilità singola.
- Nessun accesso diretto ai file legacy.
- Tutti i moduli moderni sono testati.
- La struttura S2 permette a Copilot Plan di ampliare il codice in modo incrementale, senza conflitti.

---

## 4. Come avviare il progetto

```bash
python -m src.tools.verify_cli --config path/to/config.json
```

Oppure:

```bash
python src/tools/verify_cli.py
```

---

## 5. Come contribuire allo sviluppo

1. Implementare i TODO nei moduli S2.
2. Aggiungere test corrispondenti.
3. Seguire l'architettura esistente.
4. Tenere la documentazione aggiornata.

---

## 6. Test automatici

La suite dei test si trova in:

```
src/tests/
```

Esempio:

```bash
pytest src/tests
```

---

## 7. Report generati

I renderer producono:

- HTML
- Markdown
- PDF (stub, verrà completato)

---

## 8. Configurazioni globali

Le configurazioni si trovano in:

```
src/config/
```

- units.yml
- numerics.yml
- app.yml
- features.yml

---

# NOTE DI MIGRAZIONE (OPZIONE A1)

Queste note descrivono il processo seguito.

## 1. Spostamento file legacy

Tutti i file Python esistenti nel progetto originario sono stati spostati in:

```
src/legacy/
```

I file **non vanno modificati**.

---

## 2. Creazione architettura moderna

Sono state create le seguenti directory:

```
calc/
materials/
elements/
codes/
actions/
report/
config/
tools/
tests/
```

Ognuna con `__init__.py`.

---

## 3. Creazione stub S2

Tutti i file nuovi generati sono:

- fortemente commentati
- contengono docstring complete
- includono TODO per facilitare l’uso di Copilot Plan

---

## 4. Import modernizzati

Gli import sono ora in forma:

```
from src.xxx.yyy import Z
```

Le fasi di aggiornamento interne verranno gestite dal Plan Agent.

---

## 5. Continuità con file legacy

Il sistema è pensato per:

- NON rompere i vecchi moduli
- poter migrare gradualmente la logica nel package moderno

---

## 6. Come completare l’implementazione

Utilizza Copilot Plan:

- Fornisci uno dei moduli
- Segui i TODO
- Esegui i test
- Procedi incrementalmente

---

# CHANGELOG (v0.1.0)

## Versione 0.1.0 — Ristrutturazione completa

- Creazione package `/src/`
- Creazione `legacy/` con file originali
- Creazione package moderni:
  - calc/
  - materials/
  - elements/
  - codes/
  - actions/
  - report/
  - config/
  - tools/
  - tests/
- Generazione stub S2 completi
- Creazione template HTML/MD
- Creazione CLI e exporter
- Configurazioni YAML per unità, app, features
- Test minimi per tutti i moduli

---

============================================================
FILE: src/**all**.py (stub opzionale)
============================================================

"""
**all**.py

Questo file permette import centralizzato, se utile in futuro.

STUB S2 — non contiene nulla, ma può essere ampliato:
"""

**all** = [
    "calc",
    "materials",
    "elements",
    "codes",
    "actions",
    "report",
    "config",
    "tools",
]

############################################################

# FINE BLOCCO 12 / 12

############################################################

# L'intero progetto è stato generato con successo

# Tutti i moduli, template, config, test e documentazione

# sono ora pronti per essere utilizzati con Continue + Copilot Plan
