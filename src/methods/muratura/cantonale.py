import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class TipoCopertura(Enum):
    """Tipologia di spinta della copertura sul cuneo in distacco."""

    PADIGLIONE = "Padiglione"
    CAPANNA = "Capanna"
    GENERICA = "Generica (forze note)"


class PosizioneSpinta(Enum):
    """Punto di applicazione in sommità della spinta della copertura."""

    SPIGOLO_INTERNO = "Spigolo Interno (minor braccio stabilizzante)"
    BARICENTRO_IMPRONTA = "Baricentro Impronta (nodo d'angolo)"
    SPIGOLO_ESTERNO = "Spigolo Esterno (maggior braccio stabilizzante, spesso ribaltante 0)"


@dataclass
class InputCatenaCantonale:
    """Modella una catena o tirante attiva nel cantonale."""

    quota_z_cm: float
    forza_kg: float
    angolo_pianta_gradi: float = (
        0.0  # Angolo direzionale assoluto (0° = allineata a Parete 1 asse X, 90° = Parete 2 asse Y)
    )


@dataclass
class InputSpinta:
    """Modello per la spinta del puntone della copertura sull'angolo."""

    tipo: TipoCopertura = TipoCopertura.GENERICA
    pendenza_ang_gradi: float = 0.0
    luce_cm: float = 0.0
    carico_q_kg_cm: float = 0.0  # Carico lineare scaricato dal puntone [kg/cm]
    forza_diretta_H_kg: float = 0.0  # Forza orizzontale diretta (se GENERICA)
    forza_diretta_V_kg: float = 0.0  # Forza verticale diretta (se GENERICA)

    def calcola_forze(self) -> Tuple[float, float, List[str]]:
        """
        Calcola e restituisce la tupla (H, V) in [kg] della spinta,
        insieme ai passaggi intermedi di calcolo.
        """
        passaggi = []
        if self.tipo == TipoCopertura.GENERICA:
            passaggi.append(
                f"Spinta GENERICA: inserimento diretto H={self.forza_diretta_H_kg} kg, V={self.forza_diretta_V_kg} kg"
            )
            return self.forza_diretta_H_kg, self.forza_diretta_V_kg, passaggi

        elif self.tipo in (TipoCopertura.PADIGLIONE, TipoCopertura.CAPANNA):
            if self.pendenza_ang_gradi <= 0 or self.luce_cm <= 0:
                passaggi.append(
                    "Parametri geometrici copertura nulli. Uso forze dirette come fallback."
                )
                return self.forza_diretta_H_kg, self.forza_diretta_V_kg, passaggi

            # Modello semplificato (V = q*L/2, H = V / tan(alpha))
            alpha_rad = math.radians(self.pendenza_ang_gradi)
            V = self.carico_q_kg_cm * self.luce_cm / 2.0
            H = V / math.tan(alpha_rad)

            tipo_str = self.tipo.value
            passaggi.append(
                f"Copertura a {tipo_str} con inclinazione {self.pendenza_ang_gradi}° (luce={self.luce_cm} cm)"
            )
            passaggi.append(
                f" - Taglio verticale palo V = {self.carico_q_kg_cm} * {self.luce_cm}/2 = {V:.2f} kg"
            )
            passaggi.append(
                f" - Spinta orizzontale H = {V:.2f} / tan({self.pendenza_ang_gradi}°) = {H:.2f} kg"
            )

            # Se ci sono forze addizionali applicate direttamente
            V += self.forza_diretta_V_kg
            H += self.forza_diretta_H_kg
            if self.forza_diretta_V_kg > 0 or self.forza_diretta_H_kg > 0:
                passaggi.append(
                    f" - Aggiunta forze dirette utente: Totale H={H:.2f} kg, V={V:.2f} kg"
                )

            return H, V, passaggi

        return 0.0, 0.0, ["Nessuna forza calcolabile"]


