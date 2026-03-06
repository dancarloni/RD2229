"""Modello cordolo — CA e metallico — per muratura.

Cordolo sommitale/intermedio per edifici in muratura secondo:
- NTC2018 §4.5.6.2 (cordoli obbligatori)
- NTC2018 §7.8.1.6 (requisiti sismici cordoli)
- DM 20/11/1987

Tipi supportati:
1. Cordolo in CA (calcestruzzo armato)
2. Cordolo metallico (profilo singolo)
3. Cordolo metallico reticolare (traliccio piano)

Unità: cm per geometria, kg per forze, kg/cm² per tensioni.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TipoCordolo(str, Enum):
    """Tipo di cordolo."""
    CA = "ca"                           # calcestruzzo armato
    METALLICO_SINGOLO = "metallico_singolo"   # profilo acciaio singolo
    METALLICO_RETICOLARE = "metallico_reticolare"  # traliccio acciaio


class PosizioneCordolo(str, Enum):
    """Posizione del cordolo nell'edificio."""
    SOMMITALE = "sommitale"             # in sommità alla muratura
    INTERMEDIO = "intermedio"           # a livello di solaio intermedio
    FONDAZIONE = "fondazione"           # alla base della muratura


@dataclass
class CordoloCA:
    """Cordolo in calcestruzzo armato."""
    # Geometria sezione
    b: float                     # larghezza [cm] (≥ spessore muro)
    h: float                     # altezza [cm] (min 20 cm NTC2018)

    # Armatura longitudinale
    n_barre_sup: int = 2         # numero barre superiori
    n_barre_inf: int = 2         # numero barre inferiori
    phi_long: float = 1.6        # diametro barre longitudinali [cm]

    # Armatura trasversale (staffe)
    phi_staffe: float = 0.8      # diametro staffe [cm]
    passo_staffe: float = 20.0   # passo staffe [cm]

    # Copriferro
    c: float = 3.0               # copriferro [cm]

    # Materiali
    sigma_c_adm: float = 60.0    # σ_c ammissibile cls [kg/cm²]
    sigma_s_adm: float = 2600.0  # σ_s ammissibile acciaio [kg/cm²]

    @property
    def A_s_sup(self) -> float:
        """Area armatura superiore [cm²]."""
        return self.n_barre_sup * math.pi * self.phi_long ** 2 / 4

    @property
    def A_s_inf(self) -> float:
        """Area armatura inferiore [cm²]."""
        return self.n_barre_inf * math.pi * self.phi_long ** 2 / 4

    @property
    def A_s_tot(self) -> float:
        """Area armatura totale [cm²]."""
        return self.A_s_sup + self.A_s_inf

    @property
    def A_staffa(self) -> float:
        """Area singola staffa (2 bracci) [cm²]."""
        return 2 * math.pi * self.phi_staffe ** 2 / 4

    @property
    def A_cls(self) -> float:
        """Area sezione cls [cm²]."""
        return self.b * self.h

    @property
    def d(self) -> float:
        """Altezza utile [cm]."""
        return self.h - self.c - self.phi_staffe - self.phi_long / 2

    def verifica_minimi_ntc2018(self) -> list[str]:
        """Verifica minimi geometrici e di armatura NTC2018 §7.8.1.6.

        Returns:
            Lista di messaggi di non conformità (vuota se tutto OK).
        """
        problemi: list[str] = []

        if self.h < 20:
            problemi.append(f"h={self.h:.0f} cm < 20 cm (minimo NTC2018 §7.8.1.6)")

        # Armatura minima: 8 cm² (4Φ16 o equivalente)
        if self.A_s_tot < 8.0:
            problemi.append(
                f"A_s = {self.A_s_tot:.2f} cm² < 8.0 cm² "
                f"(minimo 4Φ16 NTC2018 §7.8.1.6)"
            )

        # Staffe Φ6 passo max 25 cm
        if self.phi_staffe < 0.6:
            problemi.append(f"Φ_staffe={self.phi_staffe:.1f} cm < Φ6 (minimo)")
        if self.passo_staffe > 25:
            problemi.append(f"passo staffe={self.passo_staffe:.0f} cm > 25 cm (max)")

        return problemi


