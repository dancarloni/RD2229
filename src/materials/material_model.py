"""Modello dei materiali strutturali.

Modello completo per calcestruzzo, acciaio, muratura con:
- Parametri primari (da normativa o input utente)
- Parametri derivati (calcolati automaticamente dai primari)
- Override manuale dei parametri derivati (sovrascrivibili dall'utente)
- Serializzazione JSON
- Integrazione con archivio centralizzato

UNITÀ DI MISURA (sistema interno):
- Resistenze (f_ck, f_yk, f_k) → kg/cm²
- Moduli elastici (E, G) → kg/cm²
- Densità → kg/m³
- Coefficiente di Poisson → adimensionale

Ogni parametro derivato:
- Si ricalcola automaticamente se il parametro primario cambia
- Può essere sovrascritto manualmente dall'utente (override)
- Ha un mini-bottone "ricalcola" per ripristinare il calcolo automatico

Riferimenti normativi:
- NTC2018 (DM 17/01/2018) + Circ. 7/2019 n. 7 C.S.LL.PP.
- RD 2229/1939
- DM 14/02/1992
- DM 09/01/1996
- EC2 (EN 1992-1-1)
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# --- Valori di default Poisson per tipo materiale (da letteratura) ---
_POISSON_DEFAULT: dict[str, float] = {
    "calcestruzzo": 0.20,    # EC2 §3.1.3 → ν = 0.2
    "acciaio": 0.30,         # EC3 §3.2.6 → ν = 0.3
    "muratura": 0.15,        # Letteratura → ν = 0.10÷0.25, tipico 0.15
    "legno": 0.40,           # Valore indicativo longitudinale-trasversale
}


@dataclass
class ParametroDerivato:
    """Stato di un parametro derivato.

    Attributi:
        valore: Valore corrente del parametro.
        override: True se l'utente ha sovrascritto il valore calcolato.
        formula: Descrizione della formula usata per il calcolo automatico.
    """
    valore: float = 0.0
    override: bool = False
    formula: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serializza in dizionario."""
        return {
            "valore": self.valore,
            "override": self.override,
            "formula": self.formula,
        }

    @classmethod
    def from_dict(cls, dati: dict[str, Any]) -> ParametroDerivato:
        """Deserializza da dizionario."""
        return cls(
            valore=dati.get("valore", 0.0),
            override=dati.get("override", False),
            formula=dati.get("formula", ""),
        )


