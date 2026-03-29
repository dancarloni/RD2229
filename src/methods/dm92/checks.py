"""
Verifiche strutturali secondo DM 14/02/1992.

Implementa metodo tensioni ammissibili (TA) e stati limite (SL) in parallelo.
Formule e coefficienti da DM92 (Decreto Ministeriale 14 febbraio 1992).

Modulo con implementazioni complete per:
  - Flessione (TA + SL con asse neutro iterativo)
  - Pressoflessione (dominio N-M semplificato)
  - Taglio (V_Rd = 0.3 f_cd b d a 45°)
  - Torsione (parete sottile, T_Rd = 0.8 f_cd A_m t_m)

Licenza: MIT
"""

from dataclasses import dataclass
from typing import Any

from src.core.adapter_unita_misura import kg_cm2_to_mpa as kgcm2_to_mpa
from src.core.adapter_unita_misura import mpa_to_kg_cm2 as mpa_to_kgcm2

# ============================================================================
# COSTANTI E COEFFICIENTI
# ============================================================================

# Coefficienti di sicurezza (allineati ai cataloghi DM92 del progetto)
GAMMA_C_DM92 = 1.6  # Calcestruzzo
GAMMA_S_DM92 = 1.15  # Acciaio


def rck_to_fck(rck_mpa: float) -> float:
    """
    Relazione tra resistenza cubica (R_ck) e cilindrica (f_ck).
    Approssimazione: f_ck ≈ 0.83 · R_ck

    Args:
        rck_mpa: Resistenza cubica 28gg in MPa

    Returns:
        Resistenza cilindrica equivalente in MPa
    """
    return 0.83 * rck_mpa


# ============================================================================
# CLASSE PER FLESSIONE (TA + SL)
# ============================================================================


