# Docstring Template — Elementi Secondari (S1–S9)

## Sommario
Template Google-style docstring e type hints per agevolare aggiornamento bulk di tutti i moduli Python S1–S9.

Ogni template è basato su **S3 Parapetti** come caso esemplare di implementazione massimale.

---

## Template 1: models.py

### Enum Docstring

```python
class TipoParapetto(str, Enum):
    """Classificazione tipologiche parapetti §7.2.2 NTC2018.

    Governa:
    - Resistenza base da lookup table in checks_slu.py
    - Comportamento dinamico e fattori di riduzione
    - Output report

    Values:
        CONTINUO_MURATURA: Parapetto murario continuo su tutta la lunghezza.
        CONTINUO_ACCIAIO: Profili metallici continui (tubolari, IPE).
        MONTANTI_ACCIAIO: Sistema a montanti discrete, correnti collegati.
        VETRATO: Pannelli in vetro temperato o laminato.
        MISTO_ACCIAIO_VETRO: Combinazioni acciaio + vetri (es. ringhiera metallo + infill vetro).
        RECINZIONE_METALLICA: Reti metalliche, pannelli traforati, sistemi aperti.

    References:
        NTC2018 §7.2.2, Circ. 7/2019 §C7.2
    """
    CONTINUO_MURATURA = "continuo_muratura"
    CONTINUO_ACCIAIO = "continuo_acciaio"
    MONTANTI_ACCIAIO = "montanti_acciaio"
    VETRATO = "vetrato"
    MISTO_ACCIAIO_VETRO = "misto_acciaio_vetro"
    RECINZIONE_METALLICA = "recinzione_metallica"
```

### Dataclass Docstring (Complete)