@dataclass
class Material:
    """Modello completo di un materiale strutturale.

    Supporta calcestruzzo, acciaio, muratura con parametri primari
    e derivati. I parametri derivati si ricalcolano automaticamente
    quando cambiano i primari (salvo override utente).

    Attributi principali:
        material_id: Identificatore univoco.
        descrizione: Descrizione testuale (es. "C25/30 — NTC2018").
        famiglia: Famiglia materiale ("calcestruzzo", "acciaio", "muratura").
        norma_riferimento: Norma di riferimento (es. "NTC2018", "RD2229").
        densita_kg_m3: Densità [kg/m³].

    Attributi calcestruzzo (famiglia="calcestruzzo"):
        f_ck: Resistenza caratteristica cilindrica [kg/cm²].
        gamma_c: Coefficiente parziale calcestruzzo (1.50 NTC2018, 1.0 TA).
        alpha_cc: Coefficiente per effetti a lungo termine (0.85 NTC2018).

    Attributi acciaio (famiglia="acciaio"):
        f_yk: Resistenza caratteristica snervamento [kg/cm²].
        gamma_s: Coefficiente parziale acciaio (1.15 NTC2018, 1.0 TA).

    Attributi muratura (famiglia="muratura"):
        f_k: Resistenza caratteristica a compressione [kg/cm²].
        f_vk0: Resistenza caratteristica a taglio senza σ [kg/cm²].
        gamma_M: Coefficiente parziale muratura.

    Attributi comuni:
        E: Modulo elastico [kg/cm²].
        nu: Coefficiente di Poisson (default da letteratura, editabile).
    """
    # --- Identificazione ---
    material_id: str = ""
    descrizione: str = ""
    famiglia: str = "calcestruzzo"  # "calcestruzzo", "acciaio", "muratura"
    norma_riferimento: str = "NTC2018"
    densita_kg_m3: float = 2500.0

    # --- Parametri primari comuni ---
    E: float = 0.0               # Modulo elastico [kg/cm²]
    nu: float = 0.0              # Coefficiente di Poisson

    # --- Parametri primari calcestruzzo ---
    f_ck: float = 0.0            # Resistenza caratteristica cilindrica [kg/cm²]
    gamma_c: float = 1.50        # Coefficiente parziale cls (1.0 per TA)
    alpha_cc: float = 0.85       # Effetti lungo termine (NTC2018)

    # --- Parametri primari calcestruzzo TA (norme storiche) ---
    sigma_c28: float = 0.0       # Resistenza cubica a 28gg [kg/cm²] (TA)
    sigma_c_adm: float = 0.0     # Tensione ammissibile cls [kg/cm²] (TA)
    tau_c0_adm: float = 0.0      # Tensione tangenziale amm. cls [kg/cm²] (TA)
    tau_c1_adm: float = 0.0      # Tensione tangenziale amm. cls con staffe [kg/cm²] (TA)
    n_omogenizzazione: float = 0.0  # Coefficiente di omogenizzazione (TA)

    # --- Parametri primari acciaio ---
    f_yk: float = 0.0            # Resistenza caratteristica snervamento [kg/cm²]
    gamma_s: float = 1.15        # Coefficiente parziale acciaio (1.0 per TA)

    # --- Parametri primari acciaio TA ---
    sigma_s_adm: float = 0.0     # Tensione ammissibile acciaio [kg/cm²] (TA)

    # --- Parametri primari muratura ---
    f_k: float = 0.0             # Resistenza caratteristica a compressione [kg/cm²]
    f_vk0: float = 0.0           # Resistenza caratteristica a taglio senza σ [kg/cm²]
    gamma_M: float = 2.0         # Coefficiente parziale muratura

    # --- Parametri primari legno (EN 338 / EN 14080 / NTC2018 §4.4) ---
    f_mk: float = 0.0            # Resistenza caratteristica a flessione [kg/cm²]
    f_t0k: float = 0.0           # Resistenza car. trazione parallela [kg/cm²]
    f_t90k: float = 0.0          # Resistenza car. trazione perpendicolare [kg/cm²]
    f_c0k: float = 0.0           # Resistenza car. compressione parallela [kg/cm²]
    f_c90k: float = 0.0          # Resistenza car. compressione perpendicolare [kg/cm²]
    f_vk: float = 0.0            # Resistenza caratteristica a taglio [kg/cm²]
    E_0_mean: float = 0.0        # Modulo elastico medio parallelo alle fibre [kg/cm²]
    E_90_mean: float = 0.0       # Modulo elastico medio perpendicolare [kg/cm²]
    G_mean: float = 0.0          # Modulo di taglio medio [kg/cm²]
    classe_servizio: int = 1     # Classe di servizio (1, 2, 3)

    # --- Parametri derivati (calcolati automaticamente) ---
    _derivati: dict[str, ParametroDerivato] = field(default_factory=dict)

    # --- Note e metadati ---
    note: str = ""
    source_refs: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Inizializza Poisson di default e calcola i derivati."""
        if self.nu == 0.0:
            self.nu = _POISSON_DEFAULT.get(self.famiglia, 0.20)
        if not self._derivati:
            self.ricalcola_tutti_derivati()

    # --- Gestione parametri derivati ---

    def ottieni_derivato(self, nome: str) -> float:
        """Restituisce il valore di un parametro derivato.

        Parametri:
            nome: Nome del parametro (es. "f_cd", "G", "f_ctm", "E_cm").

        Restituisce:
            Valore del parametro derivato, o 0.0 se non presente.
        """
        pd = self._derivati.get(nome)
        return pd.valore if pd else 0.0

    def imposta_derivato_manuale(self, nome: str, valore: float) -> None:
        """Sovrascrive manualmente un parametro derivato (override utente).

        Parametri:
            nome: Nome del parametro derivato.
            valore: Nuovo valore inserito dall'utente.
        """
        if nome in self._derivati:
            self._derivati[nome].valore = valore
            self._derivati[nome].override = True
            logger.info(
                "Override manuale: %s.%s = %.4g (materiale %s)",
                nome, valore, valore, self.material_id,
            )
        else:
            self._derivati[nome] = ParametroDerivato(
                valore=valore, override=True, formula="override utente"
            )

    def ricalcola_singolo_derivato(self, nome: str) -> float:
        """Ricalcola un singolo parametro derivato dal valore automatico.

        Rimuove l'override manuale e ricalcola dalla formula.

        Parametri:
            nome: Nome del parametro derivato.

        Restituisce:
            Nuovo valore calcolato.
        """
        if nome in self._derivati:
            self._derivati[nome].override = False
        self._calcola_derivato(nome)
        return self.ottieni_derivato(nome)

    def ricalcola_tutti_derivati(self) -> None:
        """Ricalcola TUTTI i parametri derivati.

        Ricalcola anche quelli con override (utile con bottone "Ricalcola tutti").
        """
        if self.famiglia == "calcestruzzo":
            self._calcola_derivati_calcestruzzo()
        elif self.famiglia == "acciaio":
            self._calcola_derivati_acciaio()
        elif self.famiglia == "muratura":
            self._calcola_derivati_muratura()
        elif self.famiglia == "legno":
            self._calcola_derivati_legno()
        # G è comune a tutti (tranne legno che usa G_mean)
        if self.famiglia != "legno":
            self._calcola_derivato("G")

    def aggiorna_da_primario(self, nome_primario: str) -> None:
        """Ricalcola i derivati che dipendono da un parametro primario modificato.

        Ricalcola SOLO i derivati che NON hanno override manuale.

        Parametri:
            nome_primario: Nome del parametro primario modificato (es. "f_ck", "E", "nu").
        """
        # Mappa dipendenze: primario → lista derivati che dipendono
        dipendenze: dict[str, list[str]] = {
            "f_ck": ["f_cd", "f_ctm", "f_ctk_005", "f_ctk_095", "E_cm", "f_cm"],
            "f_yk": ["f_yd"],
            "E": ["G"],
            "nu": ["G"],
            "gamma_c": ["f_cd"],
            "gamma_s": ["f_yd"],
            "alpha_cc": ["f_cd"],
            "f_k": ["f_d"],
            "gamma_M": ["f_d", "f_vd"],
            "f_vk0": ["f_vd"],
            "sigma_c28": ["sigma_c_adm", "tau_c0_adm", "tau_c1_adm"],
            "f_mk": ["f_md"],
            "f_t0k": ["f_t0d"],
            "f_c0k": ["f_c0d"],
            "f_vk": ["f_vd_legno"],
        }
        nomi_derivati = dipendenze.get(nome_primario, [])
        for nome in nomi_derivati:
            if nome in self._derivati and self._derivati[nome].override:
                continue  # Mantieni override utente
            self._calcola_derivato(nome)

    def derivato_ha_override(self, nome: str) -> bool:
        """Verifica se un parametro derivato ha un override manuale."""
        pd = self._derivati.get(nome)
        return pd.override if pd else False

    def lista_derivati(self) -> dict[str, ParametroDerivato]:
        """Restituisce tutti i parametri derivati con il loro stato."""
        return dict(self._derivati)

    # --- Calcolo derivati per famiglia ---

    def _calcola_derivati_calcestruzzo(self) -> None:
        """Calcola tutti i parametri derivati per calcestruzzo."""
        for nome in ["f_cm", "f_cd", "f_ctm", "f_ctk_005", "f_ctk_095", "E_cm"]:
            self._calcola_derivato(nome)

    def _calcola_derivati_acciaio(self) -> None:
        """Calcola tutti i parametri derivati per acciaio."""
        for nome in ["f_yd", "E_s"]:
            self._calcola_derivato(nome)

    def _calcola_derivati_muratura(self) -> None:
        """Calcola tutti i parametri derivati per muratura."""
        for nome in ["f_d", "f_vd"]:
            self._calcola_derivato(nome)

    def _calcola_derivati_legno(self) -> None:
        """Calcola tutti i parametri derivati per legno."""
        for nome in ["f_md", "f_t0d", "f_c0d", "f_vd_legno", "E_0_05"]:
            self._calcola_derivato(nome)

    def _calcola_derivato(self, nome: str) -> None:
        """Calcola un singolo parametro derivato."""
        if nome in self._derivati and self._derivati[nome].override:
            return  # Preserva override

        valore = 0.0
        formula = ""

        if nome == "G":
            # Modulo di taglio: G = E / (2 × (1 + ν))
            if self.E > 0 and self.nu >= 0:
                valore = self.E / (2.0 * (1.0 + self.nu))
                formula = "G = E / (2 × (1 + ν))"

        elif nome == "f_cd":
            # Resistenza di calcolo cls: f_cd = α_cc × f_ck / γ_c
            if self.f_ck > 0 and self.gamma_c > 0:
                valore = self.alpha_cc * self.f_ck / self.gamma_c
                formula = "f_cd = α_cc × f_ck / γ_c"

        elif nome == "f_cm":
            # Resistenza media cls: f_cm = f_ck + 80 kg/cm² (EC2 §3.1.2, 80 = 8 MPa × 10.2)
            if self.f_ck > 0:
                valore = self.f_ck + 80.0
                formula = "f_cm = f_ck + 80 kg/cm² (EC2 Tab.3.1)"

        elif nome == "f_ctm":
            # Resistenza media a trazione cls
            # EC2 §3.1.3: f_ctm = 0.30 × f_ck^(2/3) per f_ck ≤ 510 kg/cm² (50 MPa)
            # Nota: in kg/cm² la formula richiede conversione
            if self.f_ck > 0:
                f_ck_mpa = self.f_ck * 0.0980665  # kg/cm² → MPa
                if f_ck_mpa <= 50:
                    f_ctm_mpa = 0.30 * f_ck_mpa ** (2.0 / 3.0)
                else:
                    f_ctm_mpa = 2.12 * math.log(1 + f_ck_mpa / 10.0 + 8.0 / 10.0)
                valore = f_ctm_mpa / 0.0980665  # MPa → kg/cm²
                formula = "f_ctm = 0.30 × f_ck^(2/3) [MPa] (EC2 §3.1.3)"

        elif nome == "f_ctk_005":
            # Frattile 5% resistenza a trazione: f_ctk,0.05 = 0.7 × f_ctm
            f_ctm = self.ottieni_derivato("f_ctm")
            if f_ctm > 0:
                valore = 0.7 * f_ctm
                formula = "f_ctk,0.05 = 0.7 × f_ctm (EC2 Tab.3.1)"

        elif nome == "f_ctk_095":
            # Frattile 95% resistenza a trazione: f_ctk,0.95 = 1.3 × f_ctm
            f_ctm = self.ottieni_derivato("f_ctm")
            if f_ctm > 0:
                valore = 1.3 * f_ctm
                formula = "f_ctk,0.95 = 1.3 × f_ctm (EC2 Tab.3.1)"

        elif nome == "E_cm":
            # Modulo elastico cls: E_cm = 22000 × (f_cm/10)^0.3 [MPa] (EC2 §3.1.3)
            f_cm = self.ottieni_derivato("f_cm")
            if f_cm > 0:
                f_cm_mpa = f_cm * 0.0980665
                E_cm_mpa = 22000.0 * (f_cm_mpa / 10.0) ** 0.3
                valore = E_cm_mpa / 0.0980665  # MPa → kg/cm²
                formula = "E_cm = 22000 × (f_cm/10)^0.3 [MPa] (EC2 §3.1.3)"
                # Aggiorna anche E se non impostato dall'utente
                if self.E == 0.0:
                    self.E = valore

        elif nome == "f_yd":
            # Resistenza di calcolo acciaio: f_yd = f_yk / γ_s
            if self.f_yk > 0 and self.gamma_s > 0:
                valore = self.f_yk / self.gamma_s
                formula = "f_yd = f_yk / γ_s"

        elif nome == "E_s":
            # Modulo elastico acciaio (convenzionale)
            if self.E == 0.0:
                valore = 2100000.0  # 2'100'000 kg/cm² = 210'000 MPa
                self.E = valore
            else:
                valore = self.E
            formula = "E_s = 2'100'000 kg/cm² (EC2 §3.2.7)"

        elif nome == "f_d":
            # Resistenza di calcolo muratura: f_d = f_k / γ_M
            if self.f_k > 0 and self.gamma_M > 0:
                valore = self.f_k / self.gamma_M
                formula = "f_d = f_k / γ_M (NTC2018 §4.5.6.1)"

        elif nome == "f_vd":
            # Resistenza di calcolo a taglio muratura: f_vd = f_vk0 / γ_M
            if self.f_vk0 > 0 and self.gamma_M > 0:
                valore = self.f_vk0 / self.gamma_M
                formula = "f_vd = f_vk0 / γ_M (NTC2018 §4.5.6.1)"

        # --- Legno (NTC2018 §4.4 / EN 1995-1-1) ---
        elif nome == "f_md":
            # Resistenza di calcolo a flessione: f_md = k_mod × f_mk / γ_M
            # k_mod dipende da classe servizio e durata carico; default 0.8 (media durata, classe 1)
            if self.f_mk > 0 and self.gamma_M > 0:
                k_mod = 0.8  # media durata, classe servizio 1
                valore = k_mod * self.f_mk / self.gamma_M
                formula = "f_md = k_mod × f_mk / γ_M (k_mod=0.8, NTC2018 §4.4)"

        elif nome == "f_t0d":
            # Resistenza di calcolo a trazione parallela
            if self.f_t0k > 0 and self.gamma_M > 0:
                k_mod = 0.8
                valore = k_mod * self.f_t0k / self.gamma_M
                formula = "f_t0d = k_mod × f_t0k / γ_M"

        elif nome == "f_c0d":
            # Resistenza di calcolo a compressione parallela
            if self.f_c0k > 0 and self.gamma_M > 0:
                k_mod = 0.8
                valore = k_mod * self.f_c0k / self.gamma_M
                formula = "f_c0d = k_mod × f_c0k / γ_M"

        elif nome == "f_vd_legno":
            # Resistenza di calcolo a taglio legno
            if self.f_vk > 0 and self.gamma_M > 0:
                k_mod = 0.8
                valore = k_mod * self.f_vk / self.gamma_M
                formula = "f_vd = k_mod × f_vk / γ_M"

        elif nome == "E_0_05":
            # Frattile 5% modulo elastico parallelo: E_0,05 = E_0_mean × 2/3
            if self.E_0_mean > 0:
                valore = self.E_0_mean * 2.0 / 3.0
                formula = "E_0,05 ≈ E_0_mean × 2/3 (EN 1995-1-1)"

        self._derivati[nome] = ParametroDerivato(
            valore=valore,
            override=False,
            formula=formula,
        )

    # --- Accesso rapido ai derivati più comuni ---

    @property
    def f_cd(self) -> float:
        """Resistenza di calcolo calcestruzzo [kg/cm²]."""
        return self.ottieni_derivato("f_cd")

    @property
    def f_ctm(self) -> float:
        """Resistenza media a trazione calcestruzzo [kg/cm²]."""
        return self.ottieni_derivato("f_ctm")

    @property
    def E_cm(self) -> float:
        """Modulo elastico calcestruzzo [kg/cm²]."""
        return self.ottieni_derivato("E_cm")

    @property
    def G(self) -> float:
        """Modulo di taglio [kg/cm²]."""
        return self.ottieni_derivato("G")

    @property
    def f_yd(self) -> float:
        """Resistenza di calcolo acciaio [kg/cm²]."""
        return self.ottieni_derivato("f_yd")

    @property
    def f_d(self) -> float:
        """Resistenza di calcolo muratura [kg/cm²]."""
        return self.ottieni_derivato("f_d")

    @property
    def f_vd(self) -> float:
        """Resistenza di calcolo a taglio muratura [kg/cm²]."""
        return self.ottieni_derivato("f_vd")

    @property
    def f_md(self) -> float:
        """Resistenza di calcolo a flessione legno [kg/cm²]."""
        return self.ottieni_derivato("f_md")

    @property
    def f_t0d(self) -> float:
        """Resistenza di calcolo a trazione parallela legno [kg/cm²]."""
        return self.ottieni_derivato("f_t0d")

    @property
    def f_c0d(self) -> float:
        """Resistenza di calcolo a compressione parallela legno [kg/cm²]."""
        return self.ottieni_derivato("f_c0d")

    # --- Metodo legacy compatibile ---

    def get_param(self, name: str) -> float | None:
        """Restituisce un parametro per nome (compatibilità con vecchio modello).

        Cerca prima tra gli attributi diretti, poi tra i derivati.
        """
        if hasattr(self, name):
            val = getattr(self, name)
            if isinstance(val, (int, float)):
                return val
        pd = self._derivati.get(name)
        if pd:
            return pd.valore
        return None

    # --- Serializzazione JSON ---

    def to_json(self) -> str:
        """Serializza il materiale in stringa JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def to_dict(self) -> dict[str, Any]:
        """Serializza il materiale in dizionario."""
        dati: dict[str, Any] = {
            "material_id": self.material_id,
            "descrizione": self.descrizione,
            "famiglia": self.famiglia,
            "norma_riferimento": self.norma_riferimento,
            "densita_kg_m3": self.densita_kg_m3,
            "E": self.E,
            "nu": self.nu,
            "note": self.note,
            "source_refs": self.source_refs,
        }

        if self.famiglia == "calcestruzzo":
            dati.update({
                "f_ck": self.f_ck,
                "gamma_c": self.gamma_c,
                "alpha_cc": self.alpha_cc,
                "sigma_c28": self.sigma_c28,
                "sigma_c_adm": self.sigma_c_adm,
                "tau_c0_adm": self.tau_c0_adm,
                "tau_c1_adm": self.tau_c1_adm,
                "n_omogenizzazione": self.n_omogenizzazione,
            })
        elif self.famiglia == "acciaio":
            dati.update({
                "f_yk": self.f_yk,
                "gamma_s": self.gamma_s,
                "sigma_s_adm": self.sigma_s_adm,
            })
        elif self.famiglia == "muratura":
            dati.update({
                "f_k": self.f_k,
                "f_vk0": self.f_vk0,
                "gamma_M": self.gamma_M,
            })
        elif self.famiglia == "legno":
            dati.update({
                "f_mk": self.f_mk,
                "f_t0k": self.f_t0k,
                "f_t90k": self.f_t90k,
                "f_c0k": self.f_c0k,
                "f_c90k": self.f_c90k,
                "f_vk": self.f_vk,
                "E_0_mean": self.E_0_mean,
                "E_90_mean": self.E_90_mean,
                "G_mean": self.G_mean,
                "classe_servizio": self.classe_servizio,
                "gamma_M": self.gamma_M,
            })

        # Serializza derivati
        dati["derivati"] = {
            nome: pd.to_dict() for nome, pd in self._derivati.items()
        }

        return dati

    @classmethod
    def from_dict(cls, dati: dict[str, Any]) -> Material:
        """Deserializza un materiale da dizionario."""
        # Estrai derivati prima della creazione
        derivati_raw = dati.pop("derivati", {})

        # Filtra solo i campi noti del dataclass
        campi_noti = {f.name for f in cls.__dataclass_fields__.values() if f.name != "_derivati"}
        dati_filtrati = {k: v for k, v in dati.items() if k in campi_noti}

        materiale = cls(**dati_filtrati)

        # Ripristina derivati con override
        if derivati_raw:
            for nome, pd_dict in derivati_raw.items():
                materiale._derivati[nome] = ParametroDerivato.from_dict(pd_dict)

        return materiale

    @classmethod
    def from_json(cls, testo_json: str) -> Material:
        """Deserializza un materiale da stringa JSON."""
        dati = json.loads(testo_json)
        return cls.from_dict(dati)

    def __str__(self) -> str:
        """Rappresentazione testuale del materiale."""
        return f"Material({self.material_id}: {self.descrizione} [{self.famiglia}])"


