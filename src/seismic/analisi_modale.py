"""Fase U.5 - Analisi modale con spettro (implementazione base testabile)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class RisultatoAutovaloriModali:
    omega: np.ndarray
    periodi: np.ndarray
    modi: np.ndarray


def risolvi_autovalori_modali(k: np.ndarray, m: np.ndarray) -> RisultatoAutovaloriModali:
    """Risolve K*phi = omega^2*M*phi usando eig(M^-1 K)."""

    if k.shape != m.shape or k.shape[0] != k.shape[1]:
        raise ValueError("k e m devono essere matrici quadrate della stessa dimensione")

    a = np.linalg.solve(m, k)
    eigvals, eigvecs = np.linalg.eig(a)

    eigvals = np.real(eigvals)
    eigvecs = np.real(eigvecs)

    if np.any(eigvals <= 0.0):
        raise ValueError("Autovalori non positivi: sistema non fisico o mal condizionato")

    order = np.argsort(eigvals)
    omega2 = eigvals[order]
    modi = eigvecs[:, order]

    omega = np.sqrt(omega2)
    periodi = 2.0 * np.pi / omega

    return RisultatoAutovaloriModali(omega=omega, periodi=periodi, modi=modi)


def fattore_partecipazione(masse: np.ndarray, modo: np.ndarray) -> float:
    """Calcola Gamma_i per un modo."""

    num = float(np.sum(masse * modo))
    den = float(np.sum(masse * modo * modo))
    if den <= 0.0:
        raise ValueError("Denominatore nullo nel fattore di partecipazione")
    return num / den


def massa_modale_effettiva(masse: np.ndarray, modo: np.ndarray) -> float:
    """Calcola M_eff,i = Gamma_i^2 * sum(masse * modo^2)."""

    gamma = fattore_partecipazione(masse, modo)
    den = float(np.sum(masse * modo * modo))
    return gamma * gamma * den


def verifica_partecipazione_minima(masse_effettive: np.ndarray, masse_totali: np.ndarray, soglia: float = 0.85) -> bool:
    """Verifica criterio >= 85% massa totale."""

    m_eff = float(np.sum(masse_effettive))
    m_tot = float(np.sum(masse_totali))
    if m_tot <= 0.0:
        raise ValueError("Massa totale deve essere > 0")
    return (m_eff / m_tot) >= soglia


def combina_srss(valori_modali: np.ndarray) -> float:
    """Combinazione SRSS."""

    return float(np.sqrt(np.sum(np.asarray(valori_modali) ** 2)))


def _rho_cqc(omega_i: float, omega_j: float, xi: float) -> float:
    """Coefficiente di correlazione CQC semplificato."""

    beta = omega_j / omega_i
    num = 8.0 * xi * xi * beta * (1.0 + beta)
    den = (1.0 - beta * beta) ** 2 + 4.0 * xi * xi * beta * (1.0 + beta) ** 2
    if den == 0.0:
        return 1.0
    return num / den


def combina_cqc(valori_modali: np.ndarray, omega: np.ndarray, xi: float = 0.05) -> float:
    """Combinazione CQC base."""

    e = np.asarray(valori_modali, dtype=float)
    w = np.asarray(omega, dtype=float)
    if len(e) != len(w):
        raise ValueError("valori_modali e omega devono avere stessa dimensione")

    totale = 0.0
    for i in range(len(e)):
        for j in range(len(e)):
            rho = _rho_cqc(w[i], w[j], xi) if i != j else 1.0
            totale += rho * e[i] * e[j]

    return float(np.sqrt(max(totale, 0.0)))


def taglio_base_modale(massa_effettiva: float, sa_t: float) -> float:
    """V_b,i = M_eff,i * S_a(T_i)."""

    if massa_effettiva < 0.0 or sa_t < 0.0:
        raise ValueError("massa_effettiva e sa_t devono essere >= 0")
    return massa_effettiva * sa_t
