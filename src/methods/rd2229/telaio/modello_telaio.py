"""Modello dati per telai piani c.a. — Cross-Pozzati (RD 2229/39).

Definisce le strutture dati fondamentali del modulo:
- VincoloEsterno:     vincoli d'appoggio (incastro, cerniera, carrello, pattino, pendolo, bipendolo)
- RilascioEstremita:  rilasci interni alle estremità delle aste
- NodoTelaio:         nodo strutturale con coordinate e vincolo
- AstaTelaio:         elemento strutturale con sezione, carichi, rilasci
- ModelloTelaio:      contenitore del modello completo

Unità: cm per geometria, kg per forze, kg/cm² per tensioni, kg/cm³ per pesi specifici.
Riferimenti: Pozzati "Teoria e Tecnica delle Strutture" vol.II; Santarella "Il Cemento Armato".
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

# ==============================================================================
# ENUMERAZIONI
# ==============================================================================

class TipoVincoloEsterno(str, Enum):
    """Vincoli ai nodi di appoggio (suolo o struttura esterna).

    Classificazione secondo Scienza delle Costruzioni (Belluzzi, Odone):
    - Incastro:    3 reazioni (H, V, M) — blocca ux, uy, θ
    - Cerniera:    2 reazioni (H, V)    — blocca ux, uy; θ libero
    - Carrello:    1 reazione (N norm.) — blocca una traslazione; θ libero
    - Pattino:     2 reazioni (N, M)    — blocca una traslazione + rotazione
    - Pendolo:     1 reazione assiale   — trasmette solo sforzo assiale
    - Bipendolo:   2 reazioni (H, V)    — ≡ cerniera tramite 2 bielle
    - Libero:      0 reazioni           — nodo interno non vincolato
    """
    INCASTRO    = "incastro"     # ux=0, uy=0, θ=0  | reaz: H, V, M
    CERNIERA    = "cerniera"     # ux=0, uy=0, θ≠0  | reaz: H, V
    CARRELLO_X  = "carrello_x"   # uy=0, ux≠0, θ≠0  | reaz: V   (scorre in X)
    CARRELLO_Y  = "carrello_y"   # ux=0, uy≠0, θ≠0  | reaz: H   (scorre in Y)
    PATTINO_X   = "pattino_x"    # uy=0, θ=0, ux≠0  | reaz: V,M (guidato in X)
    PATTINO_Y   = "pattino_y"    # ux=0, θ=0, uy≠0  | reaz: H,M (guidato in Y)
    PENDOLO     = "pendolo"      # 1 reaz. assiale lungo asse asta pendolo
    BIPENDOLO   = "bipendolo"    # 2 reaz. H,V (≡ cerniera tramite 2 bielle)
    LIBERO      = "libero"       # nodo non vincolato (nodo interno)


class TipoRilascioInterno(str, Enum):
    """Rilasci interni alle estremità delle aste.

    Determinano i fattori k e c nel metodo di Cross:
    - NODO_RIGIDO: k=4EI/L, c=+0.5 — piena continuità (c.a. monolitico)
    - CERNIERA:    k=3EI/L, c=0.0  — M=0 (giunto bullonato, trave Gerber)
    - MANICOTTO:   k=4EI/L, c=+0.5 — N=0 (giunto di dilatazione)
    - PATTINO:     k=EI/L,  c=-1.0 — V=0, rotaz. bloccata (sella Gerber, antisimm.)
    - BIPENDOLO:   k=3EI/L, c=0.0  — ≡ cerniera nel piano
    """
    NODO_RIGIDO = "nodo_rigido"
    CERNIERA    = "cerniera"
    MANICOTTO   = "manicotto"
    PATTINO     = "pattino"
    BIPENDOLO   = "bipendolo"


class TipoAsta(str, Enum):
    """Tipo elemento strutturale."""
    TRAVE     = "trave"
    PILASTRO  = "pilastro"
    SETTO     = "setto"
    MENSOLA   = "mensola"
    INCLINATA = "inclinata"
    PENDOLO   = "pendolo"   # asta biella: solo sforzo assiale, k flessionale = 0


class TipoCarico(str, Enum):
    """Tipo di carico applicabile a un'asta."""
    DISTRIBUITO_UNIFORME = "distribuito_uniforme"  # w [kg/cm]
    DISTRIBUITO_TRAPEZ   = "distribuito_trapez"    # w_sx, w_dx [kg/cm]
    CONCENTRATO          = "concentrato"           # P [kg] a posizione a [cm]
    MOMENTO_NODO         = "momento_nodo"          # M [kg·cm] al nodo i o j
    PESO_PROPRIO         = "peso_proprio"          # automatico da sezione+materiale