@dataclass
class CordoloMetallico:
    """Cordolo metallico (profilo singolo o doppio)."""
    # Profilo
    nome_profilo: str = ""           # es. "IPE 200", "HEA 160"
    A: float = 0.0                   # area profilo [cm²]
    Wx: float = 0.0                  # modulo resistente asse forte [cm³]
    Wy: float = 0.0                  # modulo resistente asse debole [cm³]
    Ix: float = 0.0                  # momento d'inerzia [cm⁴]
    h: float = 0.0                   # altezza profilo [cm]

    # Materiale
    tipo_acciaio: str = "Fe430"
    sigma_adm: float = 1900.0        # tensione ammissibile [kg/cm²]

    # Connessione alla muratura
    n_ancoraggi: int = 4             # numero barre ancoraggio per metro
    phi_ancoraggio: float = 1.6      # diametro barre ancoraggio [cm]
    L_ancoraggio: float = 30.0       # lunghezza ancoraggio nella muratura [cm]

    @property
    def M_Rd(self) -> float:
        """Momento resistente TA [kg·cm]."""
        return self.sigma_adm * self.Wx

    @property
    def V_Rd(self) -> float:
        """Taglio resistente approssimato TA [kg]."""
        tau_adm = self.sigma_adm / math.sqrt(3)
        # Area anima approssimata
        A_anima = self.A * 0.4  # stima conservativa
        return tau_adm * A_anima

    @property
    def A_ancoraggio_per_m(self) -> float:
        """Area ancoraggio per metro lineare [cm²/m]."""
        return self.n_ancoraggi * math.pi * self.phi_ancoraggio ** 2 / 4


@dataclass
class Cordolo:
    """Modello unificato cordolo (CA o metallico)."""
    tipo: TipoCordolo
    posizione: PosizioneCordolo = PosizioneCordolo.SOMMITALE
    lunghezza: float = 0.0           # lunghezza cordolo [cm]
    spessore_muro: float = 0.0       # spessore muro su cui poggia [cm]

    # Sollecitazioni
    N: float = 0.0                   # sforzo assiale [kg]
    Mx: float = 0.0                  # momento flettente [kg·cm]
    V: float = 0.0                   # taglio [kg]

    # Dettaglio tipo
    ca: Optional[CordoloCA] = None
    metallico: Optional[CordoloMetallico] = None


@dataclass
class RisultatoCordolo:
    """Risultato verifica cordolo."""
    tipo: str
    posizione: str

    # Verifiche
    verifica_flessione: bool = False
    verifica_taglio: bool = False
    verifica_minimi: bool = False
    verifica_globale: bool = False

    # Sfruttamenti
    sfruttamento_flessione: float = 0.0
    sfruttamento_taglio: float = 0.0

    # Minimi
    problemi_minimi: list[str] = field(default_factory=list)

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "posizione": self.posizione,
            "verifica_flessione": self.verifica_flessione,
            "verifica_taglio": self.verifica_taglio,
            "verifica_minimi": self.verifica_minimi,
            "verifica_globale": self.verifica_globale,
            "sfruttamento_flessione": round(self.sfruttamento_flessione, 4),
            "sfruttamento_taglio": round(self.sfruttamento_taglio, 4),
            "problemi_minimi": self.problemi_minimi,
            "passaggi": self.passaggi,
        }


def verifica_cordolo(cordolo: Cordolo) -> RisultatoCordolo:
    """Verifica cordolo (CA o metallico).

    Args:
        cordolo: modello cordolo

    Returns:
        RisultatoCordolo
    """
    passaggi: list[str] = []

    res = RisultatoCordolo(
        tipo=cordolo.tipo.value,
        posizione=cordolo.posizione.value,
    )

    passaggi.append(
        f"Cordolo {cordolo.tipo.value}, posizione: {cordolo.posizione.value}"
    )

    if cordolo.tipo == TipoCordolo.CA and cordolo.ca:
        _verifica_cordolo_ca(cordolo, res, passaggi)
    elif cordolo.tipo == TipoCordolo.METALLICO_SINGOLO and cordolo.metallico:
        _verifica_cordolo_metallico(cordolo, res, passaggi)
    else:
        passaggi.append("ERRORE: dati cordolo mancanti")

    res.passaggi = passaggi
    return res