```python
@dataclass
class ParapettoSpec:
    """Specifica di un parapetto secondario per verifica sismica §7.2.2 NTC2018.

    Contiene geometria, materiale, proprietà dinamiche e ancoraggio per verifica SLU/SLE.
    Utilizzato come input a check_slu() e check_sle(); derivabile da JSON/dict tramite spec_from_dict().

    All'istanziazione, nessuna validazione esplicita (demandata a caller). Metodi calcolano
    proprietà derivate (massa, aree). Se campo mancante, caller deve fornire default.

    Attributes:
        tipo (TipoParapetto):
            Classificazione tipologica. Governa resistenza base lookup table.
        altezza_cm (float):
            Altezza libera parapetto [cm], da supporto a bordo superiore.
            Vincoli normativi: 60–150 cm (NTC4.1.6). Valore tipico: 100 cm.
        lunghezza_cm (float):
            Sviluppo lineare del parapetto [cm]. Range: 100–1000 cm tipico.
        massa_lineare_kg_m (float):
            Massa per unità di lunghezza [kg/m]. Usata per domanda sismica.
            Tipico: muratura 150 kg/m; acciaio 50–80 kg/m.
        tipo_ancoraggio (TipoAncoraggio):
            Modalità di vincolo alla struttura. Influenza fattore riduttivo.
            Es: chimico -10% (fattore 0.9), base continua neutro.
        resistenza_ancoraggio_kn (float | None, default=None):
            Capacità degli ancoraggi [kN]. Se None, calcolata in checks_slu.py
            da lookup table. Range verificato: 5–50 kN tipico.
        interasse_montanti_cm (float | None, default=None):
            Spacing tra montanti in sistemi discreti [cm].
            Rilevante per MONTANTI_ACCIAIO. Tipico: 30–80 cm.
        spessore_parete_cm (float | None, default=None):
            Spessore parete muraria [cm]. Usato per valutazione snellezza.
            Tipico: 12–40 cm (muragione ordinaria 30 cm).
        numero_montanti (int | None, default=None):
            Conteggio montanti discreti. Influenza distribuzione carico
            e resistenza totale. Tipico: 4–12 montanti.
        area_aperture_cm2 (float, default=0.0):
            Superficie finestre/porte in parapetto [cm²].
            Riduce area resistente per logica panneliante.
            Range: 0–50% area lorda (salvaguardia: no > 100%).
        comportamento_fragile (bool, default=False):
            Flag per materiali fragili (vetri, ceramica, laterizio).
            Se True, riduzione resistenza 15% (fattore: 0.85).
        vincoli_laterali (bool, default=True):
            Disponibilità vincoli laterali (cordoli di bordo).
            Se True, bonus resistenza +10% (fattore: 1.1).

    Methods:
        area_lorda_cm2() -> float:
            Area parapetto senza detrazioni [cm²]. = altezza × lunghezza.
        area_netta_cm2() -> float:
            Area resistente dopo detrazioni aperture [cm²].
            = area_lorda - area_aperture (min: 0 per salvaguardia).
        massa_totale_kg() -> float:
            Massa totale elemento [kg]. = massa_lineare × lunghezza [m].

    Examples:
        >>> spec = ParapettoSpec(
        ...     tipo=TipoParapetto.CONTINUO_MURATURA,
        ...     altezza_cm=100,
        ...     lunghezza_cm=300,
        ...     massa_lineare_kg_m=150,
        ...     tipo_ancoraggio=TipoAncoraggio.TASSELLI_PUNTUALI,
        ...     numero_montanti=6,
        ... )
        >>> spec.massa_totale_kg()
        450.0
        >>> spec.area_lorda_cm2()
        30000.0

    Notes:
        - Riferimento FEMA E-74 Cap. 5.2: Parapetti murari; nomina resistenze base in termini di forza.
        - Fattori modificatori (fragile, anchortype, vincoli) sono applicati a resistenza base in checks_slu.py.
        - Unità interna: cm (lunghezze), kg (forze), g (accelerazioni).

    References:
        NTC2018 §7.2.2, §4.1.6; Circ. 7/2019 §C7.2; FEMA E-74 Ch. 5
    """
    tipo: TipoParapetto
    altezza_cm: float
    lunghezza_cm: float
    massa_lineare_kg_m: float
    tipo_ancoraggio: TipoAncoraggio
    resistenza_ancoraggio_kn: float | None = None
    interasse_montanti_cm: float | None = None
    spessore_parete_cm: float | None = None
    numero_montanti: int | None = None
    area_aperture_cm2: float = 0.0
    comportamento_fragile: bool = False
    vincoli_laterali: bool = True

    def area_lorda_cm2(self) -> float:
        """Area lorda parapetto [cm²] = altezza × lunghezza.

        Returns:
            float: Area senza detrazioni aperture.
        """
        return self.altezza_cm * self.lunghezza_cm

    def area_netta_cm2(self) -> float:
        """Area netta parapetto [cm²] = area_lorda - area_aperture.

        Utilizzata per calcoli di resistenza panneliante. Salvaguardia:
        se area_aperture > area_lorda, ritorna 0.0 (no negative).

        Returns:
            float: Area netta in cm² (≥ 0). Se 0, elemento non resistente.
        """
        return max(0.0, self.area_lorda_cm2() - self.area_aperture_cm2)

    def massa_totale_kg(self) -> float:
        """Massa totale parapetto [kg].

        Formula: massa_lineare_kg_m × lunghezza_m

        Returns:
            float: Massa totale in kg.

        Examples:
            >>> spec.massa_lineare_kg_m = 150  # kg/m
            >>> spec.lunghezza_cm = 300        # cm
            >>> spec.massa_totale_kg()
            450.0  # 150 * 3 m
        """
        return self.massa_lineare_kg_m * (self.lunghezza_cm / 100.0)
```

### Result Dataclass

```python
@dataclass
class RisultatoSLUParapetto:
    """Risultato verifica SLU parapetto.

    Contiene domanda sismica/servizio, resistenza, utilisation per giudizio OK/NON OK.
    Calcolato da checks_slu.verifica_slu_parapetto().

    Attributes:
        esito (bool): True → OK, False → NON OK (domanda > resistenza).
        domanda_sismica_kg (float): Forza da inerzia locale [kg].
            = massa × S_a × gamma_i per NTC.
        domanda_servizio_kg (float): Carico orizzontale servizio [kg].
            NTC4.1.6: spinta minima 40 kg per railing d'scala.
        domanda_combinata_kg (float): Inviluppo domande.
            = max(domanda_sismica, domanda_servizio).
        resistenza_ancoraggio_kg (float): Capacità ancoraggi [kg].
            Calcolata con fattori riduttivi (fragile, anchortype, vincoli).
        meccanismo_critico (str): Descrive crisi prevalente.
            Es: "ancoraggio", "pannello", "montante".
    """
    esito: bool
    domanda_sismica_kg: float
    domanda_servizio_kg: float
    domanda_combinata_kg: float
    resistenza_ancoraggio_kg: float
    meccanismo_critico: str
    rapporto_domanda_resistenza: float = field(init=False)

    def __post_init__(self) -> None:
        """Calcola rapporto utilisation con salvaguardia divisione per zero."""
        self.rapporto_domanda_resistenza = (
            self.domanda_combinata_kg / self.resistenza_ancoraggio_kg
            if self.resistenza_ancoraggio_kg > 0
            else float("inf")
        )
```