# ==============================================================================
# DATACLASS VINCOLI E RILASCI
# ==============================================================================

@dataclass
class VincoloEsterno:
    """Vincolo esterno a un nodo strutturale (appoggio al suolo o a struttura esterna).

    Args:
        tipo:               tipo di vincolo
        angolo_pendolo_deg: angolo del pendolo rispetto all'orizzontale [gradi]
                            usato solo per TipoVincoloEsterno.PENDOLO
        descrizione:        nota descrittiva (non influenza il calcolo)
    """
    tipo: TipoVincoloEsterno
    angolo_pendolo_deg: float = 90.0
    descrizione: str = ""

    @property
    def gdl_bloccati(self) -> tuple[bool, bool, bool]:
        """Ritorna (blocca_ux, blocca_uy, blocca_theta)."""
        mapping: dict[TipoVincoloEsterno, tuple[bool, bool, bool]] = {
            TipoVincoloEsterno.INCASTRO:   (True,  True,  True),
            TipoVincoloEsterno.CERNIERA:   (True,  True,  False),
            TipoVincoloEsterno.CARRELLO_X: (False, True,  False),
            TipoVincoloEsterno.CARRELLO_Y: (True,  False, False),
            TipoVincoloEsterno.PATTINO_X:  (False, True,  True),
            TipoVincoloEsterno.PATTINO_Y:  (True,  False, True),
            TipoVincoloEsterno.PENDOLO:    (False, False, False),  # gestito separatamente
            TipoVincoloEsterno.BIPENDOLO:  (True,  True,  False),
            TipoVincoloEsterno.LIBERO:     (False, False, False),
        }
        return mapping.get(self.tipo, (False, False, False))

    @property
    def blocca_rotazione(self) -> bool:
        """True se il nodo non può ruotare (non partecipa alla distribuzione Cross)."""
        return self.gdl_bloccati[2]

    @property
    def n_reazioni(self) -> int:
        """Numero di componenti di reazione."""
        if self.tipo == TipoVincoloEsterno.PENDOLO:
            return 1
        return sum(self.gdl_bloccati)

    def simbolo_grafico(self) -> str:
        """Simbolo per la GUI (canvas Qt)."""
        simboli = {
            TipoVincoloEsterno.INCASTRO:   "▪",
            TipoVincoloEsterno.CERNIERA:   "○",
            TipoVincoloEsterno.CARRELLO_X: "⊥",
            TipoVincoloEsterno.CARRELLO_Y: "∥",
            TipoVincoloEsterno.PATTINO_X:  "⊟",
            TipoVincoloEsterno.PATTINO_Y:  "⊞",
            TipoVincoloEsterno.PENDOLO:    "/",
            TipoVincoloEsterno.BIPENDOLO:  "//",
            TipoVincoloEsterno.LIBERO:     "◯",
        }
        return simboli.get(self.tipo, "?")

    def descrizione_gdl(self) -> str:
        """Descrizione testuale dei GDL bloccati."""
        nomi = ["ux", "uy", "θ"]
        bloccati = [n for n, b in zip(nomi, self.gdl_bloccati) if b]
        return ", ".join(bloccati) if bloccati else "—"

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo.value,
            "angolo_pendolo_deg": self.angolo_pendolo_deg,
            "descrizione": self.descrizione,
            "gdl_bloccati": list(self.gdl_bloccati),
            "n_reazioni": self.n_reazioni,
        }


