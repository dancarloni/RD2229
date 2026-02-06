"""Stub: calcolo compressione semplice per pilastri."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CompressioneRisultato:
    N: float
    tensione: float


def calcola_compressione(N: float, area: float) -> CompressioneRisultato:
    tensione = N / area
    return CompressioneRisultato(N=N, tensione=tensione)
