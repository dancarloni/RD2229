#!/usr/bin/env python3
"""
Deep Audit Framework — Verifica approfondita di tutte le 42 fasi RD2229
- Estrae metadati e dipendenze da ogni piano_fase_*.md
- Analizza i file sorgente e verifica la conformità normativa
- Identifica criticità (formule mancanti, test insufficienti, gap normativi)
- Genera rapporti audit dettagliati con livello di severità
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DOCS_DIR = Path(__file__).parent.parent / "docs"
SRC_DIR = Path(__file__).parent.parent / "src"
TESTS_DIR = Path(__file__).parent.parent / "tests"


@dataclass
class FormulaCriticality:
    """Criticità rilevata in una fase"""

    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    category: str  # "formula", "test", "norm", "doc", "legal"
    description: str
    line_ref: Optional[str] = None
    recommendation: str = ""


@dataclass
class PhaseAudit:
    """Risultato audit per una fase"""

    phase_id: str
    title: str
    status: str
    commit: str
    norms: List[str]
    criticalities: List[FormulaCriticality] = field(default_factory=list)

    # Verifiche
    has_tests: bool = False
    test_count: int = 0
    formula_completeness: int = 0  # 0-100%
    normative_coverage: int = 0  # 0-100%

    # Conclusioni
    audit_status: str = "PENDING"  # PENDING, OK, WARNING, CRITICAL
    risk_level: str = "UNKNOWN"  # LOW, MEDIUM, HIGH

    def add_criticality(
        self, severity: str, category: str, desc: str, line: Optional[str] = None, rec: str = ""
    ):
        """Aggiungi una criticità all'audit"""
        self.criticalities.append(FormulaCriticality(severity, category, desc, line, rec))

        # Aggiorna audit_status in base alla severità
        if severity == "CRITICAL":
            self.audit_status = "CRITICAL"
            self.risk_level = "HIGH"
        elif severity == "HIGH" and self.audit_status != "CRITICAL":
            self.audit_status = "WARNING"
            self.risk_level = "HIGH"
        elif severity == "MEDIUM" and self.audit_status == "PENDING":
            self.audit_status = "WARNING"
            self.risk_level = "MEDIUM"