@dataclass
class RilascioEstremita:
    """Rilascio interno all'estremità di un'asta (vincolo interno).

    Determina i fattori di rigidezza k e carry-over c per il metodo di Cross.
    Il fattore k e c dipendono dalla condizione del nodo LONTANO (far end):

    Nodo lontano NODO_RIGIDO: k = 4EI/L, c = +0.5  (piena continuità)
    Nodo lontano CERNIERA:    k = 3EI/L, c =  0.0  (cerniera semplice)
    Nodo lontano PATTINO:     k =  EI/L, c = -1.0  (guidato, antisimmetrico)
    Nodo lontano BIPENDOLO:   k = 3EI/L, c =  0.0  (≡ cerniera)
    Nodo lontano MANICOTTO:   k = 4EI/L, c = +0.5  (N rilasciato, M invariato)

    Riferimento: Pozzati vol.II §3.3; Santarella cap. 3.
    """
    tipo: TipoRilascioInterno

    @property
    def k_factor(self) -> float:
        """Fattore moltiplicativo per k = k_factor × E × I / L."""
        mapping = {
            TipoRilascioInterno.NODO_RIGIDO: 4.0,
            TipoRilascioInterno.CERNIERA:    3.0,
            TipoRilascioInterno.BIPENDOLO:   3.0,
            TipoRilascioInterno.MANICOTTO:   4.0,
            TipoRilascioInterno.PATTINO:     1.0,
        }
        return mapping[self.tipo]

    @property
    def carry_over(self) -> float:
        """Fattore di trasporto (carry-over) c."""
        mapping = {
            TipoRilascioInterno.NODO_RIGIDO:  0.5,
            TipoRilascioInterno.CERNIERA:     0.0,
            TipoRilascioInterno.BIPENDOLO:    0.0,
            TipoRilascioInterno.MANICOTTO:    0.5,
            TipoRilascioInterno.PATTINO:     -1.0,
        }
        return mapping[self.tipo]

    @property
    def rilascia_momento(self) -> bool:
        """True se l'estremità ha M = 0 (cerniera o bipendolo)."""
        return self.tipo in (TipoRilascioInterno.CERNIERA, TipoRilascioInterno.BIPENDOLO)

    @property
    def rilascia_assiale(self) -> bool:
        """True se l'estremità ha N = 0 (manicotto)."""
        return self.tipo == TipoRilascioInterno.MANICOTTO

    def descrizione_k_c(self) -> str:
        """Stringa descrittiva k e c per tabulato."""
        return f"k = {self.k_factor:.0f}EI/L, c = {self.carry_over:+.1f}"

    def simbolo_grafico(self) -> str:
        """Simbolo per la GUI canvas."""
        simboli = {
            TipoRilascioInterno.NODO_RIGIDO: "",    # nessun simbolo (default)
            TipoRilascioInterno.CERNIERA:    "○",   # cerchietto
            TipoRilascioInterno.MANICOTTO:   "□",   # quadratino
            TipoRilascioInterno.PATTINO:     "⊟",   # pattino
            TipoRilascioInterno.BIPENDOLO:   "⊙",   # doppia cerniera
        }
        return simboli.get(self.tipo, "")

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo.value,
            "k_factor": self.k_factor,
            "carry_over": self.carry_over,
            "rilascia_momento": self.rilascia_momento,
            "rilascia_assiale": self.rilascia_assiale,
        }