# --- Factory per materiali comuni ---

def crea_calcestruzzo_ntc2018(
    classe: str = "C25/30",
    material_id: str = "",
) -> Material:
    """Crea un materiale calcestruzzo secondo NTC2018.

    Parametri:
        classe: Classe di resistenza (es. "C25/30", "C30/37", "C35/45").
        material_id: ID univoco (generato automaticamente se vuoto).

    Restituisce:
        Material configurato per calcestruzzo NTC2018.
    """
    # Mappa classe → f_ck [kg/cm²]
    # NTC2018 Tab.4.1.I (f_ck in MPa × 10.197 = kg/cm²)
    classi_fck: dict[str, float] = {
        "C12/15": 122.4,   # 12 MPa
        "C16/20": 163.2,   # 16 MPa
        "C20/25": 203.9,   # 20 MPa
        "C25/30": 254.9,   # 25 MPa
        "C28/35": 285.5,   # 28 MPa
        "C30/37": 305.9,   # 30 MPa
        "C32/40": 326.3,   # 32 MPa
        "C35/45": 356.9,   # 35 MPa
        "C40/50": 407.9,   # 40 MPa
        "C45/55": 458.9,   # 45 MPa
        "C50/60": 509.8,   # 50 MPa
        "C55/67": 560.8,   # 55 MPa
        "C60/75": 611.8,   # 60 MPa
        "C70/85": 713.8,   # 70 MPa
        "C80/95": 815.7,   # 80 MPa
        "C90/105": 917.7,  # 90 MPa
    }

    f_ck = classi_fck.get(classe, 254.9)

    return Material(
        material_id=material_id or f"cls_{classe}",
        descrizione=f"Calcestruzzo {classe} — NTC2018",
        famiglia="calcestruzzo",
        norma_riferimento="NTC2018",
        densita_kg_m3=2500.0,
        f_ck=f_ck,
        gamma_c=1.50,
        alpha_cc=0.85,
        nu=0.20,
    )


