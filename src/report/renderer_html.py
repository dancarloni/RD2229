"""Renderer per generare report in formato HTML.

Genera un documento HTML completo con:
- Intestazione progetto e metadati
- Tabella elementi con proprietà geometriche
- Risultati verifiche con esito (OK/NON VERIFICATO)
- Dettagli parziali per ogni verifica
- CSS inline per formattazione

Unità di misura: kg/cm², cm, cm², cm⁴, kg/m³.
"""

import datetime
from typing import Any

_CSS = """\
body { font-family: 'Segoe UI', Arial, sans-serif; margin: 2em; color: #222; }
h1 { color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: .3em; }
h2 { color: #2c5f8a; margin-top: 1.5em; }
h3 { color: #444; }
table { border-collapse: collapse; width: 100%; margin: .8em 0; }
th, td { border: 1px solid #ccc; padding: .4em .7em; text-align: left; font-size: .9em; }
th { background: #f0f4f8; font-weight: 600; }
tr:nth-child(even) { background: #fafbfc; }
.ok { color: #1a7a2e; font-weight: bold; }
.fail { color: #c0392b; font-weight: bold; }
.meta { color: #666; font-size: .85em; }
.partials { font-size: .85em; color: #555; }
"""


class HTMLReportRenderer:
    """Renderer HTML per report di verifica strutturale."""

    def __init__(self, template_path: str = "") -> None:
        self.template_path = template_path

    def render(self, data: dict[str, Any]) -> str:
        """Restituisce una stringa HTML completa.

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

        parts = [
            "<!DOCTYPE html>",
            "<html lang=\"it\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            f"  <title>Report — {_esc(project)}</title>",
            f"  <style>{_CSS}</style>",
            "</head>",
            "<body>",
            f"  <h1>Report di Verifica — {_esc(project)}</h1>",
            f'  <p class="meta"><strong>Generato:</strong> {now}</p>',
        ]

        if norm:
            parts.append(f'  <p class="meta"><strong>Norma:</strong> {_esc(norm)}</p>')

        # Sezione elementi
        elements = data.get("elements", [])
        parts.append("  <h2>Elementi</h2>")
        if elements:
            parts.append(self._render_elements_table(elements))
        else:
            parts.append("  <p>Nessun elemento definito.</p>")

        # Sezione risultati
        results = data.get("results", [])
        parts.append("  <h2>Risultati Verifiche</h2>")
        if results:
            parts.append(self._render_results_table(results))
            parts.append(self._render_summary(results))
        else:
            parts.append("  <p>Nessun risultato disponibile.</p>")

        # Dettagli parziali
        if results:
            parts.append("  <h2>Dettagli</h2>")
            for i, r in enumerate(results):
                parts.append(self._render_result_detail(r, i))

        parts.extend(["</body>", "</html>"])
        return "\n".join(parts)

    def _render_elements_table(self, elements: list[dict]) -> str:
        rows = ["  <table>", "    <tr><th>#</th><th>ID</th><th>Tipo</th>"
                "<th>b [cm]</th><th>h [cm]</th><th>As [cm²]</th></tr>"]
        for i, el in enumerate(elements, 1):
            eid = _esc(str(el.get("id", el.get("element_id", f"E{i}"))))
            tipo = _esc(str(el.get("type", el.get("tipo", "-"))))
            b = el.get("b", el.get("width_cm", "-"))
            h = el.get("h", el.get("height_cm", "-"))
            As = el.get("As", "-")
            rows.append(f"    <tr><td>{i}</td><td>{eid}</td><td>{tipo}</td>"
                        f"<td>{b}</td><td>{h}</td><td>{As}</td></tr>")
        rows.append("  </table>")
        return "\n".join(rows)

    def _render_results_table(self, results: list[dict]) -> str:
        rows = ["  <table>", "    <tr><th>#</th><th>Verifica</th>"
                "<th>Esito</th><th>Messaggio</th></tr>"]
        for i, r in enumerate(results, 1):
            action_id = _esc(r.get("action_id", "-"))
            ok = r.get("ok", False)
            css = "ok" if ok else "fail"
            label = "OK" if ok else "NON VERIFICATO"
            msgs = "; ".join(r.get("messages", []))
            rows.append(f'    <tr><td>{i}</td><td>{action_id}</td>'
                        f'<td class="{css}">{label}</td>'
                        f'<td>{_esc(msgs)}</td></tr>')
        rows.append("  </table>")
        return "\n".join(rows)

    def _render_summary(self, results: list[dict]) -> str:
        total = len(results)
        passed = sum(1 for r in results if r.get("ok"))
        failed = total - passed
        return (f'  <p><strong>Riepilogo:</strong> {passed}/{total} verificate, '
                f'{failed} non verificate.</p>')

    def _render_result_detail(self, result: dict, idx: int) -> str:
        partials = result.get("partials", {})
        if not partials:
            return ""
        action_id = _esc(result.get("action_id", f"check_{idx}"))
        lines = [f"  <h3>{idx + 1}. {action_id}</h3>", '  <table class="partials">',
                 "    <tr><th>Parametro</th><th>Valore</th></tr>"]
        for k, v in partials.items():
            lines.append(f"    <tr><td>{_esc(k)}</td><td>{v}</td></tr>")
        lines.append("  </table>")
        return "\n".join(lines)


def _esc(s: str) -> str:
    """Escape HTML basilare."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