---

## Template 2: checks_slu.py

```python
"""Verifiche SLU (Stato Limite Ultimo) per parapetti.

Modulo di calcolo domanda sismica locale, resistenza e capacità ancoraggi.
Segue metodologia NTC2018 §7.2.1-2 dedotta a verifiche di forma.

Functions:
    calcola_resistenza_ancoraggio() → float: Resistenza con fattori.
    verifica_slu_parapetto() → RisultatoSLUParapetto: Esito SLU completo.
    check_slu(inputs: dict) → dict: API pubblica (dispatcher-compatible).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ..common import calcola_forza_sismica_locale
from .models import ParapettoSpec, TipoParapetto, ContestoSLUParapetto, RisultatoSLUParapetto

# Resistenze base [kN] per tipologia, da letteratura NTC + FEMA E-74 + ETA.
_RESISTENZE_BASE_KN: dict[TipoParapetto, float] = {
    TipoParapetto.CONTINUO_MURATURA: 8.5,      # Muratura 30 cm, malta ordinaria
    TipoParapetto.CONTINUO_ACCIAIO: 12.0,      # Tubolari saldati IPE200–240
    TipoParapetto.MONTANTI_ACCIAIO: 10.5,      # 4–6 montanti, interasse 60 cm
    TipoParapetto.VETRATO: 6.5,                # Vetro temperato + cornice acciaio
    TipoParapetto.MISTO_ACCIAIO_VETRO: 9.0,    # Combinazione ibrida
    TipoParapetto.RECINZIONE_METALLICA: 5.0,   # Rete, bassa rigidezza
}

# Fattori riduttivi/moltiplicativi per modifica resistenza base
_FATTORE_ANCORAGGIO_CHIMICO: float = 0.90     # NTC: ancoraggio chimico meno affidabile
_FATTORE_FRAGILE: float = 0.85                # Vetri, ceramica soggetti a crisi fragile
_FATTORE_VINCOLI_LATERALI: float = 1.10       # Bonus per cordoli laterali
_FATTORE_CORDOLO_INTEGRATO: float = 1.25      # Massimo bonus per integrazione strutturale


def calcola_resistenza_ancoraggio(spec: ParapettoSpec) -> float:
    """Calcola resistenza dell'ancoraggio parapetto con fattori modificatori.

    Algoritmo:
    1. Lookup resistenza base da _RESISTENZE_BASE_KN[spec.tipo]
    2. Applicare fattore anchortype (chimico -10%)
    3. Applicare fattore fragile (-15% se spec.comportamento_fragile)
    4. Applicare fattore vincoli laterali (+10% se spec.vincoli_laterali)
    5. Convertire kN → kg (÷ 0.00981)
    6. Ritornare max(resistenza, MIN_RESISTENZA_KG) per salvaguardia

    Args:
        spec (ParapettoSpec): Specifica parapetto con tipo, anchortype, fragile.

    Returns:
        float: Resistenza calcolata [kg].

    Examples:
        >>> spec = ParapettoSpec(..., tipo=TipoParapetto.CONTINUO_MURATURA, \
        ...                        tipo_ancoraggio=TipoAncoraggio.TASSELLI_PUNTUALI, \
        ...                        comportamento_fragile=False)
        >>> calcola_resistenza_ancoraggio(spec)
        850.0  # 8.5 kN = 866.5 kg ≈ 850

    References:
        NTC2018 §7.2.2, Circ. 7/2019; FEMA E-74 Cap. 5 (anchorages)
    """
    # Lookup base
    r_base_kn = _RESISTENZE_BASE_KN.get(spec.tipo, 5.0)  # fallback conservativo

    # Fattore anchortype
    fattore_anc = 1.0
    if spec.tipo_ancoraggio.value == "chimico":
        fattore_anc = _FATTORE_ANCORAGGIO_CHIMICO
    elif spec.tipo_ancoraggio.value == "cordolo_integrato":
        fattore_anc = _FATTORE_CORDOLO_INTEGRATO

    # Fattore fragile
    fattore_frag = _FATTORE_FRAGILE if spec.comportamento_fragile else 1.0

    # Fattore vincoli
    fattore_vinc = _FATTORE_VINCOLI_LATERALI if spec.vincoli_laterali else 1.0

    # Combinare fattori
    r_kn = r_base_kn * fattore_anc * fattore_frag * fattore_vinc

    # Convertire kN → kg (1 kN ≈ 101.97 kg)
    r_kg = r_kn * 101.97

    # Salvaguardia: resistenza minima
    MIN_RESISTENZA_KG = 50.0
    return max(MIN_RESISTENZA_KG, r_kg)


def verifica_slu_parapetto(
    spec: ParapettoSpec,
    contesto: ContestoSLUParapetto,
    passaggi: list[str]
) -> RisultatoSLUParapetto:
    """Verifica SLU parapetto: domanda vs. resistenza.

    Workflow:
    1. Calcola domanda sismica: F_a = massa × S_a × γ_i
    2. Calcola domanda servizio: carico orizzontale minimo normativo
    3. Inviluppo domande: max(sismica, servizio)
    4. Calcola resistenza ancoraggio con fattori
    5. Confronta: esito = (domanda ≤ resistenza)
    6. Registra passaggi in decision_log

    Args:
        spec (ParapettoSpec): Specifica parapetto.
        contesto (ContestoSLUParapetto): S_a, carico servizio, γ_i.
        passaggi (list[str]): Log dei calcoli (modificato in-place).

    Returns:
        RisultatoSLUParapetto: Esito completo con rapporto utilisation.

    Notes:
        - Non solleva eccezioni; registra errori in passaggi e continua.
        - Si assume spec validata dal caller.

    References:
        NTC2018 §7.2.1-2, Circ. 7/2019 §C7.2
    """
    passaggi.append("=== VERIFICA SLU PARAPETTO ===")

    # Domanda sismica
    massa_kg = spec.massa_totale_kg()
    domanda_sism = calcola_forza_sismica_locale(
        massa_kg, contesto.accelerazione_spettrale_g, contesto.gamma_i
    )
    passaggi.append(f"Massa parapetto: {massa_kg:.1f} kg")
    passaggi.append(f"Domanda sismica: {domanda_sism:.1f} kg")

    # Domanda servizio
    domanda_serv = contesto.carico_orizzontale_servizio_kg
    passaggi.append(f"Domanda servizio: {domanda_serv:.1f} kg")

    # Inviluppo
    domanda_tot = max(domanda_sism, domanda_serv)
    passaggi.append(f"Domanda combinata (inviluppo): {domanda_tot:.1f} kg")

    # Resistenza
    resistenza = calcola_resistenza_ancoraggio(spec)
    passaggi.append(f"Resistenza ancoraggio: {resistenza:.1f} kg")

    # Esito
    esito = domanda_tot <= resistenza
    meccanismo = "ancoraggio parapetto"
    passaggi.append(f"Utilisation: {domanda_tot / resistenza:.2f}")
    passaggi.append(f"ESITO: {'OK' if esito else 'NON OK'}")

    return RisultatoSLUParapetto(
        esito=esito,
        domanda_sismica_kg=domanda_sism,
        domanda_servizio_kg=domanda_serv,
        domanda_combinata_kg=domanda_tot,
        resistenza_ancoraggio_kg=resistenza,
        meccanismo_critico=meccanismo,
    )
```