@dataclass
class InputCantonale:
    """Modello dati in input per l'analisi 3D del ribaltamento cantonale."""

    h_cm: float  # Altezza del cuneo d'angolo
    t1_cm: float  # Spessore parete 1 (lungo asse X)
    t2_cm: float  # Spessore parete 2 (lungo asse Y)
    L1_dist_cm: float  # Distanza di distacco sulla parete 1, misurata dallo spigolo interno
    L2_dist_cm: float  # Distanza di distacco sulla parete 2, misurata dallo spigolo interno
    gamma_muratura_kg_cm3: float = 0.0018  # Peso specifico muratura (default 1800 kg/m3)

    spinta_copertura: Optional[InputSpinta] = None
    posizione_spinta: PosizioneSpinta = PosizioneSpinta.SPIGOLO_INTERNO
    ritegno_cordolo_kg: float = 0.0  # Contributo facoltativo cordolo orizzontale (fase D.3)

    # Parametri cinematici generici
    angolo_ribaltamento_beta_gradi: Optional[float] = (
        None  # Se None, asse di rotazione ortogonale a bisettrice fessure
    )

    # Altri carichi e azioni interne
    sovraccarico_verticale_vertice_kg: float = 0.0
    catene: List[InputCatenaCantonale] = field(default_factory=list)  # Modello analitico D2

    def valida_geometria(self) -> List[str]:
        """
        Esegue i controlli geometrici per la validità cinematica,
        strutturale o formale del modello e restituisce eventuali warning.
        """
        warnings = []
        if self.h_cm <= 0 or self.t1_cm <= 0 or self.t2_cm <= 0:
            raise ValueError("Dimensioni geometriche fondamentali (h, t1, t2) devono essere > 0.")

        if self.L1_dist_cm <= 0 or self.L2_dist_cm <= 0:
            raise ValueError("Lunghezze di distacco (L1_dist, L2_dist) devono essere > 0.")

        # Warning su validità del cuneo come macroelemento rigido
        if self.L1_dist_cm < self.t1_cm:
            warnings.append(
                f"Attenzione: L'estensione L1 ({self.L1_dist_cm} cm) è minore dello spessore t1 ({self.t1_cm} cm). Meccanismo cinetico dubbio."
            )
        if self.L2_dist_cm < self.t2_cm:
            warnings.append(
                f"Attenzione: L'estensione L2 ({self.L2_dist_cm} cm) è minore dello spessore t2 ({self.t2_cm} cm). Meccanismo cinetico dubbio."
            )

        # Warning su linee di lesione troppo piatte o innaturali (regole pratiche ReLUIS/Letteratura)
        if self.L1_dist_cm > self.h_cm * 1.5 or self.L2_dist_cm > self.h_cm * 1.5:
            warnings.append(
                "Attenzione: L'estensione del cuneo è considerevolmente maggiore dell'altezza. Angolo di fessurazione fittizio per normale tessitura muraria."
            )

        # Warning su spessori anomali rispetto all'altezza
        if self.h_cm / self.t1_cm > 20 or self.h_cm / self.t2_cm > 20:
            warnings.append("Attenzione: Snellezza estrema dei rami del cuneo d'angolo (h/t > 20).")

        return warnings


@dataclass
class RisultatoCantonale:
    """Risultato delle verifiche cinematiche per il cantonale."""

    is_verificato: bool
    alpha_0: float
    momento_ribaltante_kg_cm: float
    momento_stabilizzante_kg_cm: float
    peso_cuneo_kg: float
    passaggi_calcolo: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_verificato": self.is_verificato,
            "alpha_0": self.alpha_0,
            "momento_ribaltante_kg_cm": self.momento_ribaltante_kg_cm,
            "momento_stabilizzante_kg_cm": self.momento_stabilizzante_kg_cm,
            "peso_cuneo_kg": self.peso_cuneo_kg,
            "passaggi_calcolo": self.passaggi_calcolo,
            "warnings": self.warnings,
        }


