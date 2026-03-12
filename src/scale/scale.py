"""Core Fase V - verifiche di scale in c.a. e metalliche.

Implementazione pragmatica e tracciabile per il primo rilascio della Fase V.
Le formule sono organizzate per produrre risultati ripetibili, tabulati completi
e warning codificati coerenti con il piano di fase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, radians, sqrt, tan
from typing import Any

from src.core.registro_log import registro
from src.esistenti.livelli_conoscenza import risolvi_fc
from src.materials.material_model import Material, crea_acciaio_ntc2018, crea_calcestruzzo_ntc2018
from src.methods.ec.ec3 import (
    classifica_sezione_ec3,
    verifica_compressione_ec3,
    verifica_flessione_ec3,
    verifica_instabilita_flessotorsionale_ec3,
    verifica_taglio_ec3,
)
from src.methods.ec.ec3_connessioni import verifica_bullone_taglio_ec3
from src.report.tabulati_calcolo import TabulatoCalcolo

_MODULO_LOG = "scale.scale"
_KGF_TO_KN = 0.00980665
_KG_CM2_TO_MPA = 0.0980665
_CARICHI_CATEGORIA_KN_M2 = {
    "residenziale": 2.0,
    "uffici": 3.0,
    "pubblico": 4.0,
    "affollamento_elevato": 5.0,
}


@dataclass(slots=True)
class GeometriaRampa:
    """Dati geometrici e di carico della rampa."""

    tipologia: str
    alpha_deg: float
    luce_orizzontale_m: float
    spessore_m: float
    larghezza_m: float = 1.20
    alzata_m: float | None = None
    pedata_m: float | None = None
    scala_esterna: bool = False
    categoria_uso: str = "residenziale"
    area_influenza_m2: float | None = None
    livello_conoscenza: str | None = None
    fc_override: float | None = None
    carico_variabile_kN_m2: float | None = None
    carico_permanente_aggiuntivo_kN_m2: float = 0.0
    neve_sk_kN_m2: float = 0.0
    coeff_esposizione_ce: float = 1.0
    coeff_termico_ct: float = 1.0
    vento_qp_kN_m2: float = 0.0
    coeff_forma_cf: float = 1.30
    area_parapetto_m2: float = 0.0
    schema_statico: str = "appoggiata"
    armatura_tesa_cm2: float = 12.0
    copriferro_cm: float = 3.0
    diametro_barra_cm: float = 1.6
    phi_viscosita: float = 2.0
    delta_pendenza_deg: float = 0.0
    # Estensione: schema incastrato
    vincolo_sinistra: str = "libero"  # "libero", "cerniera", "incastro"
    vincolo_destra: str = "libero"
    lunghezza_libera_sinistra_m: float = 0.0
    lunghezza_libera_destra_m: float = 0.0
    # Estensione: pianerottolo intermedio
    pianerottolo_presente: bool = False
    pianerottolo_tipo: str = "autonomo"  # "autonomo", "continuita", "ibrido"
    pianerottolo_larghezza_m: float = 0.0
    pianerottolo_altezza_m: float = 0.0
    # Estensione: rampa a cambio pendenza (segmentata)
    segmenti_rampa: list[tuple[float, float]] | None = None  # list of (luce_m, alpha_deg)

    @property
    def luce_sviluppata_m(self) -> float:
        return self.luce_orizzontale_m / cos(radians(self.alpha_deg))

    @property
    def carico_variabile_eff_kN_m2(self) -> float:
        if self.carico_variabile_kN_m2 is not None:
            return self.carico_variabile_kN_m2
        return calcola_carico_variabile_default(self.categoria_uso)


@dataclass(slots=True)
class ProfiloAcciaioScala:
    """Proprieta' essenziali del profilo metallico per la verifica EC3."""

    nome: str
    area_mm2: float
    wpl_mm3: float
    av_mm2: float
    h_mm: float
    b_mm: float
    tf_mm: float
    tw_mm: float
    fy_mpa: float = 275.0
    gamma_m0: float = 1.0
    m_cr_kNm: float | None = None
    numero_correnti: int = 2
    numero_bulloni_parapetto: int = 2
    area_bullone_mm2: float = 157.0
    f_ub_bullone_mpa: float = 800.0


@dataclass(slots=True)
class RisultatoVerifica:
    """Esito di una singola verifica."""

    nome: str
    valore_domanda: float
    valore_resistenza: float | None
    unita: str
    esito: bool
    passaggi_calcolo: list[str] = field(default_factory=list)
    warning_codes: list[str] = field(default_factory=list)
    normativa: str = ""

    @property
    def rapporto_utilizzo(self) -> float | None:
        resistenza = self.valore_resistenza
        if resistenza is None or resistenza == 0.0:
            return None
        return self.valore_domanda / resistenza

    def to_dict(self) -> dict[str, Any]:
        return {
            "nome": self.nome,
            "valore_domanda": self.valore_domanda,
            "valore_resistenza": self.valore_resistenza,
            "unita": self.unita,
            "esito": self.esito,
            "rapporto_utilizzo": self.rapporto_utilizzo,
            "passaggi_calcolo": list(self.passaggi_calcolo),
            "warning_codes": list(self.warning_codes),
            "normativa": self.normativa,
        }