@dataclass
class VerificaDM92Flessione:
    """
    Verifica a flessione secondo DM92.

    Implementa metodo TA (tensioni ammissibili) e SL (stati limite) in parallelo.

    Attributi:
        Rck_28: Resistenza cubica 28gg [MPa]
        b: Larghezza utile della sezione [cm]
        d: Altezza utile della sezione [cm]
        As: Area di armatura tesa [cm²]
        c_nom: Copriferro nominale [cm]
        eta_s: Coefficiente modello di aderenza (default 1.0, 1.4 se ≤6mm o ≥32mm)
    """

    Rck_28: float  # MPa
    b: float  # cm
    d: float  # cm
    As: float  # cm²
    c_nom: float  # cm
    eta_s: float = 1.0

    def __post_init__(self) -> None:
        """Validazione parametri."""
        if self.Rck_28 <= 0:
            raise ValueError("Rck_28 deve essere > 0")
        if self.b <= 0 or self.d <= 0 or self.As <= 0:
            raise ValueError("Dimensioni sezione devono essere > 0")
        if self.c_nom < 0:
            raise ValueError("Copriferro non può essere negativo")

    def _calcola_e_moduli(self) -> tuple[float, float, float, float]:
        """
        Calcola moduli elastici e resistenze dalla resistenza cubica.

        Returns:
            (E_s, E_c, f_cd, f_yd): Moduli acciaio/cls e resistenze di progetto
        """
        fck_mpa = rck_to_fck(self.Rck_28)
        fck_kgcm2 = mpa_to_kgcm2(fck_mpa)

        # Moduli elastici (approssimativi, dipendono da tipo cls)
        E_c_mpa = 9500 * (self.Rck_28 ** (1 / 3))  # EC2
        E_c_kgcm2 = mpa_to_kgcm2(E_c_mpa)
        E_s_kgcm2 = 2100000.0  # Acciaio dolce

        # Resistenze di progetto (usate in SL)
        f_cd_kgcm2 = (fck_kgcm2 * 0.85) / GAMMA_C_DM92
        f_yd_kgcm2 = (4400.0) / GAMMA_S_DM92  # Acciaio Fe B44k

        return E_s_kgcm2, E_c_kgcm2, f_cd_kgcm2, f_yd_kgcm2

    def _asse_neutro_iterativo(self, f_cd: float, f_yd: float) -> float:
        """
        Calcola posizione asse neutro con equilibrio iterativo (Newton–Raphson).

        Equilibrio: A_s · f_yd = 0.8 · λ · d · b · f_cd

        Args:
            f_cd: Resistenza di progetto cls [kg/cm²]
            f_yd: Resistenza di progetto acciaio [kg/cm²]

        Returns:
            x: Posizione asse neutro [cm] (da lembo compressa)
        """
        # Stima iniziale: x ≈ A_s·f_yd / (0.8·b·f_cd)
        x = self.As * f_yd / (0.8 * self.b * f_cd)
        x = max(0.001, min(x, self.d * 0.95))  # Limita a [0, 0.95d]

        # Iterazione Newton–Raphson (10 iter, ε = 0.01 cm)
        for _ in range(10):
            residuo = self.As * f_yd - 0.8 * x * self.b * f_cd
            if abs(residuo) < 1e-3:
                break
            f_residuo = -0.8 * self.b * f_cd  # Derivata rispetto x
            delta_x = residuo / f_residuo
            x = max(0.001, min(x + delta_x, self.d * 0.95))

        return x

    def verifica_ta(self, M_k: float, sigma_amm_cls: float, sigma_amm_acc: float) -> dict[str, Any]:
        """
        Verifica a tensioni ammissibili (TA).

        Confronta tensioni calcolate vs ammissibili:
          σ_cls,calc ≤ σ_amm,cls
          σ_acc,calc ≤ σ_amm,acc

        Args:
            M_k: Momento flettente di servizio [kgcm]
            sigma_amm_cls: Tensione ammissibile cls [kg/cm²]
            sigma_amm_acc: Tensione ammissibile acciaio [kg/cm²]

        Returns:
            dict: {
                'esito': bool,
                'rateo': float,  # max(σ_cls/σ_amm, σ_acc/σ_amm)
                'sigma_cls': float,
                'sigma_acc': float,
                'sigma_amm_cls': float,
                'sigma_amm_acc': float,
                'M_k': float,
                'passaggi_calcolo': list[str]
            }
        """
        passaggi = []

        # Equilibrio momento: n = E_s / E_c
        E_s, E_c, _, _ = self._calcola_e_moduli()
        n = E_s / E_c
        passaggi.append(f"Modulo elasticità acciaio E_s = {E_s:.0f} kgcm²")
        passaggi.append(f"Modulo elasticità cls E_c = {E_c:.0f} kgcm²")
        passaggi.append(f"Rapporto n = E_s/E_c = {n:.1f}")

        # Asse neutro: da equilibrio dei momenti statici
        # Sezione rettangolare: x² · b / 2 + n · A_s · (x - d) = 0
        # Risolvendo: x = [-n·A_s ± √(n²·A_s² + 2·b·n·A_s·d)] / b
        discriminante = (n * self.As) ** 2 + 2 * self.b * n * self.As * self.d
        x_ta = (-n * self.As + discriminante**0.5) / self.b
        x_ta = max(0.01, min(x_ta, self.d * 0.95))
        passaggi.append(f"Asse neutro x = {x_ta:.2f} cm")

        # Momento d'inerzia baricentrico
        I = (self.b * x_ta**3) / 3 + n * self.As * (self.d - x_ta) ** 2
        passaggi.append(f"Momento d'inerzia I = {I:.0f} cm⁴")

        # Tensioni
        sigma_cls = M_k * x_ta / I
        sigma_acc = n * M_k * (self.d - x_ta) / I
        passaggi.append(f"Tensione cls σ_c = {sigma_cls:.2f} kg/cm²")
        passaggi.append(f"Tensione acc σ_s = {sigma_acc:.2f} kg/cm²")

        # Verifiche
        ok_cls = sigma_cls <= sigma_amm_cls * 1.001  # Tolleranza numerica
        ok_acc = sigma_acc <= sigma_amm_acc * 1.001
        rateo_cls = sigma_cls / sigma_amm_cls if sigma_amm_cls > 0 else 0
        rateo_acc = sigma_acc / sigma_amm_acc if sigma_amm_acc > 0 else 0
        rateo = max(rateo_cls, rateo_acc)

        esito = ok_cls and ok_acc
        passaggi.append(f"Verifica cls: {sigma_cls:.2f} ≤ {sigma_amm_cls:.2f}? {ok_cls}")
        passaggi.append(f"Verifica acc: {sigma_acc:.2f} ≤ {sigma_amm_acc:.2f}? {ok_acc}")

        return {
            "esito": esito,
            "rateo": rateo,
            "sigma_cls": sigma_cls,
            "sigma_acc": sigma_acc,
            "sigma_amm_cls": sigma_amm_cls,
            "sigma_amm_acc": sigma_amm_acc,
            "M_k": M_k,
            "x_asse_neutro": x_ta,
            "passaggi_calcolo": passaggi,
            "riferimento_normativo": "DM92 Flessione TA",
        }

    def verifica_sl(self, M_d: float) -> dict[str, Any]:
        """
        Verifica agli stati limite (SL).

        Calcola M_Rd = A_s · f_yd · (d - 0.4x) e confronta con M_d.

        Args:
            M_d: Momento flettente di calcolo [kgcm] (= M_k · 1.75 per carichi permanenti)

        Returns:
            dict: {
                'esito': bool,
                'rateo': float,  # M_d / M_Rd
                'M_Rd': float,
                'M_d': float,
                'x': float,
                'z': float,
                'passaggi_calcolo': list[str]
            }
        """
        passaggi = []
        _, _, f_cd, f_yd = self._calcola_e_moduli()
        passaggi.append(f"Resistenza progetto cls f_cd = {f_cd:.2f} kg/cm²")
        passaggi.append(f"Resistenza progetto acc f_yd = {f_yd:.2f} kg/cm²")

        # Asse neutro iterativo
        x = self._asse_neutro_iterativo(f_cd, f_yd)
        passaggi.append(f"Asse neutro (iterativo) x = {x:.2f} cm")

        # Verifica deformazione limite: ε_cu = 0.0035
        # ε_s = ε_cu · (d - x) / x
        eps_cu = 0.0035
        eps_s = eps_cu * (self.d - x) / x if x > 0 else 0
        passaggi.append(f"Deformazione cls ε_c = {eps_cu:.4f}")
        passaggi.append(f"Deformazione acc ε_s = {eps_s:.4f}")

        # Braccio della coppia interna
        z = self.d - 0.4 * x
        z = max(0.01, z)
        passaggi.append(f"Braccio della coppia z = d - 0.4x = {z:.2f} cm")

        # Momento resistente
        M_Rd = self.As * f_yd * z
        passaggi.append(f"Momento resistente M_Rd = A_s · f_yd · z = {M_Rd:.0f} kgcm")

        # Verifica
        rateo = M_d / M_Rd if M_Rd > 0 else 0
        esito = M_d <= M_Rd * 1.001  # Tolleranza numerica
        passaggi.append(f"Verifica: M_d = {M_d:.0f} ≤ M_Rd = {M_Rd:.0f}? {esito}")

        return {
            "esito": esito,
            "rateo": rateo,
            "M_Rd": M_Rd,
            "M_d": M_d,
            "x": x,
            "z": z,
            "epsilon_s": eps_s,
            "passaggi_calcolo": passaggi,
            "riferimento_normativo": "DM92 Flessione SL",
        }


