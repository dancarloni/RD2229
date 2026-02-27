
PLAN MASTER – Architettura Generale
Status: STABILE
Scopo
Questo documento è il riferimento architetturale principale del progetto. Definisce i principi non negoziabili, la suddivisione dei plan e le regole di integrazione tra calcolo, GUI, input e output.
Principi fondanti

Separazione rigorosa Core di calcolo / GUI / I/O
Modularità estrema: ogni norma o modulo è plug‑in
Retro‑compatibilità garantita (RD2229/39, DM92, DM96)
Tracciabilità tecnico‑normativa completa
Suddivisione dei plan

PLAN_CALCOLO.md
PLAN_GUI.md
PLAN_INPUT_COMUNE.md
PLAN_OUTPUT_COMUNE.md
Regole globali

Nessun piano contiene codice operativo
Ogni piano è vincolante per Copilot e per lo sviluppo
Le GUI non contengono logica normativa
L’output è l’unica fonte per il post‑processing
Uso in VS Code
Copilot deve considerare questi file come vincoli architetturali. Ogni violazione è da considerarsi errore progettuale.