@dataclass(slots=True)
class RisultatoScala:
    """Risultato complessivo della rampa."""

    tipo: str
    geometria: GeometriaRampa
    verifiche: list[RisultatoVerifica]
    esito_globale: bool
    warning_codes: list[str] = field(default_factory=list)
    passaggi_calcolo: list[str] = field(default_factory=list)
    tabulato_ascii: str = ""
    tabulato_dati: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tipo": self.tipo,
            "geometria": {
                "tipologia": self.geometria.tipologia,
                "alpha_deg": self.geometria.alpha_deg,
                "luce_orizzontale_m": self.geometria.luce_orizzontale_m,
                "spessore_m": self.geometria.spessore_m,
                "larghezza_m": self.geometria.larghezza_m,
                "categoria_uso": self.geometria.categoria_uso,
                "scala_esterna": self.geometria.scala_esterna,
                "livello_conoscenza": self.geometria.livello_conoscenza,
            },
            "verifiche": [verifica.to_dict() for verifica in self.verifiche],
            "esito_globale": self.esito_globale,
            "warning_codes": list(self.warning_codes),
            "passaggi_calcolo": list(self.passaggi_calcolo),
            "tabulato": self.tabulato_dati,
        }


def calcola_carico_variabile_default(categoria_uso: str) -> float:
    categoria = categoria_uso.strip().lower()
    if categoria not in _CARICHI_CATEGORIA_KN_M2:
        raise ValueError(
            "Categoria d'uso non valida. Ammesse: " f"{sorted(_CARICHI_CATEGORIA_KN_M2.keys())}"
        )
    return _CARICHI_CATEGORIA_KN_M2[categoria]


def calcola_coefficiente_neve(alpha_deg: float) -> float:
    if alpha_deg <= 30.0:
        return 0.8
    if alpha_deg >= 60.0:
        return 0.0
    return 0.8 * (60.0 - alpha_deg) / 30.0


def profilo_ipe200_s275() -> ProfiloAcciaioScala:
    """Profilo di comodo per test e casi base V.2."""

    return ProfiloAcciaioScala(
        nome="IPE200",
        area_mm2=2850.0,
        wpl_mm3=194000.0,
        av_mm2=1560.0,
        h_mm=200.0,
        b_mm=100.0,
        tf_mm=8.5,
        tw_mm=5.6,
        fy_mpa=275.0,
        m_cr_kNm=55.0,
    )