def crea_acciaio_ntc2018(
    tipo: str = "B450C",
    material_id: str = "",
) -> Material:
    """Crea un materiale acciaio da armatura secondo NTC2018.

    Parametri:
        tipo: Tipo acciaio (es. "B450C", "B450A", "B500B").
        material_id: ID univoco.

    Restituisce:
        Material configurato per acciaio NTC2018.
    """
    tipi_fyk: dict[str, float] = {
        "B450C": 4589.0,   # 450 MPa
        "B450A": 4589.0,   # 450 MPa
        "B500B": 5098.0,   # 500 MPa (EC)
    }

    f_yk = tipi_fyk.get(tipo, 4589.0)

    return Material(
        material_id=material_id or f"acc_{tipo}",
        descrizione=f"Acciaio {tipo} — NTC2018",
        famiglia="acciaio",
        norma_riferimento="NTC2018",
        densita_kg_m3=7850.0,
        f_yk=f_yk,
        gamma_s=1.15,
        E=2100000.0,  # 210'000 MPa
        nu=0.30,
    )


def crea_muratura_ntc2018(
    tipo_blocco: str = "mattoni_pieni",
    tipo_malta: str = "M10",
    material_id: str = "",
) -> Material:
    """Crea un materiale muratura secondo NTC2018 Tab.4.5.II.

    Parametri:
        tipo_blocco: Tipo di blocco (es. "mattoni_pieni", "blocchi_cls", "tufo").
        tipo_malta: Tipo di malta (es. "M2.5", "M5", "M10", "M15", "M20").
        material_id: ID univoco.

    Restituisce:
        Material configurato per muratura NTC2018.
    """
    # NTC2018 Tab.4.5.II: f_k [kg/cm²] (valori indicativi, da validare)
    # Formato: {tipo_blocco: {tipo_malta: f_k}}
    tabella_fk: dict[str, dict[str, float]] = {
        "mattoni_pieni": {
            "M2.5": 20.0, "M5": 28.0, "M10": 36.0, "M15": 42.0, "M20": 46.0,
        },
        "mattoni_semipieni": {
            "M2.5": 12.0, "M5": 18.0, "M10": 24.0, "M15": 28.0, "M20": 30.0,
        },
        "blocchi_cls": {
            "M2.5": 14.0, "M5": 20.0, "M10": 30.0, "M15": 38.0, "M20": 44.0,
        },
        "tufo": {
            "M2.5": 8.0, "M5": 11.0, "M10": 14.0, "M15": 16.0, "M20": 18.0,
        },
        "pietra_squadrata": {
            "M2.5": 12.0, "M5": 16.0, "M10": 20.0, "M15": 24.0, "M20": 26.0,
        },
    }

    f_k = 36.0  # Default mattoni pieni M10
    if tipo_blocco in tabella_fk:
        f_k = tabella_fk[tipo_blocco].get(tipo_malta, 36.0)

    # f_vk0: NTC2018 Tab.4.5.II (resistenza a taglio senza sforzo normale)
    fvk0_per_blocco: dict[str, float] = {
        "mattoni_pieni": 2.0,
        "mattoni_semipieni": 1.0,
        "blocchi_cls": 1.8,
        "tufo": 0.6,
        "pietra_squadrata": 0.8,
    }
    f_vk0 = fvk0_per_blocco.get(tipo_blocco, 2.0)

    # Modulo elastico (NTC2018 §C8.5.3.1)
    E_mur = 1000.0 * f_k  # E = 1000 × f_k (prima approssimazione)

    return Material(
        material_id=material_id or f"mur_{tipo_blocco}_{tipo_malta}",
        descrizione=f"Muratura {tipo_blocco} malta {tipo_malta} — NTC2018",
        famiglia="muratura",
        norma_riferimento="NTC2018",
        densita_kg_m3=1800.0,
        f_k=f_k,
        f_vk0=f_vk0,
        gamma_M=2.0,
        E=E_mur,
        nu=0.15,
    )


