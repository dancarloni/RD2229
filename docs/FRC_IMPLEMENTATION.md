# FRC (Fiber Reinforced Composite) Implementation

Questo documento riassume la scelta di modellazione iniziale per il supporto FRC nel progetto RD2229.

## Campi aggiunti al modello `Material` (top-level)
- `frc_enabled: bool` — flag che indica che il materiale definisce proprietà FRC.
- `frc_fFts: Optional[float]` — (opzionale) tensione caratteristica di progetto delle fibre (design)
- `frc_fFtu: Optional[float]` — (opzionale) tensione ultima delle fibre
- `frc_eps_fu: Optional[float]` — (opzionale) deformazione ultima delle fibre
- `frc_note: Optional[str]` — note libere sulla fonte o particolarità

## Modulo `core/frc.py`
- `frc_stress(material, strain)` — implementazione MVP: modello lineare fino a `eps_fu`, troncato a `fFtu`.
- `apply_frc_to_section(section, material, strain_distribution)` — placeholder; ritorna (0,0,0) per ora.

## Mapping e prossimi passi
1. Estrarre dai file Visual Basic (`visual_basic/PrincipCA_TA.bas`, `CA_SLU.bas`, `CA_SLE.bas`) le formule esatte relative a FRC e i test numerici (casi di riferimento).
2. Migrare il modello numerico `frc_stress` per ottenere parità numerica con il VB.
3. Implementare `apply_frc_to_section` per integrare i contributi delle fibre nelle verifiche SLU/SLE.

## Note
- La scelta di aggiungere i campi FRC direttamente in `Material` è pensata per semplicità e retrocompatibilità; in futuro potremo aggiungere `FrcLayer` per gestire multipli strati e geometrie avanzate.
- I test iniziali verificano la persistenza dei campi e il comportamento lineare del modello FRC.