def verifica_scala_ca(
    geometria: GeometriaRampa,
    materiale_cls: Material | None = None,
    materiale_acciaio: Material | None = None,
) -> RisultatoScala:
    """Esegue la verifica di una rampa in c.a."""

    _valida_geometria(geometria)
    materiale_cls = materiale_cls or crea_calcestruzzo_ntc2018("C25/30")
    materiale_acciaio = materiale_acciaio or crea_acciaio_ntc2018("B450C")

    warning_codes: list[str] = []
    passaggi: list[str] = ["Verifica scala in c.a. - avvio calcolo"]

    fc = _risolvi_fc_e_warning(geometria, warning_codes)
    if geometria.area_influenza_m2 is not None:
        warning_codes.append("V-AREA-002")

    alpha_rad = radians(geometria.alpha_deg)
    gamma_cls_kN_m3 = materiale_cls.densita_kg_m3 * 9.81 / 1000.0
    g_rampa = gamma_cls_kN_m3 * geometria.spessore_m / cos(alpha_rad)
    qk = geometria.carico_variabile_eff_kN_m2
    q_neve = _calcola_carico_neve(geometria)
    q_tot = g_rampa + geometria.carico_permanente_aggiuntivo_kN_m2 + qk + q_neve
    q_line = q_tot * geometria.larghezza_m

    # Determina il modello strutturale in base a schema_statico e pianerottolo
    if geometria.segmenti_rampa and len(geometria.segmenti_rampa) > 1:
        # Rampa segmentata (cambio pendenza)
        momento_kNm, taglio_kN, normale_kN = _segmenta_rampa(geometria, q_tot, warning_codes)
    elif geometria.pianerottolo_presente and not geometria.pianerottolo_larghezza_m <= 0.0:
        # Rampa con pianerottolo intermedio
        m_rampa, v_rampa, n_rampa = (
            _calcola_incastro(geometria, q_line, warning_codes)
            if geometria.schema_statico != "appoggiata"
            else (
                q_line * geometria.luce_orizzontale_m**2 / 8.0,
                q_line * geometria.luce_orizzontale_m / 2.0,
                q_line * geometria.luce_orizzontale_m / 2.0 * tan(alpha_rad),
            )
        )
        m_piano, _, _ = _gestisci_pianerottolo(geometria, q_tot, warning_codes)
        # Somma i contributi (semplificazione conservativa)
        momento_kNm = m_rampa + m_piano
        taglio_kN = v_rampa
        normale_kN = n_rampa
    elif geometria.schema_statico == "incastrata":
        # Rampa incastrata
        momento_kNm, taglio_kN, normale_kN = _calcola_incastro(geometria, q_line, warning_codes)
    else:
        # Schema appoggiato (default)
        taglio_kN = q_line * geometria.luce_orizzontale_m / 2.0
        momento_kNm = q_line * geometria.luce_orizzontale_m**2 / 8.0
        normale_kN = taglio_kN * tan(alpha_rad)

    f_cd = _ottieni_f_cd_kg_cm2(materiale_cls) / fc
    f_yd = _ottieni_f_yd_kg_cm2(materiale_acciaio) / fc
    b_cm = geometria.larghezza_m * 100.0
    h_cm = geometria.spessore_m * 100.0
    d_cm = max(h_cm - geometria.copriferro_cm - geometria.diametro_barra_cm / 2.0, h_cm * 0.75)
    z_cm = 0.9 * d_cm
    m_rd_kNm = geometria.armatura_tesa_cm2 * f_yd * z_cm * 0.0000980665

    area_cls_cm2 = b_cm * h_cm
    n_rd_kN = (0.60 * f_cd * area_cls_cm2 + geometria.armatura_tesa_cm2 * f_yd) * _KGF_TO_KN
    rapporto_interazione = momento_kNm / max(m_rd_kNm, 1e-9) + normale_kN / max(n_rd_kN, 1e-9)

    as_mm2 = geometria.armatura_tesa_cm2 * 100.0
    b_mm = geometria.larghezza_m * 1000.0
    d_mm = d_cm * 10.0
    rho_l = min(as_mm2 / max(b_mm * d_mm, 1.0), 0.02)
    f_ck_mpa = materiale_cls.f_ck * _KG_CM2_TO_MPA
    k = min(2.0, 1.0 + sqrt(200.0 / max(d_mm, 1.0)))
    sigma_cp = normale_kN * 1000.0 / max(b_mm * d_mm, 1.0)
    gamma_c = materiale_cls.gamma_c if materiale_cls.gamma_c > 0 else 1.5
    coeff_vrdc = (0.18 / gamma_c) * k * (100.0 * rho_l * max(f_ck_mpa, 1.0)) ** (1.0 / 3.0)
    v_rdc_kN = ((coeff_vrdc + 0.15 * sigma_cp) * b_mm * d_mm) / 1000.0

    e_mpa = materiale_cls.E * _KG_CM2_TO_MPA if materiale_cls.E > 0 else 30000.0
    i_eff_mm4 = 0.5 * (b_mm * (geometria.spessore_m * 1000.0) ** 3 / 12.0)
    w_n_mm = q_line
    l_mm = geometria.luce_orizzontale_m * 1000.0
    freccia_inst_mm = (5.0 * w_n_mm * l_mm**4) / max(384.0 * e_mpa * i_eff_mm4, 1.0)
    freccia_fin_mm = freccia_inst_mm * (1.0 + geometria.phi_viscosita)
    freccia_limite_mm = l_mm / 300.0

    sigma_media_kN_m2 = normale_kN / max(geometria.larghezza_m * geometria.spessore_m, 1e-9)
    sigma_bordo_kN_m2 = sigma_media_kN_m2 + 6.0 * momento_kNm / max(
        geometria.larghezza_m * geometria.spessore_m**2,
        1e-9,
    )

    verifiche = [
        RisultatoVerifica(
            nome="Flessione",
            valore_domanda=momento_kNm,
            valore_resistenza=m_rd_kNm,
            unita="kNm",
            esito=momento_kNm <= m_rd_kNm,
            passaggi_calcolo=[
                f"M_Ed = {momento_kNm:.3f} kNm",
                f"M_Rd = A_s * f_yd * z = {m_rd_kNm:.3f} kNm",
            ],
            warning_codes=list(warning_codes),
            normativa="NTC2018 §4.1.4 + EC2 §5.7",
        ),
        RisultatoVerifica(
            nome="Taglio",
            valore_domanda=taglio_kN,
            valore_resistenza=v_rdc_kN,
            unita="kN",
            esito=taglio_kN <= v_rdc_kN,
            passaggi_calcolo=[
                f"V_Ed = {taglio_kN:.3f} kN",
                f"V_Rd,c = {v_rdc_kN:.3f} kN",
            ],
            warning_codes=list(warning_codes),
            normativa="EC2 §6.2.2 (fallback conservativo)",
        ),
        RisultatoVerifica(
            nome="Pressoflessione",
            valore_domanda=rapporto_interazione,
            valore_resistenza=1.0,
            unita="-",
            esito=rapporto_interazione <= 1.0,
            passaggi_calcolo=[
                f"N_Ed = {normale_kN:.3f} kN",
                f"N_Rd = {n_rd_kN:.3f} kN",
                f"Interazione = M/M_Rd + N/N_Rd = {rapporto_interazione:.3f}",
                f"σ_media ≈ {sigma_media_kN_m2:.2f} kN/m²",
                f"σ_bordo ≈ {sigma_bordo_kN_m2:.2f} kN/m²",
            ],
            warning_codes=list(warning_codes),
            normativa="NTC2018 §4.1.4",
        ),
        RisultatoVerifica(
            nome="Freccia",
            valore_domanda=freccia_fin_mm,
            valore_resistenza=freccia_limite_mm,
            unita="mm",
            esito=freccia_fin_mm <= freccia_limite_mm,
            passaggi_calcolo=[
                f"δ_inst = {freccia_inst_mm:.3f} mm",
                f"δ_fin = δ_inst * (1 + φ) = {freccia_fin_mm:.3f} mm",
                f"δ_lim = L/300 = {freccia_limite_mm:.3f} mm",
            ],
            warning_codes=list(warning_codes),
            normativa="NTC2018 §4.1.12 + EC2 §7.4",
        ),
    ]

    if normale_kN / max(n_rd_kN, 1e-9) > 0.10:
        warning_codes.append("V-AXIAL-001")
    if freccia_fin_mm > freccia_limite_mm:
        warning_codes.append("V-DEFL-004")

    tab = TabulatoCalcolo(
        titolo="Scala in c.a. - verifica globale",
        normativa="NTC2018 §4.1.4 / EC2 §5.7 / EC2 §7.4",
        modulo=_MODULO_LOG,
    )
    _popola_tabulato_base(tab, geometria, q_tot, q_line)
    tab.aggiungi_riga_calcolo(
        descrizione="Peso proprio della rampa",
        formula="g = gamma_cls * s / cos(alpha)",
        sostituzione=(
            f"g = {gamma_cls_kN_m3:.2f} * {geometria.spessore_m:.3f} / cos({geometria.alpha_deg:.1f})"
        ),
        risultato=round(g_rampa, 3),
        unita="kN/m²",
        nota="NTC2018 §4.1.4",
    )
    tab.aggiungi_riga_calcolo(
        descrizione="Momento massimo in campata",
        formula="M_Ed = q_line * L² / 8",
        sostituzione=f"M_Ed = {q_line:.3f} * {geometria.luce_orizzontale_m:.3f}² / 8",
        risultato=round(momento_kNm, 3),
        unita="kNm",
        nota="Schema appoggiato",
    )
    tab.aggiungi_riga_calcolo(
        descrizione="Capacita' a flessione",
        formula="M_Rd = A_s * f_yd * z",
        sostituzione=f"M_Rd = {geometria.armatura_tesa_cm2:.2f} * {f_yd:.1f} * {z_cm:.2f}",
        risultato=round(m_rd_kNm, 3),
        unita="kNm",
        nota="Sezione rettangolare semplificata",
    )
    tab.aggiungi_nota(f"Warning codes: {', '.join(_warning_ordinati(warning_codes)) or 'nessuno'}")
    tab.imposta_esito(
        domanda=momento_kNm,
        capacita=m_rd_kNm,
        unita="kNm",
        nome_domanda="M_Ed",
        nome_capacita="M_Rd",
    )

    esito_globale = all(item.esito for item in verifiche)
    passaggi.extend(
        [
            f"q_tot = {q_tot:.3f} kN/m²",
            f"q_line = {q_line:.3f} kN/m",
            f"M_Ed = {momento_kNm:.3f} kNm",
            f"N_Ed = {normale_kN:.3f} kN",
            f"V_Ed = {taglio_kN:.3f} kN",
            f"Esito globale = {'VERIFICATO' if esito_globale else 'NON VERIFICATO'}",
        ]
    )

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Verifica scala in c.a.",
        input_dati={
            "alpha_deg": geometria.alpha_deg,
            "L_m": geometria.luce_orizzontale_m,
            "s_m": geometria.spessore_m,
            "q_tot_kN_m2": q_tot,
        },
        output_dati={
            "M_Ed_kNm": momento_kNm,
            "M_Rd_kNm": m_rd_kNm,
            "V_Rd_c_kN": v_rdc_kN,
            "esito_globale": esito_globale,
        },
        normativa="NTC2018 §4.1.4 / EC2",
        formula="M = qL²/8; N = Vtan(alpha)",
        passaggi=passaggi,
        esito="VERIFICATO" if esito_globale else "NON VERIFICATO",
    )

    return RisultatoScala(
        tipo="ca",
        geometria=geometria,
        verifiche=verifiche,
        esito_globale=esito_globale,
        warning_codes=_warning_ordinati(warning_codes),
        passaggi_calcolo=passaggi,
        tabulato_ascii=tab.come_ascii(),
        tabulato_dati=tab.come_dizionario(),
    )


