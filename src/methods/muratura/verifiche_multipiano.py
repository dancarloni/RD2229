"""Verifiche compressione multipiano — piano per piano con eccentricità.

Verifica compressione centrata ed eccentrica per ogni maschio di ogni piano,
con accumulo carichi top-down e tutte le fonti di eccentricità:
- Geometrica (da snellezza h_eff/t)
- Da carico solaio (appoggio non centrato)
- Accidentale (NTC2018: max(h_eff/200, 2 cm))
- Da vento/sisma fuori piano

Output: tabella sintetica per piano + tabella dettagliata per maschio.

Unità: cm, kg, kg/cm².

Riferimenti:
- NTC2018 §4.5.6 — Resistenza a compressione muratura
- NTC2018 §4.5.6.2 — Eccentricità e snellezza
- NTC2018 Tab. 4.5.V — Coefficiente Φ
- Circolare n.7/2019 §C4.5.6.2 — Eccentricità di calcolo
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.methods.muratura.carichi_verticali import CaricoMaschio
from src.methods.muratura.combinazioni_muratura import GestoreCombinazioni
from src.methods.muratura.discretizzazione import Maschio
from src.methods.muratura.verifiche import interpola_phi

# ═══════════════════════════════════════════════════════════
#  Eccentricità
# ═══════════════════════════════════════════════════════════


@dataclass
class Eccentricita:
    """Componenti di eccentricità per verifica fuori piano.

    e_tot = e_geom + e_carico + e_accidentale + e_vento
    e/t usato per Φ nella Tab. 4.5.V
    """

    e_geom: float = 0.0  # eccentricità geometrica (snellezza) [cm]
    e_carico: float = 0.0  # eccentricità da carico solaio [cm]
    e_accidentale: float = 0.0  # eccentricità accidentale [cm]
    e_vento: float = 0.0  # eccentricità da vento/sisma fuori piano [cm]

    @property
    def e_totale(self) -> float:
        """Eccentricità totale [cm]."""
        return self.e_geom + self.e_carico + self.e_accidentale + self.e_vento

    def to_dict(self) -> dict:
        return {
            "e_geom": round(self.e_geom, 2),
            "e_carico": round(self.e_carico, 2),
            "e_accidentale": round(self.e_accidentale, 2),
            "e_vento": round(self.e_vento, 2),
            "e_totale": round(self.e_totale, 2),
        }


def calcola_eccentricita(
    maschio: Maschio,
    rho: float = 1.0,
    e_carico: float = 0.0,
    M_fuori_piano: float = 0.0,
    N: float = 0.0,
) -> Eccentricita:
    """Calcola tutte le componenti di eccentricità.

    Args:
        maschio: maschio murario
        rho: fattore vincolo per h_eff
        e_carico: eccentricità da appoggio solaio non centrato [cm]
        M_fuori_piano: momento fuori piano da vento/sisma [kg·cm]
        N: sforzo normale per eccentricità da vento [kg]

    Returns:
        Eccentricita con tutte le componenti
    """
    t = maschio.t
    h_eff = rho * maschio.h

    # 1. Geometrica: eccentricità strutturale per snellezza
    # NTC2018 §4.5.6.2: e_s = 0 per compressione centrata,
    # ma la snellezza riduce Φ tramite la tabella
    # Per coerenza: e_geom = 0 (inclusa implicitamente in Φ)
    e_geom = 0.0

    # 2. Da carico solaio (input utente)
    e_car = abs(e_carico)

    # 3. Accidentale: NTC2018 §4.5.6.2
    # e_a = max(h_eff / 200, 2 cm) per NTC2018
    e_acc = max(h_eff / 200.0, 2.0)

    # 4. Da vento/sisma fuori piano
    e_vent = abs(M_fuori_piano / N) if N > 0 else 0.0

    return Eccentricita(
        e_geom=e_geom,
        e_carico=e_car,
        e_accidentale=e_acc,
        e_vento=e_vent,
    )


# ═══════════════════════════════════════════════════════════
#  Riga verifica maschio (dettagliata)
# ═══════════════════════════════════════════════════════════


@dataclass
class RigaVerificaMaschio:
    """Riga dettagliata verifica per singolo maschio."""

    id_maschio: int = 0
    id_piano: int = 0
    id_parete: int = 0

    # Geometria
    L: float = 0.0
    t: float = 0.0
    h: float = 0.0

    # Carichi
    N_Ed: float = 0.0  # sforzo normale di calcolo [kg]
    combinazione: str = ""  # nome combinazione governante

    # Tensioni
    sigma_0: float = 0.0  # σ₀ = N/(L×t) [kg/cm²]

    # Eccentricità
    e_totale: float = 0.0  # eccentricità totale [cm]
    e_t: float = 0.0  # e/t adimensionale

    # Snellezza
    h_eff: float = 0.0
    lam: float = 0.0  # λ = h_eff/t

    # Resistenza
    phi: float = 0.0  # Φ(λ, e/t)
    fd: float = 0.0  # resistenza di calcolo [kg/cm²]
    N_Rd: float = 0.0  # N_Rd = Φ×fd×A [kg]

    # Esito
    DC: float = 0.0  # D/C = N_Ed / N_Rd
    verificato: bool = True
    spanciamento_ok: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id_maschio,
            "piano": self.id_piano,
            "parete": self.id_parete,
            "L": round(self.L, 0),
            "t": round(self.t, 0),
            "h": round(self.h, 0),
            "N_Ed": round(self.N_Ed, 0),
            "combinazione": self.combinazione,
            "sigma_0": round(self.sigma_0, 2),
            "e_tot": round(self.e_totale, 2),
            "e/t": round(self.e_t, 4),
            "lambda": round(self.lam, 1),
            "Phi": round(self.phi, 4),
            "fd": round(self.fd, 2),
            "N_Rd": round(self.N_Rd, 0),
            "D/C": round(self.DC, 3),
            "verificato": self.verificato,
        }


# ═══════════════════════════════════════════════════════════
#  Riga verifica piano (sintetica)
# ═══════════════════════════════════════════════════════════


@dataclass
class RigaVerificaPiano:
    """Riga sintetica verifica per piano."""

    id_piano: int = 0
    quota: float = 0.0  # quota piano [cm]
    n_maschi: int = 0
    N_Ed_max: float = 0.0  # N_Ed massimo tra i maschi [kg]
    sigma_0_max: float = 0.0  # σ₀ massima [kg/cm²]
    DC_max: float = 0.0  # D/C massimo tra i maschi
    n_verificati: int = 0
    n_non_verificati: int = 0
    verificato: bool = True  # tutti i maschi verificati

    def to_dict(self) -> dict:
        return {
            "piano": self.id_piano,
            "quota": round(self.quota, 0),
            "n_maschi": self.n_maschi,
            "N_Ed_max": round(self.N_Ed_max, 0),
            "sigma_0_max": round(self.sigma_0_max, 2),
            "D/C_max": round(self.DC_max, 3),
            "n_verificati": self.n_verificati,
            "n_non_verificati": self.n_non_verificati,
            "verificato": self.verificato,
        }


# ═══════════════════════════════════════════════════════════
#  Tabella verifiche multipiano
# ═══════════════════════════════════════════════════════════


@dataclass
class TabellaVerificheMultipiano:
    """Risultato completo verifiche multipiano."""

    righe_maschi: list[RigaVerificaMaschio] = field(default_factory=list)
    righe_piani: list[RigaVerificaPiano] = field(default_factory=list)
    passaggi: list[str] = field(default_factory=list)

    @property
    def verificato(self) -> bool:
        """True se tutti i maschi sono verificati."""
        return all(r.verificato for r in self.righe_maschi)

    @property
    def DC_max(self) -> float:
        if not self.righe_maschi:
            return 0.0
        return max(r.DC for r in self.righe_maschi)

    def to_dict(self) -> dict:
        return {
            "verificato": self.verificato,
            "DC_max": round(self.DC_max, 3),
            "n_piani": len(self.righe_piani),
            "n_maschi": len(self.righe_maschi),
            "piani": [r.to_dict() for r in self.righe_piani],
            "maschi": [r.to_dict() for r in self.righe_maschi],
        }

    def formato_testo(self) -> str:
        """Output ASCII stile tabulato commerciale."""
        linee: list[str] = []
        linee.append("╔══════════════════════════════════════════════════════════════╗")
        linee.append("║       TABELLA VERIFICHE COMPRESSIONE MULTIPIANO            ║")
        linee.append("╠══════════════════════════════════════════════════════════════╣")

        # Tabella sintetica per piano
        linee.append("")
        linee.append("── RIEPILOGO PER PIANO ──")
        linee.append(
            f"{'Piano':>5} {'Quota':>7} {'N_maschi':>8} {'N_Ed_max':>10} "
            f"{'σ₀_max':>8} {'D/C_max':>7} {'Esito':>6}"
        )
        linee.append("─" * 60)

        for rp in self.righe_piani:
            esito = "OK" if rp.verificato else "NO"
            linee.append(
                f"{rp.id_piano:>5} {rp.quota:>7.0f} {rp.n_maschi:>8} "
                f"{rp.N_Ed_max:>10.0f} {rp.sigma_0_max:>8.2f} "
                f"{rp.DC_max:>7.3f} {esito:>6}"
            )

        # Tabella dettagliata per maschio
        linee.append("")
        linee.append("── DETTAGLIO PER MASCHIO ──")
        linee.append(
            f"{'P':>2} {'M':>3} {'L':>5} {'t':>4} {'N_Ed':>10} "
            f"{'σ₀':>7} {'e/t':>6} {'λ':>5} {'Φ':>6} "
            f"{'N_Rd':>10} {'D/C':>6} {'Esito':>5}"
        )
        linee.append("─" * 80)

        for rm in self.righe_maschi:
            esito = "OK" if rm.verificato else "NO"
            linee.append(
                f"{rm.id_piano:>2} {rm.id_maschio:>3} {rm.L:>5.0f} {rm.t:>4.0f} "
                f"{rm.N_Ed:>10.0f} {rm.sigma_0:>7.2f} {rm.e_t:>6.4f} "
                f"{rm.lam:>5.1f} {rm.phi:>6.4f} {rm.N_Rd:>10.0f} "
                f"{rm.DC:>6.3f} {esito:>5}"
            )

        linee.append("─" * 80)
        n_ok = sum(1 for r in self.righe_maschi if r.verificato)
        n_no = len(self.righe_maschi) - n_ok
        linee.append(
            f"Totale: {len(self.righe_maschi)} maschi, "
            f"{n_ok} verificati, {n_no} non verificati, "
            f"D/C max = {self.DC_max:.3f}"
        )
        linee.append("╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(linee)


# ═══════════════════════════════════════════════════════════
#  Verifica multipiano
# ═══════════════════════════════════════════════════════════


def verifica_multipiano(
    maschi_per_piano: dict[int, list[Maschio]],
    carichi_per_piano: dict[int, dict[int, CaricoMaschio]],
    piani_ordinati: list[int],
    quote_piani: dict[int, float],
    gestore_combinazioni: GestoreCombinazioni,
    rho: float = 1.0,
    e_carico_per_maschio: dict[int, float] | None = None,
    M_fuoripiano_per_maschio: dict[int, float] | None = None,
    lambda_max: float = 20.0,
) -> TabellaVerificheMultipiano:
    """Verifica compressione multipiano piano per piano.

    Per ogni maschio:
    1. Calcola N_Ed per tutte le combinazioni attive, prende il max
    2. Calcola eccentricità totale (4 fonti)
    3. Calcola Φ(λ, e/t) da Tab. 4.5.V
    4. Calcola N_Rd = Φ × fd × A
    5. D/C = N_Ed / N_Rd

    Args:
        maschi_per_piano: {id_piano: [maschi]}
        carichi_per_piano: {id_piano: {id_maschio: CaricoMaschio}}
        piani_ordinati: dal basso all'alto
        quote_piani: {id_piano: quota_z}
        gestore_combinazioni: gestore con combinazioni attive
        rho: fattore vincolo per h_eff
        e_carico_per_maschio: {id_maschio: e_carico} eccentricità da solaio
        M_fuoripiano_per_maschio: {id_maschio: M_fp} momento fuori piano
        lambda_max: snellezza massima ammissibile

    Returns:
        TabellaVerificheMultipiano
    """
    passaggi: list[str] = []
    passaggi.append("═══ VERIFICA COMPRESSIONE MULTIPIANO ═══")

    righe_maschi: list[RigaVerificaMaschio] = []
    righe_piani: list[RigaVerificaPiano] = []

    e_carico_map = e_carico_per_maschio or {}
    M_fp_map = M_fuoripiano_per_maschio or {}

    for id_piano in piani_ordinati:
        maschi = maschi_per_piano.get(id_piano, [])
        carichi = carichi_per_piano.get(id_piano, {})
        quota = quote_piani.get(id_piano, 0.0)

        if not maschi:
            continue

        passaggi.append(f"\n── Piano {id_piano} (quota {quota:.0f} cm) ──")

        rp = RigaVerificaPiano(
            id_piano=id_piano,
            quota=quota,
            n_maschi=len(maschi),
        )

        for m in maschi:
            cm = carichi.get(m.id_maschio)
            if cm is None:
                # Se non ci sono carichi, usa N_gravitazionale esistente
                G1 = m.N_gravitazionale
                G2 = 0.0
                Q = 0.0
            else:
                G1 = cm.N_G1
                G2 = cm.N_G2
                Q = cm.N_Q

            # Calcola N_Ed per tutte le combinazioni, prendi il max
            n_ed_dict = gestore_combinazioni.calcola_N_tutte(G1, G2, Q)
            if n_ed_dict:
                # Trova combinazione governante (N_Ed massimo)
                id_gov = max(n_ed_dict, key=n_ed_dict.get)
                N_Ed = n_ed_dict[id_gov]
                combo_gov = gestore_combinazioni.per_id(id_gov)
                nome_combo = combo_gov.nome if combo_gov else ""
            else:
                N_Ed = G1 + G2 + Q
                nome_combo = "caratteristica"

            # Geometria
            A = m.L * m.t
            sigma_0 = N_Ed / A if A > 0 else 0.0
            h_eff = rho * m.h
            lam = h_eff / m.t if m.t > 0 else 0.0

            # Eccentricità
            ecc = calcola_eccentricita(
                maschio=m,
                rho=rho,
                e_carico=e_carico_map.get(m.id_maschio, 0.0),
                M_fuori_piano=M_fp_map.get(m.id_maschio, 0.0),
                N=N_Ed,
            )
            e_t = ecc.e_totale / m.t if m.t > 0 else 0.0

            # Φ dalla tabella
            phi = interpola_phi(lam, e_t)

            # Resistenza
            fd = m.materiale.fd if m.materiale else 0.0
            N_Rd = phi * fd * A

            # D/C
            DC = N_Ed / N_Rd if N_Rd > 0 else float("inf")
            verificato = DC <= 1.0 and lam <= lambda_max

            # Spanciamento
            spanciamento_ok = lam <= lambda_max

            rm = RigaVerificaMaschio(
                id_maschio=m.id_maschio,
                id_piano=id_piano,
                id_parete=m.id_parete,
                L=m.L,
                t=m.t,
                h=m.h,
                N_Ed=N_Ed,
                combinazione=nome_combo,
                sigma_0=sigma_0,
                e_totale=ecc.e_totale,
                e_t=e_t,
                h_eff=h_eff,
                lam=lam,
                phi=phi,
                fd=fd,
                N_Rd=N_Rd,
                DC=DC,
                verificato=verificato,
                spanciamento_ok=spanciamento_ok,
            )
            righe_maschi.append(rm)

            passaggi.append(
                f"  M{m.id_maschio}: N_Ed={N_Ed:.0f} ({nome_combo}), "
                f"σ₀={sigma_0:.2f}, λ={lam:.1f}, e/t={e_t:.4f}, "
                f"Φ={phi:.4f}, N_Rd={N_Rd:.0f}, D/C={DC:.3f} "
                f"{'OK' if verificato else 'NO'}"
            )

        # Riepilogo piano
        righe_piano = [r for r in righe_maschi if r.id_piano == id_piano]
        if righe_piano:
            rp.N_Ed_max = max(r.N_Ed for r in righe_piano)
            rp.sigma_0_max = max(r.sigma_0 for r in righe_piano)
            rp.DC_max = max(r.DC for r in righe_piano)
            rp.n_verificati = sum(1 for r in righe_piano if r.verificato)
            rp.n_non_verificati = len(righe_piano) - rp.n_verificati
            rp.verificato = rp.n_non_verificati == 0

        righe_piani.append(rp)

    return TabellaVerificheMultipiano(
        righe_maschi=righe_maschi,
        righe_piani=righe_piani,
        passaggi=passaggi,
    )