# ============================================================================
# CLASSE PER PRESSOFLESSIONE
# ============================================================================


@dataclass
class VerificaDM92Pressoflessione:
    """
    Verifica a pressoflessione (N-M) secondo DM92.

    Dominio N-M semplificato: M_Rd aumenta con N compressivo.
    """

    Rck_28: float  # MPa
    b: float  # cm
    d: float  # cm
    As: float  # cm² (armatura tesa)
    As_c: float  # cm² (armatura compressa)
    c_nom: float  # cm
    eta_s: float = 1.0

    def verifica_pressoflessione(self, N_d: float, M_d: float) -> dict[str, Any]:
        """
        Verifica dominio N-M semplificato.

        Per N > 0 (compressione), M_Rd aumenta linearmente.

        Args:
            N_d: Sforzo assiale di calcolo [kg] (>0 compressione)
            M_d: Momento di calcolo [kgcm]

        Returns:
            dict con esito, rateo, N_Rd, M_Rd, check
        """
        passaggi = []

        fck_mpa = rck_to_fck(self.Rck_28)
        fck_kgcm2 = mpa_to_kgcm2(fck_mpa)
        f_cd_kgcm2 = (fck_kgcm2 * 0.85) / GAMMA_C_DM92
        f_yd_kgcm2 = 4400.0 / GAMMA_S_DM92

        A_c = self.b * self.d
        passaggi.append(f"Area sezione cls A_c = {A_c:.0f} cm²")

        # Resistenza a compressione pura
        N_Rd_max = A_c * f_cd_kgcm2 + (self.As + self.As_c) * f_yd_kgcm2
        passaggi.append(f"N_Rd,max = {N_Rd_max:.0f} kg")

        # Momento resistente a flessione pura (N=0)
        M_Rd_0 = self.As * f_yd_kgcm2 * (self.d - 0.4 * self.d / 2)
        passaggi.append(f"M_Rd(N=0) = {M_Rd_0:.0f} kgcm")

        # Incremento M_Rd con N compressivo (semplificato)
        # M_Rd(N) = M_Rd,0 · (1 + N / (0.5 · N_Rd,max))
        if N_d > 0:
            incremento = 1 + N_d / (0.5 * N_Rd_max) if N_Rd_max > 0 else 1
            M_Rd = M_Rd_0 * min(incremento, 2.0)  # Limita a x2
        else:
            M_Rd = M_Rd_0  # Trazione pura: no incremento

        passaggi.append(f"M_Rd(N={N_d:.0f}) = {M_Rd:.0f} kgcm")

        # Verifica
        check_N = N_d <= N_Rd_max * 1.001
        check_M = M_d <= M_Rd * 1.001
        esito = check_N and check_M
        rateo_N = N_d / N_Rd_max if N_Rd_max > 0 else 0
        rateo_M = M_d / M_Rd if M_Rd > 0 else 0
        rateo = max(rateo_N, rateo_M)

        return {
            "esito": esito,
            "rateo": rateo,
            "N_d": N_d,
            "N_Rd": N_Rd_max,
            "M_d": M_d,
            "M_Rd": M_Rd,
            "check_N": check_N,
            "check_M": check_M,
            "passaggi_calcolo": passaggi,
            "riferimento_normativo": "DM92 Pressoflessione",
        }


