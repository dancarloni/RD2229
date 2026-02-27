
REPORT_BUILDER_RD2229 – Codice Python Allineato al Builder NTC2018
Status: FILE OPERATIVO – CODICE CORE REPORT (VINCOLANTE)
Questo documento contiene il codice Python completo del ReportBuilderRD2229, allineato strutturalmente, concettualmente e funzionalmente al ReportBuilderNTC2018.
L’allineamento garantisce:

interfaccia comune (BaseReportBuilder);
stesso flusso dati (ProjectModel → VerificationResult → Markdown);
assenza totale di ricalcoli;
coerenza multi‑normativa del sistema di report.


1. Interfaccia comune (richiamo vincolante)
Il builder RD2229 implementa la stessa interfaccia dei builder NTC.

class BaseReportBuilder:
    def __init__(self, project_model):
        self.project_model = project_model

    def build(self) -> str:
        raise NotImplementedError




2. Codice – core/report/report_builder_rd2229.py

from core.report.base_report_builder import BaseReportBuilder


class ReportBuilderRD2229(BaseReportBuilder):
    """
    Generatore della Relazione di Calcolo secondo R.D. 2229/1939.
    Non esegue calcoli strutturali: utilizza solo VerificationResult.
    """

    def build(self) -> str:
        pm = self.project_model

        # Controlli preliminari
        if pm.normativa_attiva != 'RD2229':
            raise RuntimeError("Normativa attiva non compatibile con ReportBuilderRD2229")

        results = pm.verifiche_in_relazione or pm.verifiche_rd2229

        if not results:
            raise RuntimeError("Nessuna verifica RD2229 disponibile per la relazione")

        md = []

        # Intestazione
        md.append("# RELAZIONE DI CALCOLO – R.D. 2229/1939\n")
        md.append("## 1. Inquadramento generale dell’opera\n")
        md.append(f"Oggetto: {pm.dati_generali.get('oggetto','')}\n")
        md.append(f"Ubicazione: {pm.dati_generali.get('ubicazione','')}\n")
        md.append(f"Committente: {pm.dati_generali.get('committente','')}\n")

        # Materiali
        md.append("\n## 2. Materiali impiegati\n")
        if pm.materiale:
            md.append(f"Materiale: {pm.materiale.nome}\n")
            md.append(f"σ amm.: {pm.materiale.sigma_amm}\n")

        # Verifiche
        md.append("\n## 3. Verifiche a tensioni ammissibili\n")

        for r in results:
            md.append(f"### {r.reference.paragrafo}\n")
            md.append(f"- Tensione calcolata σ: {r.demand}\n")
            md.append(f"- Tensione ammissibile σₐₘₘ: {r.capacity}\n")
            md.append(f"- Rapporto σ/σₐₘₘ: {r.ratio}\n")
            md.append(f"- Esito: {r.status}\n\n")

        # Esito finale
        md.append("\n## 4. Esito complessivo\n")
        if all(r.status.value == 'OK' for r in results):
            md.append("La struttura risulta verificata alle tensioni ammissibili.\n")
        else:
            md.append("La struttura NON risulta verificata alle tensioni ammissibili.\n")

        return "\n".join(md)




3. Allineamento con ReportBuilderNTC2018

Aspetto	NTC2018	RD2229
Classe	ReportBuilderNTC2018	ReportBuilderRD2229
Interfaccia	BaseReportBuilder	BaseReportBuilder
Input	VerificationResult	VerificationResult
Output	Markdown	Markdown
Ricalcoli	❌	❌



Questo file è vincolante per l’implementazione del ReportBuilder RD2229 allineato al framework NTC2018.