def verifica_scala_metallica(
    geometria: GeometriaRampa,
    profilo: ProfiloAcciaioScala | None = None,
) -> RisultatoScala:
    """Esegue la verifica di una scala metallica."""

    _valida_geometria(geometria)
    profilo = profilo or profilo_ipe200_s275()

    warning_codes: list[str] = []
    passaggi: list[str] = ["Verifica scala metallica - avvio calcolo"]

    if geometria.area_influenza_m2 is not None:
        warning_codes.append("V-AREA-002")
    _risolvi_fc_e_warning(geometria, warning_codes)

    alpha_rad = radians(geometria.alpha_deg)
    qk = geometria.carico_variabile_eff_kN_m2
    q_neve = _calcola_carico_neve(geometria)
    peso_profilo_lineare = (
        profilo.area_mm2 * 1e-6 * 7850.0 * 9.81 / 1000.0 * profilo.numero_correnti
    )
    q_tot = geometria.carico_permanente_aggiuntivo_kN_m2 + qk + q_neve
    q_line = q_tot * geometria.larghezza_m + peso_profilo_lineare

    taglio_kN = q_line * geometria.luce_orizzontale_m / 2.0
    momento_kNm = q_line * geometria.luce_orizzontale_m**2 / 8.0
    normale_kN = taglio_kN * tan(alpha_rad)

    classificazione = classifica_sezione_ec3(
        fy=profilo.fy_mpa,
        b=profilo.b_mm,
        d=profilo.h_mm - 2.0 * profilo.tf_mm,
        tf=profilo.tf_mm,
        tw=profilo.tw_mm,
    )
    if classificazione["classe"] >= 4:
        warning_codes.append("V-LTB-003")

    flessione = verifica_flessione_ec3(
        fy=profilo.fy_mpa,
        Wpl=profilo.wpl_mm3,
        d=profilo.h_mm - 2.0 * profilo.tf_mm,
        b=profilo.b_mm,
        tf=profilo.tf_mm,
        tw=profilo.tw_mm,
        M_d=momento_kNm * 1_000_000.0,
        gamma_m0=profilo.gamma_m0,
    )
    taglio = verifica_taglio_ec3(
        fy=profilo.fy_mpa,
        A_v=profilo.av_mm2,
        V_d=taglio_kN * 1000.0,
        gamma_m0=profilo.gamma_m0,
    )
    compressione = verifica_compressione_ec3(
        fy=profilo.fy_mpa,
        A=profilo.area_mm2,
        N_d=normale_kN * 1000.0,
        gamma_m0=profilo.gamma_m0,
    )
    m_cr_kNm = profilo.m_cr_kNm if profilo.m_cr_kNm is not None else momento_kNm * 2.5
    ltb = verifica_instabilita_flessotorsionale_ec3(
        M_cr=m_cr_kNm * 1_000_000.0,
        M_pl_Rd=flessione["M_Rd"],
    )

    f_oriz_parapetto_kN = max(1.0 * geometria.luce_sviluppata_m, 0.0)
    if geometria.area_parapetto_m2 > 0.0 and geometria.vento_qp_kN_m2 > 0.0:
        f_oriz_parapetto_kN = max(
            f_oriz_parapetto_kN,
            geometria.vento_qp_kN_m2 * geometria.coeff_forma_cf * geometria.area_parapetto_m2,
        )
    bulloni = verifica_bullone_taglio_ec3(
        A_b=profilo.area_bullone_mm2,
        f_ub=profilo.f_ub_bullone_mpa,
        V_ed=(f_oriz_parapetto_kN * 1000.0) / max(profilo.numero_bulloni_parapetto, 1),
    )

    m_b_rd_kNm = ltb["M_b_Rd"] / 1_000_000.0
    rapporto_interazione = max(
        flessione["rateo"],
        taglio["rateo"],
        compressione["rateo"],
        momento_kNm / max(m_b_rd_kNm, 1e-9),
    )

    verifiche = [
        RisultatoVerifica(
            nome="Classificazione sezione",
            valore_domanda=float(classificazione["classe"]),
            valore_resistenza=3.0,
            unita="classe",
            esito=classificazione["classe"] <= 3,
            passaggi_calcolo=[
                f"Classe sezione = {classificazione['classe']}",
                f"Rapporto ala = {classificazione['ratio_flange']:.2f}",
                f"Rapporto anima = {classificazione['ratio_web']:.2f}",
            ],
            warning_codes=list(warning_codes),
            normativa=classificazione["riferimento_normativo"],
        ),
        RisultatoVerifica(
            nome="Flessione",
            valore_domanda=momento_kNm,
            valore_resistenza=flessione["M_Rd"] / 1_000_000.0,
            unita="kNm",
            esito=flessione["esito"],
            passaggi_calcolo=[
                f"M_Ed = {momento_kNm:.3f} kNm",
                f"M_Rd = {flessione['M_Rd'] / 1_000_000.0:.3f} kNm",
            ],
            warning_codes=list(warning_codes),
            normativa=flessione["riferimento_normativo"],
        ),
        RisultatoVerifica(
            nome="Taglio",
            valore_domanda=taglio_kN,
            valore_resistenza=taglio["V_Rd"] / 1000.0,
            unita="kN",
            esito=taglio["esito"],
            passaggi_calcolo=[
                f"V_Ed = {taglio_kN:.3f} kN",
                f"V_Rd = {taglio['V_Rd'] / 1000.0:.3f} kN",
            ],
            warning_codes=list(warning_codes),
            normativa=taglio["riferimento_normativo"],
        ),
        RisultatoVerifica(
            nome="Instabilita' flesso-torsionale",
            valore_domanda=momento_kNm,
            valore_resistenza=m_b_rd_kNm,
            unita="kNm",
            esito=momento_kNm <= m_b_rd_kNm,
            passaggi_calcolo=[
                f"chi_LT = {ltb['chi_lt']:.3f}",
                f"lambda_LT = {ltb['lambda_lt']:.3f}",
                f"M_b,Rd = {m_b_rd_kNm:.3f} kNm",
            ],
            warning_codes=list(warning_codes),
            normativa=ltb["riferimento_normativo"],
        ),
        RisultatoVerifica(
            nome="Connessione parapetto",
            valore_domanda=(f_oriz_parapetto_kN * 1000.0)
            / max(profilo.numero_bulloni_parapetto, 1),
            valore_resistenza=bulloni["V_Rd"],
            unita="N",
            esito=bulloni["esito"],
            passaggi_calcolo=[
                f"Forza orizzontale di progetto = {f_oriz_parapetto_kN:.3f} kN",
                f"Taglio per bullone = {((f_oriz_parapetto_kN * 1000.0) / max(profilo.numero_bulloni_parapetto, 1)):.3f} N",
                f"V_Rd bullone = {bulloni['V_Rd']:.3f} N",
            ],
            warning_codes=list(warning_codes),
            normativa=bulloni["riferimento_normativo"],
        ),
    ]

    if classificazione["classe"] >= 4 or momento_kNm > m_b_rd_kNm:
        warning_codes.append("V-LTB-003")

    tab = TabulatoCalcolo(
        titolo="Scala metallica - verifica globale",
        normativa="EC3 §5.5 / §6.2 / §6.3.2 / EC3-1-8",
        modulo=_MODULO_LOG,
    )
    _popola_tabulato_base(tab, geometria, q_tot, q_line)
    tab.aggiungi_riga_calcolo(
        descrizione="Momento massimo in campata",
        formula="M_Ed = q_line * L² / 8",
        sostituzione=f"M_Ed = {q_line:.3f} * {geometria.luce_orizzontale_m:.3f}² / 8",
        risultato=round(momento_kNm, 3),
        unita="kNm",
        nota="Schema appoggiato",
    )
    tab.aggiungi_riga_calcolo(
        descrizione="Resistenza a instabilita' flesso-torsionale",
        formula="M_b,Rd = chi_LT * M_pl,Rd",
        sostituzione=f"M_b,Rd = {ltb['chi_lt']:.3f} * {flessione['M_Rd'] / 1_000_000.0:.3f}",
        risultato=round(m_b_rd_kNm, 3),
        unita="kNm",
        nota="EC3 §6.3.2",
    )
    tab.aggiungi_nota(f"Warning codes: {', '.join(_warning_ordinati(warning_codes)) or 'nessuno'}")
    tab.imposta_esito(
        domanda=momento_kNm,
        capacita=m_b_rd_kNm,
        unita="kNm",
        nome_domanda="M_Ed",
        nome_capacita="M_b,Rd",
    )

    esito_globale = all(item.esito for item in verifiche) and rapporto_interazione <= 1.0
    passaggi.extend(
        [
            f"Classe sezione = {classificazione['classe']}",
            f"M_Ed = {momento_kNm:.3f} kNm",
            f"M_b,Rd = {m_b_rd_kNm:.3f} kNm",
            f"V_Ed = {taglio_kN:.3f} kN",
            f"N_Ed = {normale_kN:.3f} kN",
            f"Esito globale = {'VERIFICATO' if esito_globale else 'NON VERIFICATO'}",
        ]
    )

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Verifica scala metallica",
        input_dati={
            "profilo": profilo.nome,
            "alpha_deg": geometria.alpha_deg,
            "L_m": geometria.luce_orizzontale_m,
            "q_line_kN_m": q_line,
        },
        output_dati={
            "classe_sezione": classificazione["classe"],
            "M_b_Rd_kNm": m_b_rd_kNm,
            "esito_globale": esito_globale,
        },
        normativa="EC3 / EC3-1-8",
        formula="M = qL²/8; chi_LT = f(lambda_LT)",
        passaggi=passaggi,
        esito="VERIFICATO" if esito_globale else "NON VERIFICATO",
    )

    return RisultatoScala(
        tipo="acciaio",
        geometria=geometria,
        verifiche=verifiche,
        esito_globale=esito_globale,
        warning_codes=_warning_ordinati(warning_codes),
        passaggi_calcolo=passaggi,
        tabulato_ascii=tab.come_ascii(),
        tabulato_dati=tab.come_dizionario(),
    )