# Costanti per rilasci predefiniti (evita istanziazione ripetuta)
RILASCIO_RIGIDO    = RilascioEstremita(TipoRilascioInterno.NODO_RIGIDO)
RILASCIO_CERNIERA  = RilascioEstremita(TipoRilascioInterno.CERNIERA)
RILASCIO_MANICOTTO = RilascioEstremita(TipoRilascioInterno.MANICOTTO)
RILASCIO_PATTINO   = RilascioEstremita(TipoRilascioInterno.PATTINO)
RILASCIO_BIPENDOLO = RilascioEstremita(TipoRilascioInterno.BIPENDOLO)


# ==============================================================================
# DATACLASS CARICHI
# ==============================================================================

@dataclass
class CaricoAsta:
    """Carico applicato a un'asta.

    Args:
        tipo:         tipo di carico
        valore_sx:    valore al nodo i [kg/cm] per distribuito, [kg] per concentrato,
                      [kg·cm] per momento
        valore_dx:    valore al nodo j [kg/cm] — solo per DISTRIBUITO_TRAPEZ
        posizione_a:  distanza da nodo i [cm] — solo per CONCENTRATO
        direzione:    "Y" = verticale (default), "X" = orizzontale
        al_nodo_i:    True se MOMENTO_NODO è applicato al nodo i, False se al nodo j
        descrizione:  nota descrittiva (non influenza il calcolo)
    """
    tipo: TipoCarico
    valore_sx: float
    valore_dx: float = 0.0
    posizione_a: float = 0.0
    direzione: str = "Y"
    al_nodo_i: bool = True
    descrizione: str = ""

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo.value,
            "valore_sx": self.valore_sx,
            "valore_dx": self.valore_dx,
            "posizione_a": self.posizione_a,
            "direzione": self.direzione,
            "al_nodo_i": self.al_nodo_i,
            "descrizione": self.descrizione,
        }


# ==============================================================================
# DATACLASS SEZIONE
# ==============================================================================

@dataclass
class SezioneTelaio:
    """Proprietà sezionali di un'asta per il calcolo a telaio.

    Contiene le sole proprietà rilevanti per il metodo di Cross-Pozzati:
    area, inerzia, modulo resistente, modulo elastico, peso specifico.
    Può essere popolata direttamente o importata da apps/sections SectionProperties.

    Args:
        tipo:         "RECTANGULAR", "T_SECTION", "I_SECTION", ecc.
        b:            larghezza [cm]
        h:            altezza [cm]
        I:            momento d'inerzia [cm⁴] (calcolato = b·h³/12 per rettangolare)
        A:            area [cm²]
        Wx:           modulo resistente superiore/inferiore [cm³] (= I / (h/2) per simm.)
        E:            modulo elastico materiale [kg/cm²]
        gamma:        peso specifico materiale [kg/cm³] (cls: ~2.5e-3 kg/cm³)
        section_ref:  chiave in section_manager (opzionale, per dropdown Qt)
        extra:        parametri aggiuntivi (alette T, ali I, ecc.)
    """
    tipo: str
    b: float        # [cm]
    h: float        # [cm]
    I: float        # [cm⁴]
    A: float        # [cm²]
    Wx: float       # [cm³]
    E: float        # [kg/cm²]
    gamma: float    # [kg/cm³]
    section_ref: str = ""
    extra: dict = field(default_factory=dict)

    @classmethod
    def rettangolare(
        cls,
        b: float,
        h: float,
        E: float = 300_000.0,
        gamma: float = 2.5e-3,
    ) -> SezioneTelaio:
        """Crea una sezione rettangolare con proprietà calcolate automaticamente.

        Args:
            b:     larghezza [cm]
            h:     altezza [cm]
            E:     modulo elastico [kg/cm²] (default cls ~300 kg/cm², calcestruzzo storico)
            gamma: peso specifico [kg/cm³] (default 2.5e-3 = 2500 kg/m³)
        """
        A = b * h
        I = b * h**3 / 12.0
        Wx = I / (h / 2.0)
        return cls(tipo="RECTANGULAR", b=b, h=h, I=I, A=A, Wx=Wx, E=E, gamma=gamma)

    def EI(self) -> float:
        """Rigidezza flessionale EI [kg·cm²]."""
        return self.E * self.I

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "b": round(self.b, 2),
            "h": round(self.h, 2),
            "I": round(self.I, 2),
            "A": round(self.A, 2),
            "Wx": round(self.Wx, 2),
            "E": round(self.E, 0),
            "gamma": self.gamma,
            "section_ref": self.section_ref,
        }