def esegui_verifica_cantonale(input_dati: InputCantonale) -> RisultatoCantonale:
    """
    Esegue l'analisi cinematica (lineare) per il ribaltamento 3D del cantonale.
    Tutte le forze inerziali sono proiettate ortogonalmente all'asse di rotazione,
    mentre il baricentro del cuneo d'angolo è posizionato a z = 2/3 * h (modulo base in alto).
    L'asse di ribaltamento è alla base dello spigolo esterno e segue l'angolo beta (0=Y, 90=X).
    """
    passaggi = []
    warnings = input_dati.valida_geometria()

    # 1. Geometria del cuneo e Asse di Rotazione
    # L'angolo di rotazione beta definisce la direzione verso cui ribalta l'angolo in pianta.
    # beta = 45 gradi significa lungo la bisettrice standard X/Y.
    beta = input_dati.angolo_ribaltamento_beta_gradi
    if beta is None:
        # Asse calcolato come perpendicolare alla bisettrice naturale formata dagli spessori o dalle lesioni
        beta = 45.0
        passaggi.append(
            f"Angolo di ribaltamento automatico impostato a beta = {beta}° (proiezione fittizia bisettrice)"
        )
    else:
        passaggi.append(f"Angolo di ribaltamento utente: beta = {beta}°")

    beta_rad = math.radians(beta)
    # Vettore unitario della traccia di ribaltamento (periferia orizzontale)
    u_rottura = (math.cos(beta_rad), math.sin(beta_rad))
    passaggi.append(
        f"Versore di ribaltamento nel piano in pianta: u = ({u_rottura[0]:.3f}, {u_rottura[1]:.3f})"
    )

    # 2. Pesi, Volumi e Baricentri in Pianta (cuneo proiettato sull'angolo X-Y, origine in spigolo esterno piano base)
    # Parete 1 estesa lungo asse X
    # Baricentro cuneo parete 1
    xg_1 = input_dati.t2_cm + (input_dati.L1_dist_cm / 3.0)
    yg_1 = input_dati.t1_cm / 2.0
    w_1 = (
        0.5
        * input_dati.gamma_muratura_kg_cm3
        * input_dati.t1_cm
        * input_dati.L1_dist_cm
        * input_dati.h_cm
    )

    # Parete 2 estesa lungo asse Y
    xg_2 = input_dati.t2_cm / 2.0
    yg_2 = input_dati.t1_cm + (input_dati.L2_dist_cm / 3.0)
    w_2 = (
        0.5
        * input_dati.gamma_muratura_kg_cm3
        * input_dati.t2_cm
        * input_dati.L2_dist_cm
        * input_dati.h_cm
    )

    W_tot = w_1 + w_2
    # Baricentro masse proprie risultante in pianta
    xg_tot = (w_1 * xg_1 + w_2 * xg_2) / W_tot if W_tot > 0 else 0
    yg_tot = (w_1 * yg_1 + w_2 * yg_2) / W_tot if W_tot > 0 else 0

    # Quota baricentrale rispetto base
    zg_cuneo = (2.0 / 3.0) * input_dati.h_cm

    passaggi.append(f"Peso Cuneo Parete 1 = {w_1:.2f} kg (X_g={xg_1:.1f}, Y_g={yg_1:.1f} cm)")
    passaggi.append(f"Peso Cuneo Parete 2 = {w_2:.2f} kg (X_g={xg_2:.1f}, Y_g={yg_2:.1f} cm)")
    passaggi.append(
        f"Peso Totale Cuneo W = {W_tot:.2f} kg (X_G={xg_tot:.1f}, Y_G={yg_tot:.1f} cm, Z_G={zg_cuneo:.1f} cm)"
    )

    # Distanze orizzontali stabilizzanti
    # Distanza del baricentro generico (x,y) dall'asse di rotazione passante per l'origine e ortogonale alla bisettrice
    # = proiezione di (x,y) sulla direttrice di rottura beta
    dist_stab_W1 = xg_1 * u_rottura[0] + yg_1 * u_rottura[1]
    dist_stab_W2 = xg_2 * u_rottura[0] + yg_2 * u_rottura[1]

    # Momenti Peso
    M_stab_w1 = w_1 * max(0.0, dist_stab_W1)
    M_stab_w2 = w_2 * max(0.0, dist_stab_W2)

    M_stab_W = M_stab_w1 + M_stab_w2
    passaggi.append(
        f"Bracci stabilizzanti peso: cuneo1={dist_stab_W1:.2f} cm, cuneo2={dist_stab_W2:.2f} cm"
    )
    passaggi.append(f"Momento Stabilizzante Pesi M_stab_W = {M_stab_W:.2f} kg*cm")

    # 3. Spinta Copertura
    # Coordinate del punto in cui è applicata la spinta
    if input_dati.posizione_spinta == PosizioneSpinta.SPIGOLO_INTERNO:
        x_cov = input_dati.t2_cm
        y_cov = input_dati.t1_cm
    elif input_dati.posizione_spinta == PosizioneSpinta.BARICENTRO_IMPRONTA:
        x_cov = input_dati.t2_cm / 2.0
        y_cov = input_dati.t1_cm / 2.0
    else:  # SPIGOLO_ESTERNO
        x_cov = 0.0
        y_cov = 0.0

    dist_stab_cov = x_cov * u_rottura[0] + y_cov * u_rottura[1]
    passaggi.append(
        f"Punto applicazione carichi copertura: ({x_cov:.1f}, {y_cov:.1f} cm) -> braccio={dist_stab_cov:.2f} cm. Modalita: {input_dati.posizione_spinta.name}"
    )

    M_stab_cov = 0.0
    M_rib_statico_cov = 0.0
    if input_dati.spinta_copertura:
        H_cov, V_cov, sub_pass = input_dati.spinta_copertura.calcola_forze()
        passaggi.extend(["[Calcolo forza tetto] " + p for p in sub_pass])
        M_stab_cov = V_cov * dist_stab_cov
        passaggi.append(
            f"Momento Stabilizzante Taglio tetto (V={V_cov:.2f} kg) = {M_stab_cov:.2f} kg*cm"
        )

        # Sforzo orizzontale puntone, assunto spingere verso l'esterno, favorendo il ribaltamento d'angolo
        M_rib_statico_cov = H_cov * input_dati.h_cm
        passaggi.append(
            f"Momento Ribaltante Spinta Puntone (H={H_cov:.2f} kg) = {M_rib_statico_cov:.2f} kg*cm"
        )

    # Contributo Sovraccarico addizionale V:
    # Messo nello stesso punto H_cov e orientato verso il basso
    M_stab_sovr = input_dati.sovraccarico_verticale_vertice_kg * dist_stab_cov
    if input_dati.sovraccarico_verticale_vertice_kg > 0:
        passaggi.append(
            f"Momento Stabilizzante Sovraccarico V addizionale = {M_stab_sovr:.2f} kg*cm"
        )

    # 4. Catene stabilizzanti
    M_stab_catene = 0.0
    for i, cat in enumerate(input_dati.catene):
        # Angolo relativo alla direzione di ribaltamento
        angolo_rel_rad = math.radians(abs(beta - cat.angolo_pianta_gradi))
        # Forza efficace è solo quella opposta al ribaltamento
        forza_eff = cat.forza_kg * math.cos(angolo_rel_rad)
        if forza_eff > 0 and cat.quota_z_cm > 0:
            mr_cat = forza_eff * cat.quota_z_cm
            M_stab_catene += mr_cat
            passaggi.append(
                f"Catena #{i + 1} (F={cat.forza_kg} kg, angolo={cat.angolo_pianta_gradi}°, h={cat.quota_z_cm} cm): "
                f"F_utile={forza_eff:.2f} kg -> Momento Stabilizzante = {mr_cat:.2f} kg*cm"
            )

    # 5. Cordolo Orizzontale Reticolare
    M_stab_cordolo = 0.0
    if input_dati.ritegno_cordolo_kg > 0.0:
        M_stab_cordolo = input_dati.ritegno_cordolo_kg * input_dati.h_cm
        passaggi.append(
            f"Cordolo Reticolare (azione orizzontale {input_dati.ritegno_cordolo_kg} kg ad h={input_dati.h_cm} cm): Momento Stabilizzante = {M_stab_cordolo:.2f} kg*cm"
        )

    # Totali M_stab e M_rib_statico
    M_stab_totale = M_stab_W + M_stab_cov + M_stab_sovr + M_stab_catene + M_stab_cordolo
    passaggi.append(f"--- Momento Stabilizzante Complessivo = {M_stab_totale:.2f} kg*cm")
    passaggi.append(f"--- Momento Ribaltante Non Sismico (Spinte) = {M_rib_statico_cov:.2f} kg*cm")

    # Verifica stabilità statica
    M_disp = M_stab_totale - M_rib_statico_cov
    if M_disp < 0:
        warnings.append(
            "Ribaltamento intrinsecamente SPINGENTE anche senza sisma: M_rib_statico > M_stab_totale."
        )
        passaggi.append("IL MECCANISMO È SPINGENTE A RIPOSO! alpha_0 impostato a 0.0.")
        return RisultatoCantonale(
            is_verificato=False,
            alpha_0=0.0,
            momento_ribaltante_kg_cm=M_rib_statico_cov,
            momento_stabilizzante_kg_cm=M_stab_totale,
            peso_cuneo_kg=W_tot,
            passaggi_calcolo=passaggi,
            warnings=warnings,
        )

    # 6. Forze Inerziali (alpha_0)
    # Ribaltamento inerziale unitario = pesi(wi) * hi proiettati.
    # Assumiamo come sismicamente attive solo le masse murarie W_1 e W_2 a quota z = 2/3 * h
    M_sismo_unitario = W_tot * zg_cuneo
    passaggi.append(
        f"Momento Ribaltante Sismico Unitario (alfa_0 = 1.0) sulle sole masse cuneo = {M_sismo_unitario:.2f} kg*cm"
    )

    alpha_0 = 0.0
    if M_sismo_unitario > 0:
        alpha_0 = M_disp / M_sismo_unitario

    is_verif = alpha_0 > 0.02  # Esempio banale di lower-bound (l'effettiva verifica e' vs PGA)

    passaggi.append(
        f"Attivazione cinematismo (alpha_0) = {M_disp:.2f} / {M_sismo_unitario:.2f} = {alpha_0:.4f} g"
    )

    return RisultatoCantonale(
        is_verificato=is_verif,
        alpha_0=alpha_0,
        momento_ribaltante_kg_cm=M_rib_statico_cov,  # Riporto il statico, quello sismico al collasso eguaglia M_disp
        momento_stabilizzante_kg_cm=M_stab_totale,
        peso_cuneo_kg=W_tot,
        passaggi_calcolo=passaggi,
        warnings=warnings,
    )