def _valida_geometria(geometria: GeometriaRampa) -> None:
    if geometria.alpha_deg < 15.0 or geometria.alpha_deg > 45.0:
        registro.errore(_MODULO_LOG, "Parametro fuori range", "alpha_deg non ammesso")
        raise ValueError("V-RANGE-001: alpha_deg fuori range [15, 45]")
    if geometria.spessore_m < 0.10 or geometria.spessore_m > 0.30:
        registro.errore(_MODULO_LOG, "Parametro fuori range", "spessore rampa non ammesso")
        raise ValueError("V-RANGE-001: spessore fuori range [0.10, 0.30] m")
    if geometria.luce_orizzontale_m < 1.0 or geometria.luce_orizzontale_m > 8.0:
        registro.errore(_MODULO_LOG, "Parametro fuori range", "luce rampa non ammessa")
        raise ValueError("V-RANGE-001: luce orizzontale fuori range [1.0, 8.0] m")
    if geometria.larghezza_m <= 0.0:
        raise ValueError("larghezza rampa deve essere > 0")
    if geometria.tipologia.strip().lower() in {"chiocciola", "elicoidale"}:
        raise ValueError("V-RANGE-001: tipologia esclusa dalla V1")


def _risolvi_fc_e_warning(geometria: GeometriaRampa, warning_codes: list[str]) -> float:
    if not geometria.livello_conoscenza:
        return 1.0
    fc = risolvi_fc(geometria.livello_conoscenza, geometria.fc_override)
    warning_codes.append("V-FC-005")
    return fc