# ==============================================================================
# DATACLASS NODO
# ==============================================================================

@dataclass
class NodoTelaio:
    """Nodo strutturale del telaio piano.

    Args:
        id:       identificatore univoco intero (usato in AstaTelaio.nodo_i/j)
        x:        coordinata orizzontale [cm] (origine: appoggio sinistro al suolo)
        y:        coordinata verticale [cm]   (origine: piano di fondazione)
        vincolo:  vincolo esterno del nodo (default: nodo libero interno)
        piano:    piano di appartenenza (0=fondazione, 1=1° piano, 2=2° piano, ...)
        etichetta: stringa identificativa per tabulati (es. "A", "B1", "C2")
    """
    id: int
    x: float
    y: float
    vincolo: VincoloEsterno = field(
        default_factory=lambda: VincoloEsterno(TipoVincoloEsterno.LIBERO)
    )
    piano: int = 0
    etichetta: str = ""

    def __post_init__(self) -> None:
        if not self.etichetta:
            self.etichetta = str(self.id)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "vincolo": self.vincolo.to_dict(),
            "piano": self.piano,
            "etichetta": self.etichetta,
        }


# ==============================================================================
# DATACLASS ASTA
# ==============================================================================

@dataclass
class AstaTelaio:
    """Elemento strutturale del telaio piano (trave, pilastro, setto, mensola, ecc.).

    Args:
        id:          identificatore univoco intero
        nodo_i:      id del nodo di inizio (estremo i)
        nodo_j:      id del nodo di fine (estremo j)
        tipo:        tipo elemento strutturale
        sezione:     proprietà sezionali
        carichi:     carichi applicati sull'asta
        rilascio_i:  rilascio interno all'estremità i (default: nodo rigido)
        rilascio_j:  rilascio interno all'estremità j (default: nodo rigido)
        etichetta:   stringa identificativa per tabulati (es. "AB", "P1", "C12")

    Note sul metodo di Cross:
        La rigidezza k di un'asta rispetto al nodo i dipende dalla condizione
        del nodo LONTANO j (rilascio_j.k_factor):
          k_from_i = rilascio_j.k_factor × E × I / L
        Il carry-over da i verso j dipende da rilascio_j.carry_over.
    """
    id: int
    nodo_i: int
    nodo_j: int
    tipo: TipoAsta
    sezione: SezioneTelaio
    carichi: list[CaricoAsta] = field(default_factory=list)
    rilascio_i: RilascioEstremita = field(
        default_factory=lambda: RilascioEstremita(TipoRilascioInterno.NODO_RIGIDO)
    )
    rilascio_j: RilascioEstremita = field(
        default_factory=lambda: RilascioEstremita(TipoRilascioInterno.NODO_RIGIDO)
    )
    etichetta: str = ""

    def __post_init__(self) -> None:
        if not self.etichetta:
            self.etichetta = f"A{self.id}"

    # --------------------------------------------------------------------------
    # Proprietà per il metodo di Cross
    # --------------------------------------------------------------------------

    def rigidezza_from_i(self, L: float) -> float:
        """k dell'asta vista dal nodo i = rilascio_j.k_factor × EI / L.

        Se TipoAsta.PENDOLO: k = 0 (non partecipa alla distribuzione momenti).
        """
        if self.tipo == TipoAsta.PENDOLO:
            return 0.0
        return self.rilascio_j.k_factor * self.sezione.EI() / L

    def rigidezza_from_j(self, L: float) -> float:
        """k dell'asta vista dal nodo j = rilascio_i.k_factor × EI / L."""
        if self.tipo == TipoAsta.PENDOLO:
            return 0.0
        return self.rilascio_i.k_factor * self.sezione.EI() / L

    @property
    def carry_over_ij(self) -> float:
        """Carry-over da nodo i verso nodo j."""
        return self.rilascio_j.carry_over

    @property
    def carry_over_ji(self) -> float:
        """Carry-over da nodo j verso nodo i."""
        return self.rilascio_i.carry_over

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nodo_i": self.nodo_i,
            "nodo_j": self.nodo_j,
            "tipo": self.tipo.value,
            "sezione": self.sezione.to_dict(),
            "carichi": [c.to_dict() for c in self.carichi],
            "rilascio_i": self.rilascio_i.to_dict(),
            "rilascio_j": self.rilascio_j.to_dict(),
            "etichetta": self.etichetta,
        }


