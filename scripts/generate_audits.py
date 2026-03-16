import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent

template_path = root / "docs" / "audit_report_template.md"
template = template_path.read_text(encoding="utf-8")

phase_files = sorted(root.glob("docs/piano_fase_*.md"))

for phase_file in phase_files:
    text = phase_file.read_text(encoding="utf-8")
    m = re.search(r"^#\s+Fase\s+([^\s–—]+)\s*[–—]\s*(.+)$", text, re.MULTILINE)
    if m:
        phase_id = m.group(1).strip()
        phase_title = m.group(2).strip()
    else:
        phase_id = phase_file.stem.replace("piano_fase_", "")
        phase_title = ""
    status = "UNKNOWN"
    commit = "—"
    m_status = re.search(r"\*\*Stato\*\*\s*\|\s*([^\n]+)", text)
    if m_status:
        status = m_status.group(1).strip()
    m_commit = re.search(r"\*\*Commit\*\*\s*\|\s*`([0-9a-f]{6,40})`", text)
    if m_commit:
        commit = m_commit.group(1).strip()
    norms = []
    m_norms = re.search(r"\*\*Norma/e di riferimento\*\*\s*\|\s*([^\n]+)", text)
    if m_norms:
        norms = [n.strip() for n in m_norms.group(1).split(",") if n.strip()]
    if not norms:
        m_refs = re.search(r"##\s*Riferimenti normativi.*?\n\n(.*?)\n\n##", text, re.S)
        if m_refs:
            norms = [line.strip() for line in m_refs.group(1).splitlines() if line.strip()]
    referenced_tests = set(re.findall(r"`(tests/[^`]+\.py)`", text))
    missing_tests = [t for t in referenced_tests if not (root / t).exists()]
    bug_lines = []
    m_bug = re.search(
        r"## Bug corretti durante lo sviluppo\n\n\| Bug \| File \| Descrizione \|\n(.*?)(\n## |\Z)",
        text,
        re.S,
    )
    if m_bug:
        bug_lines = [
            line.strip()
            for line in m_bug.group(1).splitlines()
            if line.strip() and not line.strip().startswith("| ---")
        ]
    outcome = "OK" if "COMPLETATO" in status.upper() else "DA COMPLETARE"
    if missing_tests:
        outcome = "DA CORREGGERE"
    audit = template
    audit = audit.replace("<X>", phase_id)
    audit = audit.replace("<Titolo>", phase_title or phase_id)
    audit = audit.replace("- phase_id:", f"- phase_id: {phase_id}")
    audit = audit.replace("- status:", f"- status: {status}")
    audit = audit.replace("- last_commit:", f"- last_commit: {commit}")
    audit = audit.replace("- tags:", f"- tags: #todo")
    audit = audit.replace("- owner:", f"- owner: Daniele Carloni")
    notes = []
    if missing_tests:
        notes.append(f"Riferimenti a test mancanti: {', '.join(missing_tests)}")
    if bug_lines:
        notes.append(f"Bug documentati: {len(bug_lines)}")
    if not norms:
        notes.append("Riferimenti normativi assenti o non riconosciuti")
    if norms:
        notes.append(f"Norme menzionate: {', '.join(norms[:5])}{'...' if len(norms)>5 else ''}")
    if notes:
        audit = audit.replace("Note sintetiche:", "Note sintetiche:\n  - " + "\n  - ".join(notes))
    else:
        audit = audit.replace("Note sintetiche:", "Note sintetiche: nessuna criticità rilevata")
    audit = audit.replace("- OK / DA CORREGGERE / DA COMPLETARE", f"- {outcome}")
    out_path = root / "docs" / f"audit_fase_{phase_id}.md"
    out_path.write_text(audit, encoding="utf-8")
    print(f"Generated audit for {phase_id}")