---

## Template 3: __init__.py (API Pubblica)

```python
"""API pubblica per parapetti — Fase S3.

Entry points:
    spec_from_dict(dict) → ParapettoSpec
    check_slu(dict) → dict
    check_sle(dict) → dict
    verifica_parapetto_completa(dict) → RisultatoComponenteParapetto

Tutti i risultati includono:
    - element_type: "parapetti"
    - norm_references: lista norme applicate
    - decision_log: trace dei calcoli
    - trace.run_id: UUID esecuzione
"""

from __future__ import annotations
from typing import Optional, Any

from .models import (
    ParapettoSpec,
    TipoParapetto,
    TipoAncoraggio,
    RisultatoSLUParapetto,
    RisultatoSLEParapetto,
)
from .checks_slu import verifica_slu_parapetto
from .checks_sle import verifica_sle_parapetto


def spec_from_dict(inputs: dict) -> ParapettoSpec:
    """Converti dizionario → ParapettoSpec (factory method).

    Accetta dict con chiavi (tutti optional, con fallback default):
        - tipo: str (enum value o nome)
        - altezza_cm, lunghezza_cm, massa_lineare_kg_m: float
        - tipo_ancoraggio: str
        - comportamento_fragile: bool
        - vincoli_laterali: bool
        - ...altri campi

    Args:
        inputs (dict): Dizionario con spec parapetto.

    Returns:
        ParapettoSpec: Oggetto specifica instanziato.

    Raises:
        ValueError: Se tipo/ancoraggio non riconosciuto (enum).

    Examples:
        >>> inputs = {
        ...     "tipo": "continuo_muratura",
        ...     "altezza_cm": 100,
        ...     "lunghezza_cm": 300,
        ...     "massa_lineare_kg_m": 150,
        ...     "tipo_ancoraggio": "tasselli_puntuali",
        ... }
        >>> spec = spec_from_dict(inputs)
        >>> spec.massa_totale_kg()
        450.0
    """
    tipo = TipoParapetto(inputs.get("tipo", TipoParapetto.CONTINUO_MURATURA.value))
    ancoraggio = TipoAncoraggio(inputs.get("tipo_ancoraggio", TipoAncoraggio.TASSELLI_PUNTUALI.value))

    return ParapettoSpec(
        tipo=tipo,
        altezza_cm=float(inputs.get("altezza_cm", 100.0)),
        lunghezza_cm=float(inputs.get("lunghezza_cm", 300.0)),
        massa_lineare_kg_m=float(inputs.get("massa_lineare_kg_m", 150.0)),
        tipo_ancoraggio=ancoraggio,
        resistenza_ancoraggio_kn=inputs.get("resistenza_ancoraggio_kn"),
        numero_montanti=inputs.get("numero_montanti"),
        comportamento_fragile=bool(inputs.get("comportamento_fragile", False)),
        vincoli_laterali=bool(inputs.get("vincoli_laterali", True)),
    )


def check_slu(inputs: dict) -> dict[str, Any]:
    """Verifica SLU parapetto — dispatcher-compatible.

    Args:
        inputs (dict): Specifica + contesto (S_a, gamma_i, carico_servizio).

    Returns:
        dict: {
            'ok': bool,
            'esito': 'OK' | 'NON OK',
            'element_type': 'parapetti',
            'norm_references': list[str],
            'decision_log': list[str],
            'utilisation': float,
            'domanda_totale_kg': float,
            'resistenza_kg': float,
            'trace': {'run_id': uuid},
            ...
        }

    Notes:
        - Non solleva eccezioni; tornisce dict con 'messages' se errore.
        - Traccia completa in decision_log.
    """
    import uuid

    try:
        spec = spec_from_dict(inputs)
        passaggi: list[str] = []

        # SLU
        from .models import ContestoSLUParapetto
        context_slu = ContestoSLUParapetto(
            accelerazione_spettrale_g=float(inputs.get("S_a", 1.5)),
            carico_orizzontale_servizio_kg=float(inputs.get("carico_servizio_kg", 40)),
            gamma_i=float(inputs.get("gamma_i", 1.0)),
        )

        risultato_slu = verifica_slu_parapetto(spec, context_slu, passaggi)

        return {
            "ok": risultato_slu.esito,
            "esito": "OK" if risultato_slu.esito else "NON OK",
            "element_type": "parapetti",
            "norm_references": ["NTC2018 §7.2.2", "Circ. 7/2019 §C7.2", "Fase S3"],
            "decision_log": passaggi,
            "domanda_totale_kg": risultato_slu.domanda_combinata_kg,
            "resistenza_kg": risultato_slu.resistenza_ancoraggio_kg,
            "utilisation": round(risultato_slu.rapporto_domanda_resistenza, 4),
            "meccanismo_critico": risultato_slu.meccanismo_critico,
            "trace": {"run_id": str(uuid.uuid4())},
        }
    except Exception as e:
        return {
            "ok": False,
            "esito": "ERROR",
            "element_type": "parapetti",
            "messages": [str(e)],
            "decision_log": ["Input parsing error"],
            "trace": {"run_id": str(uuid.uuid4())},
        }


def check_sle(inputs: dict) -> dict[str, Any]:
    """Verifica SLE parapetto (damage classification)."""
    # Simile a check_slu, con contesto SLE (spostamento, ecc.)
    pass


def verifica_parapetto_completa(inputs: dict) -> Any:
    """Esecuzione integrata SLU + SLE + aggregazione risultati."""
    # Combina check_slu e check_sle, ritorna composite result
    pass


__all__ = [
    "spec_from_dict",
    "check_slu",
    "check_sle",
    "verifica_parapetto_completa",
    "ParapettoSpec",
    "TipoParapetto",
    "TipoAncoraggio",
]
```

