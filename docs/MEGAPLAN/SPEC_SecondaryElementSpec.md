Required fields: id, type (CANTILEVER|SIGNAGE|PARTITION|CHIMNEY), geometry, material_code, attachments[], loads{Gk,Qk,wind,seismic}, boundary_conditions, notes.
For each type list the mandatory checks (SLU bending/taglio/anchors; SLE deflection/crack; seismic attachment per EN1998).
Storage: project.secondary_elements[] schema (documented).
UI mapping: wire widgets in src/gui/secondary_elements/* must bind to the same field names.

File: docs/MEGAPLAN/SPEC_SecondaryElementSpec.md (estratto per template)

Per ciascun type (CANTILEVER, SIGNAGE, PARTITION, CHIMNEY) definire: modello statico, campi obbligatori (geometry, material_code, attachments[], loads{Gk,Qk,wind,seismic}), checks richiesti (SLU bending, SLU shear/anchors, SLE deflection/cracking, seismic anchors).
Esempio sintetico (CANTILEVER): checks: secondary_cantilever_moment, secondary_cantilever_shear, secondary_cantilever_anchor, secondary_cantilever_deflection.
Test fixtures (input) forniti nella sezione Test plan qui sotto.
TODO: incollare testo NTC2018 §7.2 (Circolare NTC) come reference.