def crea_legno_ntc2018(
    classe: str = "C24",
    material_id: str = "",
) -> Material:
    """Crea un materiale legno strutturale secondo EN 338 / NTC2018.

    Parametri:
        classe: Classe di resistenza (es. "C14", "C24", "C30", "GL24h", "GL28h", "GL32h").
        material_id: ID univoco (generato automaticamente se vuoto).

    Restituisce:
        Material configurato per legno NTC2018.
    """
    # EN 338 / EN 14080 — valori in kg/cm² (da MPa × 10.197)
    # Formato: classe → (f_mk, f_t0k, f_t90k, f_c0k, f_c90k, f_vk, E_0_mean, E_90_mean, G_mean, densità)
    classi: dict[str, tuple[float, ...]] = {
        "C14": (142.8, 81.6, 4.1, 163.2, 20.4, 30.6, 71379.0, 2345.0, 4487.0, 350.0),
        "C16": (163.2, 102.0, 4.1, 173.4, 20.4, 32.6, 81600.0, 2754.0, 5098.0, 370.0),
        "C18": (183.6, 112.2, 4.1, 183.6, 22.4, 34.7, 91800.0, 3060.0, 5709.0, 380.0),
        "C22": (224.4, 132.6, 4.1, 204.0, 24.5, 38.8, 102000.0, 3366.0, 6320.0, 410.0),
        "C24": (244.8, 142.8, 4.1, 214.2, 25.5, 40.8, 112200.0, 3774.0, 7140.0, 420.0),
        "C27": (275.4, 163.2, 4.1, 224.4, 25.5, 40.8, 117300.0, 3774.0, 7140.0, 450.0),
        "C30": (305.9, 183.6, 4.1, 234.6, 25.5, 40.8, 122400.0, 4080.0, 7650.0, 460.0),
        "C35": (356.9, 214.2, 4.1, 254.9, 25.5, 40.8, 132600.0, 4284.0, 7650.0, 480.0),
        "C40": (407.9, 244.8, 4.1, 265.1, 25.5, 40.8, 142800.0, 4692.0, 7650.0, 500.0),
        # Lamellare omogeneo
        "GL24h": (244.8, 193.8, 4.1, 244.8, 25.5, 35.7, 117300.0, 3906.0, 7446.0, 420.0),
        "GL28h": (285.5, 224.4, 4.1, 265.1, 25.5, 35.7, 127500.0, 4182.0, 7446.0, 460.0),
        "GL32h": (326.3, 255.0, 4.1, 285.5, 25.5, 35.7, 142800.0, 4692.0, 7650.0, 480.0),
    }

    params = classi.get(classe, classi["C24"])
    f_mk, f_t0k, f_t90k, f_c0k, f_c90k, f_vk, E_0, E_90, G_m, rho = params

    tipo = "lamellare" if classe.startswith("GL") else "massiccio"

    return Material(
        material_id=material_id or f"legno_{classe}",
        descrizione=f"Legno {tipo} {classe} — NTC2018",
        famiglia="legno",
        norma_riferimento="NTC2018",
        densita_kg_m3=rho,
        f_mk=f_mk,
        f_t0k=f_t0k,
        f_t90k=f_t90k,
        f_c0k=f_c0k,
        f_c90k=f_c90k,
        f_vk=f_vk,
        E_0_mean=E_0,
        E_90_mean=E_90,
        G_mean=G_m,
        E=E_0,
        gamma_M=1.45,
        nu=0.40,
    )