# ============================================================================
# CLASSE PER TAGLIO
# ============================================================================


@dataclass
class VerificaDM92Taglio:
    """
    Verifica a taglio secondo DM92.

    V_Rd = 0.3 · f_cd · b_w · d (ipotesi θ = 45°)
    """

    Rck_28: float  # MPa
    b_w: float  # cm (larghezza anima)
    d: float  # cm
    Asw: float  # cm²/metro (armatura di taglio, per metro di lunghezza)
    s: float  # cm (spaziatura staffe)

    def verifica_taglio(self, V_d: float) -> dict[str, Any]:
        """
        Verifica del taglio.

        Args:
            V_d: Taglio di calcolo [kg]

        Returns:
            dict con esito, rateo, V_Rd
        """
        passaggi = []

        fck_mpa = rck_to_fck(self.Rck_28)
        fck_kgcm2 = mpa_to_kgcm2(fck_mpa)
        f_cd = (fck_kgcm2 * 0.85) / GAMMA_C_DM92
        passaggi.append(f"f_cd = {f_cd:.2f} kg/cm²")

        # Resistenza cls (DM92: V_Rd ≈ 0.3·f_cd·b·d a 45°)
        V_Rd_c = 0.3 * f_cd * self.b_w * self.d
        passaggi.append(f"V_Rd,c = 0.3 · f_cd · b_w · d = {V_Rd_c:.0f} kg")

        # Resistenza armatura (formula classica, 45°)
        if self.s > 0:
            f_yd_acc = 4400.0 / GAMMA_S_DM92
            V_Rd_s = (self.Asw / self.s) * self.d * f_yd_acc  # Asw in cm²/cm
            # Conversione: Asw da cm²/metro → cm²/cm
            V_Rd_s = (self.Asw * 100 / self.s) * self.d * f_yd_acc / 100
            passaggi.append(f"V_Rd,s = {V_Rd_s:.0f} kg")
        else:
            V_Rd_s = 0

        # V_Rd = min(V_Rd,c + V_Rd,s, V_Rd,max)
        V_Rd = min(V_Rd_c + V_Rd_s, 0.9 * self.b_w * self.d * f_cd)
        passaggi.append(f"V_Rd = min(V_Rd,c + V_Rd,s, V_Rd,max) = {V_Rd:.0f} kg")

        # Verifica
        esito = V_d <= V_Rd * 1.001
        rateo = V_d / V_Rd if V_Rd > 0 else 0

        return {
            "esito": esito,
            "rateo": rateo,
            "V_d": V_d,
            "V_Rd": V_Rd,
            "V_Rd_c": V_Rd_c,
            "V_Rd_s": V_Rd_s if self.s > 0 else 0,
            "passaggi_calcolo": passaggi,
            "riferimento_normativo": "DM92 Taglio",
        }