@dataclass
class RisultatoCantonale:
    """Risultato delle verifiche cinematiche per il cantonale."""

    is_verificato: bool
    alpha_0: float
    momento_ribaltante_kg_cm: float
    momento_stabilizzante_kg_cm: float
    peso_cuneo_kg: float
    passaggi_calcolo: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_verificato": self.is_verificato,
            "alpha_0": self.alpha_0,
            "momento_ribaltante_kg_cm": self.momento_ribaltante_kg_cm,
            "momento_stabilizzante_kg_cm": self.momento_stabilizzante_kg_cm,
            "peso_cuneo_kg": self.peso_cuneo_kg,
            "passaggi_calcolo": self.passaggi_calcolo,
            "warnings": self.warnings,
        }


# ============================================================================
# FASE E.6.2 - RIDUZIONE RESISTENZA MASCHI D'ANGOLO
# ============================================================================

class TipoSogliaApertura(Enum):
    NORMATIVA_NTC = 'Normativa NTC2018: max(t, 100 cm)'
    PARAMETRICA = 'Regola parametrica proporzionale: alpha * t'
    UTENTE = 'Scelta diretta utente'


@dataclass
class InputDiagnosticaAngolo:
    distanza_apertura_cm: float
    spessore_parete_cm: float
    tipo_soglia: TipoSogliaApertura = TipoSogliaApertura.NORMATIVA_NTC
    # Parametri per modalità alternative (ignorati se NORMATIVA_NTC)
    alpha_moltiplicatore_t: float = 1.5  # Usato se tipo_soglia == PARAMETRICA
    d_min_utente_cm: float = 100.0       # Usato se tipo_soglia == UTENTE
    # Modello di riduzione con asintoto minimo (Safe lower bound)
    k_min_resistenza: float = 0.20