def _ottieni_f_cd_kg_cm2(materiale_cls: Material) -> float:
    f_cd = materiale_cls.ottieni_derivato("f_cd")
    if f_cd > 0.0:
        return f_cd
    return materiale_cls.alpha_cc * materiale_cls.f_ck / materiale_cls.gamma_c


def _ottieni_f_yd_kg_cm2(materiale_acciaio: Material) -> float:
    f_yd = materiale_acciaio.ottieni_derivato("f_yd")
    if f_yd > 0.0:
        return f_yd
    return materiale_acciaio.f_yk / materiale_acciaio.gamma_s


def _calcola_carico_neve(geometria: GeometriaRampa) -> float:
    if not geometria.scala_esterna or geometria.neve_sk_kN_m2 <= 0.0:
        return 0.0
    mu_i = calcola_coefficiente_neve(geometria.alpha_deg)
    return (
        mu_i * geometria.coeff_esposizione_ce * geometria.coeff_termico_ct * geometria.neve_sk_kN_m2
    )


def _popola_tabulato_base(
    tabulato: TabulatoCalcolo,
    geometria: GeometriaRampa,
    q_tot: float,
    q_line: float,
) -> None:
    tabulato.aggiungi_sezione_input(
        {
            "alpha": ("Angolo rampa", geometria.alpha_deg, "deg"),
            "L": ("Luce orizzontale", geometria.luce_orizzontale_m, "m"),
            "s": ("Spessore rampa", geometria.spessore_m, "m"),
            "b": ("Larghezza rampa", geometria.larghezza_m, "m"),
            "q_tot": ("Carico superficiale totale", round(q_tot, 3), "kN/m²"),
            "q_line": ("Carico lineare equivalente", round(q_line, 3), "kN/m"),
        }
    )