---

## Template 4: Widget (src/gui/.../parapetti_widget.py)

```python
"""Widget Qt per input/output parapetti.

PySide6-compatible, fallback PyQt5. Interfaccia:
- Combo box per tipo parapetto
- Spinbox numerici per dimensioni, masse
- Checkbox per comportamento fragile, vincoli
- Bottoni "Verifica SLU", "Verifica SLE"
- Areadisplay per output risultati + decision_log
"""

from __future__ import annotations
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
        QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton, QTextEdit
    )
except ImportError:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
        QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton, QTextEdit
    )

from . import spec_from_dict, check_slu, check_sle


class ParapettiWidget(QWidget):
    """Widget di configurazione e verifica parapetti.

    Attributes:
        ... (Qt widgets privati)

    Methods:
        run_slu(): Esegui check_slu() con input attuali.
        run_sle(): Esegui check_sle() con input attuali.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Inizializza widget.

        Args:
            parent: Parent widget Qt (default None).
        """
        super().__init__(parent)
        self.initUI()

    def initUI(self) -> None:
        """Costruisci layout e connetti segnali."""
        layout = QVBoxLayout()

        # Tipo parapetto
        layout.addWidget(QLabel("Tipo parapetto:"))
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems([
            "continuo_muratura", "continuo_acciaio", "montanti_acciaio",
            "vetrato", "misto_acciaio_vetro", "recinzione_metallica"
        ])
        layout.addWidget(self.tipo_combo)

        # Parametri geometrici
        layout.addWidget(QLabel("Altezza (cm):"))
        self.altezza_spin = QDoubleSpinBox()
        self.altezza_spin.setRange(50, 200)
        self.altezza_spin.setValue(100)
        layout.addWidget(self.altezza_spin)

        # ... altri widget ...

        # Bottoni verifica
        hbox = QHBoxLayout()
        self.btn_slu = QPushButton("Verifica SLU")
        self.btn_sle = QPushButton("Verifica SLE")
        hbox.addWidget(self.btn_slu)
        hbox.addWidget(self.btn_sle)
        layout.addLayout(hbox)

        # Output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Connetti segnali
        self.btn_slu.clicked.connect(self.run_slu)
        self.btn_sle.clicked.connect(self.run_sle)

        self.setLayout(layout)

    def run_slu(self) -> None:
        """Esegui SLU con parametri attuali."""
        inputs = {
            "tipo": self.tipo_combo.currentText(),
            "altezza_cm": self.altezza_spin.value(),
            # ... altri campi ...
            "S_a": 1.5,
            "gamma_i": 1.0,
        }
        result = check_slu(inputs)
        self.output_text.setText(
            f"SLU: {result['esito']}\n"
            f"Utilisation: {result['utilisation']:.4f}\n\n"
            f"Log:\n" + "\n".join(result['decision_log'])
        )

    def run_sle(self) -> None:
        """Esegui SLE con parametri attuali."""
        inputs = {...}  # come run_slu
        result = check_sle(inputs)
        self.output_text.setText(f"SLE: {result['esito']}\nStato: {result['stato_danno']}")
```

---

## Quick Reference: Applicare i Template

1. **Leggi file Python attuale** (models.py, checks_slu.py, etc.)
2. **Sostituisci docstring enum/dataclass** con template corrispondente
3. **Aggiungi docstring a funzioni** come mostrato
4. **Mantieni lo stub **`__all__` con export pubblici
5. **Run pytest** per validare non-regression

### Bulk Application Strategy

Per applicare a tutte le fasi (S1–S9):
```bash
# Auto-format + add type hints
ruff format src/codes/ntc2018/secondary_elements/*/
isort src/codes/ntc2018/secondary_elements/*/

# Verify synta x
mypy src/codes/ntc2018/secondary_elements/ --strict
```

---

## Checklist per Completamento Docstring

- [ ] models.py: Enum + dataclass docstring
- [ ] checks_slu.py: Funzioni docstring + commenti formule
- [ ] checks_sle.py: Idem
- [ ] __init__.py: API docstring + contract
- [ ] <fase>_widget.py: Qt widget docstring (se presente)
- [ ] Run pytest su S1–S9
- [ ] Run mypy tipo-check su tutti i moduli
- [ ] Generate docs con Sphinx (optional, futuro)
