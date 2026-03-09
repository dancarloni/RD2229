"""Modelli dati per elementi secondari — DM 09/01/1996.

Il DM96 utilizza un approccio sismico semplificato per gli elementi
non strutturali, con forza orizzontale F_h = C * W dove C dipende
dalla zona sismica e dal piano dell'edificio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Coefficienti sismici C per zona e importanza (DM96 §3.2)
# Zona: 1 (alta sismicita), 2 (media), 3 (bassa)
COEFFICIENTE_SISMICO_C: dict[int, float] = {
    1: 0.10,
    2: 0.07,
    3: 0.04,
}


@dataclass
class SecondaryElementSpecDM96:
    """Specifica per elemento secondario secondo DM96.

    Attributes:
        element_type: tipo elemento (tramezzo, parapetto, camino, etc.)
        W_kN: peso dell'elemento [kN]
        zona_sismica: zona sismica 1, 2 o 3
        piano: numero del piano (1-based, piano terra = 1)
        n_piani: numero totale di piani dell'edificio
        beta_piano: fattore di amplificazione per piano (default: calcolato)
        F_Rd_kN: resistenza di progetto ancoraggio [kN] (opzionale)
        drift_value: spostamento interpiano relativo (adimensionale, opzionale)
        drift_limit: limite drift ammissibile (default h/300 = 0.00333)
        influence_on_global_model: se True, richiede analisi globale
    """

    element_type: str = ""
    W_kN: float = 0.0
    zona_sismica: int = 2
    piano: int = 1
    n_piani: int = 1
    beta_piano: float | None = None
    F_Rd_kN: float | None = None
    drift_value: float | None = None
    drift_limit: float = 0.00333  # h/300
    influence_on_global_model: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def calcola_beta_piano(self) -> float:
        """Fattore di amplificazione per piano (DM96).

        Varia linearmente da 1.0 al piano terra a 1.0 + 0.5*(piano/n_piani)
        per i piani superiori. Semplificazione conservativa.
        """
        if self.beta_piano is not None:
            return self.beta_piano
        if self.n_piani <= 0:
            return 1.0
        return 1.0 + 0.5 * (self.piano / self.n_piani)

    def validate(self) -> list[str]:
        """Validazione minima dello spec."""
        errs: list[str] = []
        if not self.element_type:
            errs.append("element_type deve essere specificato")
        if self.W_kN <= 0:
            errs.append("W_kN deve essere > 0")
        if self.zona_sismica not in (1, 2, 3):
            errs.append("zona_sismica deve essere 1, 2 o 3")
        if self.piano < 1:
            errs.append("piano deve essere >= 1")
        return errs
