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
    params: dict[str, float] = field(default_factory=dict)

    def get_param(self, name: str) -> float | None:
        """
        Restituisce un parametro del materiale, oppure None se mancante.

        TODO Copilot:
        - Validazione su nome parametro.
        - Logging esteso.
        """
        return self.params.get(name)


# ======================================================================
# FINE FILE
# ======================================================================
