"""Renderer per generare report in formato Markdown.

Genera un documento Markdown con:
- Intestazione progetto e metadati
- Tabella elementi con proprietà geometriche
- Risultati verifiche con esito
- Dettagli parziali per ogni verifica
- Riferimenti normativi

Unità di misura: kg/cm², cm, cm², cm⁴, kg/m³.
"""

import datetime
from typing import Any


class MarkdownReportRenderer:
    """Renderer Markdown per report di verifica strutturale."""

    def __init__(self, template_path: str = "") -> None:
        self.template_path = template_path

    def render(self, data: dict[str, Any]) -> str:
        """Restituisce una stringa Markdown del report.

        Args:
            data: dizionario con chiavi:
                - project_name (str): nome del progetto
                - norm_code (str): norma di riferimento
                - elements (list[dict]): elementi strutturali
                - results (list[dict]): risultati verifiche
                - normative (dict): parametri normativi
                - settings (dict): impostazioni
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        project = data.get("project_name", "Progetto")
        norm = data.get("norm_code", "")

        lines: list[str] = []
        lines.append(f"# Report di Verifica — {project}")
        lines.append("")
        lines.append(f"**Generato:** {now}")
        if norm:
            lines.append(f"**Norma:** {norm}")
        lines.append("")

        # Sezione elementi
        elements = data.get("elements", [])
        lines.append("## Elementi")
        lines.append("")
        if elements:
            lines.extend(self._render_elements_table(elements))
        else:
            lines.append("Nessun elemento definito.")
        lines.append("")

        # Sezione risultati
        results = data.get("results", [])
        lines.append("## Risultati Verifiche")
        lines.append("")
        if results:
            lines.extend(self._render_results_table(results))
            lines.append("")
            lines.append(self._render_summary(results))
        else:
            lines.append("Nessun risultato disponibile.")
        lines.append("")

        # Dettagli parziali
        if results:
            lines.append("## Dettagli")
            lines.append("")
            for i, r in enumerate(results):
                detail = self._render_result_detail(r, i)
                if detail:
                    lines.extend(detail)
                    lines.append("")

        return "\n".join(lines)

    def _render_elements_table(self, elements: list[dict]) -> list[str]:
        lines = [
            "| # | ID | Tipo | b [cm] | h [cm] | As [cm²] |",
            "|---|-----|------|--------|--------|----------|",
        ]
        for i, el in enumerate(elements, 1):
            eid = str(el.get("id", el.get("element_id", f"E{i}")))
            tipo = str(el.get("type", el.get("tipo", "-")))
            b = el.get("b", el.get("width_cm", "-"))
            h = el.get("h", el.get("height_cm", "-"))
            As = el.get("As", "-")
            lines.append(f"| {i} | {eid} | {tipo} | {b} | {h} | {As} |")
        return lines

    def _render_results_table(self, results: list[dict]) -> list[str]:
        lines = [
            "| # | Verifica | Esito | Messaggio |",
            "|---|----------|-------|-----------|",
        ]
        for i, r in enumerate(results, 1):
            action_id = r.get("action_id", "-")
            ok = r.get("ok", False)
            label = "OK" if ok else "NON VERIFICATO"
            msgs = "; ".join(r.get("messages", []))
            lines.append(f"| {i} | {action_id} | **{label}** | {msgs} |")
        return lines

    def _render_summary(self, results: list[dict]) -> str:
        total = len(results)
        passed = sum(1 for r in results if r.get("ok"))
        failed = total - passed
        return f"**Riepilogo:** {passed}/{total} verificate, {failed} non verificate."

    def _render_result_detail(self, result: dict, idx: int) -> list[str]:
        partials = result.get("partials", {})
        if not partials:
            return []
        action_id = result.get("action_id", f"check_{idx}")
        lines = [
            f"### {idx + 1}. {action_id}",
            "",
            "| Parametro | Valore |",
            "|-----------|--------|",
        ]
        for k, v in partials.items():
            lines.append(f"| {k} | {v} |")
        return lines
