
REPORT_BUILDER_NTC2018 – Codice Allineato al Builder RD2229
Status: FILE OPERATIVO – GENERAZIONE AUTOMATICA RELAZIONE (VINCOLANTE)
Questo documento definisce il codice del ReportBuilder per NTC2018, allineato strutturalmente e concettualmente al REPORT_BUILDER_RD2229, così da garantire un framework di reporting unico e coerente.
Principi comuni NTC2018 / RD2229:

nessun ricalcolo;
nessuna interpretazione degli esiti;
input esclusivo: ProjectModel + VerificationResult;
output Markdown, poi esportabile PDF/DOCX.


1. Interfaccia comune (vincolante)
Tutti i ReportBuilder devono implementare la stessa interfaccia.

class BaseReportBuilder:
    def __init__(self, project_model):
        self.project_model = project_model

    def build(self) -> str:
        """
        Genera la relazione di calcolo in formato Markdown
        senza eseguire alcun calcolo strutturale.
        """
        raise NotImplementedError




2. Codice – core/report/report_builder_ntc2018.py

from core.report.base_report_builder import BaseReportBuilder


class ReportBuilderNTC2018(BaseReportBuilder):
    """
    Generatore della Relazione di Calcolo secondo NTC2018.
    Usa esclusivamente VerificationResult già validati.
    """

    def build(self) -> str:
        pm = self.project_model

        if pm.normativa_attiva != 'NTC2018':
            raise RuntimeError("Normativa attiva non compatibile con ReportBuilderNTC2018")

        results = pm.verifiche_in_relazione or (pm.verifiche_cap4 + pm.verifiche_cap7)

        md = []
        md.append("# RELAZIONE DI CALCOLO – NTC2018\n")
        md.append("## 1. Inquadramento generale\n")
        md.append(f"Oggetto: {pm.dati_generali.get('oggetto','')}\n")

        md.append("\n## 2. Verifiche strutturali\n")
        for r in results:
            md.append(f"### {r.reference.paragrafo}\n")
            md.append(f"- Capitolo NTC: {r.capitolo_ntc}\n")
            md.append(f"- Domanda Ed: {r.demand}\n")
            md.append(f"- Capacità Rd: {r.capacity}\n")
            md.append(f"- Rapporto Ed/Rd: {r.ratio}\n")
            md.append(f"- Esito: {r.status}\n\n")

        return "\n".join(md)




3. Allineamento con RD2229

Aspetto	NTC2018	RD2229
Classe	ReportBuilderNTC2018	ReportBuilderRD2229
Interfaccia	BaseReportBuilder	BaseReportBuilder
Input	VerificationResult	VerificationResult
Output	Markdown	Markdown
Ricalcoli	❌	❌



Questo file è vincolante per la generazione automatica della Relazione NTC2018.