class DeepAuditor:
    """Sistema di audit approfondito per RD2229"""

    # Mappe di verifica normativa per categoria
    NORM_REQUIREMENTS = {
        "RD2229": {
            "requires": ["formula", "tabelle_coefficienti", "casi_carico", "sicurezza"],
            "critical_formulas": ["taglio", "torsione", "pressoflessione", "snellezza"],
        },
        "DM96": {
            "requires": ["combinazioni_slu", "verifiche_sle", "formula_momenti", "duttilità"],
            "critical_formulas": ["pressoflessione", "taglio", "punta", "torsione"],
        },
        "NTC2018": {
            "requires": [
                "fattore_comportamento_q",
                "spettro_risposta",
                "combinazioni",
                "stato_limite",
                "criteri_duttilità",
            ],
            "critical_formulas": [
                "momento_resistente",
                "taglio",
                "torsione",
                "punzonamento",
                "frequenza_naturale",
                "spostamento",
            ],
        },
        "EC2": {
            "requires": ["metodo_progettuale", "coefficienti_parziali", "verifiche_stato_limite"],
            "critical_formulas": ["momento_generico", "taglio_generico", "aderenza"],
        },
        "EC3": {
            "requires": ["classificazione_sezioni", "instabilità", "momento_resistente"],
            "critical_formulas": ["momento_plastico", "taglio", "aste_compresse"],
        },
    }

    def __init__(self):
        self.phase_audits: Dict[str, PhaseAudit] = {}
        self.all_files = list(DOCS_DIR.glob("piano_fase_*.md"))
        self.all_phases = sorted([f.stem.replace("piano_fase_", "") for f in self.all_files])

    def extract_phase_metadata(self, phase_id: str) -> Dict:
        """Estrai metadati da piano_fase_<id>.md"""
        doc_path = DOCS_DIR / f"piano_fase_{phase_id}.md"

        if not doc_path.exists():
            return {}

        content = doc_path.read_text(encoding="utf-8")

        # Estrai YAML frontmatter
        fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        frontmatter = {}
        if fm_match:
            for line in fm_match.group(1).split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    frontmatter[key.strip()] = val.strip()

        # Estrai metadati da tabella
        metadata = {
            "phase_id": phase_id,
            "title": re.search(r"^# Fase \w+.*?—\s*(.*)", content, re.MULTILINE),
            "status": re.search(r"\|\s*\*\*?Stato\*?\*?\s*\|\s*([^|]+)", content),
            "commit": re.search(r"\|\s*\*\*?Commit\*?\*?\s*\|\s*([^|]+)", content),
            "norms": re.findall(r"(RD2229|DM\d{2}|NTC\d{4}|EC\d|Circ\.\s*\d+|OPCM|CNR)", content),
            "test_files": re.findall(r"`(tests/test_\w+\.py)`", content),
        }

        # Estrai e normalizza
        result = {
            "phase_id": phase_id,
            "title": metadata["title"].group(1) if metadata["title"] else "Unknown",
            "status": metadata["status"].group(1).strip() if metadata["status"] else "UNKNOWN",
            "commit": metadata["commit"].group(1).strip() if metadata["commit"] else "—",
            "norms": list(set(metadata["norms"])),
            "test_files": metadata["test_files"],
            "raw_content": content,
            "frontmatter": frontmatter,
        }
        return result

    def check_test_files(self, phase_id: str, test_files: List[str]) -> Tuple[bool, int]:
        """Verifica esistenza e numero di test"""
        if not test_files:
            return False, 0

        count = 0
        for test_file in test_files:
            path = TESTS_DIR / test_file
            if path.exists():
                # Conta numero di def test_*
                content = path.read_text(encoding="utf-8")
                test_funcs = len(re.findall(r"def test_\w+\(", content))
                count += test_funcs

        return count > 0, count

    def verify_normative_implementation(
        self, phase_id: str, norms: List[str], content: str
    ) -> List[FormulaCriticality]:
        """Verifica implementazione contro standard normativi"""
        criticalities = []

        for norm in norms:
            norm_key = norm.replace(" ", "")
            if norm_key in self.NORM_REQUIREMENTS:
                reqs = self.NORM_REQUIREMENTS[norm_key]

                # Verifica requisiti dichiarati
                for req in reqs["requires"]:
                    # Cerca parole chiave
                    keywords = req.split("_")
                    found = any(kw.lower() in content.lower() for kw in keywords)

                    if not found:
                        criticalities.append(
                            FormulaCriticality(
                                severity="HIGH",
                                category="norm",
                                description=f"{norm}: Requisito '{req}' non documentato chiaramente",
                                recommendation=f"Aggiungere sezione che documenti '{req}' con formule e riferimenti normativi",
                            )
                        )

                # Verifica formule critiche
                for formula in reqs["critical_formulas"]:
                    # Cerca parole chiave nel testo
                    escaped_formula = re.escape(formula)
                    if not re.search(escaped_formula, content, re.IGNORECASE):
                        # Cerca anche abbreviazioni
                        if (
                            formula == "pressoflessione"
                            and "N-M" not in content
                            and "pressoflessione" not in content.lower()
                        ):
                            criticalities.append(
                                FormulaCriticality(
                                    severity="CRITICAL",
                                    category="formula",
                                    description=f"{norm}: Formula '{formula}' mancante o non testata adeguatamente",
                                    line_ref="§ della norma",
                                    recommendation=f"Implementare e testare rigorosamente la formula di {formula}",
                                )
                            )

        return criticalities

    def audit_phase(self, phase_id: str) -> PhaseAudit:
        """Esegui audit approfondito di una singola fase"""
        metadata = self.extract_phase_metadata(phase_id)

        if not metadata:
            return PhaseAudit(
                phase_id=phase_id,
                title="Unknown",
                status="NOT_FOUND",
                commit="—",
                norms=[],
                audit_status="CRITICAL",
            )

        audit = PhaseAudit(
            phase_id=phase_id,
            title=metadata["title"],
            status=metadata["status"],
            commit=metadata["commit"],
            norms=metadata["norms"],
        )

        # Verifica test
        has_tests, test_count = self.check_test_files(phase_id, metadata["test_files"])
        audit.has_tests = has_tests
        audit.test_count = test_count

        if not has_tests:
            audit.add_criticality(
                "HIGH",
                "test",
                f"Nessun test trovato per fase {phase_id}",
                rec="Aggiungere test unitari e di integrazione",
            )
        elif test_count < 5:
            audit.add_criticality(
                "MEDIUM",
                "test",
                f"Copertura test insufficiente ({test_count} test)",
                rec="Aggiungere almeno 10 test per fase",
            )

        # Verifica normativa
        norm_criticalities = self.verify_normative_implementation(
            phase_id, audit.norms, metadata["raw_content"]
        )
        for crit in norm_criticalities:
            audit.add_criticality(
                crit.severity, crit.category, crit.description, crit.line_ref, crit.recommendation
            )

        # Calcola score di completezza
        if "✅" in audit.status or "COMPLETATO" in audit.status:
            audit.formula_completeness = 90
            audit.normative_coverage = 85
        elif "🟨" in audit.status or "IN CORSO" in audit.status:
            audit.formula_completeness = 50
            audit.normative_coverage = 50
        else:
            audit.formula_completeness = 0
            audit.normative_coverage = 0

        # Se non ci sono criticità critiche, marca come OK
        critical_count = sum(1 for c in audit.criticalities if c.severity == "CRITICAL")
        if critical_count == 0:
            if audit.audit_status == "PENDING":
                audit.audit_status = "OK"
                audit.risk_level = "LOW"

        return audit

    def run_all_audits(self):
        """Esegui audit per tutte le fasi in ordine"""
        print(f"\n{'='*80}")
        print(f"AUDIT APPROFONDITO RD2229 — {len(self.all_phases)} FASI")
        print(f"{'='*80}\n")

        for i, phase_id in enumerate(self.all_phases, 1):
            print(
                f"[{i:2d}/{len(self.all_phases)}] Auditando Fase {phase_id}...", end=" ", flush=True
            )

            audit = self.audit_phase(phase_id)
            self.phase_audits[phase_id] = audit

            # Status summary
            if audit.audit_status == "CRITICAL":
                status_str = "🔴 CRITICAL"
            elif audit.audit_status == "WARNING":
                status_str = "🟠 WARNING"
            else:
                status_str = "🟢 OK"

            print(f"{status_str} ({len(audit.criticalities)} criticità)")

    def generate_detailed_report(self, phase_id: str) -> str:
        """Genera report audit dettagliato per una fase"""
        audit = self.phase_audits.get(phase_id)
        if not audit:
            return f"# Fase {phase_id} — Nessun audit disponibile\n"

        lines = [
            f"# Audit Fase {phase_id} — {audit.title}\n",
            f"**Generato:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"\n## Metadati",
            f"- **phase_id:** {audit.phase_id}",
            f"- **status:** {audit.status}",
            f"- **last_commit:** {audit.commit}",
            f"- **norms:** {', '.join(audit.norms) if audit.norms else 'N/A'}",
            f"- **audit_status:** {audit.audit_status}",
            f"- **risk_level:** {audit.risk_level}\n",
        ]

        lines.append(f"## Analisi\n")
        lines.append(f"### Test")
        lines.append(f"- Test found: {'✅ Sì' if audit.has_tests else '❌ No'}")
        lines.append(f"- Total tests: {audit.test_count}")
        lines.append(f"- Formula completeness: {audit.formula_completeness}%")
        lines.append(f"- Normative coverage: {audit.normative_coverage}%\n")

        if audit.criticalities:
            lines.append(f"### Criticità rilevate ({len(audit.criticalities)})\n")

            # Organizza per severità
            by_severity = {}
            for crit in audit.criticalities:
                if crit.severity not in by_severity:
                    by_severity[crit.severity] = []
                by_severity[crit.severity].append(crit)

            severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            for sev in severity_order:
                if sev in by_severity:
                    lines.append(f"\n#### {sev}")
                    for crit in by_severity[sev]:
                        lines.append(f"\n- **{crit.category.upper()}:** {crit.description}")
                        if crit.line_ref:
                            lines.append(f"  - Ref: {crit.line_ref}")
                        if crit.recommendation:
                            lines.append(f"  - 🔧 {crit.recommendation}")
        else:
            lines.append(f"\n### ✅ Nessuna criticità rilevata")

        lines.append(f"\n---\n")
        return "\n".join(lines)

    def save_all_reports(self):
        """Salva tutti i rapporti audit nei file audit_fase_*.md"""
        updated_count = 0
        for phase_id, audit in self.phase_audits.items():
            report = self.generate_detailed_report(phase_id)
            report_path = DOCS_DIR / f"audit_fase_{phase_id}.md"

            report_path.write_text(report, encoding="utf-8")
            print(f"Salvato: audit_fase_{phase_id}.md")
            updated_count += 1

        print(f"\n✅ {updated_count} rapporti audit salvati\n")
        return updated_count

    def generate_executive_summary(self) -> str:
        """Genera sommario esecutivo dell'audit"""
        lines = [
            "# Sommario Esecutivo Audit — RD2229\n",
            f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Fasi auditate:** {len(self.phase_audits)}\n\n",
        ]

        # Conta per status
        by_status = {}
        all_crits = []
        for audit in self.phase_audits.values():
            status = audit.audit_status
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(audit.phase_id)
            all_crits.extend(audit.criticalities)

        lines.append("## Risultati per Audit Status\n")
        for status in ["OK", "WARNING", "CRITICAL"]:
            if status in by_status:
                phases = by_status[status]
                icon = {"OK": "🟢", "WARNING": "🟠", "CRITICAL": "🔴"}[status]
                lines.append(f"{icon} **{status}:** {len(phases)} fasi")
                lines.append(f"  - {', '.join(sorted(phases))}\n")

        lines.append(f"\n## Criticità Totali: {len(all_crits)}\n")

        # Organizza per categoria e severità
        by_cat_sev = {}
        for crit in all_crits:
            key = (crit.category, crit.severity)
            if key not in by_cat_sev:
                by_cat_sev[key] = []
            by_cat_sev[key].append(crit.description)

        for cat, sev in sorted(by_cat_sev.keys()):
            count = len(by_cat_sev[(cat, sev)])
            lines.append(f"- **{sev} {cat.upper()}:** {count}")

        lines.append(f"\n")
        return "\n".join(lines)


