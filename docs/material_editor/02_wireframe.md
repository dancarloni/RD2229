# Material Editor GUI — Wireframe e layout

## Schema grafico (side panel)

┌───────────────────────────── Material Editor ─────────────────────────────┐
│ [Calcestruzzi] [Acciai] [Legno] [Muratura] [Compositi] [Terreni]         │
│ ┌───────────────┬───────────────────────────────┐                        │
│ │  Tabella      │  Frame dettaglio materiale    │                        │
│ │  materiali    │  (campi editabili, override)  │                        │
│ │  [seleziona]  │  Codice:        [_____]       │                        │
│ │               │  Descrizione:   [_____]       │                        │
│ │               │  Norma:         [_____]       │                        │
│ │               │  f_ck:          [_____] [□]   │ ← override manuale    │
│ │               │  γ_c:           [_____] [□]   │ ← override manuale    │
│ │               │  ... (tutti i parametri)      │                        │
│ │               │  Extra/avanzate:              │                        │
│ │               │  [parametro_custom] [_____]   │                        │
│ │               │  [Salva] [Annulla] [Ctrl+S]   │                        │
│ │               │  [Undo] [Redo]                │                        │
│ └───────────────┴───────────────────────────────┘                        │
│ [Aggiungi] [Carica] [Salva] [Reset layout] [Apri log]                    │
│ [Filtro: Norma ▼] [Tipo ▼] [Descrizione: ____] [Solo attivi]             │
│ [Esporta: ▼ HTML/Markdown/CSV/TXT] [Copia] [Importa]                     │
│ [Messaggi di warning/validazione qui]                                    │
└──────────────────────────────────────────────────────────────────────────┘

## Schema grafico (frame sotto)

┌───────────────────────────── Material Editor ─────────────────────────────┐
│ [Tab tipologia]                                                         │
│ ┌───────────────────────────────────────────────────────────────────────┐ │
│ │ Tabella materiali                                                    │ │
│ └───────────────────────────────────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────────────────────────────────┐ │
│ │ Dettaglio materiale (campi editabili, override)                      │ │
│ │ Codice:        [_____]                                               │ │
│ │ Descrizione:   [_____]                                               │ │
│ │ ...                                                                 │ │
│ │ [Salva] [Annulla] [Ctrl+S] [Undo] [Redo]                            │ │
│ └───────────────────────────────────────────────────────────────────────┘ │
│ ...toolbar, filtri, esportazione...                                     │
└─────────────────────────────────────────────────────────────────────────┘

---

Per la logica di layout adattivo, vedi docs/material_editor/09_layout.md.