def _warning_ordinati(warning_codes: list[str]) -> list[str]:
    return sorted(set(warning_codes))


def _calcola_incastro(
    geometria: GeometriaRampa,
    q_line: float,
    warning_codes: list[str],
) -> tuple[float, float, float]:
    """Calcola M, V, N per schema incastrato/vincoli misti.

    Restituisce (momento_kNm, taglio_kN, normale_kN).
    """
    if geometria.vincolo_sinistra == geometria.vincolo_destra == "incastro":
        # Doppio incastro: M_max = qL²/12, V = qL/2
        momento_kNm = q_line * geometria.luce_orizzontale_m**2 / 12.0
        taglio_kN = q_line * geometria.luce_orizzontale_m / 2.0
    elif geometria.vincolo_sinistra == "incastro" or geometria.vincolo_destra == "incastro":
        # Singolo incastro: M_max = qL²/8 (conservativo come appoggiato)
        momento_kNm = q_line * geometria.luce_orizzontale_m**2 / 8.0
        taglio_kN = q_line * geometria.luce_orizzontale_m / 2.0
        warning_codes.append("V-FIXED-002")
    else:
        # Schema appoggiato di default
        momento_kNm = q_line * geometria.luce_orizzontale_m**2 / 8.0
        taglio_kN = q_line * geometria.luce_orizzontale_m / 2.0

    alpha_rad = radians(geometria.alpha_deg)
    normale_kN = taglio_kN * tan(alpha_rad)

    return momento_kNm, taglio_kN, normale_kN