def _verifica_cordolo_ca(
    cordolo: Cordolo,
    res: RisultatoCordolo,
    passaggi: list[str],
) -> None:
    """Verifica cordolo in CA."""
    ca = cordolo.ca
    assert ca is not None

    passaggi.append(f"Sezione: {ca.b:.0f}×{ca.h:.0f} cm, d={ca.d:.1f} cm")
    passaggi.append(f"Armatura: {ca.n_barre_sup+ca.n_barre_inf}Φ{ca.phi_long*10:.0f}, A_s={ca.A_s_tot:.2f} cm²")

    # Minimi NTC2018
    problemi = ca.verifica_minimi_ntc2018()
    res.problemi_minimi = problemi
    res.verifica_minimi = len(problemi) == 0

    if problemi:
        for p in problemi:
            passaggi.append(f"⚠ {p}")
    else:
        passaggi.append("Minimi NTC2018: OK")

    # Flessione TA semplificata: M_Rd = σ_s × A_s × 0.9d
    M_Rd = ca.sigma_s_adm * ca.A_s_inf * 0.9 * ca.d
    if M_Rd > 0:
        res.sfruttamento_flessione = abs(cordolo.Mx) / M_Rd
    res.verifica_flessione = abs(cordolo.Mx) <= M_Rd

    passaggi.append(
        f"M_Rd = σ_s×A_s×0.9d = {ca.sigma_s_adm:.0f}×{ca.A_s_inf:.2f}×0.9×{ca.d:.1f} "
        f"= {M_Rd:.0f} kg·cm"
    )
    passaggi.append(
        f"|Mx| = {abs(cordolo.Mx):.0f} {'≤' if res.verifica_flessione else '>'} "
        f"M_Rd = {M_Rd:.0f} → {'OK' if res.verifica_flessione else 'NON VERIFICATO'}"
    )

    # Taglio TA: V_Rd = τ_c × b × d (approssimato)
    tau_c = 4.0  # τ_c approssimato [kg/cm²]
    V_Rd_cls = tau_c * ca.b * ca.d
    # Contributo staffe
    V_Rd_staffe = ca.sigma_s_adm * ca.A_staffa * ca.d / ca.passo_staffe
    V_Rd = V_Rd_cls + V_Rd_staffe

    if V_Rd > 0:
        res.sfruttamento_taglio = abs(cordolo.V) / V_Rd
    res.verifica_taglio = abs(cordolo.V) <= V_Rd

    passaggi.append(
        f"|V| = {abs(cordolo.V):.0f} {'≤' if res.verifica_taglio else '>'} "
        f"V_Rd = {V_Rd:.0f} → {'OK' if res.verifica_taglio else 'NON VERIFICATO'}"
    )

    res.verifica_globale = (
        res.verifica_flessione and res.verifica_taglio and res.verifica_minimi
    )


def _verifica_cordolo_metallico(
    cordolo: Cordolo,
    res: RisultatoCordolo,
    passaggi: list[str],
) -> None:
    """Verifica cordolo metallico (profilo singolo)."""
    met = cordolo.metallico
    assert met is not None

    passaggi.append(f"Profilo: {met.nome_profilo}, acciaio: {met.tipo_acciaio}")
    passaggi.append(f"σ_adm = {met.sigma_adm:.0f} kg/cm²")

    # Flessione
    M_Rd = met.M_Rd
    if M_Rd > 0:
        res.sfruttamento_flessione = abs(cordolo.Mx) / M_Rd
    res.verifica_flessione = abs(cordolo.Mx) <= M_Rd

    passaggi.append(
        f"M_Rd = σ_adm×Wx = {met.sigma_adm:.0f}×{met.Wx:.1f} = {M_Rd:.0f} kg·cm"
    )
    passaggi.append(
        f"|Mx| = {abs(cordolo.Mx):.0f} {'≤' if res.verifica_flessione else '>'} "
        f"M_Rd = {M_Rd:.0f} → {'OK' if res.verifica_flessione else 'NON VERIFICATO'}"
    )

    # Taglio
    V_Rd = met.V_Rd
    if V_Rd > 0:
        res.sfruttamento_taglio = abs(cordolo.V) / V_Rd
    res.verifica_taglio = abs(cordolo.V) <= V_Rd

    passaggi.append(
        f"|V| = {abs(cordolo.V):.0f} {'≤' if res.verifica_taglio else '>'} "
        f"V_Rd = {V_Rd:.0f} → {'OK' if res.verifica_taglio else 'NON VERIFICATO'}"
    )

    # Minimi (larghezza minima ≥ spessore muro)
    res.problemi_minimi = []
    if cordolo.spessore_muro > 0 and met.h < cordolo.spessore_muro * 0.5:
        res.problemi_minimi.append(
            f"h profilo={met.h:.0f} cm < 0.5×t_muro={cordolo.spessore_muro*0.5:.0f} cm"
        )
    res.verifica_minimi = len(res.problemi_minimi) == 0

    res.verifica_globale = (
        res.verifica_flessione and res.verifica_taglio and res.verifica_minimi
    )


# ═══════════════════════════════════════════════════════════
#  Catene e paletti — E.5
# ═══════════════════════════════════════════════════════════

class TipoPiastra(str, Enum):
    """Tipo piastra di ancoraggio catena."""
    CIRCOLARE = "circolare"
    QUADRATA = "quadrata"
    A_PALETTO = "a_paletto"     # paletto passante


