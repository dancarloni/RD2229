# SPEC_01A Domain Model Insufficienze (LOCKED Resolution)

Fonte primaria: `docs/MEGAPLAN/AGGREGAZIONE.md`.

## Obiettivo

Risolvere solo le insufficienze dati emerse, senza riscrittura radicale del modello.

## LOCKED risolto

1. `LoadCase` include spazio per variabili ambientali:
   - campi base tipizzati (`actions`) + contenitore `environmental` per neve/vento/altre variabili non meccaniche.
2. Distinzione elemento primario/secondario:
   - campo `role` nell’entità `Element`.
3. `FireProfile`:
   - entità autonoma a livello progetto con possibile override per elemento.

## OPEN (da confermare in evoluzione)

- Catalogo completo categorie ambientali e unità standard per ciascuna categoria.
- Politica definitiva di override incendio per portfolio multi-modulo.

## Impatto tracciato

- Flussi: validazione più esplicita in creazione load case e routing checks.
- Persistence: repository devono preservare `role`, `environmental`, `fire_profile`.
- Plugin: capabilities possono filtrare per `Element.role` e `LoadCase.category`.

## Decisioni immediate

- Nessuna nuova gerarchia complessa: specializzazione semantica tramite campi e contratti.
- Le estensioni future restano additive e retrocompatibili tramite migrazione schema.