# ==============================================================================
# DATACLASS PIANO
# ==============================================================================

@dataclass
class PianoTelaio:
    """Dati di un piano del telaio (per calcolo sismico).

    Args:
        id_piano:        identificatore piano (1=primo piano, 2=secondo, ...)
        quota:           quota del solaio [cm] (y dei nodi trave di piano)
        peso_piano:      peso totale del piano [kg] (solaio + tamponature + metà colonne)
                         0.0 = da calcolare automaticamente
        forza_sismica_x: forza sismica orizzontale ondulatorio [kg] (calcolata da sisma_telaio)
        forza_sismica_z: forza sismica verticale sussultorio [kg]
        descrizione:     nota (es. "Piano tipo", "Copertura")
    """
    id_piano: int
    quota: float
    peso_piano: float = 0.0
    forza_sismica_x: float = 0.0
    forza_sismica_z: float = 0.0
    descrizione: str = ""

    def to_dict(self) -> dict:
        return {
            "id_piano": self.id_piano,
            "quota": round(self.quota, 1),
            "peso_piano": round(self.peso_piano, 1),
            "forza_sismica_x": round(self.forza_sismica_x, 1),
            "forza_sismica_z": round(self.forza_sismica_z, 1),
            "descrizione": self.descrizione,
        }


# ==============================================================================
# DATACLASS MODELLO TELAIO
# ==============================================================================