@dataclass
class RisultatoDiagnosticaAngolo:
    is_ok: bool
    status: str          # 'OK', 'WARNING', 'FAIL'
    distanza_minima_richiesta_cm: float
    coeff_riduzione_k: float   # [k_min, 1.0]
    passaggi_calcolo: List[str]
    
    def to_dict(self) -> dict:
        return {
            'is_ok': self.is_ok,
            'status': self.status,
            'distanza_minima_richiesta_cm': self.distanza_minima_richiesta_cm,
            'coeff_riduzione_k': self.coeff_riduzione_k,
            'passaggi_calcolo': self.passaggi_calcolo
        }


def calcola_resistenza_residua_angolo(input_diag: InputDiagnosticaAngolo) -> RisultatoDiagnosticaAngolo:
    '''
    Valuta l'indebolimento del maschio d'angolo a causa di aperture troppo ravvicinate.
    Implementa le scelte architetturali E.6.2: Soglia flessibile e Riduzione asintotica (B2).
    '''
    passaggi = []
    # 1. Calcolo distanza minima richiesta
    d_min = 0.0
    if input_diag.tipo_soglia == TipoSogliaApertura.NORMATIVA_NTC:
        d_min = max(input_diag.spessore_parete_cm, 100.0)
        passaggi.append(f'Criterio soglia: NTC2018 -> max(t={input_diag.spessore_parete_cm:.1f} cm, 100.0 cm) = {d_min:.1f} cm')
    elif input_diag.tipo_soglia == TipoSogliaApertura.PARAMETRICA:
        d_min = input_diag.alpha_moltiplicatore_t * input_diag.spessore_parete_cm
        passaggi.append(f'Criterio soglia: Parametrica -> {input_diag.alpha_moltiplicatore_t} * t({input_diag.spessore_parete_cm:.1f} cm) = {d_min:.1f} cm')
    else:
        d_min = input_diag.d_min_utente_cm
        passaggi.append(f'Criterio soglia: Utente -> {d_min:.1f} cm')

    # 2. Verifica dello status e del coefficiente
    d_eff = input_diag.distanza_apertura_cm
    status = 'OK'
    is_ok = True
    k = 1.0
    if d_eff >= d_min:
        passaggi.append(f'Distanza reale {d_eff:.1f} cm >= {d_min:.1f} cm limite. Nessuna penalizzazione.')
    else:
        is_ok = False
        # Limitazione a soglia asintotica k_min per evitare labilità totale (B2)
        k_lineare = d_eff / d_min if d_min > 0 else 1.0
        k = max(input_diag.k_min_resistenza, k_lineare)
        status = 'FAIL' if k <= input_diag.k_min_resistenza else 'WARNING'
        passaggi.append(f'Distanza reale {d_eff:.1f} cm < {d_min:.1f} cm limite (STATUS: {status}).')
        passaggi.append(f'Calcolo penalizzazione: limite_lineare = {d_eff:.1f}/{d_min:.1f} = {k_lineare:.3f} | k_min = {input_diag.k_min_resistenza:.3f}')
        passaggi.append(f'Coefficiente di riduzione resistenza assunto = {k:.3f}')

    return RisultatoDiagnosticaAngolo(
        is_ok=is_ok,
        status=status,
        distanza_minima_richiesta_cm=d_min,
        coeff_riduzione_k=k,
        passaggi_calcolo=passaggi
    )