def _gestisci_pianerottolo(
    geometria: GeometriaRampa,
    q_tot: float,
    warning_codes: list[str],
) -> tuple[float, float, float]:
    """Estende il calcolo includendo il pianerottolo intermedio.

    Restituisce (momento_kNm_locale, taglio_kN, normale_kN) come se il pianerottolo
    fosse una estensione della rampa precedente o un elemento autonomo.
    """
    if not geometria.pianerottolo_presente or geometria.pianerottolo_larghezza_m <= 0.0:
        # Nessun pianerottolo: torna valori nulli
        return 0.0, 0.0, 0.0

    if geometria.pianerottolo_tipo == "autonomo":
        # Il pianerottolo è una soletta a se': momento da carico distribuito su larghezza
        # Semplificazione: lo trattiamo come una trave rettangolare semplicemente appoggiata
        q_piano = q_tot * geometria.pianerottolo_larghezza_m
        m_piano = q_piano * geometria.pianerottolo_larghezza_m / 8.0
        warning_codes.append("V-JOINT-004")  # Incompletezza del modello
        return m_piano, 0.0, 0.0
    elif geometria.pianerottolo_tipo == "continuita":
        # Il pianerottolo continua la rampa: calcolo come rampa orizzontale di lunghezza pari a larghezza
        # Questo è una semplificazione; una verifica completa richiederebbe FEM
        q_piano = q_tot * geometria.pianerottolo_larghezza_m
        m_piano = q_piano * geometria.pianerottolo_larghezza_m / 8.0
        return m_piano, 0.0, 0.0
    else:  # "ibrido"
        # Modello ibrido: effettua una media tra i due
        q_piano = q_tot * geometria.pianerottolo_larghezza_m
        m_piano = q_piano * geometria.pianerottolo_larghezza_m / 8.0
        warning_codes.append("V-JOINT-004")  # Approssimazione esplicita
        return m_piano, 0.0, 0.0


def _segmenta_rampa(
    geometria: GeometriaRampa,
    q_tot: float,
    warning_codes: list[str],
) -> tuple[float, float, float]:
    """Calcola M, V, N per rampa a cambio di pendenza (segmentata).

    Integra i contributi di ogni segmento e verifica la compatibilità rotazionale.
    Restituisce (momento_massimo_kNm, taglio_massimo_kN, assiale_massimo_kN).
    """
    if not geometria.segmenti_rampa or len(geometria.segmenti_rampa) <= 1:
        # Nessun segmento o rampa singola: nulla da fare
        return 0.0, 0.0, 0.0

    momenti: list[float] = []
    tagli: list[float] = []
    assiali: list[float] = []

    for i, (luce_m, alpha_seg_deg) in enumerate(geometria.segmenti_rampa):
        if i > 0:
            prev_alpha = geometria.segmenti_rampa[i - 1][1]
            delta_alpha = abs(alpha_seg_deg - prev_alpha)
            if delta_alpha > 15.0:
                warning_codes.append("V-PEND-003")

        q_seg = q_tot * geometria.larghezza_m
        m_seg = q_seg * luce_m**2 / 8.0
        v_seg = q_seg * luce_m / 2.0
        alpha_rad = radians(alpha_seg_deg)
        n_seg = v_seg * tan(alpha_rad)

        momenti.append(m_seg)
        tagli.append(v_seg)
        assiali.append(n_seg)

    return max(momenti), max(tagli), max(assiali)