@dataclass
class InputCatena:
    """Input per verifica catena e paletto."""
    # Catena
    phi_catena: float = 2.0          # diametro catena [cm]
    sigma_s_adm: float = 1400.0      # tensione ammissibile catena [kg/cm²]

    # Forza di progetto
    F: float = 0.0                   # forza nella catena [kg]

    # Piastra
    tipo_piastra: TipoPiastra = TipoPiastra.QUADRATA
    lato_piastra: float = 20.0       # lato o diametro piastra [cm]
    spessore_piastra: float = 1.5    # spessore piastra [cm]

    # Muratura
    fd_mur: float = 10.0             # resistenza compressione muratura [kg/cm²]
    spessore_muro: float = 30.0      # spessore muro [cm]


@dataclass
class RisultatoCatena:
    """Risultato verifica catena e paletto."""
    F: float                         # forza [kg]

    # Catena
    A_catena: float                  # area catena [cm²]
    sigma_catena: float              # tensione catena [kg/cm²]
    verifica_trazione: bool

    # Piastra
    A_piastra: float                 # area piastra [cm²]
    sigma_piastra: float             # pressione su muratura [kg/cm²]
    verifica_punzonamento: bool

    sfruttamento_trazione: float
    sfruttamento_punzonamento: float

    verifica_globale: bool
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "F": round(self.F, 1),
            "sigma_catena": round(self.sigma_catena, 1),
            "sigma_piastra": round(self.sigma_piastra, 2),
            "verifica_trazione": self.verifica_trazione,
            "verifica_punzonamento": self.verifica_punzonamento,
            "verifica_globale": self.verifica_globale,
            "passaggi": self.passaggi,
        }


def verifica_catena(inp: InputCatena) -> RisultatoCatena:
    """Verifica catena a trazione e punzonamento locale piastra.

    1. Trazione catena: σ = F / A_catena ≤ σ_s_adm
    2. Punzonamento piastra: σ_p = F / A_piastra ≤ fd_muratura

    Args:
        inp: dati di input

    Returns:
        RisultatoCatena
    """
    passaggi: list[str] = []

    # Area catena
    A_catena = math.pi * inp.phi_catena ** 2 / 4
    sigma_catena = abs(inp.F) / A_catena if A_catena > 0 else 0.0

    passaggi.append(f"Catena: Φ{inp.phi_catena*10:.0f}, A = {A_catena:.2f} cm²")
    passaggi.append(f"σ_catena = F/A = {abs(inp.F):.0f}/{A_catena:.2f} = {sigma_catena:.1f} kg/cm²")

    verifica_trazione = sigma_catena <= inp.sigma_s_adm
    sfruttamento_traz = sigma_catena / inp.sigma_s_adm if inp.sigma_s_adm > 0 else 0

    passaggi.append(
        f"σ_catena = {sigma_catena:.1f} {'≤' if verifica_trazione else '>'} "
        f"σ_s_adm = {inp.sigma_s_adm:.0f} → {'OK' if verifica_trazione else 'NON VERIFICATO'}"
    )

    # Area piastra
    if inp.tipo_piastra == TipoPiastra.CIRCOLARE:
        A_piastra = math.pi * inp.lato_piastra ** 2 / 4
    elif inp.tipo_piastra == TipoPiastra.QUADRATA:
        A_piastra = inp.lato_piastra ** 2
    else:
        # Paletto: area rettangolare (lato × spessore_muro)
        A_piastra = inp.lato_piastra * inp.spessore_muro

    sigma_piastra = abs(inp.F) / A_piastra if A_piastra > 0 else 0.0

    passaggi.append(
        f"Piastra {inp.tipo_piastra.value}: "
        f"A = {A_piastra:.1f} cm², σ = {sigma_piastra:.2f} kg/cm²"
    )

    verifica_punz = sigma_piastra <= inp.fd_mur
    sfruttamento_punz = sigma_piastra / inp.fd_mur if inp.fd_mur > 0 else 0

    passaggi.append(
        f"σ_piastra = {sigma_piastra:.2f} {'≤' if verifica_punz else '>'} "
        f"fd_mur = {inp.fd_mur:.1f} → {'OK' if verifica_punz else 'NON VERIFICATO'}"
    )

    verifica_globale = verifica_trazione and verifica_punz
    stato = "VERIFICATO" if verifica_globale else "NON VERIFICATO"
    passaggi.append(f"═══ ESITO: {stato} ═══")

    return RisultatoCatena(
        F=abs(inp.F),
        A_catena=A_catena,
        sigma_catena=sigma_catena,
        verifica_trazione=verifica_trazione,
        A_piastra=A_piastra,
        sigma_piastra=sigma_piastra,
        verifica_punzonamento=verifica_punz,
        sfruttamento_trazione=sfruttamento_traz,
        sfruttamento_punzonamento=sfruttamento_punz,
        verifica_globale=verifica_globale,
        passaggi=passaggi,
    )