@dataclass
class ModelloTelaio:
    """Modello completo del telaio piano.

    Contiene nodi, aste, piani e parametri globali. Fornisce metodi
    di accesso e navigazione per l'algoritmo di Cross-Pozzati.

    Args:
        nome:          nome del progetto / telaio
        nodi:          lista nodi strutturali (qualsiasi numero)
        aste:          lista aste strutturali (qualsiasi numero)
        piani:         lista piani (ordinati per quota crescente)
        zona_sismica:  "non_sismico", "bassa", "media", "alta" (RD2229)
        note:          note generali
    """
    nome: str
    nodi: list[NodoTelaio]
    aste: list[AstaTelaio]
    piani: list[PianoTelaio] = field(default_factory=list)
    zona_sismica: str = "media"
    note: str = ""

    # --------------------------------------------------------------------------
    # Cache interna (evita ricalcoli)
    # --------------------------------------------------------------------------
    _nodi_map: dict[int, NodoTelaio] = field(default_factory=dict, repr=False)
    _aste_map: dict[int, AstaTelaio] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._nodi_map = {n.id: n for n in self.nodi}
        self._aste_map = {a.id: a for a in self.aste}

    def _aggiorna_cache(self) -> None:
        self._nodi_map = {n.id: n for n in self.nodi}
        self._aste_map = {a.id: a for a in self.aste}

    # --------------------------------------------------------------------------
    # Accesso per ID
    # --------------------------------------------------------------------------

    def nodo_by_id(self, id_nodo: int) -> NodoTelaio:
        return self._nodi_map[id_nodo]

    def asta_by_id(self, id_asta: int) -> AstaTelaio:
        return self._aste_map[id_asta]

    # --------------------------------------------------------------------------
    # Query strutturali
    # --------------------------------------------------------------------------

    def aste_per_nodo(self, id_nodo: int) -> list[AstaTelaio]:
        """Tutte le aste che convergono al nodo id_nodo."""
        return [a for a in self.aste if a.nodo_i == id_nodo or a.nodo_j == id_nodo]

    def aste_del_tipo(self, tipo: TipoAsta) -> list[AstaTelaio]:
        """Tutte le aste di un certo tipo."""
        return [a for a in self.aste if a.tipo == tipo]

    def colonne_piano(self, id_piano: int) -> list[AstaTelaio]:
        """Colonne (pilastri/setti) del piano id_piano.

        Sono le aste verticali i cui nodi appartengono al piano id_piano-1 (in basso)
        e id_piano (in alto). Semplificazione: aste tipo PILASTRO o SETTO con un
        nodo al piano id_piano-1 e uno al piano id_piano.
        """
        result = []
        for a in self.aste:
            if a.tipo not in (TipoAsta.PILASTRO, TipoAsta.SETTO):
                continue
            ni = self._nodi_map.get(a.nodo_i)
            nj = self._nodi_map.get(a.nodo_j)
            if ni is None or nj is None:
                continue
            piani_asta = {ni.piano, nj.piano}
            if piani_asta == {id_piano - 1, id_piano}:
                result.append(a)
        return result

    def travi_piano(self, id_piano: int) -> list[AstaTelaio]:
        """Travi (tipo TRAVE) del piano id_piano."""
        return [
            a for a in self.aste
            if a.tipo == TipoAsta.TRAVE
            and self._nodi_map.get(a.nodo_i, None) is not None
            and self._nodi_map[a.nodo_i].piano == id_piano
        ]

    def nodi_liberi(self) -> list[NodoTelaio]:
        """Nodi che partecipano alla distribuzione Cross (θ non bloccato)."""
        return [n for n in self.nodi if not n.vincolo.blocca_rotazione]

    def nodi_vincolati(self) -> list[NodoTelaio]:
        """Nodi con rotazione bloccata (incastro, pattino)."""
        return [n for n in self.nodi if n.vincolo.blocca_rotazione]

    # --------------------------------------------------------------------------
    # Geometria
    # --------------------------------------------------------------------------

    def lunghezza_asta(self, id_asta: int) -> float:
        """Lunghezza dell'asta [cm]."""
        a = self._aste_map[id_asta]
        ni = self._nodi_map[a.nodo_i]
        nj = self._nodi_map[a.nodo_j]
        return math.hypot(nj.x - ni.x, nj.y - ni.y)

    def angolo_asta_deg(self, id_asta: int) -> float:
        """Angolo dell'asta rispetto all'orizzontale [gradi]."""
        a = self._aste_map[id_asta]
        ni = self._nodi_map[a.nodo_i]
        nj = self._nodi_map[a.nodo_j]
        return math.degrees(math.atan2(nj.y - ni.y, nj.x - ni.x))

    def altezza_piano(self, id_piano: int) -> float:
        """Altezza interpiano [cm] tra piano id_piano-1 e id_piano."""
        p_inf = next((p for p in self.piani if p.id_piano == id_piano - 1), None)
        p_sup = next((p for p in self.piani if p.id_piano == id_piano), None)
        if p_inf is None or p_sup is None:
            # Fallback: usa le quote dei nodi fondazione e primo piano
            col = self.colonne_piano(id_piano)
            if not col:
                raise ValueError(f"Impossibile calcolare altezza piano {id_piano}")
            a = col[0]
            return self.lunghezza_asta(a.id)
        return p_sup.quota - p_inf.quota

    # --------------------------------------------------------------------------
    # Diagnostica strutturale
    # --------------------------------------------------------------------------

    def iperstaticita_esterna(self) -> int:
        """Grado di iperstaticità esterna = Σ(n_reazioni) - 3."""
        return sum(n.vincolo.n_reazioni for n in self.nodi) - 3

    def verifica_connettivita(self) -> list[str]:
        """Verifica che tutti gli id nodi nelle aste esistano nel modello."""
        problemi = []
        for a in self.aste:
            if a.nodo_i not in self._nodi_map:
                problemi.append(f"Asta {a.etichetta}: nodo_i={a.nodo_i} non trovato")
            if a.nodo_j not in self._nodi_map:
                problemi.append(f"Asta {a.etichetta}: nodo_j={a.nodo_j} non trovato")
        return problemi

    # --------------------------------------------------------------------------
    # Serializzazione
    # --------------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "zona_sismica": self.zona_sismica,
            "note": self.note,
            "nodi": [n.to_dict() for n in self.nodi],
            "aste": [a.to_dict() for a in self.aste],
            "piani": [p.to_dict() for p in self.piani],
        }

    @classmethod
    def from_dict(cls, d: dict) -> ModelloTelaio:
        """Ricostruisce il modello da un dict (es. da JSON)."""
        def _vincolo(v: dict) -> VincoloEsterno:
            return VincoloEsterno(
                tipo=TipoVincoloEsterno(v["tipo"]),
                angolo_pendolo_deg=v.get("angolo_pendolo_deg", 90.0),
                descrizione=v.get("descrizione", ""),
            )

        def _rilascio(r: dict) -> RilascioEstremita:
            return RilascioEstremita(TipoRilascioInterno(r["tipo"]))

        def _sezione(s: dict) -> SezioneTelaio:
            return SezioneTelaio(
                tipo=s["tipo"],
                b=s["b"], h=s["h"], I=s["I"], A=s["A"],
                Wx=s["Wx"], E=s["E"], gamma=s["gamma"],
                section_ref=s.get("section_ref", ""),
            )

        def _carico(c: dict) -> CaricoAsta:
            return CaricoAsta(
                tipo=TipoCarico(c["tipo"]),
                valore_sx=c["valore_sx"],
                valore_dx=c.get("valore_dx", 0.0),
                posizione_a=c.get("posizione_a", 0.0),
                direzione=c.get("direzione", "Y"),
                al_nodo_i=c.get("al_nodo_i", True),
                descrizione=c.get("descrizione", ""),
            )

        nodi = [
            NodoTelaio(
                id=n["id"], x=n["x"], y=n["y"],
                vincolo=_vincolo(n["vincolo"]),
                piano=n.get("piano", 0),
                etichetta=n.get("etichetta", str(n["id"])),
            )
            for n in d.get("nodi", [])
        ]

        aste = [
            AstaTelaio(
                id=a["id"],
                nodo_i=a["nodo_i"],
                nodo_j=a["nodo_j"],
                tipo=TipoAsta(a["tipo"]),
                sezione=_sezione(a["sezione"]),
                carichi=[_carico(c) for c in a.get("carichi", [])],
                rilascio_i=_rilascio(a.get("rilascio_i", {"tipo": "nodo_rigido"})),
                rilascio_j=_rilascio(a.get("rilascio_j", {"tipo": "nodo_rigido"})),
                etichetta=a.get("etichetta", f"A{a['id']}"),
            )
            for a in d.get("aste", [])
        ]

        piani = [
            PianoTelaio(
                id_piano=p["id_piano"],
                quota=p["quota"],
                peso_piano=p.get("peso_piano", 0.0),
                forza_sismica_x=p.get("forza_sismica_x", 0.0),
                forza_sismica_z=p.get("forza_sismica_z", 0.0),
                descrizione=p.get("descrizione", ""),
            )
            for p in d.get("piani", [])
        ]

        return cls(
            nome=d.get("nome", ""),
            nodi=nodi,
            aste=aste,
            piani=piani,
            zona_sismica=d.get("zona_sismica", "media"),
            note=d.get("note", ""),
        )
