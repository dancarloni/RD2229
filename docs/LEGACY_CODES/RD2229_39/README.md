# RD 2229/1939 — Modulo Normativo (Legacy)

## Scopo
Implementare in modo incrementale e altamente modulare i metodi di azione sismica previsti dal **RD 2229/39**.

## MVP previsto (STEP 3)
- Forze ondulatorie per piano da percentuale della massa di piano.
- Componente sussultoria derivata: 125% dell'ondulatorio (tracciata).
- Policy masse: impalcato + 1/2 verticali sopra/sotto (configurabile).

## Estendibilità futura
- Nuovi metodi = nuovi file in `methods/`.
- Nuove interpretazioni = nuove `policies/`.
- Ogni modifica significativa va in changelog e, se architetturale, in ADR.
