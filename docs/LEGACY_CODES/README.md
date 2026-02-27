# Legacy Codes

Questa cartella contiene l'infrastruttura documentale per normative storiche/legacy (es. **RD 2229/1939**, DM92, DM96).

## Principi
1. Ogni calcolo deve produrre output con **TraceRecord** completo.
2. Le norme legacy sono implementate come **provider isolati** (`src/codes/<code_id>/...`).
3. Le parti interpretative (attribuzione masse, piani estremi) devono stare in `policies/`.
4. Ogni metodo deve essere un modulo separato in `methods/`, con test dedicati.
