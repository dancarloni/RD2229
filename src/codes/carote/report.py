"""Report HTML e export JSON/CSV per analisi carote."""

from __future__ import annotations

import csv
import json
import logging

from src.codes.carote.analysis import CoreAnalysisResult

logger = logging.getLogger(__name__)


def genera_report_html_carote(analysis: CoreAnalysisResult) -> str:
    """Genera report HTML completo dell'analisi carote.

    Sezioni: intestazione, tabella carote, risultati per formulazione,
    statistiche, parametri derivati, passaggi di calcolo.
    """
    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append("<html lang='it'><head><meta charset='utf-8'>")
    parts.append("<title>Report Analisi Carote</title>")
    parts.append("<style>")
    parts.append("body{font-family:Arial,sans-serif;margin:20px;}")
    parts.append("table{border-collapse:collapse;margin:10px 0;}")
    parts.append("th,td{border:1px solid #ccc;padding:6px 10px;text-align:right;}")
    parts.append("th{background:#f0f0f0;}")
    parts.append("h1{color:#333;}h2{color:#555;border-bottom:1px solid #ddd;}")
    parts.append(".ok{color:green;}.warn{color:orange;}")
    parts.append("</style></head><body>")

    # Intestazione
    parts.append("<h1>Report Analisi Carote Calcestruzzo</h1>")
    parts.append(f"<p>Data: {analysis.timestamp}</p>")
    parts.append(f"<p>Numero carote: {len(analysis.samples)}</p>")

    # Tabella carote
    if analysis.samples:
        parts.append("<h2>Carote analizzate</h2>")
        parts.append("<table><tr><th>ID</th><th>f_core [MPa]</th><th>D [mm]</th>")
        parts.append("<th>L [mm]</th><th>L/D</th><th>Dir.</th><th>Note</th></tr>")
        for s in analysis.samples:
            parts.append(
                f"<tr><td>{s.sample_id}</td><td>{s.f_core_mpa:.1f}</td>"
                f"<td>{s.diameter_mm:.0f}</td><td>{s.length_mm:.0f}</td>"
                f"<td>{s.ld_ratio:.2f}</td><td>{s.direction}</td>"
                f"<td>{s.note}</td></tr>"
            )
        parts.append("</table>")

    # Risultati per formulazione
    for fname, conv_list in analysis.conversions.items():
        stats = analysis.statistics.get(fname)
        derived = analysis.derived.get(fname)

        parts.append(f"<h2>Formulazione: {fname}</h2>")

        # Tabella conversioni
        parts.append("<table><tr><th>ID</th><th>f_core [MPa]</th>")
        parts.append("<th>k_total</th><th>f_is [MPa]</th></tr>")
        for c in conv_list:
            parts.append(
                f"<tr><td>{c.sample_id}</td><td>{c.f_core_mpa:.1f}</td>"
                f"<td>{c.k_total:.4f}</td><td>{c.f_is_mpa:.2f}</td></tr>"
            )
        parts.append("</table>")

        # Statistiche
        if stats:
            parts.append("<h3>Analisi statistica</h3>")
            parts.append("<table>")
            parts.append(f"<tr><td>Media f_is</td><td>{stats.summary.mean:.3f} MPa</td></tr>")
            parts.append(f"<tr><td>Dev. std.</td><td>{stats.summary.std:.3f} MPa</td></tr>")
            parts.append(f"<tr><td>CoV</td><td>{stats.summary.cov:.4f}</td></tr>")
            for lc_key in ("LC1", "LC2", "LC3"):
                ntc = stats.ntc2018.get(lc_key)
                if ntc:
                    parts.append(
                        f"<tr><td>f_ck,is NTC2018 {lc_key}</td>"
                        f"<td>{ntc.f_ck_is:.3f} MPa</td></tr>"
                    )
            if stats.en13791_b:
                parts.append(
                    f"<tr><td>f_ck,is EN13791 B</td>"
                    f"<td>{stats.en13791_b.f_ck_is:.3f} MPa</td></tr>"
                )
            if stats.en13791_a:
                parts.append(
                    f"<tr><td>f_ck,is EN13791 A</td>"
                    f"<td>{stats.en13791_a.f_ck_is:.3f} MPa</td></tr>"
                )
            parts.append(f"<tr><td>Classificazione</td><td>{stats.classification}</td></tr>")
            parts.append("</table>")

            # Outlier
            grubbs_out = [o for o in stats.outliers_grubbs if o.is_outlier]
            chauvenet_out = [o for o in stats.outliers_chauvenet if o.is_outlier]
            if grubbs_out or chauvenet_out:
                parts.append("<h3>Outlier rilevati</h3><ul>")
                for o in grubbs_out:
                    parts.append(
                        f"<li class='warn'>Grubbs: {o.value:.2f} MPa "
                        f"(G={o.test_statistic:.3f} > {o.critical_value:.3f})</li>"
                    )
                for o in chauvenet_out:
                    parts.append(
                        f"<li class='warn'>Chauvenet: {o.value:.2f} MPa "
                        f"(z={o.test_statistic:.3f})</li>"
                    )
                parts.append("</ul>")

        # Parametri derivati
        if derived:
            parts.append("<h3>Parametri derivati</h3>")
            parts.append("<table>")
            parts.append(f"<tr><td>f_ck,is</td><td>{derived.f_ck_is_mpa:.3f} MPa</td></tr>")
            parts.append(f"<tr><td>f_cm</td><td>{derived.f_cm_is_mpa:.3f} MPa</td></tr>")
            parts.append(f"<tr><td>E_cm</td><td>{derived.E_cm_mpa:.0f} MPa</td></tr>")
            parts.append(f"<tr><td>f_ctm</td><td>{derived.f_ctm_mpa:.3f} MPa</td></tr>")
            parts.append(f"<tr><td>Rck</td><td>{derived.Rck_mpa:.2f} MPa</td></tr>")
            parts.append(
                f"<tr><td>σ_c_adm (storica)</td>"
                f"<td>{derived.sigma_c_adm_kgcm2:.1f} kg/cm²</td></tr>"
            )
            parts.append("</table>")

    # Passaggi di calcolo
    if analysis.passaggi_calcolo:
        parts.append("<h2>Passaggi di calcolo</h2><ol>")
        for p in analysis.passaggi_calcolo:
            parts.append(f"<li>{p}</li>")
        parts.append("</ol>")

    parts.append("</body></html>")
    return "\n".join(parts)


def esporta_json_carote(analysis: CoreAnalysisResult, path: str) -> None:
    """Esporta risultati analisi in JSON."""
    data = analysis.to_dict()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("Esportato JSON carote in '%s'.", path)


def esporta_csv_carote(analysis: CoreAnalysisResult, path: str) -> int:
    """Esporta risultati analisi in CSV.

    Colonne: sample_id, formulation, f_core_mpa, k_total, f_is_mpa.

    Returns:
        Numero di righe scritte.
    """
    rows = 0
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_id", "formulation", "f_core_mpa", "k_total", "f_is_mpa"])
        for fname, conv_list in analysis.conversions.items():
            for c in conv_list:
                writer.writerow(
                    [
                        c.sample_id,
                        c.formulation,
                        f"{c.f_core_mpa:.2f}",
                        f"{c.k_total:.4f}",
                        f"{c.f_is_mpa:.3f}",
                    ]
                )
                rows += 1
    logger.info("Esportato CSV carote in '%s' (%d righe).", path, rows)
    return rows
