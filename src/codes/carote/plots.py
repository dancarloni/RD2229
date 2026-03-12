"""Grafici matplotlib headless per analisi carote.

4 funzioni: istogramma+gaussiana, scatter conversione, boxplot comparativo, barre f_ck.
Ogni funzione restituisce una matplotlib Figure (nessun backend forzato).
"""

from __future__ import annotations

import math

import numpy as np
from matplotlib.figure import Figure

from src.codes.carote.analysis import CoreAnalysisResult


def grafico_istogramma_gaussiana(
    analysis: CoreAnalysisResult,
    formulation: str = "NTC2018",
) -> Figure:
    """Istogramma delle f_is con curva gaussiana sovrapposta.

    Args:
        analysis: risultato analisi
        formulation: formulazione di riferimento

    Returns:
        matplotlib Figure
    """
    conv_list = analysis.conversions.get(formulation)
    if not conv_list:
        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, f"Nessun dato per {formulation}", ha="center", va="center")
        return fig

    values = [c.f_is_mpa for c in conv_list]
    stats = analysis.statistics.get(formulation)

    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)

    # Istogramma
    n_bins = max(5, len(values) // 2)
    ax.hist(
        values,
        bins=n_bins,
        density=True,
        alpha=0.6,
        color="steelblue",
        edgecolor="white",
        label="f_is",
    )

    # Gaussiana sovrapposta
    if stats and stats.summary.std > 0:
        mean = stats.summary.mean
        std = stats.summary.std
        x = np.linspace(mean - 4 * std, mean + 4 * std, 200)
        y = (1.0 / (std * math.sqrt(2 * math.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
        ax.plot(x, y, "r-", linewidth=2, label=f"N({mean:.1f}, {std:.2f})")

        # Linea f_ck,is
        f_ck = stats.ntc2018["LC2"].f_ck_is
        ax.axvline(
            f_ck, color="green", linestyle="--", linewidth=1.5, label=f"f_ck,is = {f_ck:.1f} MPa"
        )

    ax.set_xlabel("f_is [MPa]")
    ax.set_ylabel("Densita")
    ax.set_title(f"Distribuzione resistenze in situ — {formulation}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def grafico_scatter_conversione(
    analysis: CoreAnalysisResult,
    formulation: str = "NTC2018",
) -> Figure:
    """Scatter f_core vs f_is per una formulazione.

    Args:
        analysis: risultato analisi
        formulation: formulazione di riferimento

    Returns:
        matplotlib Figure
    """
    conv_list = analysis.conversions.get(formulation)
    if not conv_list:
        fig = Figure(figsize=(7, 7))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, f"Nessun dato per {formulation}", ha="center", va="center")
        return fig

    f_core = [c.f_core_mpa for c in conv_list]
    f_is = [c.f_is_mpa for c in conv_list]

    fig = Figure(figsize=(7, 7))
    ax = fig.add_subplot(111)
    ax.scatter(f_core, f_is, c="steelblue", s=60, edgecolors="navy", zorder=3)

    # Bisettrice (f_is = f_core)
    lim_min = min(min(f_core), min(f_is)) * 0.9
    lim_max = max(max(f_core), max(f_is)) * 1.1
    ax.plot([lim_min, lim_max], [lim_min, lim_max], "k--", alpha=0.3, label="f_is = f_core")

    # Etichette campioni
    for c in conv_list:
        ax.annotate(
            c.sample_id,
            (c.f_core_mpa, c.f_is_mpa),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )

    ax.set_xlabel("f_core [MPa]")
    ax.set_ylabel("f_is [MPa]")
    ax.set_title(f"Conversione f_core -> f_is — {formulation}")
    ax.set_aspect("equal")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def grafico_boxplot_comparativo(analysis: CoreAnalysisResult) -> Figure:
    """Boxplot comparativo delle f_is per tutte le formulazioni.

    Returns:
        matplotlib Figure
    """
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    if not analysis.conversions:
        ax.text(0.5, 0.5, "Nessun dato", ha="center", va="center")
        return fig

    labels = []
    data = []
    for fname in sorted(analysis.conversions.keys()):
        conv_list = analysis.conversions[fname]
        values = [c.f_is_mpa for c in conv_list]
        if values:
            labels.append(fname)
            data.append(values)

    bp = ax.boxplot(data, labels=labels, patch_artist=True)
    colors = [
        "#4C72B0",
        "#55A868",
        "#C44E52",
        "#8172B2",
        "#CCB974",
        "#64B5CD",
        "#E88C30",
        "#8C8C8C",
        "#DA8BC3",
    ]
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colors[i % len(colors)])
        patch.set_alpha(0.7)

    ax.set_ylabel("f_is [MPa]")
    ax.set_title("Confronto formulazioni — f_is")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    return fig


def grafico_barre_fck(analysis: CoreAnalysisResult) -> Figure:
    """Grafico a barre f_ck,is per ogni formulazione (NTC2018 LC2).

    Returns:
        matplotlib Figure
    """
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    if not analysis.statistics:
        ax.text(0.5, 0.5, "Nessun dato", ha="center", va="center")
        return fig

    names = []
    fck_values = []
    for fname in sorted(analysis.statistics.keys()):
        stats = analysis.statistics[fname]
        fck = stats.ntc2018["LC2"].f_ck_is
        names.append(fname)
        fck_values.append(fck)

    colors = [
        "#4C72B0",
        "#55A868",
        "#C44E52",
        "#8172B2",
        "#CCB974",
        "#64B5CD",
        "#E88C30",
        "#8C8C8C",
        "#DA8BC3",
    ]
    bar_colors = [colors[i % len(colors)] for i in range(len(names))]

    bars = ax.bar(names, fck_values, color=bar_colors, alpha=0.8, edgecolor="gray")

    # Etichette valori
    for bar, val in zip(bars, fck_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            f"{val:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_ylabel("f_ck,is [MPa]")
    ax.set_title("f_ck,is per formulazione (NTC2018 LC2)")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    return fig