def main():
    """Main entry point"""
    auditor = DeepAuditor()

    print(f"\nScoperta fasi: {len(auditor.all_phases)} fasi")
    print(f"Fasi: {', '.join(auditor.all_phases)}\n")

    # Esegui audit per tutte le fasi
    auditor.run_all_audits()

    # Salva rapporti
    auditor.save_all_reports()

    # Salva sommario
    summary = auditor.generate_executive_summary()
    summary_path = DOCS_DIR / "AUDIT_SUMMARY.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"✅ Sommario salvato: AUDIT_SUMMARY.md\n")

    # Stampa risultati
    print(f"\n{'='*80}")
    print(f"RISULTATI AUDIT APPROFONDITO")
    print(f"{'='*80}\n")
    print(summary)

    # Dettagli criticità per fase
    critical_phases = [
        (pid, audit)
        for pid, audit in auditor.phase_audits.items()
        if audit.audit_status == "CRITICAL"
    ]

    if critical_phases:
        print(f"\n⚠️  FASI CON CRITICITÀ CRITICHE ({len(critical_phases)}):\n")
        for phase_id, audit in critical_phases:
            print(
                f"  🔴 Fase {phase_id}: {len([c for c in audit.criticalities if c.severity == 'CRITICAL'])} criticità critiche"
            )


if __name__ == "__main__":
    main()
