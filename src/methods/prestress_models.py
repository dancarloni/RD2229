"""
Strutture dati per la precompressione (c.a.p.) - DM 14/02/1992 e DM 9/1/1996.

Modulo che definisce le dataclass per la gestione dei dati di precompressione
nel motore di verifica strutturale. Queste strutture sono pensate per essere:
- compilate dalla GUI (senza dipendenze da GUI nel modulo),
- passate al core di calcolo tramite CalcInput o config dedicata,
- allineate con i contratti esistenti (CalcInput, VerificationTemplate).

Strutture principali:
- TendonType: enum tipo cavo (aderente/non aderente)
- PrestressStage: enum fase di analisi (tesatura/trasferimento/esercizio)
- PrestressingTendon: singolo cavo/tendine
- PrecompressionData: dati complessivi di precompressione per un elemento

NormReference: DM 14/02/1992, DM 9/1/1996, EC2 Parte 1-1 (per formule generali)

TODO: valutare estensione di CalcInput per includere
PrecompressionData (da definire col maintainer del core).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TendonType(StrEnum):
    """Tipo di cavo da precompressione.

    Attributi
    ---------
    ADERENTE : cavo aderente (bonded) - aderenza con il calcestruzzo tramite iniezione.
    NON_ADERENTE : cavo non aderente (unbonded) - libero di scorrere nella guaina.
    """

    ADERENTE = "aderente"
    NON_ADERENTE = "non_aderente"


class PrestressStage(StrEnum):
    """Fase di analisi della precompressione.

    Attributi
    ---------
    TESATURA : fase di applicazione della forza di tiro (tensioning).
    TRASFERIMENTO : fase di trasferimento della precompressione al calcestruzzo.
    ESERCIZIO : condizioni di esercizio a lungo termine.
    """

    TESATURA = "tesatura"
    TRASFERIMENTO = "trasferimento"
    ESERCIZIO = "esercizio"


@dataclass
class PrestressingTendon:
    """Singolo cavo/tendine di precompressione.

    Rappresenta un cavo o tendine con le sue proprietà geometriche,
    meccaniche e i parametri di perdita. Tutti i parametri che l'utente
    può impostare sono campi espliciti (nessun valore hardcodato).

    Attributi
    ---------
    id_tendine : str
        Identificatore univoco del tendine.
    material_id : str
        Chiave materiale da precompressione (riferimento a DM92.jsoncode
        sezione prestressing_steel_types).
    area_mm2 : float
        Area totale del tendine [mm²].
    tendon_type : TendonType
        Tipo di cavo: aderente o non aderente.
    z_mm : float
        Quota del baricentro del tendine nella sezione [mm] rispetto
        al lembo inferiore.
        TODO: estendere a lista di punti (y, z) per profili curvi.
    initial_prestress_force_kN : float
        Forza di tiro iniziale [kN] (parametro utente via GUI).
    friction_mu : float
        Coefficiente di attrito μ cavo-guaina (parametro utente via GUI).
    wobble_k_per_m : float
        Coefficiente di deviazione parassitica k [1/m] (parametro utente via GUI).
    anchor_slip_mm : float
        Scorrimento degli ancoraggi [mm] (parametro utente via GUI).
    bonded_length_mm : float | None
        Lunghezza aderente [mm] (solo per tendini aderenti).
    note : str
        Note libere per tracciabilità.

    NormReference: DM 14/02/1992, DM 9/1/1996, EC2 Parte 1-1 §5.10
    """

    id_tendine: str
    material_id: str
    area_mm2: float
    tendon_type: TendonType
    z_mm: float
    initial_prestress_force_kN: float
    friction_mu: float
    wobble_k_per_m: float
    anchor_slip_mm: float = 0.0
    bonded_length_mm: float | None = None
    note: str = ""


@dataclass
class PrecompressionData:
    """Dati di precompressione per un elemento strutturale.

    Raccoglie tutti i dati necessari per le verifiche di precompressione
    di un elemento: tendini, fase di analisi, coefficienti di sicurezza,
    modello di perdite e relativi parametri.

    Tutti i parametri a scelta dell'utente sono campi espliciti e devono
    essere impostati dalla GUI o da file di configurazione.

    Attributi
    ---------
    element_id : str
        Identificatore dell'elemento (allineato con CalcInput.element_name).
    tendons : list[PrestressingTendon]
        Elenco dei tendini presenti nell'elemento.
    prestress_stage : PrestressStage
        Fase di analisi corrente (tesatura, trasferimento, esercizio).
    gamma_p : float | None
        Coefficiente parziale per l'acciaio da precompressione.
        None = non specificato (il check userà il valore del template normativo).
    consider_losses : bool
        Se True, si applica il modello di perdite specificato.
    losses_model_id : str
        Identificatore del modello di perdite scelto dall'utente.
        TODO: definire modelli disponibili (es. "dm92_simplified", "ec2_detailed").
    user_loss_parameters : dict
        Dizionario con parametri di perdite forniti dall'utente:
        - "creep_coefficient": coefficiente di fluage φ(t, t0)
        - "shrinkage_strain": deformazione da ritiro ε_cs
        - "relaxation_class": classe di rilassamento (1, 2, 3)
        - "relaxation_rho_1000": perdita per rilassamento a 1000 ore [%]
        - "ambient_humidity_percent": umidità relativa ambiente [%]
        Nessun parametro viene hardcodato: i valori devono venire dalla GUI.
    note : str
        Note libere per tracciabilità.

    NormReference: DM 14/02/1992, DM 9/1/1996, EC2 §5.10

    TODO: allineare con CalcInput. Possibile futuro campo in CalcInput:
        precompression_data: Optional[PrecompressionData] = None
    """

    element_id: str
    tendons: list[PrestressingTendon] = field(default_factory=list)
    prestress_stage: PrestressStage = PrestressStage.ESERCIZIO
    gamma_p: float | None = None
    consider_losses: bool = True
    losses_model_id: str = "TODO"
    user_loss_parameters: dict = field(default_factory=dict)
    note: str = ""