# ============================================================================
# CLASSE PER TORSIONE
# ============================================================================


@dataclass
class VerificaDM92Torsione:
    """
    Verifica a torsione secondo DM92.

    Analogia parete sottile: T_Rd = 0.8 · f_cd · A_m · t_m
    dove A_m = area racchiusa, t_m = spessore medio
    """

    Rck_28: float  # MPa
    A_m: float  # cm² (area racchiusa dal percorso del flusso di taglio)
    t_m: float  # cm (spessore medio parete)

    def verifica_torsione(self, T_d: float) -> dict[str, Any]:
        """
        Verifica della torsione.

        Args:
            T_d: Momento torcente di calcolo [kgcm]

        Returns:
            dict con esito, rateo, T_Rd
        """
        passaggi = []

        fck_mpa = rck_to_fck(self.Rck_28)
        fck_kgcm2 = mpa_to_kgcm2(fck_mpa)
        f_cd = (fck_kgcm2 * 0.85) / GAMMA_C_DM92
        passaggi.append(f"f_cd = {f_cd:.2f} kg/cm²")

        # Momento torcente resistente (parete sottile, DM92)
        T_Rd = 0.8 * f_cd * self.A_m * self.t_m
        passaggi.append(f"T_Rd = 0.8 · f_cd · A_m · t_m = {T_Rd:.0f} kgcm")

        # Verifica
        esito = T_d <= T_Rd * 1.001
        rateo = T_d / T_Rd if T_Rd > 0 else 0

        return {
            "esito": esito,
            "rateo": rateo,
            "T_d": T_d,
            "T_Rd": T_Rd,
            "A_m": self.A_m,
            "passaggi_calcolo": passaggi,
            "riferimento_normativo": "DM92 Torsione",
        }


# ============================================================================
# FUNZIONI DI ALTO LIVELLO (INTERFACCIA SEMPLICE)
# ============================================================================


def verifica_flessione_ta(
    Rck_28: float,
    b: float,
    d: float,
    As: float,
    c_nom: float,
    M_k: float,
    sigma_amm_cls: float,
    sigma_amm_acc: float,
    eta_s: float = 1.0,
) -> dict[str, Any]:
    """Verifica flessione TA — interfaccia funzionale."""
    vf = VerificaDM92Flessione(Rck_28, b, d, As, c_nom, eta_s)
    return vf.verifica_ta(M_k, sigma_amm_cls, sigma_amm_acc)


def verifica_flessione_sl(
    Rck_28: float, b: float, d: float, As: float, c_nom: float, M_d: float, eta_s: float = 1.0
) -> dict[str, Any]:
    """Verifica flessione SL — interfaccia funzionale."""
    vf = VerificaDM92Flessione(Rck_28, b, d, As, c_nom, eta_s)
    return vf.verifica_sl(M_d)


def verifica_pressoflessione(
    Rck_28: float,
    b: float,
    d: float,
    As: float,
    As_c: float,
    c_nom: float,
    N_d: float,
    M_d: float,
    eta_s: float = 1.0,
) -> dict[str, Any]:
    """Verifica pressoflessione — interfaccia funzionale."""
    vp = VerificaDM92Pressoflessione(Rck_28, b, d, As, As_c, c_nom, eta_s)
    return vp.verifica_pressoflessione(N_d, M_d)


def verifica_taglio(
    Rck_28: float, b_w: float, d: float, Asw: float, s: float, V_d: float
) -> dict[str, Any]:
    """Verifica taglio — interfaccia funzionale."""
    vt = VerificaDM92Taglio(Rck_28, b_w, d, Asw, s)
    return vt.verifica_taglio(V_d)


def verifica_torsione(Rck_28: float, A_m: float, t_m: float, T_d: float) -> dict[str, Any]:
    """Verifica torsione — interfaccia funzionale."""
    vtor = VerificaDM92Torsione(Rck_28, A_m, t_m)
    return vtor.verifica_torsione(T_d)
