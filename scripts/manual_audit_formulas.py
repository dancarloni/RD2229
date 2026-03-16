#!/usr/bin/env python3
"""
Audit Manuale Approfondito — Verifica formule nel codice sorgente
Esamina direttamente il codice implementato per identificare:
- Formule corrette secondo normativa
- Gap di implementazione
- Errori di calcolo
- Mancanza di vincoli normativi
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

SRC_DIR = Path(__file__).parent.parent / "src"
DOCS_DIR = Path(__file__).parent.parent / "docs"

KEY_MODULES = {
    "A": {
        "title": "Database Materiali",
        "key_files": ["core/materials_repository.py", "data/materials/"],
        "checks": [
            "Verificare che i coefficienti di sicurezza per ogni norma siano corretti",
            "Verificare che le classi di resistenza siano complete per RD2229, DM96, NTC2018",
            "Verificare formule di conversione kg/cm² ↔ MPa",
        ],
    },
    "C": {
        "title": "Pipeline di Calcolo",
        "key_files": ["core/pipeline.py", "core/verification_engine.py"],
        "checks": [
            "Verificare orchestrazione pipeline step 1-8",
            "Verificare dispatcher di calcolo per TA/SLU/SLE/DM96",
            "Verificare gestione schema versioning",
        ],
    },
    "N": {
        "title": "Carote CLS",
        "key_files": ["core_calculus/carote.py", "calculations/carote"],
        "checks": [
            "Verificare 10 formule di conversione carota → cilindrica",
            "Verificare EN 13791 e NTC2018 § 11.8.6",
            "Verificare calcolo scarto quadratico medio",
        ],
    },
    "O": {
        "title": "Sismicità e Spettri",
        "key_files": ["seismic/spettro_ntc2018.py", "seismic/ingv_hazard.py"],
        "checks": [
            "Verificare spettro NTC2018 §3.2.3 e 3.2.4",
            "Verificare interpolazione griglia INGV",
            "Verificare formule di accelerazione spettrale",
        ],
    },
    "X3": {
        "title": "Verifiche SLU Solai",
        "key_files": ["core_calculus/verifiche_slu_solai.py", "calculations/solai"],
        "checks": [
            "Verificare formula momento resistente M_Rd",
            "Verificare formula di taglio V_Rd",
            "Verificare punzonamento NTC2018 §4.1.2.1.4.2",
        ],
    },
}


class ManualAuditor:
    """Audit manuale approfondito via ispezione codice"""

    def __init__(self):
        self.findings: Dict[str, List[Dict]] = {}

    def analyze_phase_code(self, phase_id: str, key_files: List[str]) -> List[str]:
        """Analizza il codice di una fase e estrae le formule implementate"""
        findings = []

        for pattern in key_files:
            # Espandi glob pattern
            if "*" in pattern:
                matches = list(SRC_DIR.glob(pattern))
            else:
                matches = [SRC_DIR / pattern]

            for file_path in matches:
                if not file_path.exists():
                    findings.append(f"⚠️  File non trovato: {file_path}")
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    # Cerca formule (pattern: variabili = ... calcoli ...)
                    formulas = re.findall(r"(\w+)\s*=\s*([^#\n]*?)(?:\n|#)", content)

                    # Cerca docstring e commenti sulla norma
                    docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)

                    findings.append(f"✓ {file_path.relative_to(SRC_DIR)}")
                    findings.append(f"  - Formule trovate: {len(formulas)}")
                    findings.append(f"  - Docstring: {len(docstrings)}")

                    # Cerca riferimenti normativi
                    norm_refs = re.findall(
                        r"(NTC2018|NTC2008|DM96|DM92|RD2229|EC2|EC3|EC8|Circ\.|OPCM)", content
                    )
                    if norm_refs:
                        findings.append(f"  - Norme citate: {', '.join(set(norm_refs))}")

                except Exception as e:
                    findings.append(f"❌ Errore lettura {file_path}: {e}")

        return findings

    def check_phase(self, phase_id: str):
        """Audit completo di una fase"""
        if phase_id not in KEY_MODULES:
            return

        spec = KEY_MODULES[phase_id]
        print(f"\n{'='*80}")
        print(f"AUDIT APPROFONDITO FASE {phase_id} — {spec['title']}")
        print(f"{'='*80}\n")

        findings = self.analyze_phase_code(phase_id, spec["key_files"])
        for line in findings:
            print(line)

        print(f"\n Checklist di verifica normativa:")
        for check in spec["checks"]:
            print(f"  ☐ {check}")

        self.findings[phase_id] = findings

    def run_all_audits(self):
        """Esegui audit manuale di tutte le fasi critiche"""
        print("\n" + "=" * 80)
        print("AUDIT MANUALE APPROFONDITO - Verifica formule nel codice")
        print("=" * 80)

        for phase_id in KEY_MODULES.keys():
            self.check_phase(phase_id)

        self.print_summary()

    def print_summary(self):
        """Stampa sommario finale"""
        print(f"\n{'='*80}")
        print(f"SOMMARIO AUDIT MANUALE")
        print(f"{'='*80}\n")

        print("Fasi critiche analizzate:")
        for phase_id in KEY_MODULES.keys():
            findings = self.findings.get(phase_id, [])
            print(f"  • Fase {phase_id}: {len(findings)} righe di analisi")


def main():
    auditor = ManualAuditor()
    auditor.run_all_audits()


if __name__ == "__main__":
    main()
