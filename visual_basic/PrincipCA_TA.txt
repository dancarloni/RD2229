Attribute VB_Name = "PrincipCA_TA"
Option Explicit
'CONST E VARIAB PUBBLICHE GENERALI
Public Const DataFineSw1 As String = "31/12/2025"
Public Const DurataggProvaSw = 93
Public Const NomeCartella As String = "c:\Software.Az"
Public Const VersioneSw As String = "SezioniCA.Az 9.0"
Public Const PièPagina As String = VersioneSw & "-Licenza d'uso "
Public Const IDsw As Integer = 1190
Public Const NomeFileControllo As String = NomeCartella & "\" & IDsw & ".txt"
Public Const N°carattIDsw As Integer = 4
Public Const NmaxCalc As Integer = 20
Public Const PasswordMe As String = "ciroaz1"
Public Const MessFineCalc_o_Tempo = "E' stato raggiunto il numero massimo di calcolazioni possibili o è scaduto il termine per l'utilizzazione della presente versione dell'applicativo. Per ottenere la versione senza limitazioni contattare l'Autore."
Public Const TipoCaratt = "Calibri" '"Arial"
Public Const Hcaratt = 11
Public BarraProgramma As Object
Public Ncalcolaz%
Public PrimoAvvio As Boolean
Public iF1%, iF1pr%
Public i%, j%, k% 'contatori
Public SwAttivato As Boolean
'CONST E VARIAB PUBBLICHE SPECIALI
Public Const PiGreco = 3.141592654
Public Asez#, Ac#, Aci#
Public Alfa_ta#, Alfa_to#
Public Af#, A1f#, Aft#, Af1t# 'armatura in zona tesa, zona compressa, totale, di una barra
Public Ainf#, Asup# 'armatura lembo inferiore e lembo superiore
Public Al_to#, Asw_ta#, Asw_tay#, Asw_taz#, Asw_to#
Public aM#
Public B#, Bo#, B_frp#
Public Beta_y#, Beta_z#
Public blnVerifCarPunta As Boolean, blnVerifSLE As Boolean, blnVerifDuttilità As Boolean
Public blnParabRettang As Boolean, blnTriangRettang As Boolean, blnStressBlock As Boolean, blnElastPerfettPlastico As Boolean, blnBilineare As Boolean
Public blnLineareIncrud As Boolean, blnLineareDegrad As Boolean, blnRigidoPlastico As Boolean
Public blnCarichiBrevi As Boolean, blnCDA As Boolean
Public blnConfinNessuno As Boolean, blnConfinStaffe As Boolean, blnConfinFRP As Boolean, blnConfinCamicieAcc As Boolean
Public CemArmOrd As Boolean, CemCAP As Boolean, CalcVerif As Boolean, CemFRC As Boolean, CondizAmb As String
'Public CostruzNuova As Boolean, CostruzEsist As Boolean
Public CosAlfa_ii#, SinAlfa_ii#
Public Cf#, ClsResistTraz As Boolean
Public D#, Di#, Dst_ta#, Dst_to#, dfp#
Public Db#() 'vettore contenente i diametri di ogni barra
Public dsup#, dinf#, Df#, Delta#, DeltaSup#, DeltaInf#
Public Ec#, Es#, Es_a#, E_frp# 'moduli elastici longitudinali cls, acciaio, composito frp
Public Eps_c2#, Eps_c3#, Eps_c4#, Eps_cu#, Eps_c2c#, Eps_cuc#, Eps0#, Eps_Fs#, Eps_Fu#, Eps_pu#, Eps_pk#, Eps0f#
Public Eps_yd#, Eps_su#, Eps_yd_e#
Public FormSez As String
Public fcd#, fck#, fcm#, fctm#, fctk#, fctd#, fck_c#, fcd_c#, fFts#, fFtu#, fccd#
Public fyd#, fyk#, fyk2#, ftk_a#, fyk_a#, fyd_a#, fym#, fyd_e#
Public fmF#, fmFL#, fmL#, fmL2#, fmFL_2#, fmDiamTond#, fmL3#, fmL4#, fcUM#, fc1#, fc3#
Public Gammac#, Gammas#, Gammas_a#, Gammaf#, Gammaf_dist#, Gammas_e#
Public H#, Hu#, H_frp#
Public Iy#
Public Kincr#, KK#
Public L#, Lsi#
Public Mx#, My#, Mz#, Medy#, Medz#, Myu_s#, Myu_i#
Public Mr#, Med#, Mi#, Mk#, Mfess#
Public MetodoTA As Boolean, MetodoSL08 As Boolean, MetodoSL18 As Boolean
Public MetodoFess1996 As Boolean, MetodoFess2008 As Boolean
Public Nx#, Nr#, Ned#
Public Nbs%, Nbi%, Nb#
Public Npolig As Byte, Np%, Npacch%, Nbry As Byte, Nbrz As Byte
Public Nbar% 'n° totale di tondini presenti in sezione
Public n# 'coeff. omogeneizzazione
Public Omega#
Public Pilastro As Boolean, Psez#
Public Pst_ta#, Pst_to#, Pmax#
Public Perc_cls_c#, Perc_cls_qp#, Perc_acc_c#
Public Rck%
Public RegioneRottura As Byte, RinfFRP As Boolean, RinfCamicieAcc As Boolean, RinfCamicieCA As Boolean
Public Sigc#, Sigc_pos#, Sigc_max#, Sigc_min#, SigCR#
Public Sigf#, Sig_fi#(), Sigf_max#
Public SistemaTecnico As Boolean
Public S#, SollecPiane As Boolean
Public StaffeCircSingole As Boolean, StaffeSpirale As Boolean, SensibArmat As String
Public Tz#, Ty#, Ted#, Teta_ta#, Teta_to#
Public TipoAcciaioCA As String, TipoAcciaio As String, TondArmonico() As Boolean, TondNuovo() As Boolean
Public Trave As Boolean, TraveFondaz As Boolean
Public umForze As String, umMomenti As String, umL As String, umL2 As String, umL3 As String, umL4 As String, umTens As String, umDiamTond As String
Public VerifResist As Boolean
Public xx#, x_u#
Public yG_pr#, yGr_pr#, y3_pr#, y4_pr#
Public Ymin_pr#, Ymax_pr#
Public Yb_pr#(), Yb#(), Ys_pr#(), Yfrp_pr#, Yfrp#
Public Zs_pr#(), Zb_pr#(), Zb#(), Zfrp_pr#, Zfrp#
Public z1_pr#, z2_pr#, Zmin_pr#, Zmax_pr#, zG_pr#, zGr_pr#
'CONST E VARIAB A LIVELLO DI MODULO
Dim Armat2Lembi As Boolean, Afmin#, Afmax#, Afmin1#, Afmin2#, Alfa_ta_frp#, Alfa_fib#
Dim B_f#, Bf_# ', Bj#
Dim ContinuitàFRP As String
Dim D1#, DisposizFRP As String
Dim Eps(), EpsVert#()
Dim Eta_a#, Eta1#
Dim fpk#, fpd#, fpd_sle#, FC As Single, ffdd#, ffed#
Dim Iyr#
Dim Iy_pr#, Iz_pr#, Iyz_pr#, Iz#, Iyz#, Iyp#, Izp#, Iyzp#
Dim Led#
Dim Mu_#, Mu#, Mu_min#
Dim Npolig_ns As Byte, Np_ns%
Dim p_f#, Perc_H#, pf_# ', pj#
Dim ryp#, rzp#, RigidezzaFRP As String, rc#, rc_#
Dim Sigfa#, Sigcar#, Sigca#, Sigfac%, SigMed#
Dim SigVert#()
Dim Sy_pr#, Sz_pr#, Sy#, Sz#
Dim sLmin#
Dim TauC0#, TauC1#, Tauxz_max#
Dim TipoFRP As String, TipoConfinFRP As String, TipoConfinCamicieAcc2 As String ', TipoConfinCamicieAcc As String
Dim t_f#, tf_# ', tj#
Dim yP#, zP#
Dim ZonaSismStruttDissip As Boolean

Sub Programma_principale()
Dim Time1, Time2
Time1 = Time
'1) INPUT
'1.1 DATI GENERALI
'1.1.1 Dati Generali
'CA/CAP, sistema per le unità di misura e tipo di calcolo
CemArmOrd = Foglio2.Cells(20, 1)
CemCAP = Foglio2.Cells(21, 1)
CemFRC = Foglio2.Cells(26, 1)
CalcVerif = Foglio2.Cells(25, 1)
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnitàMisura
'tipo costruzione e rinforzi
RinfFRP = Foglio2.Cells(81, 1)
RinfCamicieAcc = Foglio2.Cells(22, 4)
RinfCamicieCA = Foglio2.Cells(23, 4)
'normativa di riferimento e tipo di calcolo
MetodoTA = Foglio2.Cells(57, 1)
MetodoSL08 = Foglio2.Cells(58, 1)
MetodoSL18 = Foglio2.Cells(59, 1)
'forma sezione e tipo di asta
FormSez = Foglio2.Cells(54, 1)
If Foglio2.Cells(3, 26) = "" Then Npolig = 0 Else Npolig = Foglio2.Cells(3, 26)
Pilastro = Foglio2.Cells(36, 1)
Trave = Foglio2.Cells(37, 1)
TraveFondaz = Foglio2.Cells(38, 1)
'stato di sollecitazione
SollecPiane = Foglio2.Cells(28, 1)
'altre verifiche
blnVerifSLE = Foglio2.Cells(32, 6)
blnVerifCarPunta = Foglio2.Cells(46, 1)
blnVerifDuttilità = Foglio2.Cells(22, 1)
'1.1.2 Confinamento cls
If MetodoSL18 And CalcVerif And (FormSez = "Rettangolare" Or FormSez = "Circolare piena o cava") Then
    blnConfinNessuno = Foglio2.Cells(66, 5)
    blnConfinStaffe = Foglio2.Cells(67, 5)
    blnConfinFRP = Foglio2.Cells(68, 5)
    blnConfinCamicieAcc = Foglio2.Cells(69, 5)
Else
    blnConfinNessuno = True
    blnConfinStaffe = False
    blnConfinFRP = False
    blnConfinCamicieAcc = False
End If
'1.2 GEOMETRIA SEZIONE
'1.2.1 dimensioni sezione e dati armature
If FormSez = "Rettangolare" Or FormSez = "a T" Or FormSez = "a T rovescia" Or FormSez = "a doppio T" Or FormSez = "Scatolare" Then
    If Foglio2.Cells(9, 1) = "" Then B = 0 Else B = Foglio2.Cells(9, 1) * fmL
    If Foglio2.Cells(10, 1) = "" Then H = 0 Else H = Foglio2.Cells(10, 1) * fmL
    If Foglio2.Cells(16, 1) = "" Then Cf = 0 Else Cf = Foglio2.Cells(16, 1) * fmL
    If FormSez = "a T" Or FormSez = "a T rovescia" Or FormSez = "a doppio T" Then
        If Foglio2.Cells(14, 11) = "" Then Bo = 0 Else Bo = Foglio2.Cells(14, 11) * fmL
        If Foglio2.Cells(15, 11) = "" Then S = 0 Else S = Foglio2.Cells(15, 11) * fmL
    ElseIf FormSez = "Scatolare" Then
        If Foglio2.Cells(15, 11) = "" Then S = 0 Else S = Foglio2.Cells(15, 11) * fmL
    End If
    Armat2Lembi = Foglio2.Cells(23, 1)
    If Armat2Lembi Then
        If Foglio2.Cells(12, 1) = "" Then dsup = 0 Else dsup = Foglio2.Cells(12, 1) * fmDiamTond
        If Foglio2.Cells(14, 1) = "" Then dinf = 0 Else dinf = Foglio2.Cells(14, 1) * fmDiamTond
        If Foglio2.Cells(13, 1) = "" Then Nbs = 0 Else Nbs = Foglio2.Cells(13, 1)
        If Foglio2.Cells(15, 1) = "" Then Nbi = 0 Else Nbi = Foglio2.Cells(15, 1)
        Delta = Cf + Application.Max(dsup, dinf) / 2
    End If
ElseIf FormSez = "Circolare piena o cava" Then
    If Foglio2.Cells(9, 11) = "" Then D = 0 Else D = Foglio2.Cells(9, 11) * fmL
    If Foglio2.Cells(12, 11) = "" Then Di = 0 Else Di = Foglio2.Cells(12, 11) * fmL
    If Foglio2.Cells(10, 11) = "" Then Df = 0 Else Df = Foglio2.Cells(10, 11) * fmDiamTond
    If Foglio2.Cells(16, 1) = "" Then Cf = 0 Else Cf = Foglio2.Cells(16, 1) * fmL
    H = D
    B = D
    Delta = Cf + Df / 2
    Foglio2.Cells(9, 1) = B / fmL
    Foglio2.Cells(10, 1) = H / fmL
End If
'Per far calcolare le coordinate vertici sezione e scaricarle in Fg2 quando l'utente cambia forma sezione in Dati Gen senza
'premere il tasto "Salva i dati" in Sezione
'If FormSez = "Rettangolare" Then
'    frmGeomSezRettCA.bttSalvaChiudi_Click 'la sub non deve essere privata
'ElseIf FormSez = "a T" Then
'    frmGeomSezT.bttSalvaChiudi_Click
'ElseIf FormSez = "a T rovescia" Then
'    frmGeomSezTrovescia.bttSalvaChiudi_Click
'ElseIf FormSez = "a doppio T" Then
'    frmGeomSezDoppioT.bttSalvaChiudi_Click
'ElseIf FormSez = "Scatolare" Then
'    frmGeomSezScat.bttSalvaChiudi_Click
'ElseIf FormSez = "Circolare piena o cava" Then
'    frmGeomSezCircCA.bttSalvaChiudi_Click
'End If
'Npacch, n. complessivo di barre presenti e dimensionamento vettori ccordinate e diametri barr
If CalcVerif Then
    If Foglio2.Cells(3, 42) = "" Then Npacch = 0 Else Npacch = Foglio2.Cells(3, 42)
    If FormSez <> "Circolare piena o cava" Then
        Nbar = 0
        For j = 1 To Npacch Step 1
            If Foglio2.Cells(4 + j, 42) <> "" Then Nbar = Nbar + Foglio2.Cells(4 + j, 42)
        Next j
    Else
        Nbar = Foglio2.Cells(11, 11)
    End If
Else
    Npacch = 0
    Nbar = 0
End If
If Nbar > 0 Then
    ReDim Yb_pr#(1 To Nbar), Zb_pr#(1 To Nbar), Db#(1 To Nbar)
End If
'determina coordinate barre di armatura e Nbar
CoordBaricentriTondini '1.1
'1.2.2 composito FRP, rinforzo a flessione e taglio
If RinfFRP Then
    If Foglio2.Cells(87, 1) = "" Then H_frp = 0 Else H_frp = Foglio2.Cells(87, 1) * fmL
    If Foglio2.Cells(88, 1) = "" Then B_frp = 0 Else B_frp = Foglio2.Cells(88, 1) * fmL
    If Foglio2.Cells(91, 1) = "" Then t_f = 0 Else t_f = Foglio2.Cells(91, 1) * fmL
    If Foglio2.Cells(92, 1) = "" Then B_f = 0 Else B_f = Foglio2.Cells(92, 1) * fmL
    If Foglio2.Cells(93, 1) = "" Then p_f = 0 Else p_f = Foglio2.Cells(93, 1) * fmL
    If Foglio2.Cells(94, 1) = "" Then Alfa_ta_frp = 0 Else Alfa_ta_frp = Foglio2.Cells(94, 1) * PiGreco / 180
    DisposizFRP = Foglio2.Cells(95, 1)
    ContinuitàFRP = Foglio2.Cells(98, 1)
    If Foglio2.Cells(96, 1) = "" Then Perc_H = 0 Else Perc_H = Foglio2.Cells(96, 1) / 100
    If Foglio2.Cells(97, 1) = "" Then rc = 0 Else rc = Foglio2.Cells(97, 1) * fmL
End If
'1.2.3 confinamento con compositi FRP
If blnConfinFRP Then
    TipoConfinFRP = Foglio2.Cells(105, 1)
    If Foglio2.Cells(101, 1) = "" Then tf_ = 0 Else tf_ = Foglio2.Cells(101, 1) * fmL
    If Foglio2.Cells(102, 1) = "" Then Bf_ = 0 Else Bf_ = Foglio2.Cells(102, 1) * fmL
    If TipoConfinFRP = "continuo" Then
        pf_ = Bf_
    ElseIf TipoConfinFRP = "discontinuo" Then
        If Foglio2.Cells(103, 1) = "" Then pf_ = 0 Else pf_ = Foglio2.Cells(103, 1) * fmL
    End If
    If Foglio2.Cells(104, 1) = "" Then Alfa_fib = 0 Else Alfa_fib = Foglio2.Cells(104, 1) * PiGreco / 180
    If Foglio2.Cells(106, 1) = "" Then rc_ = 0 Else rc_ = Foglio2.Cells(106, 1) * fmL
End If
'1.2.4 Confinamento e Rinforzo a taglio con calastrelli in acciaio
'If RinfCamicieAcc Then
    'TipoConfinCamicieAcc = Foglio2.Cells(105, 10)
    'If Foglio2.Cells(101, 10) = "" Then tj = 0 Else tj = Foglio2.Cells(101, 10) * fmL
    'If Foglio2.Cells(102, 10) = "" Then Bj = 0 Else Bj = Foglio2.Cells(102, 10) * fmL
    'If TipoConfinCamicieAcc = "continuo" Then
        'pj = Bj
    'ElseIf TipoConfinCamicieAcc = "discontinuo" Then
        'If Foglio2.Cells(103, 10) = "" Then pj = 0 Else pj = Foglio2.Cells(103, 10) * fmL
    'End If
'End If
'1.2.5 confinamento con calastrelli in acciaio
If RinfCamicieAcc Or blnConfinCamicieAcc Then
    TipoConfinCamicieAcc2 = Foglio2.Cells(105, 5)
    If Foglio2.Cells(101, 5) = "" Then tf_ = 0 Else tf_ = Foglio2.Cells(101, 5) * fmL
    If Foglio2.Cells(102, 5) = "" Then Bf_ = 0 Else Bf_ = Foglio2.Cells(102, 5) * fmL
    If TipoConfinCamicieAcc2 = "continuo" Then
        pf_ = Bf_
    ElseIf TipoConfinCamicieAcc2 = "discontinuo" Then
        If Foglio2.Cells(103, 5) = "" Then pf_ = 0 Else pf_ = Foglio2.Cells(103, 5) * fmL
    End If
    If Foglio2.Cells(106, 5) = "" Then rc_ = 0 Else rc_ = Foglio2.Cells(106, 5) * fmL
End If
'1.3 MATERIALI
'1.3.1. cls e acciaio
If Foglio2.Cells(19, 1) = "" Then Rck = 0 Else Rck = Foglio2.Cells(19, 1) * fmFL_2
TipoAcciaioCA = Foglio2.Cells(18, 1)
If Foglio2.Cells(9, 8) = "" Then Ec = 0 Else Ec = Foglio2.Cells(9, 8) * fmFL_2
If Foglio2.Cells(62, 1) = "" Then Es = 0 Else Es = Foglio2.Cells(62, 1) * fmFL_2
If Foglio2.Cells(23, 8) = "" Then n = 0 Else n = Foglio2.Cells(23, 8)
If Foglio2.Cells(10, 8) = "" Then Sigca = 0 Else Sigca = Foglio2.Cells(10, 8) * fmFL_2
If Foglio2.Cells(13, 8) = "" Then Sigfa = 0 Else Sigfa = Foglio2.Cells(13, 8) * fmFL_2
If Foglio2.Cells(14, 8) = "" Then Sigfac = 0 Else Sigfac = Foglio2.Cells(14, 8) * fmFL_2
If Foglio2.Cells(11, 8) = "" Then TauC0 = 0 Else TauC0 = Foglio2.Cells(11, 8) * fmFL_2
If Foglio2.Cells(12, 8) = "" Then TauC1 = 0 Else TauC1 = Foglio2.Cells(12, 8) * fmFL_2
blnParabRettang = Foglio2.Cells(65, 1)
blnTriangRettang = Foglio2.Cells(67, 1)
blnStressBlock = Foglio2.Cells(66, 1)
If Foglio2.Cells(60, 1) = "" Then Gammac = 0 Else Gammac = Foglio2.Cells(60, 1)
If Foglio2.Cells(61, 1) = "" Then Gammas = 0 Else Gammas = Foglio2.Cells(61, 1)
If Foglio2.Cells(64, 1) = "" Then Eps_c2 = 0 Else Eps_c2 = Foglio2.Cells(64, 1) / 100
If Foglio2.Cells(63, 3) = "" Then Eps_c3 = 0 Else Eps_c3 = Foglio2.Cells(63, 3) / 100
If Foglio2.Cells(64, 3) = "" Then Eps_c4 = 0 Else Eps_c4 = Foglio2.Cells(64, 3) / 100
If Foglio2.Cells(63, 1) = "" Then Eps_cu = 0 Else Eps_cu = Foglio2.Cells(63, 1) / 100
If Foglio2.Cells(15, 8) = "" Then fcm = 0 Else fcm = Foglio2.Cells(15, 8) * fmFL_2
If Foglio2.Cells(16, 8) = "" Then fck = 0 Else fck = Foglio2.Cells(16, 8) * fmFL_2
If Foglio2.Cells(17, 8) = "" Then fcd = 0 Else fcd = Foglio2.Cells(17, 8) * fmFL_2
If Foglio2.Cells(18, 8) = "" Then fctm = 0 Else fctm = Foglio2.Cells(18, 8) * fmFL_2
If Foglio2.Cells(19, 8) = "" Then fctk = 0 Else fctk = Foglio2.Cells(19, 8) * fmFL_2
If Foglio2.Cells(20, 8) = "" Then fctd = 0 Else fctd = Foglio2.Cells(20, 8) * fmFL_2
blnElastPerfettPlastico = Foglio2.Cells(24, 8)
blnBilineare = Foglio2.Cells(25, 8)
If Foglio2.Cells(26, 8) = "" Then Eps_su = 0 Else Eps_su = Foglio2.Cells(26, 8) / 100
If Foglio2.Cells(27, 8) = "" Then Kincr = 0 Else Kincr = Foglio2.Cells(27, 8)
If Foglio2.Cells(21, 8) = "" Then fyk = 0 Else fyk = Foglio2.Cells(21, 8) * fmFL_2
If Foglio2.Cells(22, 8) = "" Then fyd = 0 Else fyd = Foglio2.Cells(22, 8) * fmFL_2
If Es > 0 Then Eps_yd = fyd / Es
Sigcar = f_Sigcar
'ipotesi di cls resistente a trazione o non
If CemArmOrd Then
    ClsResistTraz = False
ElseIf CemCAP Then 'è cemento armato precompresso
    ClsResistTraz = True
    If Foglio2.Cells(29, 8) = "" Then fyk2 = 0 Else fyk2 = Foglio2.Cells(29, 8) * fmFL_2
End If
'1.3.2. acciaio esistente
If RinfCamicieCA Then
    If Foglio2.Cells(72, 10) = "" Then Gammas_e = 0 Else Gammas_e = Foglio2.Cells(72, 10)
    If Foglio2.Cells(73, 10) = "" Then FC = 0 Else FC = Foglio2.Cells(73, 10)
    If Foglio2.Cells(74, 10) = "" Then fym = 0 Else fym = Foglio2.Cells(74, 10) * fmFL_2
    If Foglio2.Cells(75, 10) = "" Then fyd_e = 0 Else fyd_e = Foglio2.Cells(75, 10) * fmFL_2
    If Es > 0 Then Eps_yd_e = fyd_e / Es
End If
'1.3.3 Calcestruzzo fibrorinforzato FRC
If CemFRC Then
    blnLineareIncrud = Foglio2.Cells(76, 1)
    blnLineareDegrad = Foglio2.Cells(77, 1)
    blnRigidoPlastico = Foglio2.Cells(78, 1)
    If Foglio2.Cells(72, 1) = "" Then Eps_Fs = 0 Else Eps_Fs = Foglio2.Cells(72, 1) / 100
    If Foglio2.Cells(73, 1) = "" Then Eps_Fu = 0 Else Eps_Fu = Foglio2.Cells(73, 1) / 100
    If Foglio2.Cells(74, 1) = "" Then fFts = 0 Else fFts = Foglio2.Cells(74, 1) * fmFL_2
    If Foglio2.Cells(75, 1) = "" Then fFtu = 0 Else fFtu = Foglio2.Cells(75, 1) * fmFL_2
    If blnRigidoPlastico Then
        Eps_Fs = 0
        fFts = fFtu
    End If
End If
'1.3.4 Composito FRP
If RinfFRP Or blnConfinFRP Then
    RigidezzaFRP = Foglio2.Cells(83, 5)
    TipoFRP = Foglio2.Cells(82, 5)
    If Foglio2.Cells(83, 1) = "" Then E_frp = 0 Else E_frp = Foglio2.Cells(83, 1) * fmFL_2
    If Foglio2.Cells(84, 5) = "" Then fpk = 0 Else fpk = Foglio2.Cells(84, 5) * fmFL_2
    If Foglio2.Cells(86, 5) = "" Then Gammaf = 0 Else Gammaf = Foglio2.Cells(86, 5)
    If Foglio2.Cells(87, 5) = "" Then Gammaf_dist = 0 Else Gammaf_dist = Foglio2.Cells(87, 5)
    If Foglio2.Cells(89, 5) = "" Then Eta_a = 0 Else Eta_a = Foglio2.Cells(89, 5)
    If Foglio2.Cells(90, 5) = "" Then Eta1 = 0 Else Eta1 = Foglio2.Cells(90, 5)
    If Foglio2.Cells(91, 5) = "" Then FC = 0 Else FC = Foglio2.Cells(91, 5)
    If Foglio2.Cells(85, 5) = "" Then fpd = 0 Else fpd = Foglio2.Cells(85, 5) * fmFL_2
    If Foglio2.Cells(88, 5) = "" Then fpd_sle = 0 Else fpd_sle = Foglio2.Cells(88, 5) * fmFL_2
    If Foglio2.Cells(93, 5) = "" Then Eps_pk = 0 Else Eps_pk = Foglio2.Cells(93, 5) / 100
    If Foglio2.Cells(84, 1) = "" Then Eps_pu = 0 Else Eps_pu = Foglio2.Cells(84, 1) / 100
    If Foglio2.Cells(85, 1) = "" Then Eps0f = 0 Else Eps0f = Foglio2.Cells(85, 1) / 100
End If
'1.3.5 Acciaio angolari e calastrelli
If RinfCamicieAcc Or blnConfinCamicieAcc Then
    TipoAcciaio = Foglio2.Cells(72, 5)
    If Foglio2.Cells(73, 5) = "" Then Es_a = 0 Else Es_a = Foglio2.Cells(73, 5) * fmFL_2
    If Foglio2.Cells(74, 5) = "" Then ftk_a = 0 Else ftk_a = Foglio2.Cells(74, 5) * fmFL_2
    If Foglio2.Cells(75, 5) = "" Then fyk_a = 0 Else fyk_a = Foglio2.Cells(75, 5) * fmFL_2
    If Foglio2.Cells(76, 5) = "" Then Gammas_a = 0 Else Gammas_a = Foglio2.Cells(76, 5)
    If Foglio2.Cells(77, 5) = "" Then fyd_a = 0 Else fyd_a = Foglio2.Cells(77, 5) * fmFL_2
End If
'1.4 SOLLECITAZIONI
'1.4.1 Per verifiche di resistenza allo SLU
If Foglio2.Cells(31, 1) = "" Then Nx = 0 Else Nx = Foglio2.Cells(31, 1) * fmF
If Foglio2.Cells(32, 1) = "" Then Tz = 0 Else Tz = Foglio2.Cells(32, 1) * fmF
If Foglio2.Cells(11, 1) = "" Then My = 0 Else My = Foglio2.Cells(11, 1) * fmFL
If SollecPiane Then
    Ty = 0
    Mx = 0
    Mz = 0
Else
    If Foglio2.Cells(27, 1) = "" Then Ty = 0 Else Ty = Foglio2.Cells(27, 1) * fmF
    If Foglio2.Cells(30, 1) = "" Then Mx = 0 Else Mx = Foglio2.Cells(30, 1) * fmFL
    If Foglio2.Cells(17, 1) = "" Then Mz = 0 Else Mz = Foglio2.Cells(17, 1) * fmFL
End If
Ned = Nx
Ted = Tz
Med = My
'1.4.2 Per verifiche allo SLE
'vengono caricate nel relativo modulo
'1.5 STABILITA' ASTA
If Foglio2.Cells(51, 1) = "" Then Nr = 0 Else Nr = Foglio2.Cells(51, 1) * fmF
If Foglio2.Cells(52, 1) = "" Then Mr = 0 Else Mr = Foglio2.Cells(52, 1) * fmFL
If MetodoSL08 Then
    If Foglio2.Cells(51, 3) = "" Then Mi = 0 Else Mi = Foglio2.Cells(51, 3) * fmFL
    If Foglio2.Cells(52, 3) = "" Then Mk = 0 Else Mk = Foglio2.Cells(52, 3) * fmFL
End If
If Foglio2.Cells(39, 1) = "" Then L = 0 Else L = Foglio2.Cells(39, 1) * fmL
If Foglio2.Cells(47, 1) = "" Then Beta_y = 0 Else Beta_y = Foglio2.Cells(47, 1)
If Foglio2.Cells(48, 1) = "" Then Beta_z = 0 Else Beta_z = Foglio2.Cells(48, 1)
'1.6 ALTRI DATI
'dati per il progetto armature a flessione
ZonaSismStruttDissip = Foglio2.Cells(9, 14)
blnCDA = Foglio2.Cells(11, 14)
If Foglio2.Cells(35, 1) = "" Then dfp = 0 Else dfp = Foglio2.Cells(35, 1) * fmDiamTond
If Foglio2.Cells(34, 1) = "" Then Pmax = 0 Else Pmax = Foglio2.Cells(34, 1) * fmL
If Foglio2.Cells(40, 1) = "" Then sLmin = 0 Else sLmin = Foglio2.Cells(40, 1) * fmL
If Foglio2.Cells(41, 1) = "" Then Mu_ = 0 Else Mu_ = Foglio2.Cells(41, 1)
'armatura a taglio
If Foglio2.Cells(16, 14) = "" Then Alfa_ta = 0 Else Alfa_ta = Foglio2.Cells(16, 14) * PiGreco / 180
If Foglio2.Cells(13, 14) = "" Then Teta_ta = 0 Else Teta_ta = Foglio2.Cells(13, 14) * PiGreco / 180
If Foglio2.Cells(14, 14) = "" Then Dst_ta = 0 Else Dst_ta = Foglio2.Cells(14, 14) * fmDiamTond
If Foglio2.Cells(15, 14) = "" Then Pst_ta = 0 Else Pst_ta = Foglio2.Cells(15, 14) * fmL
If Foglio2.Cells(17, 14) = "" Then Nbrz = 0 Else Nbrz = Foglio2.Cells(17, 14)
If Foglio2.Cells(18, 14) = "" Then Nbry = 0 Else Nbry = Foglio2.Cells(18, 14)
StaffeCircSingole = Foglio2.Cells(17, 18)
StaffeSpirale = Foglio2.Cells(18, 18)
Asw_ta = PiGreco * Dst_ta ^ 2 / 4
Asw_tay = Nbry * Asw_ta
Asw_taz = Nbrz * Asw_ta
'armatura a torsione
If Foglio2.Cells(20, 14) = "" Then Al_to = 0 Else Al_to = Foglio2.Cells(20, 14) * fmL2
If Foglio2.Cells(23, 14) = "" Then Alfa_to = 0 Else Alfa_to = Foglio2.Cells(23, 14) * PiGreco / 180
If Foglio2.Cells(21, 14) = "" Then Dst_to = 0 Else Dst_to = Foglio2.Cells(21, 14) * fmDiamTond
If Foglio2.Cells(22, 14) = "" Then Pst_to = 0 Else Pst_to = Foglio2.Cells(22, 14) * fmL
Teta_to = 45 * PiGreco / 180
Asw_to = 2 * PiGreco * Dst_to ^ 2 / 4 'staffe a 2 braccia per la torsione
'deformazione iniziale Eps0 (%) dovuta alla pretensione delle armature
If CemCAP Then
    If Foglio2.Cells(42, 1) = "" Then Eps0 = 0 Else Eps0 = Foglio2.Cells(42, 1) / 100
End If
'1.7 VERIFICHE SLE
CondizAmb = Foglio2.Cells(37, 6)
SensibArmat = Foglio2.Cells(38, 6)
If Foglio2.Cells(39, 6) = "" Then Perc_cls_c = 0 Else Perc_cls_c = Foglio2.Cells(39, 6)
If Foglio2.Cells(40, 6) = "" Then Perc_cls_qp = 0 Else Perc_cls_qp = Foglio2.Cells(40, 6)
If Foglio2.Cells(41, 6) = "" Then Perc_acc_c = 0 Else Perc_acc_c = Foglio2.Cells(41, 6)
blnCarichiBrevi = Foglio2.Cells(42, 6)
MetodoFess1996 = Foglio2.Cells(44, 6)
MetodoFess2008 = Foglio2.Cells(45, 6)
If Foglio2.Cells(46, 6) = "" Then KK = 0 Else KK = Foglio2.Cells(46, 6)
'1.8 Armatura in zona tesa Af e in zona compressa A1f
If CalcVerif Then
    If Armat2Lembi Then
        Asup = (Nbs * PiGreco * dsup ^ 2 / 4)
        Ainf = (Nbi * PiGreco * dinf ^ 2 / 4)
    Else
        Asup = Aft / 2 'form. approssimate
        Ainf = Aft / 2 'form. approssimate
    End If
    If My >= 0 Then
        A1f = Asup
        Af = Ainf
    Else
        A1f = Ainf
        Af = Asup
    End If
End If
'2)CONTROLLO DATI
iF1 = 5 'riga da cui cominciano gli output
ControlloDati
'3) OUTPUT INPUT
OutInput
'4 e 5) VERIF DI RESISTENZA ALLE TENS. NORMALI O CALCOLO DI PROGETTO A SFORZO NORMALE ECCENTRICO
If CalcVerif Then
    DatiSezioneCA '4.1
    OutDatiSezioneCA '4.2
    If MetodoTA Then
        CalcoloTensNormali Nx, My, Mz, True '4.3
        OutCalcoloTensNormali '4.4
        VerifResistCA_TA '4.5
    ElseIf MetodoSL08 Or MetodoSL18 Then
        If MetodoSL18 Then
            If blnConfinStaffe Then
                ClsConfinatoStaffe '4.6
            ElseIf blnConfinFRP Then
                ClsConfinatoFRP '4.11
            ElseIf blnConfinCamicieAcc Then
                ClsConfinatoCalastr '4.12
            End If
            If RinfFRP Then VerificheSLUdistaccoDalSupporto '4.10
        End If
        VerifResistCA_SLU_TensNorm '4.7
        CalcoloTensNormali Nx, My, Mz, False '4.3
        OutCalcoloTensNormali '4.4
        If MetodoSL18 And blnVerifDuttilità Then
            CostruzioneDiagrMomentiCurvatura '4.8
        End If
    End If
    LimitiArmaturaLong '4.9  per verifica che vengano rispettati
Else
    ProgCA '5  calcolo di progetto delle armature a flessione
End If
'6) VERIFICA/PROGETTO A TAGLIO
Taglio 'calcolo di verifica o di progetto delle armature a taglio
'7) VERIFICA/PROGETTO A TORSIONE
Torsione 'calcolo di verifica o di progetto delle armature a torsione
'8) VERIFICA DI STABILITA' ASTA
If Pilastro And blnVerifCarPunta Then
    VerifStabilitàAstaCA
End If
'9) VERIFICHE SLE CON NTC
If MetodoTA = False And blnVerifSLE Then
    VerificheSLE
End If
'10) OUTPUT FINALE
With Foglio1
    .Activate
    .Cells(iF1 + 1, 6) = "Il Tecnico"
    .Cells(iF1 + 2, 6).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1 + 2, 6) = Foglio2.Cells(16, 4)
    iF1 = iF1 + 3
    .Range("A5:A" & iF1).Rows.AutoFit 'adatta altezza righe
End With
Time2 = Time
MsgBox "Tempo di esecuzione calcoli (hh:mm:ss)=" & CDate(Time2 - Time1), vbInformation, VersioneSw
End Sub

Sub CoordBaricentriTondini() '1.1
'calcola le coordinate dei baricentri dei tondini rispetto al sistema di riferimento utente y'z'
Dim Alfaf#, Alfa#
Dim dtond#
Dim Ntond As Byte, Nf%
Dim i%, j%, k%
Dim Rf#
Dim y_in#, z_in#, y_fi#, z_fi#
'ESECUZ
If Nbar > 0 Then
    ReDim Yb_pr#(1 To Nbar)
    ReDim Zb_pr#(1 To Nbar)
    ReDim Db#(1 To Nbar)
    ReDim TondArmonico(1 To Nbar) As Boolean
    ReDim TondNuovo(1 To Nbar) As Boolean
End If
If FormSez = "Circolare piena o cava" Then
    Rf = D / 2 - Cf - Df / 2
    If Nbar > 0 Then Alfaf = 2 * PiGreco / Nbar
    For i = 1 To Nbar Step 1
        Alfa = Alfaf * (i - 1)
        Yb_pr(i) = Rf * Sin(Alfa)
        Zb_pr(i) = Rf * Cos(Alfa)
        Db(i) = Df
        TondNuovo(i) = True
    Next i
Else
    k = 0
    For j = 1 To Npacch Step 1
        If Foglio2.Cells(4 + j, 38) = "" Then y_in = 0 Else y_in = Foglio2.Cells(4 + j, 38) * fmL
        If Foglio2.Cells(4 + j, 39) = "" Then z_in = 0 Else z_in = Foglio2.Cells(4 + j, 39) * fmL
        If Foglio2.Cells(4 + j, 40) = "" Then y_fi = 0 Else y_fi = Foglio2.Cells(4 + j, 40) * fmL
        If Foglio2.Cells(4 + j, 41) = "" Then z_fi = 0 Else z_fi = Foglio2.Cells(4 + j, 41) * fmL
        If Foglio2.Cells(4 + j, 42) = "" Then Ntond = 0 Else Ntond = Foglio2.Cells(4 + j, 42)
        If Foglio2.Cells(4 + j, 43) = "" Then dtond = 0 Else dtond = Foglio2.Cells(4 + j, 43) * fmDiamTond
        '1° tondino del pacchetto
        If Ntond > 0 Then
            k = k + 1
            Yb_pr(k) = y_in
            Zb_pr(k) = z_in
            Db(k) = dtond
            If Foglio2.Cells(4 + j, 44) = "Si" Then TondArmonico(k) = True Else TondArmonico(k) = False
            If Foglio2.Cells(4 + j, 36) = "Si" Then TondNuovo(k) = True Else TondNuovo(k) = False
        End If
        'dal 2° all'altimo tondino
        For i = 2 To Ntond Step 1
            k = k + 1
            Yb_pr(k) = y_in + (i - 1) / (Ntond - 1) * (y_fi - y_in)
            Zb_pr(k) = z_in + (i - 1) / (Ntond - 1) * (z_fi - z_in)
            Db(k) = dtond
            If Foglio2.Cells(4 + j, 44) = "Si" Then TondArmonico(k) = True Else TondArmonico(k) = False
            If Foglio2.Cells(4 + j, 36) = "Si" Then TondNuovo(k) = True Else TondNuovo(k) = False
        Next i
    Next j
End If
'OUTPUT su Fg2
With Foglio2
    .Cells(3, 47) = Nbar
    For i = 1 To Nbar Step 1
        .Cells(4 + i, 46) = Yb_pr(i) / fmL
        .Cells(4 + i, 47) = Zb_pr(i) / fmL
        .Cells(4 + i, 48) = Db(i) / fmDiamTond
        .Cells(4 + i, 49) = TondArmonico(i)
        .Cells(4 + i, 50) = TondNuovo(i)
    Next i
End With
End Sub

Sub CaricaDaFg2CoordPolig(j%) '1.2
Np = Foglio2.Cells(4, 22 + 2 * j)
If Np > 0 Then
    ReDim Ys_pr#(1 To Np)
    ReDim Zs_pr#(1 To Np)
End If
For i = 1 To Np Step 1
    Ys_pr(i) = Foglio2.Cells(5 + i, 21 + 2 * j) * fmL
    Zs_pr(i) = Foglio2.Cells(5 + i, 22 + 2 * j) * fmL
Next i
End Sub

Sub DatiSezioneCA() '4.1
'Di una sezione in C.A., anche cava, di cui si conoscono nel sistema di riferimento utente y'z' le coordinate dei vertici della sezione
'e dei baricentri dei tondini, calcola l'area, i momenti statici e di inerzia rispetto al sistema di riferimento y'z' e le stesse
'grandezze rispetto al sistema di riferimento yz, parallelo a y'z' e passante per il baricentro G della sezione omogeneizzata
Dim A#, Alfa#, Afi#
Dim dd#
Dim i%, i1%, j%
Dim Ymin#, Zmax#, Ymax#, Zmin#
Dim Wy_sup#, Wy_inf#, Wz_dx#, Wz_sx#
'ESECUZ
'1 calcolo area e perimetro sezione, momenti statici e d'inerzia rispetto agli assi y'z'
Asez = 0
Psez = 0
Sy_pr = 0
Sz_pr = 0
Iy_pr = 0
Iz_pr = 0
Iyz_pr = 0
Ymin_pr = 0
Ymax_pr = 0
Zmin_pr = 0
Zmax_pr = 0
For j = 1 To Npolig Step 1
    'carica coordinate poligonale j
    CaricaDaFg2CoordPolig j '1.2
    'contributo poligonale j
    For i = 1 To Np Step 1
        If i = Np Then
            i1 = 1
        Else
            i1 = i + 1
        End If
        A = Ys_pr(i1) - Ys_pr(i)
        dd = Zs_pr(i1) - Zs_pr(i)
        Asez = Asez + A * (Zs_pr(i) + dd / 2)
        Psez = Psez + (A ^ 2 + dd ^ 2) ^ 0.5
        Sy_pr = Sy_pr + A * Zs_pr(i) * Zs_pr(i) / 2 + A * dd / 2 * (Zs_pr(i) + dd / 3)
        Sz_pr = Sz_pr - dd * Ys_pr(i) * Ys_pr(i) / 2 - dd * A / 2 * (Ys_pr(i) + A / 3)
        Iy_pr = Iy_pr + A * Zs_pr(i) ^ 3 / 3 + A * dd ^ 3 / 36 + A * dd / 2 * (Zs_pr(i) + dd / 3) ^ 2
        Iz_pr = Iz_pr - dd * Ys_pr(i) ^ 3 / 3 - dd * A ^ 3 / 36 - dd * A / 2 * (Ys_pr(i) + A / 3) ^ 2
        Iyz_pr = Iyz_pr + A * (Ys_pr(i) / 2 * (Zs_pr(i) ^ 2 + dd ^ 2 / 3 + dd * Zs_pr(i)) + A / 2 * (Zs_pr(i) ^ 2 / 2 + dd ^ 2 / 4 + 2 * dd * Zs_pr(i) / 3))
    Next i
    If Np > 0 Then
        Ymin = Application.Min(Ys_pr())
        Ymax = Application.Max(Ys_pr())
        Zmin = Application.Min(Zs_pr())
        Zmax = Application.Max(Zs_pr())
    End If
    If Ymin < Ymin_pr Then Ymin_pr = Ymin
    If Ymax > Ymax_pr Then Ymax_pr = Ymax
    If Zmin < Zmin_pr Then Zmin_pr = Zmin
    If Zmax > Zmax_pr Then Zmax_pr = Zmax
Next j
If FormSez = "Generica" Then
    B = Ymax_pr - Ymin_pr
    H = Zmax_pr - Zmin_pr
    Foglio2.Cells(9, 1) = B / fmL
    Foglio2.Cells(10, 1) = H / fmL
End If
If Asez < 0 Then
    MsgBox "Occorre inserire i vertici della sezione in senso orario (SEZIONE). Il calcolo verrà arrestato.", vbCritical, VersioneSw
    End
ElseIf Asez = 0 Then
    MsgBox "La sezione ha area nulla. Il calcolo verrà arrestato.", vbCritical, VersioneSw
    End
End If
'2 contributo delle armature metalliche
Aft = 0
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    Aft = Aft + Afi
    Sy_pr = Sy_pr + n * Afi * Zb_pr(i)
    Sz_pr = Sz_pr + n * Afi * Yb_pr(i)
    Iy_pr = Iy_pr + n * Afi * Zb_pr(i) ^ 2
    Iz_pr = Iz_pr + n * Afi * Yb_pr(i) ^ 2
    Iyz_pr = Iyz_pr + n * Afi * Zb_pr(i) * Yb_pr(i)
Next i
Ac = Asez
Aci = Ac + n * Aft
'3 calcolo coordinate baricentro G sezione omogeneizzata rispetto al sistema y'z'
yG_pr = Sz_pr / Aci
zG_pr = Sy_pr / Aci
'4 calcolo momenti di inerzia sez. omog. rispetto agli assi yz passanti per il baricentro G e paralleli a y'z'
Iy = Iy_pr - Aci * zG_pr ^ 2
Iz = Iz_pr - Aci * yG_pr ^ 2
Iyz = Iyz_pr - Aci * yG_pr * zG_pr
'5 calcolo momenti principali di inerzia e raggi giratori di inerzia
If Round(Iy, 2) = Round(Iz, 2) Then
    Alfa = PiGreco / 4
Else
    Alfa = (Atn(-2 * Iyz / (Iy - Iz))) / 2
End If
'Iyp = (Iy + Iz) / 2 - 0.5 * ((Iy - Iz) ^ 2 + 4 * Iyz ^ 2) ^ 0.5
'Izp = (Iy + Iz) / 2 + 0.5 * ((Iy - Iz) ^ 2 + 4 * Iyz ^ 2) ^ 0.5
Iyp = Iy * (Cos(Alfa)) ^ 2 + Iz * (Sin(Alfa)) ^ 2 - 2 * Iyz * Sin(Alfa) * Cos(Alfa)
Izp = Iy * (Sin(Alfa)) ^ 2 + Iz * (Cos(Alfa)) ^ 2 + 2 * Iyz * Sin(Alfa) * Cos(Alfa)
Iyzp = Iyz * Cos(2 * Alfa) + 0.5 * (Iy - Iz) * Sin(2 * Alfa)
ryp = (Iyp / Aci) ^ 0.5
rzp = (Izp / Aci) ^ 0.5
'6 calcolo coordinate dei punti che individuano gli assi principali di inerzia
z1_pr = (Ymin_pr - yG_pr) * Tan(Alfa) + zG_pr
z2_pr = (Ymax_pr - yG_pr) * Tan(Alfa) + zG_pr
y3_pr = (Zmin_pr - zG_pr) * Tan(-Alfa) + yG_pr
y4_pr = (Zmax_pr - zG_pr) * Tan(-Alfa) + yG_pr
'7 calcolo moduli di resistenza sezione rispetto a yz
Wy_sup = Iy / Abs(Zmax_pr - zG_pr)
Wy_inf = Iy / Abs(Zmin_pr - zG_pr)
Wz_dx = Iz / Abs(Ymin_pr - yG_pr)
Wz_sx = Iz / Abs(Ymax_pr - yG_pr)
'8 calcolo coordinate barre rispetto al baricentro G della sezione omogoneizzata
If Nbar > 0 Then
    ReDim Zb#(1 To Nbar)
    ReDim Yb#(1 To Nbar)
End If
For i = 1 To Nbar Step 1
    Zb(i) = Zb_pr(i) - zG_pr
    Yb(i) = Yb_pr(i) - yG_pr
Next i
'calcolo altezza utile sezione
If CalcVerif And Nbar > 0 Then Hu = H - (Cf + Db(Nbar) / 2) Else Hu = H - (Cf + dfp / 2)
End Sub

Sub CalcoloTensNormali(Nx#, My#, Mz#, LegameCostitLineare As Boolean) '4.3
'Per sezioni di forma qualunque in C.A. soggette al caso più generale di presso/tenso flessione deviata, calcola, con il metodo della
'matrice di rigidezza della sezione, le tensioni normali in ogni vertice della sezione (ipotesi di legge sig-eps lineare sui materiali),
'anche nei vertici delle poligonali che racchiudano cavità, e nei tondini di armatura
Dim Eps_fi#
Dim Iteraz%, i%, j%, i1%
Dim MM#(1 To 3, 1 To 3), MM_1#(1 To 3, 1 To 3)
Dim Norma1#, Norma2#
Dim Soll#(1 To 3, 1 To 1)
'1. vettore sollecitazioni
Soll(1, 1) = Nx
Soll(2, 1) = My
Soll(3, 1) = -Mz
'2. PRIMA ITERAZIONE
Iteraz = 1 'sezione tutta compressa e quindi interamente reagente
'Eps(1, 1) = -1
'Eps(2, 1) = 0
'Eps(3, 1) = 0
'riempi matrice sezione MM
CalcoloAreaMomStaticiMomInerziaSezReagente Npolig, 4  '4.3.1   sezione intera (quella originaria non parzializzata)
yG_pr = yGr_pr 'infatti la sezione omogeneizzata coincide in questa prima iterazione con quella reagente
zG_pr = zGr_pr
MM(1, 1) = Aci
MM(1, 2) = Sy
MM(1, 3) = Sz
MM(2, 1) = MM(1, 2)
MM(2, 2) = Iy
MM(2, 3) = Iyz
MM(3, 1) = MM(1, 3)
MM(3, 2) = MM(2, 3)
MM(3, 3) = Iz
'inverti MM
For i = 1 To 3
    For j = 1 To 3
        MM_1(i, j) = Application.Index(Application.MInverse(MM()), i, j)
    Next j
Next i
'calcola vettore deformazione e norma prima iterazione
Eps = Application.MMult(MM_1, Soll)
For i = 1 To 3
    Eps(i, 1) = Eps(i, 1) / Ec
Next i
Norma1 = (Eps(1, 1) ^ 2 + Eps(2, 1) ^ 2 + Eps(3, 1) ^ 2) ^ 0.5
'calcolo tensioni del cls in tutti i vertici della sezione intera originaria
For j = 1 To Npolig Step 1
    CaricaDaFg2CoordPolig j '1.2
    ReDim SigVert#(1 To Np), EpsVert#(1 To Np)
    For i = 1 To Np Step 1
        EpsVert(i) = Eps(1, 1) + Eps(2, 1) * (Zs_pr(i) - zGr_pr) + Eps(3, 1) * (Ys_pr(i) - yGr_pr)
        If LegameCostitLineare Then
            SigVert(i) = Ec * EpsVert(i)
        Else
            SigVert(i) = f_Sigc(EpsVert(i)) '4.3.3
        End If
        Foglio2.Cells(5 + i, 50 + j) = SigVert(i) / fmFL_2
        Foglio2.Cells(5 + i, 55 + j) = EpsVert(i)
    Next i
Next j
'3. CICLO ITERATIVO
Do
    If Iteraz > 1 Then Norma1 = Norma2
    Iteraz = Iteraz + 1
    If Iteraz > 100 Then
        MsgBox "Calcolo tensioni normali nella sezione non convergente. Controllare l'input. Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If ClsResistTraz = False Then
        SezioneParzializzata LegameCostitLineare '4.3.2
        CalcoloAreaMomStaticiMomInerziaSezReagente Foglio2.Cells(106, 26), 107 '4.3.1
        'aggiorna matrice sezione
        MM(1, 1) = Aci
        MM(1, 2) = Sy
        MM(1, 3) = Sz
        MM(2, 1) = MM(1, 2)
        MM(2, 2) = Iy
        MM(2, 3) = Iyz
        MM(3, 1) = MM(1, 3)
        MM(3, 2) = MM(2, 3)
        MM(3, 3) = Iz
        'inverti MM
        For i = 1 To 3
            For j = 1 To 3
                MM_1(i, j) = Application.Index(Application.MInverse(MM()), i, j)
            Next
        Next i
    End If
    'aggiorna vettore sollecitazione
    Soll(2, 1) = My + Nx * (zG_pr - zGr_pr)
    Soll(3, 1) = -(Mz - Nx * (yG_pr - yGr_pr))
    'calcola vettore deformazione
    Eps = Application.MMult(MM_1, Soll)
    For i = 1 To 3
        Eps(i, 1) = Eps(i, 1) / Ec
    Next i
    Norma2 = (Eps(1, 1) ^ 2 + Eps(2, 1) ^ 2 + Eps(3, 1) ^ 2) ^ 0.5
    'calcolo tensioni nel cls in tutti i vertici della sezione intera originaria
    For j = 1 To Npolig Step 1
        CaricaDaFg2CoordPolig j '1.2
        ReDim SigVert#(1 To Np), EpsVert#(1 To Np)
        For i = 1 To Np Step 1
            EpsVert(i) = Eps(1, 1) + Eps(2, 1) * (Zs_pr(i) - zGr_pr) + Eps(3, 1) * (Ys_pr(i) - yGr_pr)
            If LegameCostitLineare Then
                SigVert(i) = Ec * EpsVert(i)
            Else
                SigVert(i) = f_Sigc(EpsVert(i)) '4.3.3
            End If
            Foglio2.Cells(5 + i, 50 + j) = SigVert(i) / fmFL_2
            Foglio2.Cells(5 + i, 55 + j) = EpsVert(i)
        Next i
    Next j
Loop Until Abs(Norma2 - Norma1) <= 0.000000001
'MsgBox "Numero di iterazioni=" & Iteraz
If ClsResistTraz = False Then
    SezioneParzializzata LegameCostitLineare '4.3.2
    CalcoloAreaMomStaticiMomInerziaSezReagente Foglio2.Cells(106, 26), 107 '4.3.1
Else
    CalcoloAreaMomStaticiMomInerziaSezReagente Npolig, 4 '4.3.1   sezione originaria (intera)
End If
'momento di inerzia della sezione reagente rispetto all'asse yr
Iyr = Iy 'serve per il calcolo tensioni tangenziali
'4. RICERCA TENSIONE MASSIMA E MINIMA, CON SEGNO, NEL CLS
Sigc_max = Foglio2.Cells(6, 51) * fmFL_2
Sigc_min = Sigc_max
For j = 1 To Npolig Step 1
    Np = Foglio2.Cells(4, 22 + 2 * j)
    For i = 1 To Np Step 1
        SigVert(i) = Foglio2.Cells(5 + i, 50 + j) * fmFL_2
        If SigVert(i) < Sigc_min Then Sigc_min = SigVert(i)
        If SigVert(i) > Sigc_max Then Sigc_max = SigVert(i)
    Next i
Next j
'4.1)tensione massima di compressione (negativa) e tensione massima di trazione (positiva) nel cls
If Sigc_min <= 0 Then
    Sigc = Sigc_min
Else
    Sigc = 0
End If
If Sigc_max > 0 Then
    Sigc_pos = Sigc_max
Else
    Sigc_pos = 0
End If
'4.2)tensione media di compressione nel cls
If Nx < 0 Then SigMed = Nx / Aci Else SigMed = 0
'5. CALCOLO TENSIONI IN TUTTI I TONDINI E CALCOLO TENSIONE MASSIMA Sigf (di traz posit o compress nega), E MAX DI TRAZIONE Sigf_max
Sigf = 0
Sigf_max = 0
If Nbar > 0 Then
    ReDim Sig_fi#(1 To Nbar)
    For i = 1 To Nbar Step 1
        Eps_fi = Eps(1, 1) + Eps(2, 1) * (Zb_pr(i) - zGr_pr) + Eps(3, 1) * (Yb_pr(i) - yGr_pr)
        If LegameCostitLineare Then
            Sig_fi(i) = n * Ec * Eps_fi
        Else 'elastico-perfett plastico o bilineare con incrudimento
            Sig_fi(i) = f_Sigf(Eps_fi) '4.3.4
        End If
        If Abs(Sig_fi(i)) > Abs(Sigf) Then Sigf = Sig_fi(i)
        If Sig_fi(i) > Sigf_max Then Sigf_max = Sig_fi(i)
    Next i
End If
End Sub

Sub CalcoloAreaMomStaticiMomInerziaSezReagente(Npol As Byte, Nrig%) '4.3.1
Dim A#, dd#, Afi#, Asez#
Dim i%, i1%, j%
Dim Y#(), Z#()
Asez = 0
Sy_pr = 0
Sz_pr = 0
Iy_pr = 0
Iz_pr = 0
Iyz_pr = 0
For j = 1 To Npol Step 1
    'carica coordinate poligonale j
    Np = Foglio2.Cells(Nrig, 22 + 2 * j)
    If Np > 0 Then
        ReDim Y#(1 To Np)
        ReDim Z#(1 To Np)
    End If
    For i = 1 To Np Step 1
        Y(i) = Foglio2.Cells(Nrig + 1 + i, 21 + 2 * j) * fmL
        Z(i) = Foglio2.Cells(Nrig + 1 + i, 22 + 2 * j) * fmL
    Next i
    'contributo poligonali j
    For i = 1 To Np Step 1
        If i = Np Then
            i1 = 1
        Else
            i1 = i + 1
        End If
        A = Y(i1) - Y(i)
        dd = Z(i1) - Z(i)
        Asez = Asez + A * (Z(i) + dd / 2)
        Sy_pr = Sy_pr + A * Z(i) * Z(i) / 2 + A * dd / 2 * (Z(i) + dd / 3)
        Sz_pr = Sz_pr - dd * Y(i) * Y(i) / 2 - dd * A / 2 * (Y(i) + A / 3)
        Iy_pr = Iy_pr + A * Z(i) ^ 3 / 3 + A * dd ^ 3 / 36 + A * dd / 2 * (Z(i) + dd / 3) ^ 2
        Iz_pr = Iz_pr - dd * Y(i) ^ 3 / 3 - dd * A ^ 3 / 36 - dd * A / 2 * (Y(i) + A / 3) ^ 2
        Iyz_pr = Iyz_pr + A * (Y(i) / 2 * (Z(i) ^ 2 + dd ^ 2 / 3 + dd * Z(i)) + A / 2 * (Z(i) ^ 2 / 2 + dd ^ 2 / 4 + 2 * dd * Z(i) / 3))
    Next i
Next j
'contributo delle armature metalliche
Af = 0
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    Af = Af + Afi
    Sy_pr = Sy_pr + n * Afi * Zb_pr(i)
    Sz_pr = Sz_pr + n * Afi * Yb_pr(i)
    Iy_pr = Iy_pr + n * Afi * Zb_pr(i) ^ 2
    Iz_pr = Iz_pr + n * Afi * Yb_pr(i) ^ 2
    Iyz_pr = Iyz_pr + n * Afi * Zb_pr(i) * Yb_pr(i)
Next i
Ac = Asez
Aci = Ac + n * Af
'calcolo coordinate baricentro Gr della sezione reagente rispetto a y'z'
yGr_pr = Sz_pr / Aci
zGr_pr = Sy_pr / Aci
'calcolo momenti di inerzia rispetto agli assi yr,zr passanti per il baricentro Gr della sezione reagente e paralleli agli y',z'
Iy = Iy_pr - Aci * zGr_pr ^ 2
Iz = Iz_pr - Aci * yGr_pr ^ 2
Iyz = Iyz_pr - Aci * yGr_pr * zGr_pr
'calcolo momenti statici rispetto agli assi yr,zr passanti per il baricentro Gr della sezione reagente e paralleli agli y',z'
Sy = Sy_pr - Aci * zGr_pr
Sz = Sz_pr - Aci * yGr_pr
End Sub

Sub SezioneParzializzata(LegameCostitLineare As Boolean) '4.3.2
'costruisce la sezione parzializzata relativa alla generica iterazione sulla base dei segni delle tensioni nei vertici della sezione
'originaria. Il sistema di riferimento è quello y',z'
Dim i%, i1%, j%
Dim Zmin#, Zmax#
'ESECUZ
Zmin = 0
Zmax = 0
Npolig_ns = 0 'ns sta per nuova sezione
For j = 1 To Npolig Step 1
    Np_ns = 0
    'carica coordinate poligonale j
    CaricaDaFg2CoordPolig j '1.2
    ReDim Yns#(1 To 2 * Np), Zns#(1 To 2 * Np)
    'carica tensioni della poligonale j dell'intera sezione
    For i = 1 To Np Step 1
        SigVert(i) = Foglio2.Cells(5 + i, 50 + j) * fmFL_2
    Next i
    'poligonale j
    For i = 1 To Np
        If i = Np Then i1 = 1 Else i1 = i + 1
        If SigVert(i) < 0 And SigVert(i1) < 0 Then 'vertici entrambi compressi
            'entrambi i vertici appartengono alla sezione reagente
            If i = 1 Then
                Np_ns = Np_ns + 1
                Yns(Np_ns) = Ys_pr(i)
                Zns(Np_ns) = Zs_pr(i)
            End If
            If i1 <> 1 Then
                Np_ns = Np_ns + 1
                Yns(Np_ns) = Ys_pr(i1)
                Zns(Np_ns) = Zs_pr(i1)
            End If
        ElseIf SigVert(i) < 0 Then 'SigVert(i1) >= 0
            'il vertice i e un vertice intermedio tra i e i1 appartengono alla sezione reagente
            If i = 1 Then
                Np_ns = Np_ns + 1
                Yns(Np_ns) = Ys_pr(i)
                Zns(Np_ns) = Zs_pr(i)
            End If
            'determina coordinate punto con tens=0
            If LegameCostitLineare Then
                yP = Ys_pr(i) - (Ys_pr(i) - Ys_pr(i1)) * Abs(SigVert(i)) / (Abs(SigVert(i1)) + Abs(SigVert(i)))
                zP = Zs_pr(i) - (Zs_pr(i) - Zs_pr(i1)) * Abs(SigVert(i)) / (Abs(SigVert(i1)) + Abs(SigVert(i)))
            Else
                Call PuntoP(Ys_pr(i), Zs_pr(i), Ys_pr(i1), Zs_pr(i1), SigVert(i), SigVert(i1)) '4.3.2.1
            End If
            Np_ns = Np_ns + 1
            Yns(Np_ns) = yP
            Zns(Np_ns) = zP
        ElseIf SigVert(i1) < 0 Then 'SigVert(i) >= 0
            'il vertice i1 e un vertice intermedio tra i e i1 appartengono alla sezione reagente
            'determina coordinate punto con tens=0
            If LegameCostitLineare Then
                yP = Ys_pr(i) - (Ys_pr(i) - Ys_pr(i1)) * Abs(SigVert(i)) / (Abs(SigVert(i1)) + Abs(SigVert(i)))
                zP = Zs_pr(i) - (Zs_pr(i) - Zs_pr(i1)) * Abs(SigVert(i)) / (Abs(SigVert(i1)) + Abs(SigVert(i)))
            Else
                Call PuntoP(Ys_pr(i), Zs_pr(i), Ys_pr(i1), Zs_pr(i1), SigVert(i), SigVert(i1)) '4.3.2.1
            End If
            Np_ns = Np_ns + 1
            Yns(Np_ns) = yP
            Zns(Np_ns) = zP
            If i1 <> 1 Then
                Np_ns = Np_ns + 1
                Yns(Np_ns) = Ys_pr(i1)
                Zns(Np_ns) = Zs_pr(i1)
            End If
        End If
    Next i
    If Np_ns > 0 Then Npolig_ns = Npolig_ns + 1
    'output coordinate poligonale j della sezione parzializzata
    Foglio2.Cells(107, 22 + 2 * j) = Np_ns
    For i = 1 To Np_ns Step 1
        Foglio2.Cells(108 + i, 21 + 2 * j) = Yns(i) / fmL
        Foglio2.Cells(108 + i, 22 + 2 * j) = Zns(i) / fmL
    Next i
    'aggiornamento Zmin e Zmax
    If j = 1 Then
        Zmin = Zns(1)
        Zmax = Zmin
        For i = 2 To Np_ns Step 1
            If Zns(i) < Zmin Then Zmin = Zns(i)
            If Zns(i) > Zmax Then Zmax = Zns(i)
        Next i
    ElseIf j > 1 Then
        For i = 1 To Np_ns Step 1
            If Zns(i) < Zmin Then Zmin = Zns(i)
            If Zns(i) > Zmax Then Zmax = Zns(i)
        Next i
    End If
Next j
Foglio2.Cells(106, 26) = Npolig_ns
'distanza lunzo z asse neutro da lembo compresso
xx = Zmax - Zmin
End Sub

Sub PuntoP(Yi#, Zi#, Yi1#, Zi1#, Sigi#, Sigi1#) '4.3.2.1
'calcola, con il metodo bisezione, le coordinate punto P (yP,zP) ove la tensione del cls è nulla nel caso di legge non lineare
Dim Cont As Byte
Dim Dab#
Dim Errore#, EpsP#
Dim Siga#, Sigb#, SigP#
Dim Ya#, Yb#
Dim Za#, Zb#
Ya = Yi
Za = Zi
Yb = Yi1
Zb = Zi1
Dab = ((Zb - Za) ^ 2 + (Yb - Ya) ^ 2) ^ 0.5
Errore = Dab / 1000
Siga = Sigi
Sigb = Sigi1
Cont = 1
While Cont <= 100 And Dab >= Errore
    yP = (Ya + Yb) / 2
    zP = (Za + Zb) / 2
    EpsP = Eps(1, 1) + Eps(2, 1) * (zP - zGr_pr) + Eps(3, 1) * (yP - yGr_pr)
    SigP = f_Sigc(EpsP) '4.3.3
    If Siga * SigP <= 0 Then
        Yb = yP
        Zb = zP
        Sigb = SigP
    Else
        Ya = yP
        Za = zP
        Siga = SigP
    End If
    Dab = ((Zb - Za) ^ 2 + (Yb - Ya) ^ 2) ^ 0.5
    Cont = Cont + 1
Wend
End Sub

Function f_Sigc#(Eps#) '4.3.3
'calcola la tensione nel cls (>0 trazione, <0 compressione), nota la deformazione Eps (>0 trazione, <0 compress)
'nelle leggi non lineari
If Eps <= 0 Then 'tensione di compressione
    If blnParabRettang Then
        If Abs(Eps) < Eps_c2 Then
            f_Sigc = fcd * Eps ^ 2 / (Eps_c2 ^ 2) + 2 * fcd * Eps / Eps_c2
        Else
            f_Sigc = -fcd
        End If
    Else
        If Abs(Eps) < Eps_c3 Then
            f_Sigc = fcd * Eps / Eps_c3
        Else
            f_Sigc = -fcd
        End If
    End If
ElseIf Eps > 0 Then 'tensione di trazione
    f_Sigc = Ec * Eps
End If
End Function

Function f_Sigf#(Eps#) '4.3.4
'calcola la tensione nella barra di acciaio (>0 trazione, <0 compressione) nota la sua deformazione Eps (>0 trazione, <0 compress)
'nelle leggi non lineari
If Abs(Eps) < Eps_yd Then
    f_Sigf = Es * Eps
Else
    If blnElastPerfettPlastico Then
        If Eps > 0 Then
            f_Sigf = fyd
        Else
            f_Sigf = -fyd
        End If
    ElseIf blnBilineare Then
        If Eps > 0 Then
            f_Sigf = fyd + (Kincr * fyd - fyd) * (Eps - Eps_yd) / (Eps_su - Eps_yd)
        Else
            f_Sigf = -(fyd + (Kincr * fyd - fyd) * (Eps - Eps_yd) / (Eps_su - Eps_yd))
        End If
    End If
End If
End Function

Sub VerifResistCA_TA() '4.5
If Abs(Sigc) <= Sigca And Abs(Sigf) <= Sigfa And Abs(SigMed) <= Sigcar Then
    VerifResist = True
Else
    VerifResist = False
End If
'OUTPUT
If CalcVerif Then
    With Foglio1
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "VERIFICA DI RESISTENZA DELLA SEZIONE PER TENSIONI NORMALI"
        If VerifResist Then
            .Cells(iF1 + 1, 1) = "Le tensioni normali non superano quelle ammissibili dei materiali: verifica soddisfatta!"
        Else
            .Cells(iF1 + 1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
            .Cells(iF1 + 1, 1) = "Le tensioni normali superano le tensioni ammissibili dei materiali: verifica non soddisfatta!"
        End If
        iF1 = iF1 + 3
    End With
End If
End Sub

Sub ClsConfinatoStaffe() '4.6
'con NTC2018 determina le proprietà del cls confinato con staffe chiuse e legature. Solo per sezioni rettang e circ
Dim Alfa#, Alfan#, Alfas#
Dim By#, Bz#
Dim D0#
Dim i As Byte, i1 As Byte
Dim Sig_l#, Sig_ly#, Sig_lz#, Sig2#, Somm_bi2#
Dim Vst_conf#, Vnucleo_conf#
Dim w_wd#
If FormSez = "Rettangolare" Or FormSez = "Circolare piena o cava" Then
    'calcolo alfa, sig_l, volume staffe di confinamento (in ogni passo), volume nucle cls confinato (in ogni passo)
    If FormSez = "Rettangolare" Then
        By = B - 2 * Cf + Dst_ta
        Bz = H - 2 * Cf + Dst_ta
        Somm_bi2 = 0
        If Nbry = 2 And Nbrz = 2 Then 'solo le 4 barre agli angoli
            Somm_bi2 = 2 * (B - 2 * (Cf + Db(1) / 2)) ^ 2 + 2 * (H - 2 * (Cf + Db(1) / 2)) ^ 2
        ElseIf Nbry < 2 Or Nbrz < 2 Then
            Somm_bi2 = 0
        Else 'tutte le barre
            For i = 1 To Nbar
                If i = Nbar Then i1 = 1 Else i1 = i + 1
                Somm_bi2 = Somm_bi2 + (Yb_pr(i1) - Yb_pr(i)) ^ 2 + (Zb_pr(i1) - Zb_pr(i)) ^ 2
            Next i
        End If
        Alfan = 1 - Somm_bi2 / (6 * By * Bz)
        Alfas = (1 - Pst_ta / (2 * By)) * (1 - Pst_ta / (2 * Bz))
        Sig_ly = Asw_tay * fyk / (Bz * Pst_ta)
        Sig_lz = Asw_taz * fyk / (By * Pst_ta)
        Sig_l = (Sig_ly * Sig_lz) ^ 0.5
        Vst_conf = Asw_tay * By + Asw_taz * Bz
        Vnucleo_conf = By * Bz * Pst_ta
    ElseIf FormSez = "Circolare piena o cava" Then
        D0 = D - 2 * Cf + Dst_ta
        Alfan = 1
        If StaffeCircSingole Then
            Alfas = (1 - Pst_ta / (2 * D0)) ^ 2
            Vst_conf = Asw_ta * (PiGreco * D0)
        Else
            Alfas = (1 - Pst_ta / (2 * D0)) ^ 1
            Vst_conf = Asw_ta * (PiGreco * D0) / 2
        End If
        Sig_l = 2 * Asw_ta * fyk / (D0 * Pst_ta)
        Vnucleo_conf = (PiGreco * D0 ^ 2 / 4) * Pst_ta
    End If
    Alfa = Alfan * Alfas
    'calcolo sig2
    Sig2 = Alfa * Sig_l
    'calcolo dati cls confinato
    If Sig2 <= 0.05 * fck Then fck_c = fck * (1 + 5 * Sig2 / fck) Else fck_c = fck * (1.125 + 2.5 * Sig2 / fck)
    fcd_c = 0.85 * fck_c / Gammac
    Eps_c2c = Eps_c2 * (fck_c / fck) ^ 2
    Eps_cuc = Eps_cu + 0.2 * Sig2 / fck
    'calcolo rapporto meccanico armatura trasv. di confinamento
    w_wd = Vst_conf * fyd / (Vnucleo_conf * fcd)
    'output utente
    With Foglio1
        .Activate
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "CALCESTRUZZO CONFINATO DA STAFFE CHIUSE E LEGATURE"
        If FormSez = "Rettangolare" Then
            .Cells(iF1 + 1, 1) = "dimensione nucleo confinato in direzione y,   By=" & Round(By / fmL, 2) & umL
            .Cells(iF1 + 2, 1) = "dimensione nucleo confinato in direzione z,   Bz=" & Round(Bz / fmL, 2) & umL
            iF1 = iF1 + 3
        ElseIf FormSez = "Circolare piena o cava" Then
            .Cells(iF1 + 1, 1) = "diametro del nucleo confinato,   Do=" & Round(D0 / fmL, 2) & umL
            iF1 = iF1 + 2
        End If
        .Cells(iF1, 1) = "rapporto meccanico armatura trasversale di confinamento,   w_wd=" & Round(w_wd, 3)
        .Cells(iF1 + 1, 1) = "coefficiente   alfa_n=" & Round(Alfan, 3)
        .Cells(iF1 + 2, 1) = "coefficiente   alfa_s=" & Round(Alfas, 3)
        .Cells(iF1 + 3, 1) = "coefficiente di efficienza del confinamento,   alfa=alfa_n*alfa_s=" & Round(Alfa, 3)
        .Cells(iF1 + 4, 1) = "pressione di confinamento,   sig_l=" & FormatNumber(Sig_l / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 5, 1) = "pressione laterale efficace di confinamento,   sig2=" & FormatNumber(Sig2 / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 6, 1) = "resistenza caratteristica a compress. cilindrica cls confinato,   fck_c=" & FormatNumber(fck_c / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 7, 1) = "resistenza di calcolo a compressione cls confinato,   fcd_c=" & FormatNumber(fcd_c / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 8, 1) = "deformazione alla resistenza massima del cls confinato,   ec2_c=" & Round(Eps_c2c * 100, 2) & "%"
        .Cells(iF1 + 9, 1) = "deformazione di rottura o ultima cls confinato,   ecu_c=" & Round(Eps_cuc * 100, 2) & "%"
        iF1 = iF1 + 11
    End With
End If
End Sub

Sub LimitiArmaturaLong() '4.9
'Pilastri: calcola Afmin, Afmax armatura minima e massima su tutta la sezione
'Trave: calcolo Afmin1, Afmax armatura minima e massima in zona tesa
Dim Acsn#
Dim Bt#
Dim Ro_comp#
If Pilastro Then
    Afmin1 = 0.003 * Asez
    If MetodoTA Then
        If Nx < 0 Then
            Acsn = Abs(Nx) / Sigcar
            Afmin2 = 0.008 * Acsn
        End If
        Afmax = 0.06 * Asez
    ElseIf MetodoSL08 Or MetodoSL18 Then
        If ZonaSismStruttDissip Then
            Afmin2 = 0.01 * Asez
        Else
            If Nx < 0 Then Afmin2 = 0.1 * Abs(Nx) / fyd
        End If
        Afmax = 0.04 * Asez
    End If
    Afmin = Application.Max(Afmin1, Afmin2)
ElseIf Trave Or TraveFondaz Then
    If MetodoTA Then
        If TipoAcciaioCA = "Fe B 38 k" Or TipoAcciaioCA = "Fe B 44 k" Then
            Afmin1 = 0.0015 * Asez 'barre ad aderenza migliorata
        Else
            Afmin1 = 0.0025 * Asez
        End If
        Afmax = 0.04 * Asez
    ElseIf MetodoSL08 Or MetodoSL18 Then
        If TraveFondaz Then
            Afmin1 = 0.002 * Asez
            Afmax = 0.04 * Asez
        ElseIf Trave Then
            If ZonaSismStruttDissip Then
                Afmin1 = 1.4 * Asez / (fyk * fc1)
                D1 = 3.5 * Asez / (fyk * fc1)
                Afmax = A1f + D1
            Else
                If FormSez = "Rettangolare" Or FormSez = "a doppio T" Or FormSez = "Scatolare" Then
                    Bt = B
                ElseIf FormSez = "a T" Or FormSez = "a T rovescia" Then
                    Bt = (B + Bo) / 2
                ElseIf FormSez = "Circolare piena o cava" Then
                    Bt = 0.6 * D
                End If
                Afmin1 = 0.26 * fctm / fyk * Bt * Hu
                If Afmin1 < 0.0013 * Bt * Hu Then Afmin1 = 0.0013 * Bt * Hu
                Afmax = 0.04 * Asez
            End If
        End If
    End If
End If
'output se calcolo di verifica
If CalcVerif Then
    With Foglio1
        .Activate
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "LIMITI DI ARMATURA LONGITUDINALE PREVISTI DALLA NORMA"
        iF1 = iF1 + 1
        If Pilastro Then
            .Cells(iF1, 1) = "armatura minima:"
            If FormSez = "Circolare piena o cava" Then
                .Cells(iF1 + 1, 1) = "   1) almeno 6 tondini"
            Else
                .Cells(iF1 + 1, 1) = "   1) almeno 4 tondini del diametro 12 mm, di area complessiva pari a 4,52 cmq"
            End If
            .Cells(iF1 + 2, 1) = "   2) 0,3% Asez=" & Round(Afmin1 / fmL2, 2) & " cmq"
            iF1 = iF1 + 3
            If MetodoTA And Nx < 0 Then
                .Cells(iF1, 1) = "   3) 0,8% Ac strett. necessaria=" & Round(Afmin2 / fmL2, 2) & " cmq"
                iF1 = iF1 + 1
            ElseIf MetodoSL08 Or MetodoSL18 Then
                If ZonaSismStruttDissip Then
                    .Cells(iF1, 1) = "   3) strutture a comportam. dissipativo in zona sismica,   1% Asez=" & Round(Afmin2 / fmL2, 2) & " cmq"
                    iF1 = iF1 + 1
                Else
                    If Nx < 0 Then
                        .Cells(iF1, 1) = "   3) 0,1 del rapporto Nx/fyd    -> " & Round(Afmin2 / fmL2, 2) & " cmq"
                        iF1 = iF1 + 1
                    End If
                End If
            End If
            .Cells(iF1, 1) = "   armatura minima,   Afmin=" & Round(Afmin / fmL2, 2) & " cmq"
            If MetodoTA Then
                .Cells(iF1 + 1, 1) = "armatura massima,   Afmax=6% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
            ElseIf MetodoSL08 Or MetodoSL18 Then
                .Cells(iF1 + 1, 1) = "armatura massima,   Afmax=4% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
            End If
            iF1 = iF1 + 3
        ElseIf Trave Or TraveFondaz Then
            If MetodoTA Then
                .Cells(iF1, 1) = "Armatura minima in zona tesa pari allo 0,15% di Asez (" & Round(0.0015 * Asez / fmL2, 2) & " cmq), per "
                .Cells(iF1 + 1, 1) = "   barre ad aderenza migliorata, e allo 0,25% di Asez (" & Round(0.0025 * Asez / fmL2, 2) & " cmq) per barre lisce."
                .Cells(iF1 + 2, 1) = "Armatura massima in zona tesa,   Afmax=4% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
                iF1 = iF1 + 4
            ElseIf MetodoSL08 Or MetodoSL18 Then
                If Trave Then
                    If ZonaSismStruttDissip Then
                        .Cells(iF1, 1) = "Armatura minima in zona tesa,   Afmin=1,4 Asez/fyk=" & Round(Afmin1 / fmL2, 2) & " cmq"
                        .Cells(iF1 + 1, 1) = "Armatura massima in zona tesa,   Afmax=A'f+3,5 Asez/fyk=" & Round(Afmax / fmL2, 2) & " cmq"
                    Else
                        .Cells(iF1, 1) = "Armatura minima in zona tesa,   Afmin=" & Round(Afmin1 / fmL2, 2) & " cmq"
                        .Cells(iF1 + 1, 1) = "Armatura massima in zona tesa,   Afmax=4% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
                    End If
                ElseIf TraveFondaz Then
                    .Cells(iF1, 1) = "Armatura minima in zona tesa,   Afmin=0,2% Asez=" & Round(Afmin1 / fmL2, 2) & " cmq"
                    .Cells(iF1 + 1, 1) = "Armatura massima in zona tesa,   Afmax=4% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
                End If
                iF1 = iF1 + 3
            End If
        End If
    End With
End If
End Sub

Sub VerificheSLUdistaccoDalSupporto() '4.10
'Nel caso di rinforzo con FRP, calcola la lunghezza ottimale di ancoraggio, la resistenza allo SLU per distacco di estremità (modo 1)
'e la resistenza allo SLU per distacco intermedio (modo 2)
Dim Eps_fdd#
Dim fbd#, ffdd2#
Dim Kb#, Kg#, Kq#, Kg2#
Dim Led1#, LamdaFd#
Dim Rapp#
'1. Calcolo lunghezza ottimale di ancoraggio
If FormSez = "a T" Then
    Rapp = B_frp / Bo
Else
    Rapp = B_frp / B
End If
If Rapp < 0.25 Then Rapp = 0.25
Kb = ((2 - Rapp) / (1 + Rapp)) ^ 0.5
If Kb < 1 Then Kb = 1
If TipoFRP = "composito preformato" Then
    Kg = 0.023 / fc3
ElseIf TipoFRP = "composito impregnato in situ" Then
    Kg = 0.037 / fc3
End If
LamdaFd = (Kb * Kg / FC) * (fcm * fctm) ^ 0.5
fbd = 2 * LamdaFd / (0.25 / fc3)
Led1 = (1 / (1.25 * fbd)) * (PiGreco ^ 2 * E_frp * H_frp * LamdaFd / 2) ^ 0.5
Led = Application.Max(200 / fc3, Led1)
'2. Resistenza allo SLU per distacco di estremità (modo 1)
ffdd = (1 / Gammaf_dist) * (2 * E_frp * LamdaFd / H_frp) ^ 0.5
'3. Resistenza allo SLU per distacco intermedio (modo 2)
Kq = 1.25
Kg2 = 0.1 / fc3
ffdd2 = (Kq / Gammaf_dist) * (2 * E_frp * Kb * Kg2 * (fcm * fctm) ^ 0.5 / (H_frp * FC)) ^ 0.5
Eps_fdd = ffdd2 / E_frp
'aggiorna Eps_pu se maggiore di Eps_fdd ai fini del calcolo del momento resistente
If Eps_pu > Eps_fdd Then Eps_pu = Eps_fdd
'4. Output utente
With Foglio1
    .Activate
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "CALCOLO RESISTENZA COMPOSITO FRP NEI CONFRONTI DEL DISTACCO"
    .Cells(iF1 + 1, 1) = "lunghezza ottimale di ancoraggio di progetto,   Led=" & Round(Led / fmL, 1) & umL
    .Cells(iF1 + 2, 1) = "max tensione nel composito senza che si verifichi il distacco di estremità,   ffdd=" & Round(ffdd / fmFL_2, 2) & umTens
    .Cells(iF1 + 3, 1) = "max tensione nel composito senza che si verifichi il distacco intermedio,   ffdd2=" & Round(ffdd2 / fmFL_2, 2) & umTens
    .Cells(iF1 + 4, 1) = "max deformazione nel composito affinchè non si verifichi il distacco intermedio,   Eps_fdd=" & Round(Eps_fdd * 100, 4) & "%"
    iF1 = iF1 + 6
End With
End Sub

Sub ClsConfinatoFRP() '4.11
'Determina la resistenza a compressione del cls confinato con FRP fccd e la sua deformazione ultima Eps_cuc
'solo per sezione rettangolare e circolare
Dim Ag#
Dim Bpr#
Dim dmin#
Dim Eps_fdrid#, Eps_fdrid2#
Dim f_lat#, f_lat_eff#, f_lat_eff2#
Dim Hpr#
Dim Kh#, Kv#, Ka#, Keff#
Dim Ro_f#
'1. Calcolo coefficiente di efficienza Keff
If FormSez = "Rettangolare" Then
    Bpr = B - 2 * rc_
    Hpr = H - 2 * rc_
    Ag = Asez
    Kh = 1 - (Bpr ^ 2 + Hpr ^ 2) / (3 * Ag)
    Ro_f = 2 * (B + H) * tf_ * Bf_ / (B * H * pf_)
    dmin = Application.Min(B, H)
ElseIf FormSez = "Circolare piena o cava" Then
    Kh = 1
    Ro_f = 4 * tf_ * Bf_ / (D * pf_)
    dmin = D
End If
If TipoConfinFRP = "continuo" Then
    Kv = 1
ElseIf TipoConfinFRP = "discontinuo" Then
    Kv = (1 - (pf_ - Bf_) / (2 * dmin)) ^ 2
End If
Ka = 1 / (1 + Tan(Alfa_fib) ^ 2)
Keff = Kh * Kv * Ka
If Keff > 1 Then Keff = 1
'2. calcolo pressione laterale di confinamento f_lat e pressione efficace di confinamento
Eps_fdrid = Application.Min(Eps_pu, 0.004)
f_lat = 0.5 * Ro_f * E_frp * Eps_fdrid
f_lat_eff = Keff * f_lat
'3. calcolo fccd e Eps_cuc
fccd = fcd * (1 + 2.6 * (f_lat_eff / fcd) ^ (2 / 3))
Eps_fdrid2 = Eps_pu
If Eps_fdrid2 > 0.6 * fpk / E_frp Then Eps_fdrid2 = 0.6 * fpk / E_frp
f_lat_eff2 = Keff * (0.5 * Ro_f * E_frp * Eps_fdrid2)
Eps_cuc = 0.0035 + 0.015 * (f_lat_eff2 / fcd) ^ 0.5
Eps_c2c = Eps_c2
'4. Output utente
With Foglio1
    .Activate
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "CALCESTRUZZO CONFINATO CON COMPOSITI FRP"
    .Cells(iF1 + 1, 1) = "coeff. di efficienza orizzontale,   Kh=" & Round(Kh, 4)
    .Cells(iF1 + 2, 1) = "coeff. di efficienza verticale,   Kv=" & Round(Kv, 4)
    .Cells(iF1 + 3, 1) = "coeff. di efficienza per inclinaz. fibre composito,   Ka=" & Round(Ka, 4)
    .Cells(iF1 + 4, 1) = "coeff. di efficienza,   Keff=" & Round(Keff, 4)
    .Cells(iF1 + 5, 1) = "percentuale geometrica di rinforzo,   Ro_f=" & Round(Ro_f, 4)
    .Cells(iF1 + 6, 1) = "deformazione ridotta di calcolo del FRP,   Eps_rid=" & Round(Eps_fdrid, 4)
    .Cells(iF1 + 7, 1) = "pressione laterale di confinamento,   sig_l=" & FormatNumber(f_lat / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 8, 1) = "pressione laterale efficace di confinamento,   sig_l_eff=" & FormatNumber(f_lat_eff / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 9, 1) = "resistenza di progetto a compress. del cls confinato,   fccd=" & FormatNumber(fccd / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 10, 1) = "deformazione di rottura o ultima del cls confinato,   ecu_c=" & Round(Eps_cuc * 100, 2) & "%"
    iF1 = iF1 + 12
End With
End Sub

Sub ClsConfinatoCalastr() '4.12
'Determina la resistenza a compressione del cls fccd confinato con calastrelli in acciaio e la sua deformazione ultima Eps_cuc
'solo per sezione rettangolare e circolare
Dim Alfa_n#, Alfa_s#
Dim Bpr#
Dim f_lat_eff#
Dim Hpr#
Dim Ro_s#
'1. Calcolo dei fattori di efficienza e rapporto volumetrico di armatura trasversale
If FormSez = "Rettangolare" Then
    Bpr = B - 2 * rc_
    Hpr = H - 2 * rc_
    Alfa_n = 1 - (Bpr ^ 2 + Hpr ^ 2) / (3 * Asez)
    Alfa_s = (1 - (pf_ - Bf_) / (2 * B)) * (1 - (pf_ - Bf_) / (2 * H))
    Ro_s = 2 * (B + H) * tf_ * Bf_ / (B * H * pf_)
ElseIf FormSez = "Circolare piena o cava" Then
    Alfa_n = 1
    Alfa_s = (1 - (pf_ - Bf_) / (2 * D)) * (1 - (pf_ - Bf_) / (2 * D))
    Ro_s = 4 * tf_ * Bf_ / (D * pf_)
End If
'2. calcolo pressione laterale efficace di confinamento f_lat
f_lat_eff = 0.5 * Alfa_n * Alfa_s * Ro_s * fyd
'3. calcolo fccd e Eps_cuc
fccd = fcd * (1 + 3.7 * (f_lat_eff / fcd) ^ 0.86)
Eps_cuc = 0.0035 + 0.5 * (f_lat_eff / fccd)
Eps_c2c = Eps_c2 * (1 + 5 * (fccd / fcd - 1))
'4. Output utente
With Foglio1
    .Activate
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "CALCESTRUZZO CONFINATO CON CAMICIE IN ACCIAIO (ANGOLARI+CALASTRELLI)"
    .Cells(iF1 + 1, 1) = "fattore di efficienza nella sezione,   alfa_n=" & Round(Alfa_n, 4)
    .Cells(iF1 + 2, 1) = "fattore di efficienza lungo l'asta,   alfa_s=" & Round(Alfa_s, 4)
    .Cells(iF1 + 3, 1) = "rapporto volumetrico di armatura di rinforzo,   Ro_s=" & Round(Ro_s, 4)
    .Cells(iF1 + 4, 1) = "pressione laterale efficace di confinamento,   sig_l_eff=" & FormatNumber(f_lat_eff / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 5, 1) = "resistenza di progetto a compress. del cls confinato,   fccd=" & FormatNumber(fccd / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 6, 1) = "deformazione alla resistenza massima del cls confinato,   ec2_c=" & Round(Eps_c2c * 100, 2) & "%"
    .Cells(iF1 + 7, 1) = "deformazione di rottura o ultima del cls confinato,   ecu_c=" & Round(Eps_cuc * 100, 2) & "%"
    iF1 = iF1 + 9
End With
End Sub

Sub ProgCA() '5.
'CALCOLO ARMATURA LONGITUDINALE A FLESSIONE (pilastri e travi), SIA CON METODO T.A. CHE CON S.L.U.
'si esclude a monte la sezione Generica
'Dim Afmin1#, Afmin#, Afmax#
Dim Binf#, Bsup#
'Dim D1#
Dim k#
Dim Nbp%(), Nb1#
Dim p#
Dim sL1#, sL#(), sL_min#, sL_max#
'1. CALCOLO DATI VALIDI PER OGNI SEZIONE
Af1t = PiGreco * dfp ^ 2 / 4
Delta = Cf + dfp / 2
Hu = H - Delta
VerifResist = False
DatiSezioneCA '4.1   per calcolare Asez
'2. CALCOLO MINIMI E MASSIMI ARMATURA
LimitiArmaturaLong '4.9
'3. SEZIONE CIRCOLARE
If FormSez = "Circolare piena o cava" Then
    '3.1 numero minimo di barre in ogni caso
    Nbar = 6
    '3.2 eventuale correzione Nbar per adeguare ai minimi normativa
    If Pilastro Then
        If Nbar < Afmin / Af1t Then Nbar = Int(Afmin / Af1t) + 1
    Else 'è trave o trave fondaz
        If Nbar < 2 * Afmin1 / Af1t Then Nbar = Int(2 * Afmin1 / Af1t) + 1
    End If
    '3.3 rispetto dell'interasse massimo fissato dall'utente
    Nb1 = PiGreco * (D - 2 * Cf - dfp) / Pmax
    If Nb1 - Int(Nb1) > 0 Then Nb1 = Int(Nb1) + 1
    If Nb1 > Nbar Then Nbar = Nb1
    '3.4 ciclo: aumento Nbar finchè non verifica
    Nbar = Nbar - 1
    Do
        Nbar = Nbar + 1
        CoordBaricentriTondini '1.1
        sL1 = ((Zb_pr(2) - Zb_pr(1)) ^ 2 + (Yb_pr(2) - Yb_pr(1)) ^ 2) ^ 0.5 - dfp
        If sL1 < sLmin Then Exit Do
        DatiSezioneCA '4.1
        Aft = Nbar * Af1t
        Af = Aft / 2 'zona tesa
        A1f = Aft / 2 'zona compressa
        If Pilastro And Aft > Afmax Then
            OutNoProg '5.1
            End
        Else 'è trave
            If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                If Af > Afmax Then
                    OutNoProg '5.1
                    End
                End If
            Else
                Afmax = A1f + D1
                If Af >= Afmax Then
                    OutNoProg '5.1
                    End
                End If
            End If
        End If
        If MetodoTA Then
            CalcoloTensNormali Nx, My, Mz, True '4.3
            VerifResistCA_TA '4.5
        ElseIf MetodoSL08 Or MetodoSL18 Then
            VerifResistCA_SLU_TensNorm '4.7
        End If
    Loop Until VerifResist
'4. SEZIONE RETTANGOLARE E SCATOLARE
ElseIf FormSez = "Rettangolare" Or FormSez = "Scatolare" Then
    Npacch = 4
    Foglio2.Cells(3, 42) = Npacch
    ReDim Nbp%(1 To Npacch)
    ReDim sL#(1 To Npacch)
    '4.1)calcolo numero barre per ogni pacchetto in modo che non si superi il passo massimo fissato dall'utente
    Nbp(1) = Nbh(B) '5.2
    Nbp(2) = Nbp(1)
    Nbp(3) = Nbv(H) '5.3
    Nbp(4) = Nbp(3)
    Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4)
    Aft = Nbar * Af1t
    sL(1) = f_sL(B, Nbp(1), dfp) '5.4
    sL(2) = sL(1)
    sL(3) = f_sL(H, Nbp(3) + 2, dfp)
    sL(4) = sL(3)
    sL_max = Application.Max(sL())
    '4.2)eventuale correzione Nbp() per adeguare ai minimi normativa
    If Pilastro Then
        While Aft < Afmin 'inserisci una barra nel lembo con i ferri più distanti tra loro
            If sL(1) = sL_max Then
                Nbp(1) = Nbp(1) + 1
                sL(1) = f_sL(B, Nbp(1), dfp)
            ElseIf sL(2) = sL_max Then
                Nbp(2) = Nbp(2) + 1
                sL(2) = f_sL(B, Nbp(2), dfp)
            ElseIf sL(3) = sL_max Then
                Nbp(3) = Nbp(3) + 1
                sL(3) = f_sL(H, Nbp(3) + 2, dfp)
            ElseIf sL(4) = sL_max Then
                Nbp(4) = Nbp(4) + 1
                sL(4) = f_sL(H, Nbp(4) + 2, dfp)
            End If
            sL_max = Application.Max(sL())
            Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4)
            Aft = Nbar * Af1t
        Wend
    Else 'è trave o trave fondaz
        If Abs(Mz) <= Abs(My) Then
            If My >= 0 Then 'sono tese le fibre inferiori
                Af = Af1t * (Nbp(2) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                'A1f = Af1t * (Nbp(1) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                While Af < Afmin1 And sL(2) >= sLmin 'aumenta una barra lembo 2 inferiore
                    Nbp(2) = Nbp(2) + 1
                    Af = Af1t * (Nbp(2) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    sL(2) = f_sL(B, Nbp(2), dfp)
                Wend
                While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembi laterali 3 e 4
                    Nbp(3) = Nbp(3) + 1
                    Nbp(4) = Nbp(4) + 1
                    Af = Af1t * (Nbp(2) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            Else 'sono tese le fibre superiori 1
                Af = Af1t * (Nbp(1) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                While Af < Afmin1 And sL(1) >= sLmin 'aumenta una barra lembo 2 inferiore
                    Nbp(1) = Nbp(1) + 1
                    Af = Af1t * (Nbp(1) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    sL(1) = f_sL(B, Nbp(1), dfp)
                Wend
                While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembi laterali 3 e 4
                    Nbp(3) = Nbp(3) + 1
                    Nbp(4) = Nbp(4) + 1
                    Af = Af1t * (Nbp(1) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            End If
        Else
            If Mz >= 0 Then 'sono tese le fibre lembo destro 4
                Af = Af1t * (Nbp(4) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                While Af < Afmin1 And sL(4) >= sLmin 'aumenta una barra lembo 4 destro
                    Nbp(4) = Nbp(4) + 1
                    Af = Af1t * (Nbp(4) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    sL(4) = f_sL(H, Nbp(4) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(1) >= sLmin 'aumenta una barra lembi inf 2 e sup 1
                    Nbp(1) = Nbp(1) + 1
                    Nbp(2) = Nbp(2) + 1
                    Af = Af1t * (Nbp(4) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    sL(1) = f_sL(B, Nbp(1), dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            Else 'sono tese le fibre lembo sinistro 3
                Af = Af1t * (Nbp(3) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembo 4 destro
                    Nbp(3) = Nbp(3) + 1
                    Af = Af1t * (Nbp(3) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(1) >= sLmin 'aumenta una barra lembi inf 2 e sup 1
                    Nbp(1) = Nbp(1) + 1
                    Nbp(2) = Nbp(2) + 1
                    Af = Af1t * (Nbp(3) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    sL(1) = f_sL(B, Nbp(1), dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            End If
        End If
    End If
    sL_max = Application.Max(sL())
    '4.3 aumenta barre finchè non verifica
    '4.3.1 prima diminuisci di una unità
    If Pilastro Then
        If sL(1) = sL_max Then
            Nbp(1) = Nbp(1) - 1
        ElseIf sL(2) = sL_max Then
            Nbp(2) = Nbp(2) - 1
        ElseIf sL(3) = sL_max Then
            Nbp(3) = Nbp(3) - 1
        ElseIf sL(4) = sL_max Then
            Nbp(4) = Nbp(4) - 1
        End If
    Else 'è trave o trave fondaz
        If Abs(Mz) <= Abs(My) Then
            If My >= 0 Then
                Nbp(2) = Nbp(2) - 1
            Else
                Nbp(1) = Nbp(1) - 1
            End If
        Else
            If Mz >= 0 Then
                Nbp(4) = Nbp(4) - 1
            Else
                Nbp(3) = Nbp(3) - 1
            End If
        End If
    End If
    Do
        '4.3.2 aumenta di una o due barre il/i pacchetto/i più opportuno in base alle sollecitaz agenti
        If Pilastro Then
            'aumenta di una barra il lembo con le barre più distanti
            If sL(1) = sL_max Then
                Nbp(1) = Nbp(1) + 1
                sL(1) = f_sL(B, Nbp(1), dfp)
                If sL(1) < sLmin Then Exit Do
            ElseIf sL(2) = sL_max Then
                Nbp(2) = Nbp(2) + 1
                sL(2) = f_sL(B, Nbp(2), dfp)
                If sL(2) < sLmin Then Exit Do
            ElseIf sL(3) = sL_max Then
                Nbp(3) = Nbp(3) + 1
                sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                If sL(3) < sLmin Then Exit Do
            ElseIf sL(4) = sL_max Then
                Nbp(4) = Nbp(4) + 1
                sL(4) = f_sL(H, Nbp(4) + 2, dfp)
                If sL(4) < sLmin Then Exit Do
            End If
            sL_max = Application.Max(sL())
            Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4)
            Aft = Nbar * A1f
            'verifica che armatura non superi il massimo normativa
            If Aft > Afmax Then
                OutNoProg '5.1
                End
            End If
        Else 'è trave o trave fondaz
            If Abs(Mz) <= Abs(My) Then
                If My >= 0 Then 'sono tese le fibre inferiori lembo 2
                    Nbp(2) = Nbp(2) + 1
                    sL(2) = f_sL(B, Nbp(2), dfp)
                    If sL(2) < sLmin Then 'aumenta barre lembi 3 e 4
                        Nbp(2) = Nbp(2) - 1
                        Nbp(3) = Nbp(3) + 1
                        Nbp(4) = Nbp(4) + 1
                        sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                        If sL(3) < sLmin Then 'aumenta barre nel pacchetto 1
                            Nbp(3) = Nbp(3) - 1
                            Nbp(4) = Nbp(4) - 1
                            Nbp(1) = Nbp(1) + 1
                            sL(1) = f_sL(B, Nbp(1), dfp)
                            If sL(1) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(2) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    A1f = Af1t * (Nbp(1) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(1) >= sLmin
                        'aumenta una barra lembo superiore 1 compresso
                        Nbp(1) = Nbp(1) + 1
                        sL(1) = f_sL(B, Nbp(1), dfp)
                        A1f = Af1t * (Nbp(1) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                ElseIf My < 0 Then 'sono tese le fibre superiori lembo 1
                    Nbp(1) = Nbp(1) + 1
                    sL(1) = f_sL(B, Nbp(1), dfp)
                    If sL(1) < sLmin Then 'aumenta barre lembi 3 e 4
                        Nbp(1) = Nbp(1) - 1
                        Nbp(3) = Nbp(3) + 1
                        Nbp(4) = Nbp(4) + 1
                        sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                        If sL(3) < sLmin Then 'aumenta barre nel pacchetto 2
                            Nbp(3) = Nbp(3) - 1
                            Nbp(4) = Nbp(4) - 1
                            Nbp(2) = Nbp(2) + 1
                            sL(2) = f_sL(B, Nbp(2), dfp)
                            If sL(2) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(1) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    A1f = Af1t * (Nbp(2) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(2) >= sLmin
                        'aumenta una barra lembo inferiore 2 compresso
                        Nbp(2) = Nbp(2) + 1
                        sL(2) = f_sL(B, Nbp(2), dfp)
                        A1f = Af1t * (Nbp(2) + Int(Nbp(3) / 2) + Int(Nbp(4) / 2))
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                End If
            ElseIf Abs(Mz) > Abs(My) Then
                If Mz >= 0 Then 'sono tese le fibre lembo 4
                    Nbp(4) = Nbp(4) + 1
                    sL(4) = f_sL(H, Nbp(4) + 2, dfp)
                    If sL(4) < sLmin Then 'aumenta barre lembi 1 e 2
                        Nbp(4) = Nbp(4) - 1
                        Nbp(1) = Nbp(1) + 1
                        Nbp(2) = Nbp(2) + 1
                        sL(1) = f_sL(B, Nbp(1), dfp)
                        If sL(1) < sLmin Then 'aumenta barra lembo 3
                            Nbp(1) = Nbp(1) - 1
                            Nbp(2) = Nbp(2) - 1
                            Nbp(3) = Nbp(3) + 1
                            sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                            If sL(3) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(4) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    A1f = Af1t * (Nbp(3) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(1) >= sLmin
                        'aumenta una barra lembo sinistro 3 compresso
                        Nbp(3) = Nbp(3) + 1
                        sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                        A1f = Af1t * (Nbp(3) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                ElseIf Mz < 0 Then 'sono tese le fibre lembo 3
                    Nbp(3) = Nbp(3) + 1
                    sL(3) = f_sL(H, Nbp(3) + 2, dfp)
                    If sL(3) < sLmin Then 'aumenta barre lembi 1 e 2
                        Nbp(3) = Nbp(3) - 1
                        Nbp(1) = Nbp(1) + 1
                        Nbp(2) = Nbp(2) + 1
                        sL(1) = f_sL(B, Nbp(1), dfp)
                        If sL(1) < sLmin Then 'aumenta barra lembo 4
                            Nbp(1) = Nbp(1) - 1
                            Nbp(2) = Nbp(2) - 1
                            Nbp(4) = Nbp(4) + 1
                            sL(4) = f_sL(H, Nbp(4) + 2, dfp)
                            If sL(4) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(3) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    A1f = Af1t * (Nbp(4) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(1) >= sLmin
                        'aumenta una barra lembo destro 4 compresso
                        Nbp(4) = Nbp(4) + 1
                        sL(4) = f_sL(H, Nbp(4) + 2, dfp)
                        A1f = Af1t * (Nbp(4) + Int(Nbp(1) / 2) + Int(Nbp(2) / 2))
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                End If
            End If
        End If
        '4.3.3 calcolo Nbar
        Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4)
        Aft = Nbar * Af1t
        '4.3.4 scarica su fg2 i dati sui 4 pacchetti di armatura che verranno poi ripresi da CoordBaricentriTondini e quindi da DatiSezioneCa
        PacchArmat 1, Delta, Delta, B - Delta, Delta, Nbp(1), dfp '5.4
        PacchArmat 2, Delta, H - Delta, B - Delta, H - Delta, Nbp(2), dfp '5.4
        p = (H - 2 * Delta) / (1 + Nbp(3))
        PacchArmat 3, B - Delta, Delta + p, B - Delta, Delta + p * Nbp(3), Nbp(3), dfp '5.4
        p = (H - 2 * Delta) / (1 + Nbp(4))
        PacchArmat 4, Delta, Delta + p, Delta, Delta + p * Nbp(4), Nbp(4), dfp '5.4
        '4.3.5 calcola baricentri tondini e procedi alla verifica
        CoordBaricentriTondini '1.1
        DatiSezioneCA '4.1
        If MetodoTA Then
            CalcoloTensNormali Nx, My, Mz, True '4.3
            VerifResistCA_TA '4.5
        ElseIf MetodoSL08 Or MetodoSL18 Then
            VerifResistCA_SLU_TensNorm '4.7
        End If
    Loop Until VerifResist
'5)SEZIONE A T e a T rovescia
ElseIf FormSez = "a T" Or FormSez = "a T rovescia" Then
    Npacch = 8
    Foglio2.Cells(3, 42) = Npacch
    ReDim Nbp%(1 To Npacch)
    ReDim sL#(1 To Npacch)
    '5.1)calcolo numero barre per ogni pacchetto in modo che non si superi il passo massimo fissato dall'utente
    If FormSez = "a T" Then
        Binf = Bo
        Bsup = B
    ElseIf FormSez = "a T rovescia" Then
        Binf = B
        Bsup = Bo
    End If
    Nbp(1) = Nbh(Bsup)
    Nbp(2) = Nbh(Binf)
    Nbp(3) = Nbh((B - Bo) / 2 + 2 * Delta)
    Nbp(4) = Nbp(3)
    Nbp(5) = Nbv(S)
    Nbp(6) = Nbp(5)
    Nbp(7) = Nbv(H - S + 2 * Delta)
    Nbp(8) = Nbp(7)
    Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6) + Nbp(7) + Nbp(8)
    Aft = Nbar * Af1t
    sL(1) = f_sL(Bsup, Nbp(1), dfp)
    sL(2) = f_sL(Binf, Nbp(2), dfp)
    sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
    sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
    sL(5) = f_sL(S, Nbp(5) + 2, dfp)
    sL(6) = f_sL(S, Nbp(6) + 2, dfp)
    sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
    sL(8) = f_sL(H - S + 2 * Delta, Nbp(8) + 2, dfp)
    sL_max = Application.Max(sL())
    '5.2)eventuale correzione Nbp() per adeguare ai minimi normativa
    If Pilastro Then
        While Aft < Afmin 'aumenta una barra nel lembo con la barre più distanti
            If sL(1) = sL_max Then
                Nbp(1) = Nbp(1) + 1
                sL(1) = f_sL(Bsup, Nbp(1), dfp)
            ElseIf sL(2) = sL_max Then
                Nbp(2) = Nbp(2) + 1
                sL(2) = f_sL(Binf, Nbp(2), dfp)
            ElseIf sL(3) = sL_max Then
                Nbp(3) = Nbp(3) + 1
                sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
            ElseIf sL(4) = sL_max Then
                Nbp(4) = Nbp(4) + 1
                sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
            ElseIf sL(5) = sL_max Then
                Nbp(5) = Nbp(5) + 1
                sL(5) = f_sL(S, Nbp(5) + 2, dfp)
            ElseIf sL(6) = sL_max Then
                Nbp(6) = Nbp(6) + 1
                sL(6) = f_sL(S, Nbp(6) + 2, dfp)
            ElseIf sL(7) = sL_max Then
                Nbp(7) = Nbp(7) + 1
                sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
            ElseIf sL(8) = sL_max Then
                Nbp(8) = Nbp(8) + 1
                sL(8) = f_sL(H - S + 2 * Delta, Nbp(8) + 2, dfp)
            End If
            sL_max = Application.Max(sL())
            Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6) + Nbp(7) + Nbp(8)
            Aft = Nbar * Af1t
        Wend
    Else 'è trave
        If Abs(Mz) <= Abs(My) Then
            If My >= 0 Then 'teso il lembo inferiore 2
                If FormSez = "a T" Then 'armatura tesa
                    Af = Af1t * (Nbp(2) + Nbp(7) + Nbp(8))
                    While Af < Afmin1 And sL(2) >= sLmin 'aumenta una barra lembo 2 inferiore
                        Nbp(2) = Nbp(2) + 1
                        Af = Af1t * (Nbp(2) + Nbp(7) + Nbp(8))
                        sL(2) = f_sL(Binf, Nbp(2), dfp)
                    Wend
                    While Af < Afmin1 And sL(7) >= sLmin 'aumenta una barra lembi laterali inferiori 7-8
                        Nbp(7) = Nbp(7) + 1
                        Nbp(8) = Nbp(8) + 1
                        Af = Af1t * (Nbp(2) + Nbp(7) + Nbp(8))
                        sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                    Wend
                ElseIf FormSez = "a T rovescia" Then
                    Af = Af1t * (Nbp(2) + Nbp(5) + Nbp(6) + Nbp(3) + Nbp(4))
                    While Af < Afmin1 And sL(2) >= sLmin 'aumenta una barra lembo 2 inferiore
                        Nbp(2) = Nbp(2) + 1
                        Af = Af1t * (Nbp(2) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6))
                        sL(2) = f_sL(Binf, Nbp(2), dfp)
                    Wend
                    While Af < Afmin1 And sL(5) >= sLmin 'aumenta una barra lembi laterali inferiori 5-6
                        Nbp(5) = Nbp(5) + 1
                        Nbp(6) = Nbp(6) + 1
                        Af = Af1t * (Nbp(2) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6))
                        sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                    Wend
                    While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembi orizz 3 e 4
                        Nbp(3) = Nbp(3) + 1
                        Nbp(4) = Nbp(4) + 1
                        Af = Af1t * (Nbp(2) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6))
                        sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                    Wend
                End If
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            ElseIf My < 0 Then 'teso il lembo superiore 1
                If FormSez = "a T" Then 'armatura tesa
                    Af = Af1t * (Nbp(1) + Nbp(5) + Nbp(6) + Nbp(3) + Nbp(4))
                    While Af < Afmin1 And sL(1) >= sLmin 'aumenta una barra lembo 1 superiore
                        Nbp(1) = Nbp(1) + 1
                        Af = Af1t * Af1t * (Nbp(1) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6))
                        sL(1) = f_sL(Bsup, Nbp(1), dfp)
                    Wend
                    While Af < Afmin1 And sL(5) >= sLmin 'aumenta una barra lembi laterali superiori 5-6
                        Nbp(5) = Nbp(5) + 1
                        Nbp(6) = Nbp(6) + 1
                        Af = Af1t * Af1t * (Nbp(1) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6))
                        sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                    Wend
                    While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembi orizz 3 e 4
                        Nbp(3) = Nbp(3) + 1
                        Nbp(4) = Nbp(4) + 1
                        Af = Af1t * Af1t * (Nbp(1) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6))
                        sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                    Wend
                ElseIf FormSez = "a T rovescia" Then
                    Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8))
                    While Af < Afmin1 And sL(1) >= sLmin 'aumenta una barra lembo 1 superiore
                        Nbp(1) = Nbp(1) + 1
                        Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8))
                        sL(1) = f_sL(Bsup, Nbp(1), dfp)
                    Wend
                    While Af < Afmin1 And sL(7) >= sLmin 'aumenta una barra lembi laterali superiori 7-8
                        Nbp(7) = Nbp(7) + 1
                        Nbp(8) = Nbp(8) + 1
                        Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8))
                        sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                    Wend
                End If
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            End If
        ElseIf Abs(Mz) > Abs(My) Then
            If Mz >= 0 Then 'tesi lembi laterali destri
                Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(4) + Nbp(6) + Nbp(8))
                While Af < Afmin1 And sL(6) >= sLmin 'aumenta una barra lembo vert 6 superiore
                    Nbp(6) = Nbp(6) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(4) + Nbp(6) + Nbp(8))
                    sL(6) = f_sL(S, Nbp(6) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(4) >= sLmin 'aumenta una barra lembo 4
                    Nbp(4) = Nbp(4) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(4) + Nbp(6) + Nbp(8))
                    sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                Wend
                While Af < Afmin1 And sL(8) >= sLmin 'aumenta una barra lembo 8
                    Nbp(8) = Nbp(8) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(4) + Nbp(6) + Nbp(8))
                    sL(8) = f_sL(H - S + 2 * Delta, Nbp(8) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(1) >= sLmin 'aumenta una barra lembo 1
                    Nbp(1) = Nbp(1) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(4) + Nbp(6) + Nbp(8))
                    sL(1) = f_sL(Bsup, Nbp(1), dfp)
                Wend
                While Af < Afmin1 And sL(2) >= sLmin 'aumenta una barra lembo 2
                    Nbp(2) = Nbp(2) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(4) + Nbp(6) + Nbp(8))
                    sL(2) = f_sL(Binf, Nbp(2), dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            ElseIf Mz < 0 Then 'tesi lembi laterali sinistri
                Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(3) + Nbp(5) + Nbp(7))
                While Af < Afmin1 And sL(5) >= sLmin 'aumenta una barra lembo vert 5 superiore
                    Nbp(5) = Nbp(5) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(3) + Nbp(5) + Nbp(7))
                    sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembo 3
                    Nbp(3) = Nbp(3) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(3) + Nbp(5) + Nbp(7))
                    sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                Wend
                While Af < Afmin1 And sL(7) >= sLmin 'aumenta una barra lembo 7
                    Nbp(7) = Nbp(7) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(3) + Nbp(5) + Nbp(7))
                    sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(1) >= sLmin 'aumenta una barra lembo 1
                    Nbp(1) = Nbp(1) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(3) + Nbp(5) + Nbp(7))
                    sL(1) = f_sL(Bsup, Nbp(1), dfp)
                Wend
                While Af < Afmin1 And sL(2) >= sLmin 'aumenta una barra lembo 2
                    Nbp(2) = Nbp(2) + 1
                    Af = Af1t * (Nbp(1) + Nbp(2) + Nbp(3) + Nbp(5) + Nbp(7))
                    sL(2) = f_sL(Binf, Nbp(2), dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            End If
        End If
    End If
    '5.3 aumenta barre finchè non verifica
    '5.3.1 prima diminuisci di una unità
    If Pilastro Then
        If sL(1) = sL_max Then
            Nbp(1) = Nbp(1) - 1
        ElseIf sL(2) = sL_max Then
            Nbp(2) = Nbp(2) - 1
        ElseIf sL(3) = sL_max Then
            Nbp(3) = Nbp(3) - 1
        ElseIf sL(4) = sL_max Then
            Nbp(4) = Nbp(4) - 1
        ElseIf sL(5) = sL_max Then
            Nbp(5) = Nbp(5) - 1
        ElseIf sL(6) = sL_max Then
            Nbp(6) = Nbp(6) - 1
        ElseIf sL(7) = sL_max Then
            Nbp(7) = Nbp(7) - 1
        ElseIf sL(8) = sL_max Then
            Nbp(8) = Nbp(8) - 1
        End If
    Else
        If Abs(Mz) <= Abs(My) Then
            If My >= 0 Then
                Nbp(2) = Nbp(2) - 1
            Else
                Nbp(1) = Nbp(1) - 1
            End If
        Else
            If Mz >= 0 Then
                Nbp(6) = Nbp(6) - 1
            Else
                Nbp(5) = Nbp(5) - 1
            End If
        End If
    End If
    Do
        '5.3.2 aumenta di una barra il pacchetto più opportuno in base alle sollecitaz agenti
        If Pilastro Then
            If sL(1) = sL_max Then
                Nbp(1) = Nbp(1) + 1
                sL(1) = f_sL(Bsup, Nbp(1), dfp)
                If sL(1) < sLmin Then Exit Do
            ElseIf sL(2) = sL_max Then
                Nbp(2) = Nbp(2) + 1
                sL(2) = f_sL(Binf, Nbp(2), dfp)
                If sL(2) < sLmin Then Exit Do
            ElseIf sL(3) = sL_max Then
                Nbp(3) = Nbp(3) + 1
                sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                If sL(3) < sLmin Then Exit Do
            ElseIf sL(4) = sL_max Then
                Nbp(4) = Nbp(4) + 1
                sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                If sL(4) < sLmin Then Exit Do
            ElseIf sL(5) = sL_max Then
                Nbp(5) = Nbp(5) + 1
                sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                If sL(5) < sLmin Then Exit Do
            ElseIf sL(6) = sL_max Then
                Nbp(6) = Nbp(6) + 1
                sL(6) = f_sL(S, Nbp(6) + 2, dfp)
                If sL(6) < sLmin Then Exit Do
            ElseIf sL(7) = sL_max Then
                Nbp(7) = Nbp(7) + 1
                sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                If sL(7) < sLmin Then Exit Do
            ElseIf sL(8) = sL_max Then
                Nbp(8) = Nbp(8) + 1
                sL(8) = f_sL(H - S + 2 * Delta, Nbp(8) + 2, dfp)
                If sL(8) < sLmin Then Exit Do
            End If
            sL_max = Application.Max(sL())
            Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6) + Nbp(7) + Nbp(8)
            Aft = Nbar * A1f
            'verifica che armatura non superi il massimo normativa
            If Aft > Afmax Then
                OutNoProg '5.1
                End
            End If
        Else 'è trave
            If Abs(Mz) <= Abs(My) Then
                If My >= 0 Then
                    Nbp(2) = Nbp(2) + 1 'aumenta barre lembo 2
                    sL(2) = f_sL(Binf, Nbp(2), dfp)
                    If FormSez = "a T" Then
                        If sL(2) < sLmin Then 'aumenta barre lembi 7 e 8
                            Nbp(2) = Nbp(2) - 1
                            Nbp(7) = Nbp(7) + 1
                            Nbp(8) = Nbp(8) + 1
                            sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                            If sL(7) < sLmin Then Exit Do
                        End If
                        Af = Af1t * (Nbp(2) + Nbp(7) / 2 + Nbp(8) / 2)
                        A1f = Af1t * (Nbp(1) + Nbp(5) / 2 + Nbp(6) / 2)
                        Mu = A1f / Af
                        'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                        If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                            If Af > Afmax Then
                                OutNoProg '5.1
                                End
                            End If
                            Mu_min = Mu_
                        Else
                            Afmax = A1f + D1
                            Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                        End If
                        While Mu < Mu_min And sL(1) >= sLmin
                            'aumenta una barra lembo superiore 1 compresso
                            Nbp(1) = Nbp(1) + 1
                            sL(1) = f_sL(Bsup, Nbp(1), dfp)
                            A1f = Af1t * (Nbp(1) + Nbp(5) / 2 + Nbp(6) / 2)
                            Mu = A1f / Af
                        Wend
                        While Mu < Mu_min And sL(5) >= sLmin
                            'aumenta una barra lembi superiore 5 e 6 compressi
                            Nbp(5) = Nbp(5) + 1
                            Nbp(6) = Nbp(6) + 1
                            sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                            A1f = Af1t * (Nbp(1) + Nbp(5) / 2 + Nbp(6) / 2)
                            Mu = A1f / Af
                        Wend
                        If Mu < Mu_min Then
                            OutNoProg '5.1
                            End
                        End If
                    ElseIf FormSez = "a T rovescia" Then
                        If sL(2) < sLmin Then 'aumenta barre lembi 5 e 6
                            Nbp(2) = Nbp(2) - 1
                            Nbp(5) = Nbp(5) + 1
                            Nbp(6) = Nbp(6) + 1
                            sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                            If sL(5) < sLmin Then Exit Do
                        End If
                        Af = Af1t * (Nbp(2) + Nbp(5) / 2 + Nbp(6) / 2)
                        A1f = Af1t * (Nbp(1) + Nbp(7) / 2 + Nbp(8) / 2)
                        Mu = A1f / Af
                        'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                        If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                            If Af > Afmax Then
                                OutNoProg '5.1
                                End
                            End If
                            Mu_min = Mu_
                        Else
                            Afmax = A1f + D1
                            Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                        End If
                        While Mu < Mu_min And sL(1) >= sLmin
                            'aumenta una barra lembo superiore 1 compresso
                            Nbp(1) = Nbp(1) + 1
                            sL(1) = f_sL(Bsup, Nbp(1), dfp)
                            A1f = Af1t * (Nbp(1) + Nbp(7) / 2 + Nbp(8) / 2)
                            Mu = A1f / Af
                        Wend
                        While Mu < Mu_min And sL(7) >= sLmin
                            'aumenta una barra lembi superiore 7 e 8 compressi
                            Nbp(7) = Nbp(7) + 1
                            Nbp(8) = Nbp(8) + 1
                            sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                            A1f = Af1t * (Nbp(1) + Nbp(7) / 2 + Nbp(8) / 2)
                            Mu = A1f / Af
                        Wend
                        If Mu < Mu_min Then
                            OutNoProg '5.1
                            End
                        End If
                    End If
                ElseIf My < 0 Then
                    Nbp(1) = Nbp(1) + 1 'aumenta lembo 1
                    sL(1) = f_sL(Bsup, Nbp(1), dfp)
                    If FormSez = "a T" Then
                        If sL(1) < sLmin Then 'aumenta barre lembi 5 e 6
                            Nbp(1) = Nbp(1) - 1
                            Nbp(5) = Nbp(5) + 1
                            Nbp(6) = Nbp(6) + 1
                            sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                            If sL(5) < sLmin Then 'aumenta barre lembi 3 e 4
                                Nbp(5) = Nbp(5) - 1
                                Nbp(6) = Nbp(6) - 1
                                Nbp(3) = Nbp(3) + 1
                                Nbp(4) = Nbp(4) + 1
                                sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                                If sL(3) < sLmin Then Exit Do
                            End If
                        End If
                        Af = Af1t * (Nbp(1) + Nbp(5) / 2 + Nbp(6) / 2)
                        A1f = Af1t * (Nbp(2) + Nbp(7) / 2 + Nbp(8) / 2)
                        Mu = A1f / Af
                        'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                        If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                            If Af > Afmax Then
                                OutNoProg '5.1
                                End
                            End If
                            Mu_min = Mu_
                        Else
                            Afmax = A1f + D1
                            Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                        End If
                        While Mu < Mu_min And sL(2) >= sLmin
                            'aumenta una barra lembo superiore 2 compresso
                            Nbp(2) = Nbp(2) + 1
                            sL(2) = f_sL(Binf, Nbp(2), dfp)
                            A1f = Af1t * (Nbp(2) + Nbp(7) / 2 + Nbp(8) / 2)
                            Mu = A1f / Af
                        Wend
                        While Mu < Mu_min And sL(7) >= sLmin
                            'aumenta una barra lembi superiore 7 e 8 compressi
                            Nbp(7) = Nbp(7) + 1
                            Nbp(8) = Nbp(8) + 1
                            sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                            A1f = Af1t * (Nbp(2) + Nbp(7) / 2 + Nbp(8) / 2)
                            Mu = A1f / Af
                        Wend
                        If Mu < Mu_min Then
                            OutNoProg '5.1
                            End
                        End If
                    ElseIf FormSez = "a T rovescia" Then
                        If sL(1) < sLmin Then 'aumenta barre lembi 7 e 8
                            Nbp(1) = Nbp(1) - 1
                            Nbp(7) = Nbp(7) + 1
                            Nbp(8) = Nbp(8) + 1
                            sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                            If sL(7) < sLmin Then Exit Do
                        End If
                        Af = Af1t * (Nbp(1) + Nbp(7) / 2 + Nbp(8) / 2)
                        A1f = Af1t * (Nbp(2) + Nbp(5) / 2 + Nbp(6) / 2)
                        Mu = A1f / Af
                        'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                        If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                            If Af > Afmax Then
                                OutNoProg '5.1
                                End
                            End If
                            Mu_min = Mu_
                        Else
                            Afmax = A1f + D1
                            Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                        End If
                        While Mu < Mu_min And sL(2) >= sLmin
                            'aumenta una barra lembo inferiore 2 compresso
                            Nbp(2) = Nbp(2) + 1
                            sL(2) = f_sL(Binf, Nbp(2), dfp)
                            A1f = Af1t * (Nbp(2) + Nbp(5) / 2 + Nbp(6) / 2)
                            Mu = A1f / Af
                        Wend
                        While Mu < Mu_min And sL(5) >= sLmin
                            'aumenta una barra lembi inferiori 5 e 6 compressi
                            Nbp(5) = Nbp(5) + 1
                            Nbp(6) = Nbp(6) + 1
                            sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                            A1f = Af1t * (Nbp(2) + Nbp(5) / 2 + Nbp(6) / 2)
                            Mu = A1f / Af
                        Wend
                        If Mu < Mu_min Then
                            OutNoProg '5.1
                            End
                        End If
                    End If
                End If
            ElseIf Abs(Mz) > Abs(My) Then
                If Mz >= 0 Then
                    Nbp(6) = Nbp(6) + 1
                    sL(6) = f_sL(S, Nbp(6) + 2, dfp)
                    If sL(6) < sLmin Then 'aumenta barre lembo 4
                        Nbp(6) = Nbp(6) - 1
                        Nbp(4) = Nbp(4) + 1
                        sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                        If sL(4) < sLmin Then 'aumenta barre lembo 1
                            Nbp(4) = Nbp(4) - 1
                            Nbp(1) = Nbp(1) + 1
                            sL(1) = f_sL(Bsup, Nbp(1), dfp)
                            If sL(1) < sLmin Then 'aumenta barre lembo 8
                                Nbp(1) = Nbp(1) - 1
                                Nbp(8) = Nbp(8) + 1
                                sL(8) = f_sL(H - S + 2 * Delta, Nbp(8) + 2, dfp)
                                If sL(8) < sLmin Then 'aumenta barre lembo 2
                                    Nbp(8) = Nbp(8) - 1
                                    Nbp(2) = Nbp(2) + 1
                                    sL(2) = f_sL(Binf, Nbp(2), dfp)
                                    If sL(2) < sLmin Then Exit Do
                                End If
                            End If
                        End If
                    End If
                    Af = Af1t * (Nbp(6) + Nbp(4) + Nbp(8) + Nbp(1) / 2 + Nbp(2) / 2)
                    A1f = Af1t * (Nbp(3) + Nbp(5) + Nbp(7) + Nbp(1) / 2 + Nbp(2) / 2)
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(5) >= sLmin
                        'aumenta una barra lembo superiore 5 compresso
                        Nbp(5) = Nbp(5) + 1
                        sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                        A1f = Af1t * (Nbp(3) + Nbp(5) + Nbp(7) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(3) >= sLmin
                        'aumenta una barra lembo 3
                        Nbp(3) = Nbp(3) + 1
                        sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                        A1f = Af1t * (Nbp(3) + Nbp(5) + Nbp(7) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(7) >= sLmin
                        'aumenta una barra lembo 7
                        Nbp(7) = Nbp(7) + 1
                        sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                        A1f = Af1t * (Nbp(3) + Nbp(5) + Nbp(7) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                ElseIf Mz < 0 Then
                    Nbp(5) = Nbp(5) + 1
                    sL(5) = f_sL(S, Nbp(5) + 2, dfp)
                    If sL(5) < sLmin Then 'aumenta barre lembo 3
                        Nbp(5) = Nbp(5) - 1
                        Nbp(3) = Nbp(3) + 1
                        sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                        If sL(3) < sLmin Then 'aumenta barre lembo 1
                            Nbp(3) = Nbp(3) - 1
                            Nbp(1) = Nbp(1) + 1
                            sL(1) = f_sL(Bsup, Nbp(1), dfp)
                            If sL(1) < sLmin Then 'aumenta barre lembo 7
                                Nbp(1) = Nbp(1) - 1
                                Nbp(7) = Nbp(7) + 1
                                sL(7) = f_sL(H - S + 2 * Delta, Nbp(7) + 2, dfp)
                                If sL(7) < sLmin Then 'aumenta barre lembo 2
                                    Nbp(7) = Nbp(7) - 1
                                    Nbp(2) = Nbp(2) + 1
                                    sL(2) = f_sL(Binf, Nbp(2), dfp)
                                    If sL(2) < sLmin Then Exit Do
                                End If
                            End If
                        End If
                    End If
                    Af = Af1t * (Nbp(5) + Nbp(3) + Nbp(7) + Nbp(1) / 2 + Nbp(2) / 2)
                    A1f = Af1t * (Nbp(4) + Nbp(6) + Nbp(8) + Nbp(1) / 2 + Nbp(2) / 2)
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(6) >= sLmin
                        'aumenta una barra lembo superiore 6 compresso
                        Nbp(6) = Nbp(6) + 1
                        sL(6) = f_sL(S, Nbp(6) + 2, dfp)
                        A1f = Af1t * (Nbp(4) + Nbp(6) + Nbp(8) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(4) >= sLmin
                        'aumenta una barra lembo 4
                        Nbp(4) = Nbp(4) + 1
                        sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                        A1f = Af1t * (Nbp(4) + Nbp(6) + Nbp(8) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(8) >= sLmin
                        'aumenta una barra lembo 8
                        Nbp(8) = Nbp(8) + 1
                        sL(8) = f_sL(H - S + 2 * Delta, Nbp(8) + 2, dfp)
                        A1f = Af1t * (Nbp(4) + Nbp(6) + Nbp(8) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                End If
            End If
        End If
        '5.3.3 calcolo Nbar
        Nbar = 0
        For i = 1 To Npacch Step 1
            Nbar = Nbar + Nbp(i)
        Next i
        '5.3.4 scarica su fg2 i dati sui 4 pacchetti di armatura che verranno poi ripresi da CoordBaricentriTondini e quindi da DatiSezioneCa
        If FormSez = "a T" Then
            PacchArmat 1, Delta, Delta, B - Delta, Delta, Nbp(1), dfp
            PacchArmat 2, (B - Bo) / 2 + Delta, H - Delta, (B + Bo) / 2 - Delta, H - Delta, Nbp(2), dfp
            PacchArmat 3, (B + Bo) / 2 - Delta, S - Delta, B - Delta, S - Delta, Nbp(3), dfp
            PacchArmat 4, Delta, S - Delta, (B - Bo) / 2 + Delta, S - Delta, Nbp(4), dfp
            p = (S - 2 * Delta) / (1 + Nbp(5))
            PacchArmat 5, B - Delta, Delta + p, B - Delta, Delta + p * Nbp(5), Nbp(5), dfp
            p = (S - 2 * Delta) / (1 + Nbp(6))
            PacchArmat 6, Delta, Delta + p, Delta, Delta + p * Nbp(6), Nbp(6), dfp
            p = (H - S) / (1 + Nbp(7))
            PacchArmat 7, (B + Bo) / 2 - Delta, S - Delta + p, (B + Bo) / 2 - Delta, S - Delta + p * Nbp(7), Nbp(7), dfp
            p = (H - S) / (1 + Nbp(8))
            PacchArmat 8, (B - Bo) / 2 + Delta, S - Delta + p, (B - Bo) / 2 + Delta, S - Delta + p * Nbp(8), Nbp(8), dfp
        ElseIf FormSez = "a T rovescia" Then
            PacchArmat 1, (B - Bo) / 2 + Delta, Delta, (B + Bo) / 2 - Delta, Delta, Nbp(1), dfp
            PacchArmat 2, Delta, H - Delta, B - Delta, H - Delta, Nbp(2), dfp
            PacchArmat 3, (B + Bo) / 2 - Delta, H - S + Delta, B - Delta, H - S + Delta, Nbp(3), dfp
            PacchArmat 4, Delta, H - S + Delta, (B - Bo) / 2 + Delta, H - S + Delta, Nbp(4), dfp
            p = (S - 2 * Delta) / (1 + Nbp(5))
            PacchArmat 5, B - Delta, H - S + Delta + p, B - Delta, H - S + Delta + p * Nbp(5), Nbp(5), dfp
            p = (S - 2 * Delta) / (1 + Nbp(6))
            PacchArmat 6, Delta, H - S + Delta + p, Delta, H - S + Delta + p * Nbp(6), Nbp(6), dfp
            p = (H - S) / (1 + Nbp(7))
            PacchArmat 7, (B + Bo) / 2 - Delta, Delta + p, (B + Bo) / 2 - Delta, Delta + p * Nbp(7), Nbp(7), dfp
            p = (H - S) / (1 + Nbp(8))
            PacchArmat 8, (B - Bo) / 2 + Delta, Delta + p, (B - Bo) / 2 + Delta, Delta + p * Nbp(8), Nbp(8), dfp
        End If
        '5.3.5 calcola baricentri tondini e procedi alla vaerifica
        CoordBaricentriTondini '1.1
        DatiSezioneCA '4.1
        If MetodoTA Then
            CalcoloTensNormali Nx, My, Mz, True '4.3
            VerifResistCA_TA '4.5
        ElseIf MetodoSL08 Or MetodoSL18 Then
            VerifResistCA_SLU_TensNorm '4.7
        End If
    Loop Until VerifResist
'6)SEZIONE A DOPPIO T
ElseIf FormSez = "a doppio T" Then
    Npacch = 12
    Foglio2.Cells(3, 42) = Npacch
    ReDim Nbp%(1 To Npacch)
    ReDim sL#(1 To Npacch)
    '6.1)calcolo numero barre per ogni pacchetto in modo che non si superi il passo massimo fissato dall'utente
    Nbp(1) = Nbh(B)
    Nbp(2) = Nbp(1)
    Nbp(3) = Nbh((B - Bo) / 2 + 2 * Delta)
    Nbp(4) = Nbp(3)
    Nbp(5) = Nbp(3)
    Nbp(6) = Nbp(3)
    Nbp(7) = Nbv(S)
    Nbp(8) = Nbp(7)
    Nbp(9) = Nbp(7)
    Nbp(10) = Nbp(7)
    Nbp(11) = Nbv(H - 2 * S + 4 * Delta)
    Nbp(12) = Nbp(11)
    Nbar = 0
    For i = 1 To Npacch Step 1
        Nbar = Nbar + Nbp(i)
    Next i
    Aft = Nbar * Af1t
    sL(1) = f_sL(B, Nbp(1), dfp)
    sL(2) = f_sL(B, Nbp(2), dfp)
    sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
    sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
    sL(5) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(5), dfp)
    sL(6) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(6), dfp)
    sL(7) = f_sL(S, Nbp(7) + 2, dfp)
    sL(8) = f_sL(S, Nbp(8) + 2, dfp)
    sL(9) = f_sL(S, Nbp(9) + 2, dfp)
    sL(10) = f_sL(S, Nbp(10) + 2, dfp)
    sL(11) = f_sL(H - 2 * S + 4 * Delta, Nbp(11) + 2, dfp)
    sL(12) = f_sL(H - 2 * S + 4 * Delta, Nbp(12) + 2, dfp)
    sL_max = Application.Max(sL())
    '6.2)eventuale correzione Nbp() per adeguare ai minimi normativa
    If Pilastro Then
        While Aft < Afmin
            If sL(1) = sL_max Then
                Nbp(1) = Nbp(1) + 1
                sL(1) = f_sL(B, Nbp(1), dfp)
            ElseIf sL(2) = sL_max Then
                Nbp(2) = Nbp(2) + 1
                sL(2) = f_sL(B, Nbp(2), dfp)
            ElseIf sL(3) = sL_max Then
                Nbp(3) = Nbp(3) + 1
                sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
            ElseIf sL(4) = sL_max Then
                Nbp(4) = Nbp(4) + 1
                sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
            ElseIf sL(5) = sL_max Then
                Nbp(5) = Nbp(5) + 1
                sL(5) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(5), dfp)
            ElseIf sL(6) = sL_max Then
                Nbp(6) = Nbp(6) + 1
                sL(6) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(6), dfp)
            ElseIf sL(7) = sL_max Then
                Nbp(7) = Nbp(7) + 1
                sL(7) = f_sL(S, Nbp(7) + 2, dfp)
            ElseIf sL(8) = sL_max Then
                Nbp(8) = Nbp(8) + 1
                sL(8) = f_sL(S, Nbp(8) + 2, dfp)
            ElseIf sL(9) = sL_max Then
                Nbp(9) = Nbp(9) + 1
                sL(9) = f_sL(S, Nbp(9) + 2, dfp)
            ElseIf sL(10) = sL_max Then
                Nbp(10) = Nbp(10) + 1
                sL(10) = f_sL(S, Nbp(10) + 2, dfp)
            ElseIf sL(11) = sL_max Then
                Nbp(11) = Nbp(11) + 1
                sL(11) = f_sL(H - 2 * S + 4 * Delta, Nbp(11) + 2, dfp)
            ElseIf sL(12) = sL_max Then
                Nbp(12) = Nbp(12) + 1
                sL(12) = f_sL(H - 2 * S + 4 * Delta, Nbp(12) + 2, dfp)
            End If
            sL_max = Application.Max(sL())
            Nbar = Nbar + 1
            Aft = Nbar * Af1t
        Wend
    Else 'è trave
        If Abs(Mz) <= Abs(My) Then
            If My >= 0 Then
                Af = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                While Af < Afmin1 And sL(2) >= sLmin 'aumenta una barra lembo 2 inferiore
                    Nbp(2) = Nbp(2) + 1
                    Af = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                    sL(2) = f_sL(B, Nbp(2), dfp)
                Wend
                While Af < Afmin1 And sL(9) >= sLmin 'aumenta una barra lembi laterali inferiori 9-10
                    Nbp(9) = Nbp(9) + 1
                    Nbp(10) = Nbp(10) + 1
                    Af = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                    sL(9) = f_sL(S, Nbp(9) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(5) >= sLmin 'aumenta una barra lembi inferiori 5-6
                    Nbp(5) = Nbp(5) + 1
                    Nbp(6) = Nbp(6) + 1
                    Af = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                    sL(5) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(5), dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            ElseIf My < 0 Then
                Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                While Af < Afmin1 And sL(2) >= sLmin 'aumenta una barra lembo 1 superiore
                    Nbp(1) = Nbp(1) + 1
                    Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                    sL(1) = f_sL(B, Nbp(1), dfp)
                Wend
                While Af < Afmin1 And sL(7) >= sLmin 'aumenta una barra lembi laterali inferiori 7-8
                    Nbp(7) = Nbp(7) + 1
                    Nbp(8) = Nbp(8) + 1
                    Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                    sL(7) = f_sL(S, Nbp(7) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembi inferiori 3-4
                    Nbp(3) = Nbp(3) + 1
                    Nbp(4) = Nbp(4) + 1
                    Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                    sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            End If
        ElseIf Abs(Mz) > Abs(My) Then
            If Mz >= 0 Then
                Af = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                While Af < Afmin1 And sL(8) >= sLmin 'aumenta una barra lembi 8 e 10
                    Nbp(8) = Nbp(8) + 1
                    Nbp(10) = Nbp(10) + 1
                    Af = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                    sL(8) = f_sL(S, Nbp(8) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(4) >= sLmin 'aumenta una barra lembi 4-6
                    Nbp(4) = Nbp(4) + 1
                    Nbp(6) = Nbp(6) + 1
                    Af = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                    sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                Wend
                While Af < Afmin1 And sL(12) >= sLmin 'aumenta una barra lembo 12
                    Nbp(12) = Nbp(12) + 1
                    Af = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                    sL(12) = f_sL(H - 2 * S + 4 * Delta, Nbp(12) + 2, dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            ElseIf Mz < 0 Then
                Af = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                While Af < Afmin1 And sL(7) >= sLmin 'aumenta una barra lembi 7 e 9
                    Nbp(7) = Nbp(7) + 1
                    Nbp(9) = Nbp(9) + 1
                    Af = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                    sL(7) = f_sL(S, Nbp(7) + 2, dfp)
                Wend
                While Af < Afmin1 And sL(3) >= sLmin 'aumenta una barra lembi 3-5
                    Nbp(3) = Nbp(3) + 1
                    Nbp(5) = Nbp(5) + 1
                    Af = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                    sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                Wend
                While Af < Afmin1 And sL(5) >= sLmin 'aumenta una barra lembo 11
                    Nbp(11) = Nbp(11) + 1
                    Af = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                    sL(11) = f_sL(H - 2 * S + 4 * Delta, Nbp(11) + 2, dfp)
                Wend
                If Af < Afmin1 Then
                    OutNoProg '5.1
                    End
                End If
            End If
        End If
    End If
    '6.3 aumenta barre finchè non verifica
    '6.3.1 prima diminuisci di una unità
    If Pilastro Then
        If sL(1) = sL_max Then
            Nbp(1) = Nbp(1) - 1
        ElseIf sL(2) = sL_max Then
            Nbp(2) = Nbp(2) - 1
        ElseIf sL(3) = sL_max Then
            Nbp(3) = Nbp(3) - 1
        ElseIf sL(4) = sL_max Then
            Nbp(4) = Nbp(4) - 1
        ElseIf sL(5) = sL_max Then
            Nbp(5) = Nbp(5) - 1
        ElseIf sL(6) = sL_max Then
            Nbp(6) = Nbp(6) - 1
        ElseIf sL(7) = sL_max Then
            Nbp(7) = Nbp(7) - 1
        ElseIf sL(8) = sL_max Then
            Nbp(8) = Nbp(8) - 1
        ElseIf sL(9) = sL_max Then
            Nbp(9) = Nbp(9) - 1
        ElseIf sL(10) = sL_max Then
            Nbp(10) = Nbp(10) - 1
        ElseIf sL(11) = sL_max Then
            Nbp(11) = Nbp(11) - 1
        ElseIf sL(12) = sL_max Then
            Nbp(12) = Nbp(12) - 1
        End If
    Else
        If Abs(Mz) <= Abs(My) Then
            If My >= 0 Then
                Nbp(2) = Nbp(2) - 1
            Else
                Nbp(1) = Nbp(1) - 1
            End If
        Else
            If Mz >= 0 Then
                Nbp(8) = Nbp(8) - 1
            Else
                Nbp(7) = Nbp(7) - 1
            End If
        End If
    End If
    Do
        '6.3.2 aumenta di una barra il pacchetto più opportuno in base alle sollecitaz agenti
        If Pilastro Then
            If sL(1) = sL_max Then
                Nbp(1) = Nbp(1) + 1
                sL(1) = f_sL(B, Nbp(1), dfp)
                If sL(1) < sLmin Then Exit Do
            ElseIf sL(2) = sL_max Then
                Nbp(2) = Nbp(2) + 1
                sL(2) = f_sL(B, Nbp(2), dfp)
                If sL(2) < sLmin Then Exit Do
            ElseIf sL(3) = sL_max Then
                Nbp(3) = Nbp(3) + 1
                sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                If sL(3) < sLmin Then Exit Do
            ElseIf sL(4) = sL_max Then
                Nbp(4) = Nbp(4) + 1
                sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                If sL(4) < sLmin Then Exit Do
            ElseIf sL(5) = sL_max Then
                Nbp(5) = Nbp(5) + 1
                sL(5) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(5), dfp)
                If sL(4) < sLmin Then Exit Do
            ElseIf sL(6) = sL_max Then
                Nbp(6) = Nbp(6) + 1
                sL(6) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(6), dfp)
                If sL(6) < sLmin Then Exit Do
            ElseIf sL(7) = sL_max Then
                Nbp(7) = Nbp(7) + 1
                sL(7) = f_sL(S, Nbp(7) + 2, dfp)
                If sL(7) < sLmin Then Exit Do
            ElseIf sL(8) = sL_max Then
                Nbp(8) = Nbp(8) + 1
                sL(8) = f_sL(S, Nbp(8) + 2, dfp)
                If sL(8) < sLmin Then Exit Do
            ElseIf sL(9) = sL_max Then
                Nbp(9) = Nbp(9) + 1
                sL(9) = f_sL(S, Nbp(9) + 2, dfp)
                If sL(9) < sLmin Then Exit Do
            ElseIf sL(10) = sL_max Then
                Nbp(10) = Nbp(10) + 1
                sL(10) = f_sL(S, Nbp(10) + 2, dfp)
                If sL(10) < sLmin Then Exit Do
            ElseIf sL(11) = sL_max Then
                Nbp(11) = Nbp(11) + 1
                sL(11) = f_sL(H - 2 * S + 4 * Delta, Nbp(11) + 2, dfp)
                If sL(11) < sLmin Then Exit Do
            ElseIf sL(12) = sL_max Then
                Nbp(12) = Nbp(12) + 1
                sL(12) = f_sL(H - 2 * S + 4 * Delta, Nbp(12) + 2, dfp)
                If sL(12) < sLmin Then Exit Do
            End If
            sL_max = Application.Max(sL())
            Nbar = Nbp(1) + Nbp(2) + Nbp(3) + Nbp(4) + Nbp(5) + Nbp(6) + Nbp(7) + Nbp(8) + Nbp(9) + Nbp(10) + Nbp(11) + Nbp(12)
            Aft = Nbar * A1f
            'verifica che armatura non superi il massimo normativa
            If Aft > Afmax Then
                OutNoProg '5.1
                End
            End If
        Else 'è trave
            If Abs(Mz) <= Abs(My) Then
                If My >= 0 Then
                    Nbp(2) = Nbp(2) + 1 'aumenta barre lembo 2
                    sL(2) = f_sL(B, Nbp(2), dfp)
                    If sL(2) < sLmin Then 'aumenta barre lembi 9 e 10
                        Nbp(2) = Nbp(2) - 1
                        Nbp(9) = Nbp(9) + 1
                        Nbp(10) = Nbp(10) + 1
                        sL(9) = f_sL(S, Nbp(9) + 2, dfp)
                        If sL(9) < sLmin Then 'aumenta barre lembi 5 e 6
                            Nbp(9) = Nbp(9) - 1
                            Nbp(10) = Nbp(10) - 1
                            Nbp(5) = Nbp(5) + 1
                            Nbp(6) = Nbp(6) + 1
                            sL(5) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(5), dfp)
                            If sL(5) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                    A1f = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(1) >= sLmin
                        'aumenta una barra lembo superiore 1 compresso
                        Nbp(1) = Nbp(1) + 1
                        sL(1) = f_sL(B, Nbp(1), dfp)
                        A1f = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(7) >= sLmin
                        'aumenta una barra lembi superiore 7 e 8 compressi
                        Nbp(7) = Nbp(7) + 1
                        Nbp(8) = Nbp(8) + 1
                        sL(7) = f_sL(S, Nbp(7) + 2, dfp)
                        A1f = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(3) >= sLmin
                        'aumenta una barra lembi superiore 3 e 4 compressi
                        Nbp(3) = Nbp(3) + 1
                        Nbp(4) = Nbp(4) + 1
                        sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                        A1f = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                ElseIf My < 0 Then
                    Nbp(1) = Nbp(1) + 1 'aumenta barre lembo 1
                    sL(1) = f_sL(B, Nbp(1), dfp)
                    If sL(1) < sLmin Then 'aumenta barre lembi 7 e 8
                        Nbp(1) = Nbp(1) - 1
                        Nbp(7) = Nbp(7) + 1
                        Nbp(8) = Nbp(8) + 1
                        sL(7) = f_sL(S, Nbp(7) + 2, dfp)
                        If sL(7) < sLmin Then 'aumenta barre lembi 3 e 4
                            Nbp(7) = Nbp(7) - 1
                            Nbp(8) = Nbp(8) - 1
                            Nbp(3) = Nbp(3) + 1
                            Nbp(4) = Nbp(4) + 1
                            sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                            If sL(3) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(1) + Nbp(7) + Nbp(8) + Nbp(3) + Nbp(4) + Nbp(11) / 2 + Nbp(12) / 2)
                    A1f = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(1) >= sLmin
                        'aumenta una barra lembo inferiore 2 compresso
                        Nbp(2) = Nbp(2) + 1
                        sL(2) = f_sL(B, Nbp(2), dfp)
                        A1f = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(9) >= sLmin
                        'aumenta una barra lembi 9 e 10 compressi
                        Nbp(9) = Nbp(9) + 1
                        Nbp(10) = Nbp(10) + 1
                        sL(9) = f_sL(S, Nbp(9) + 2, dfp)
                        A1f = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(5) >= sLmin
                        'aumenta una barra lembi 5 e 6 compressi
                        Nbp(5) = Nbp(5) + 1
                        Nbp(6) = Nbp(6) + 1
                        sL(5) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(5), dfp)
                        A1f = Af1t * (Nbp(2) + Nbp(9) + Nbp(10) + Nbp(5) + Nbp(6) + Nbp(11) / 2 + Nbp(12) / 2)
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                End If
            ElseIf Abs(Mz) > Abs(My) Then
                If Mz >= 0 Then
                    Nbp(8) = Nbp(8) + 1 'aumenta barre lembo 8 e 10
                    Nbp(10) = Nbp(10) + 1
                    sL(8) = f_sL(S, Nbp(8) + 2, dfp)
                    If sL(8) < sLmin Then 'aumenta barre lembi 4 e 6
                        Nbp(8) = Nbp(8) - 1
                        Nbp(10) = Nbp(10) - 1
                        Nbp(4) = Nbp(4) + 1
                        Nbp(6) = Nbp(6) + 1
                        sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                        If sL(4) < sLmin Then 'aumenta barre lembo 12
                            Nbp(4) = Nbp(4) - 1
                            Nbp(6) = Nbp(6) - 1
                            Nbp(12) = Nbp(12) + 1
                            sL(12) = f_sL(H - 2 * S + 4 * Delta, Nbp(12) + 2, dfp)
                            If sL(12) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                    A1f = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(7) >= sLmin
                        'aumenta una barra lembi 7 e 9 compressi
                        Nbp(7) = Nbp(7) + 1
                        Nbp(9) = Nbp(9) + 1
                        sL(7) = f_sL(S, Nbp(7) + 2, dfp)
                        A1f = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(3) >= sLmin
                        'aumenta una barra lembi 3 e 5 compressi
                        Nbp(3) = Nbp(3) + 1
                        Nbp(5) = Nbp(5) + 1
                        sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                        A1f = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(11) >= sLmin
                        'aumenta una barra lembo 11
                        Nbp(11) = Nbp(11) + 1
                        sL(11) = f_sL(H - 2 * S + 4 * Delta, Nbp(11) + 2, dfp)
                        A1f = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                ElseIf Mz < 0 Then
                    Nbp(7) = Nbp(7) + 1 'aumenta barre lembo 7 e 9
                    Nbp(9) = Nbp(9) + 1
                    sL(7) = f_sL(S, Nbp(7) + 2, dfp)
                    If sL(7) < sLmin Then 'aumenta barre lembi 3 e 5
                        Nbp(7) = Nbp(7) - 1
                        Nbp(9) = Nbp(9) - 1
                        Nbp(3) = Nbp(3) + 1
                        Nbp(5) = Nbp(5) + 1
                        sL(3) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(3), dfp)
                        If sL(3) < sLmin Then 'aumenta barre lembo 11
                            Nbp(3) = Nbp(3) - 1
                            Nbp(5) = Nbp(5) - 1
                            Nbp(11) = Nbp(11) + 1
                            sL(11) = f_sL(H - 2 * S + 4 * Delta, Nbp(11) + 2, dfp)
                            If sL(11) < sLmin Then Exit Do
                        End If
                    End If
                    Af = Af1t * (Nbp(7) + Nbp(9) + Nbp(3) + Nbp(5) + Nbp(11) + Nbp(1) / 2 + Nbp(2) / 2)
                    A1f = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                    Mu = A1f / Af
                    'verifica che non si superi Afmax e che si rispetti rapp armatura Mu_
                    If MetodoTA Or ZonaSismStruttDissip = False Or TraveFondaz Then
                        If Af > Afmax Then
                            OutNoProg '5.1
                            End
                        End If
                        Mu_min = Mu_
                    Else
                        Afmax = A1f + D1
                        Mu_min = Application.Max(Mu_, 1 - D1 / Af)
                    End If
                    While Mu < Mu_min And sL(7) >= sLmin
                        'aumenta una barra lembi 8 e 10 compressi
                        Nbp(8) = Nbp(8) + 1
                        Nbp(10) = Nbp(10) + 1
                        sL(8) = f_sL(S, Nbp(8) + 2, dfp)
                        A1f = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(4) >= sLmin
                        'aumenta una barra lembi 4 e 6 compressi
                        Nbp(4) = Nbp(4) + 1
                        Nbp(6) = Nbp(6) + 1
                        sL(4) = f_sL((B - Bo) / 2 + 2 * Delta, Nbp(4), dfp)
                        A1f = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    While Mu < Mu_min And sL(12) >= sLmin
                        'aumenta una barra lembo 12
                        Nbp(12) = Nbp(12) + 1
                        sL(12) = f_sL(H - 2 * S + 4 * Delta, Nbp(12) + 2, dfp)
                        A1f = Af1t * (Nbp(8) + Nbp(10) + Nbp(4) + Nbp(6) + Nbp(12) + Nbp(1) / 2 + Nbp(2) / 2)
                        Mu = A1f / Af
                    Wend
                    If Mu < Mu_min Then
                        OutNoProg '5.1
                        End
                    End If
                End If
            End If
        End If
        '6.3.3 calcolo Nbar
        Nbar = 0
        For i = 1 To Npacch Step 1
            Nbar = Nbar + Nbp(i)
        Next i
        '6.3.4 scarica su fg2 i dati sui 4 pacchetti di armatura che verranno poi ripresi da CoordBaricentriTondini e quindi da DatiSezioneCa
        PacchArmat 1, Delta, Delta, B - Delta, Delta, Nbp(1), dfp
        PacchArmat 2, Delta, H - Delta, B - Delta, H - Delta, Nbp(2), dfp
        PacchArmat 3, (B + Bo) / 2 - Delta, S - Delta, B - Delta, S - Delta, Nbp(3), dfp
        PacchArmat 4, Delta, S - Delta, (B - Bo) / 2 + Delta, S - Delta, Nbp(4), dfp
        PacchArmat 5, (B + Bo) / 2 - Delta, H - S + Delta, B - Delta, H - S + Delta, Nbp(5), dfp
        PacchArmat 6, Delta, H - S + Delta, (B - Bo) / 2 + Delta, H - S + Delta, Nbp(6), dfp
        p = (S - 2 * Delta) / (1 + Nbp(7))
        PacchArmat 7, B - Delta, Delta + p, B - Delta, Delta + p * Nbp(7), Nbp(7), dfp
        p = (S - 2 * Delta) / (1 + Nbp(8))
        PacchArmat 8, Delta, Delta + p, Delta, Delta + p * Nbp(8), Nbp(8), dfp
        p = (S - 2 * Delta) / (1 + Nbp(9))
        PacchArmat 9, B - Delta, H - S + Delta + p, B - Delta, H - S + Delta + p * Nbp(9), Nbp(9), dfp
        p = (S - 2 * Delta) / (1 + Nbp(10))
        PacchArmat 10, Delta, H - S + Delta + p, Delta, H - S + Delta + p * Nbp(10), Nbp(10), dfp
        p = (H - 2 * S + 2 * Delta) / (1 + Nbp(11))
        PacchArmat 11, (B + Bo) / 2 - Delta, S - Delta + p, (B + Bo) / 2 - Delta, S - Delta + p * Nbp(11), Nbp(11), dfp
        p = (H - 2 * S + 2 * Delta) / (1 + Nbp(12))
        PacchArmat 12, (B - Bo) / 2 + Delta, S - Delta + p, (B - Bo) / 2 + Delta, S - Delta + p * Nbp(12), Nbp(12), dfp
        '6.3.5 calcola baricentri tondini e procedi alla vaerifica
        CoordBaricentriTondini '1.1
        DatiSezioneCA '4.1
        If MetodoTA Then
            CalcoloTensNormali Nx, My, Mz, True '4.3
            VerifResistCA_TA '4.5
        ElseIf MetodoSL08 Or MetodoSL18 Then
            VerifResistCA_SLU_TensNorm '4.7
        End If
    Loop Until VerifResist
End If
'7)OUTPUT (armatura di progetto)
With Foglio1
    If VerifResist = False Then
        .Range(Cells(iF1, 1), Cells(iF1 + 2, 1)).Select
         FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
        .Cells(iF1, 1) = "Calcolo di progetto non possibile: l'armatura necessaria non è fisicamente posizionabile lungo"
        .Cells(iF1 + 1, 1) = "i lembi della sezione. Occorre variare i dati di progetto (forma e/o dimensioni sezione,"
        .Cells(iF1 + 2, 1) = "materiali, diametro tondini, interferro ecc.)"
        iF1 = iF1 + 3
    Else
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "ARMATURA DI PROGETTO"
        iF1 = iF1 + 1
        If FormSez = "Rettangolare" Or FormSez = "Scatolare" Then
            .Cells(iF1, 1) = "tondini lembo superiore: " & Nbp(1) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(1) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 1, 1) = "tondini lembo inferiore: " & Nbp(2) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(2) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 2, 1) = "tondini lembo sinistro: " & Nbp(3) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(3) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 3, 1) = "tondini lembo destro: " & Nbp(4) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(4) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 4, 1) = "armatura complessiva: " & Nbar & " fi " & dfp / fmDiamTond & " (" & Round(Aft / fmL2, 2) & umL2 & ")"
            iF1 = iF1 + 5
        ElseIf FormSez = "a T" Or FormSez = "a T rovescia" Then
            .Cells(iF1, 1) = "tondini lembo superiore: " & Nbp(1) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(1) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 1, 1) = "tondini lembo inferiore: " & Nbp(2) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(2) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 2, 1) = "tondini lembo orizzontale intermedio sinistro: " & Nbp(3) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(3) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 3, 1) = "tondini lembo orizzontale intermedio destro: " & Nbp(4) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(4) / fmL2, 2) & umL2 & ")"
            If FormSez = "a T" Then
                .Cells(iF1 + 4, 1) = "tondini lembo verticale sinistro superiore: " & Nbp(5) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(5) / fmL2, 2) & umL2 & ")"
                .Cells(iF1 + 5, 1) = "tondini lembo verticale destro superiore: " & Nbp(6) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(6) / fmL2, 2) & umL2 & ")"
                .Cells(iF1 + 6, 1) = "tondini lembo verticale sinistro inferiore: " & Nbp(7) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(7) / fmL2, 2) & umL2 & ")"
                .Cells(iF1 + 7, 1) = "tondini lembo verticale destro inferiore: " & Nbp(8) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(8) / fmL2, 2) & umL2 & ")"
            ElseIf FormSez = "a T rovescia" Then
                .Cells(iF1 + 4, 1) = "tondini lembo verticale sinistro inferiore: " & Nbp(5) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(5) / fmL2, 2) & umL2 & ")"
                .Cells(iF1 + 5, 1) = "tondini lembo verticale destro enferiore: " & Nbp(6) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(6) / fmL2, 2) & umL2 & ")"
                .Cells(iF1 + 6, 1) = "tondini lembo verticale sinistro superiore: " & Nbp(7) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(7) / fmL2, 2) & umL2 & ")"
                .Cells(iF1 + 7, 1) = "tondini lembo verticale destro inferiore: " & Nbp(8) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(8) / fmL2, 2) & umL2 & ")"
            End If
            .Cells(iF1 + 8, 1) = "armatura complessiva: " & Nbar & " fi " & dfp / fmDiamTond & " (" & Round(Aft / fmL2, 2) & umL2 & ")"
            iF1 = iF1 + 9
        ElseIf FormSez = "a doppio T" Then
            .Cells(iF1, 1) = "tondini lembo superiore: " & Nbp(1) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(1) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 1, 1) = "tondini lembo inferiore: " & Nbp(2) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(2) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 2, 1) = "tondini lembo orizzontale superiore sinistro: " & Nbp(3) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(3) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 3, 1) = "tondini lembo orizzontale superiore destro: " & Nbp(4) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(4) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 4, 1) = "tondini lembo orizzontale inferiore sinistro: " & Nbp(5) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(5) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 5, 1) = "tondini lembo orizzontale inferiore destro: " & Nbp(6) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(6) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 6, 1) = "tondini lembo verticale sinistro superiore: " & Nbp(7) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(7) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 7, 1) = "tondini lembo verticale destro superiore: " & Nbp(8) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(8) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 8, 1) = "tondini lembo verticale sinistro centrale: " & Nbp(9) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(9) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 9, 1) = "tondini lembo verticale destro centrale: " & Nbp(10) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(10) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 10, 1) = "tondini lembo verticale sinistro inferiore: " & Nbp(11) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(11) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 11, 1) = "tondini lembo verticale destro infereriore: " & Nbp(12) & " fi " & dfp / fmDiamTond & " (" & Round(Af1t * Nbp(12) / fmL2, 2) & umL2 & ")"
            .Cells(iF1 + 12, 1) = "armatura complessiva: " & Nbar & " fi " & dfp / fmDiamTond & " (" & Round(Aft / fmL2, 2) & umL2 & ")"
            iF1 = iF1 + 13
        ElseIf FormSez = "Circolare piena o cava" Then
            .Cells(iF1, 1) = "tondini: " & Nbar & " fi " & dfp / fmDiamTond & " (" & Round(Nbar * Af1t / fmL2, 2) & umL2 & ")"
            iF1 = iF1 + 1
        End If
        'minimi e massimi di armatura
        If MetodoTA Then
            If Pilastro Then
                .Cells(iF1, 1) = "N.B. Le sezioni delle armature determinate rispettano i minimi e massimi previsti dalla normativa"
                .Cells(iF1 + 1, 1) = "armatura minima:"
                If FormSez = "Circolare piena o cava" Then
                    .Cells(iF1 + 2, 1) = "   1) almeno 6 tondini"
                Else
                    .Cells(iF1 + 2, 1) = "   1) almeno 4 tondini del diametro 12 mm, di area complessiva pari a 4,52 cmq"
                End If
                .Cells(iF1 + 3, 1) = "   2) 0,3% Asez=" & Round(Afmin1 / fmL2, 2) & " cmq"
                iF1 = iF1 + 4
                If Nx < 0 Then
                    .Cells(iF1, 1) = "   3) 0,8% Ac strett. necessaria=" & Round(Afmin2 / fmL2, 2) & " cmq"
                    iF1 = iF1 + 1
                End If
                .Cells(iF1, 1) = "armatura massima,   Afmax=6% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
                iF1 = iF1 + 1
            Else 'trave
                .Cells(iF1, 1) = "N.B. Le sezioni delle armature determinate rispettano i minimi e massimi previsti dalla normativa"
                .Cells(iF1 + 1, 1) = "Armatura minima in zona tesa pari allo 0,15% di Asez (" & Round(0.0015 * Asez / fmL2, 2) & " cmq), per "
                .Cells(iF1 + 2, 1) = "   barre ad aderenza migliorata, e allo 0,25% di Asez (" & Round(0.0025 * Asez / fmL2, 2) & " cmq) per barre lisce."
                .Cells(iF1 + 3, 1) = "Armatura massima in zona tesa,   Afmax=4% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
                iF1 = iF1 + 4
            End If
        ElseIf MetodoSL08 Or MetodoSL18 Then
            If Pilastro Then
                .Cells(iF1, 1) = "N.B. Le sezioni delle armature determinate rispettano i minimi e massimi previsti dalla normativa"
                .Cells(iF1 + 1, 1) = "armatura minima:"
                .Cells(iF1 + 2, 1) = "   1) 0,3% Asez=" & Round(Afmin1 / fmL2, 2) & " cmq"
                iF1 = iF1 + 3
                If ZonaSismStruttDissip Then
                    .Cells(iF1, 1) = "   2) strutture a comportam. dissipativo in zona sismica,   1% Asez=" & Round(Afmin2 / fmL2, 2) & " cmq"
                    iF1 = iF1 + 1
                Else
                    If Nx < 0 Then
                        .Cells(iF1, 1) = "   2) 0,1 del rapporto Nx/fyd    -> " & Round(Afmin2 / fmL2, 2) & " cmq"
                        iF1 = iF1 + 1
                    End If
                End If
                .Cells(iF1, 1) = "armatura massima,   Afmax=4% Asez=" & Round(0.04 * Asez / fmL2, 2) & " cmq"
                iF1 = iF1 + 1
            Else
                .Cells(iF1, 1) = "N.B. Le sezioni delle armature determinate rispettano i minimi e massimi previsti dalla normativa"
                .Cells(iF1 + 1, 1) = "Armatura minima in zona tesa,   Afmin1=" & Round(Afmin1 / fmL2, 2) & " cmq"
                iF1 = iF1 + 2
                If Trave And ZonaSismStruttDissip Then
                    .Cells(iF1, 1) = "Armatura massima in zona tesa,   Afmax=A'f+3,5 Asez/fyk=" & Round(Afmax / fmL2, 2) & " cmq"
                Else
                    .Cells(iF1, 1) = "Armatura massima in zona tesa,   Afmax=4% Asez=" & Round(Afmax / fmL2, 2) & " cmq"
                End If
                iF1 = iF1 + 1
            End If
        End If
    End If
End With
'8)VERIFICHE DI RESISTENZA SEZIONE PROGETTATA E OUTPUT
If VerifResist Then
    CalcVerif = True
    DatiSezioneCA '4.1
    OutDatiSezioneCA '4.2
    If MetodoTA Then
        CalcoloTensNormali Nx, My, Mz, True '4.3
        OutCalcoloTensNormali '4.4
        VerifResistCA_TA '4.5
    ElseIf MetodoSL08 Or MetodoSL18 Then
        VerifResistCA_SLU_TensNorm '4.7
    End If
    CalcVerif = False
End If
End Sub

Function Nbh%(L#) '5.2
'calcola il numero di barre (min 2) in un generico pacchetto orizzontale in modo da non superare il massimo interasse fissato dall'utente
Dim p#
Nbh = 1
Do
    Nbh = Nbh + 1
    p = f_sL(L, Nbh, dfp) + dfp
Loop Until p <= Pmax
End Function

Function f_sL#(L#, Nb%, Df#) '5.2.1
'spazio libero tra le barre in un lembo di sezione
f_sL = Round((L - 2 * Cf - Nb * Df) / (Nb - 1), 2)
End Function

Function Nbv%(L#) '5.3
'calcola il numero di barre (min 0) in un generico pacchetto verticale in modo da non superare il massimo interasse fissato dall'utente
Dim p#
Nbv = -1
Do
    Nbv = Nbv + 1
    p = (L - 2 * Delta) / (1 + Nbv)
Loop Until p <= Pmax
End Function

Sub PacchArmat(n As Byte, yin#, zin#, yfi#, zfi#, Nb%, dfp#) '5.4
With Foglio2
    .Cells(4 + n, 38) = yin / fmL
    .Cells(4 + n, 39) = zin / fmL
    .Cells(4 + n, 40) = yfi / fmL
    .Cells(4 + n, 41) = zfi / fmL
    .Cells(4 + n, 42) = Nb
    .Cells(4 + n, 43) = dfp / fmDiamTond
End With
End Sub

Sub Taglio() '6.
'Verifica a taglio o progetto con calcolo armature a taglio x sezioni in C.A. con metodi T.A. e S.L.U.
Const Nc = 41
Dim alfac#, Afj#
Dim Bw_z#, Bw_y#, b_i#, Beta_st#
Dim CotgAlfa#
Dim Deltz#, d_i#, d_j#, dmin#
Dim fbd#, FiR#
Dim i1%, i%
Dim Hu_z#, Hu_y#, H1#
Dim Ys_min#
Dim k#, Kb#, Kg#
Dim LamdaFd#, Led1#
Dim Nst#
Dim Pst_ta_z#, Pst_ta_y#, Pst_r1#, Pst_r2#, Pst_r3#, Pst_r4#, Pst_r#
Dim ro_l#, Rapp#
Dim Syr_st#, Syr_st_c#, Syr_st_b#
Dim Sig_cp#, Sst#, SecondoTermine#
Dim Tau_xz#()
Dim Tcls_z#, Tcls_y#
Dim v#, v_min#
Dim Vrcd_z#, Vrcd_y#, Vrsd_z#, Vrsd_y#, Vrpd_z#, Vrpd_y#, Vrd_z#, Vrd_y#, Vrj_z#, Vrj_y#
Dim Zs_min#
Dim z_compr#(1 To 10), z1#, z2#, z_i#, z_ib#, zb_j#
'ESECUZ
If Ty <> 0 Or Tz <> 0 Then
    With Foglio1
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        If CalcVerif Then
            .Cells(iF1, 1) = "VERIFICA A TAGLIO (Stato limite di resistenza)"
        Else
            .Cells(iF1, 1) = "PROGETTO A TAGLIO (Stato limite di resistenza)"
        End If
        iF1 = iF1 + 1
    End With
    If FormSez = "Rettangolare" Or FormSez = "a T" Or FormSez = "a T rovescia" Or FormSez = "a doppio T" Or FormSez = "Circolare piena o cava" Or FormSez = "Scatolare" Then
        'calcolo altezze utili Hu_z, Hu_y
        Zs_min = Zmin_pr - zG_pr
        Hu_z = Application.Max(Zb()) - Zs_min
        Ys_min = Ymin_pr - yG_pr
        Hu_y = Application.Max(Yb()) - Ys_min
        'calcolo basi
        If FormSez = "Rettangolare" Then
            Bw_z = B
            Bw_y = H
            dmin = Application.Min(B, H) 'dimens minima sezione
        ElseIf FormSez = "a T" Or FormSez = "a T rovescia" Then
            Bw_z = Bo
            Bw_y = S
            dmin = Application.Min(B, H)
        ElseIf FormSez = "a doppio T" Then
            Bw_z = Bo
            Bw_y = 2 * S
            dmin = Application.Min(B, H)
        ElseIf FormSez = "Circolare piena o cava" Then
            If Di = 0 Then
                Bw_z = H / 2 * (PiGreco ^ 0.5)
            Else
                Bw_z = D - Di
            End If
            Bw_y = Bw_z
            dmin = D
        ElseIf FormSez = "Scatolare" Then
            Bw_z = 2 * S
            Bw_y = Bw_z
            dmin = Application.Min(B, H)
        End If
        '1. METODO T.A.
        If MetodoTA Then
            If Ty = 0 Then
                '1.1 Calcolo ordinate z1 e z2 che individuano la zona compressa della sezione
                k = 0
                For j = 1 To Npolig_ns Step 1
                    Np = Foglio2.Cells(107, 22 + 2 * j)
                    If Np > 0 Then
                        ReDim Ys_pr#(1 To Np)
                        ReDim Zs_pr#(1 To Np)
                    End If
                    For i = 1 To Np Step 1
                        Ys_pr(i) = Foglio2.Cells(108 + i, 21 + 2 * j) * fmL
                        Zs_pr(i) = Foglio2.Cells(108 + i, 22 + 2 * j) * fmL
                    Next i
                    For i = 1 To Np Step 1
                        If i = Np Then i1 = 1 Else i1 = i + 1
                        If Ys_pr(i) <> Ys_pr(i1) Then
                            If (Ys_pr(i) <= 0 And Ys_pr(i1) >= 0) Or (Ys_pr(i) >= 0 And Ys_pr(i1) <= 0) Then
                                k = k + 1
                                z_compr(k) = (Zs_pr(i) * Ys_pr(i1) - Zs_pr(i1) * Ys_pr(i)) / (Ys_pr(i1) - Ys_pr(i)) - zG_pr
                            End If
                        End If
                    Next i
                Next j
                z1 = z_compr(1)
                z2 = z1
                For i = 2 To k Step 1
                    If z_compr(k) < z1 Then z1 = z_compr(k)
                    If z_compr(k) > z2 Then z2 = z_compr(k)
                Next i
                '1.2) Calcolo tensioni tangenziali in ogni corda e output x grafico
                ReDim Tau_xz#(1 To Nc)
                Syr_st = 0
                Deltz = H / (Nc + 1)
                For i = 1 To Nc Step 1
                    z_i = (Zmax_pr - zG_pr) - Deltz * i
                    z_ib = z_i + Deltz / 2
                    CosAlfa_ii = 1
                    SinAlfa_ii = 0
                    Calcola_Lsi_yci z_i
                    b_i = Lsi
                    Calcola_Lsi_yci z_ib
                    If z_ib >= z1 And z_ib <= z2 Then
                        d_i = z_ib + (zG_pr - zGr_pr)
                        Syr_st_c = Syr_st_c + Lsi * Deltz * d_i
                    End If
                    Syr_st_b = 0
                    For j = 1 To Nbar Step 1
                        zb_j = Zb_pr(j) - zG_pr
                        If zb_j > z_i Then
                            d_j = zb_j + (zG_pr - zGr_pr)
                            Afj = PiGreco * Db(j) ^ 2 / 4
                            Syr_st_b = Syr_st_b + n * Afj * d_j
                        End If
                    Next j
                    Syr_st = Syr_st_c + Syr_st_b
                    Tau_xz(i) = Abs(Tz) * Syr_st / (Iyr * b_i)
                    'output su Fg4
                    With Foglio4
                        .Cells(5 + i, 18) = Round(z_i / fmL, 2)
                        .Cells(5 + i, 19) = Round(b_i / fmL, 2)
                        .Cells(5 + i, 20) = Round(Syr_st / fmL3, 2)
                        .Cells(5 + i, 21) = Round(Tau_xz(i) / fmFL_2, 2)
                        .Cells(5 + i, 22) = Round(Syr_st_c / fmL3, 2)
                        .Cells(5 + i, 23) = Round(Syr_st_b / fmL3, 2)
                    End With
                Next i
                '1.3 Calcolo tensione tang massima e output su Fg4
                Tauxz_max = Application.Max(Tau_xz())
                Foglio4.Cells(49, 21) = Round(Tauxz_max / fmFL_2, 2)
                Foglio4.Cells(5, 18) = Round((Zmax_pr - zG_pr) / fmL, 2)
                Foglio4.Cells(47, 18) = Round((Zmin_pr - zG_pr) / fmL, 2)
                '1.4) Verifica o progetto a taglio
                If Tauxz_max > TauC1 Then
                    With Foglio1
                        .Cells(iF1, 1).Select
                        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                        .Cells(iF1, 1) = "Occorre riprogettare la sezione: tensioni tangenziali molto elevate"
                        iF1 = iF1 + 1
                    End With
                Else
                    'calcolo passo da armatura minima regolamentare
                    If Pilastro Then
                        Pst_r1 = 25 * fmL 'passo massimo 25 cm
                        Pst_r2 = 15 * Application.Min(Db())
                        Pst_r = Int(Application.Min(Pst_r1, Pst_r2))
                    Else 'è trave
                        Pst_r1 = 33.3 * fmL '3 staffe al metro
                        Pst_r2 = 0.8 * Hu_z
                        Nst = 0.1 * Bw_z / Asw_taz
                        Pst_r3 = 100 * fmL / Nst
                        Pst_r = Int(Application.Min(Pst_r1, Pst_r2, Pst_r3))
                    End If
                    'ulteriori casi
                    If Tauxz_max > TauC0 Then
                        'scorrimento valutato su un metro di trave (ip di Tauxz_max cost) fatto assorbire interamente alle staffe
                        Sst = Bw_z * (100 * fmL) * Tauxz_max
                        If CalcVerif Then
                            Sigf = Pst_ta * Sst * Sin(Teta_ta) / (100 * fmL * Asw_taz * Sin(PiGreco - Teta_ta - Alfa_ta))
                        Else
                            Nst = Sst * Sin(Teta_ta) / (Asw_taz * Sigfa * Sin(PiGreco - Teta_ta - Alfa_ta))
                            If Nst = 0 Then
                                Pst_ta = Pst_r
                            Else
                                Pst_ta = 100 * fmL / Nst
                                If Pst_ta > Pst_r Then Pst_ta = Pst_r
                            End If
                        End If
                        With Foglio1
                            .Cells(iF1, 1) = "tensione tangenziale massima nel cls,   txz_max=" & Round(Tauxz_max / fmFL_2, 2) & umTens
                            .Cells(iF1 + 1, 1) = "Occorre specifica armatura a taglio"
                            If CalcVerif Then
                                .Cells(iF1 + 2, 1) = "tensione nell'armatura trasversale,   sig_f=" & FormatNumber(Sigf / fmFL_2, 2, , , vbTrue) & umTens
                                If Sigf <= Sigfa Then
                                    .Cells(iF1 + 3, 1) = "Verifica a taglio soddisfatta"
                                Else
                                    .Cells(iF1 + 3, 1).Select
                                    FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                                    .Cells(iF1 + 3, 1) = "Verifica a taglio non soddisfatta"
                                End If
                            Else
                                .Cells(iF1 + 2, 1) = "passo massimo delle armature trasversali da prescrizione regolamentari,   p_r=" & Round(Pst_r / fmL, 1) & umL
                                .Cells(iF1 + 3, 1) = "passo adottato per le armature trasversali,   p=" & Round(Pst_ta / fmL, 1) & umL
                            End If
                            iF1 = iF1 + 5
                        End With
                    ElseIf Tauxz_max <= TauC0 Then
                        With Foglio1
                            .Cells(iF1, 1) = "Tensione tangenziale massima,   txz_max=" & Round(Tauxz_max / fmFL_2, 2) & umTens
                            .Cells(iF1 + 1, 1) = "Non occorre specifica armatura a taglio"
                            .Cells(iF1 + 2, 1) = "Passo delle armature trasversali da prescrizione regolamentari,   p_r=" & Round(Pst_r / fmL, 1) & umL
                            iF1 = iF1 + 4
                        End With
                    End If
                End If
            ElseIf Ty <> 0 Then
                With Foglio1
                    .Cells(iF1, 1) = "Calcolo non implementato per taglio deviato con il metodo alle tens. ammissibili"
                    iF1 = iF1 + 2
                End With
            End If
        '2. METODO AGLI STATI LIMITE
        ElseIf MetodoSL08 Or MetodoSL18 Then
            '2.1 calcolo passo staffe regolamentare
            'If CalcVerif = False Then
                If ZonaSismStruttDissip Then
                    If Pilastro Then
                        If blnCDA Then
                            Pst_r1 = 1 / 3 * dmin
                            Pst_r2 = 12.5 * fmL
                            Pst_r3 = 6 * Application.Min(Db())
                        Else
                            Pst_r1 = 1 / 2 * dmin
                            Pst_r2 = 17.5 * fmL
                            Pst_r3 = 8 * Application.Min(Db())
                        End If
                        Pst_r = Int(Application.Min(Pst_r1, Pst_r2, Pst_r3))
                    Else 'è trave
                        Pst_r1 = 0.25 * Hu_z
                        If blnCDA Then
                            Pst_r2 = 17.5 * fmL
                            Pst_r3 = 6 * Application.Min(Db())
                        Else
                            Pst_r2 = 22.5 * fmL
                            Pst_r3 = 8 * Application.Min(Db())
                        End If
                        Pst_r4 = 24 * Dst_ta
                        Pst_r = Int(Application.Min(Pst_r1, Pst_r2, Pst_r3, Pst_r4))
                    End If
                Else
                    If Pilastro Then
                        Pst_r1 = 25 * fmL 'passo massimo 25 cm
                        Pst_r2 = 12 * Application.Min(Db())
                        Pst_r = Int(Application.Min(Pst_r1, Pst_r2))
                    Else 'è trave
                        Pst_r1 = 33.3 * fmL '3 staffe al metro
                        Pst_r2 = 0.8 * Hu_z
                        Nst = 1.5 * Bw_z / (Asw_taz * fc3)
                        Pst_r3 = 100 * fmL / Nst
                        If MetodoSL18 Then
                            Pst_r4 = 15 * Application.Min(Db())
                            Pst_r = Int(Application.Min(Pst_r1, Pst_r2, Pst_r3, Pst_r4))
                        Else
                            Pst_r = Int(Application.Min(Pst_r1, Pst_r2, Pst_r3))
                        End If
                    End If
                End If
            'End If
            '2.2 Calcolo della resistenza Tcls (taglio sopportato dal solo cls)
            'sigcp
            If Ned < 0 Then
                Sig_cp = Abs(Ned) / Asez
                If Sig_cp > 0.2 * fcd Then Sig_cp = 0.2 * fcd
            ElseIf Ned >= 0 Then
                Sig_cp = 0
            End If
            'Tcls_z
            ro_l = Aft / (Bw_z * Hu_z)
            If ro_l > 0.02 Then ro_l = 0.02
            k = 1 + (200 / (Hu_z * fc3)) ^ 0.5
            v_min = (0.035 * k ^ 1.5 * (fck * fc1) ^ 0.5) / fc1
            v = ((0.18 * k * (100 * ro_l * fck * fc1) ^ (1 / 3)) / Gammac) / fc1
            If v < v_min Then v = v_min
            Tcls_z = (v + 0.15 * Sig_cp) * Bw_z * Hu_z
            'Tcls_y
            ro_l = Aft / (Bw_y * Hu_y)
            If ro_l > 0.02 Then ro_l = 0.02
            k = 1 + (200 / (Hu_y * fc3)) ^ 0.5
            v_min = (0.035 * k ^ 1.5 * (fck * fc1) ^ 0.5) / fc1
            v = ((0.18 * k * (100 * ro_l * fck * fc1) ^ (1 / 3)) / Gammac) / fc1
            If v < v_min Then v = v_min
            Tcls_y = (v + 0.15 * Sig_cp) * Bw_y * Hu_y
            '2.3 Calcolo resistenze Vrcd lato cls
            Sig_cp = -Ned / Asez
            If Sig_cp <= 0 Then
                alfac = 1
            ElseIf Sig_cp < 0.25 * fcd Then
                alfac = 1 + Sig_cp / fcd
            ElseIf Sig_cp < 0.5 * fcd Then
                alfac = 1.25
            ElseIf Sig_cp < fcd Then
                alfac = 2.5 * (1 - Sig_cp / fcd)
            Else
                alfac = 0
            End If
            If RinfFRP Then 'l'angolo alfa è quello delle fibre FRP
                If Round(Alfa_ta_frp, 6) = Round(PiGreco / 2, 6) Then
                    CotgAlfa = 0
                Else
                    CotgAlfa = 1 / Tan(Alfa_ta_frp)
                End If
            Else
                If Round(Alfa_ta, 6) = Round(PiGreco / 2, 6) Then
                    CotgAlfa = 0
                Else
                    CotgAlfa = 1 / Tan(Alfa_ta)
                End If
            End If
            Vrcd_z = 0.9 * Bw_z * Hu_z * alfac * (0.5 * fcd) * (1 / Tan(Teta_ta) + CotgAlfa) * (Sin(Teta_ta)) ^ 2
            Vrcd_y = 0.9 * Bw_y * Hu_y * alfac * (0.5 * fcd) * (1 / Tan(Teta_ta) + CotgAlfa) * (Sin(Teta_ta)) ^ 2
            '2.4 Verifica con calcolo resistenza lato armatura e reistenza al taglio. Calcolo armatura
            If CalcVerif Then
                'resistenze lato armatura
                If Round(Alfa_ta, 6) = Round(PiGreco / 2, 6) Then
                    CotgAlfa = 0
                Else
                    CotgAlfa = 1 / Tan(Alfa_ta)
                End If
                Vrsd_z = 0.9 * Hu_z * Asw_taz / Pst_ta * fyd * (1 / Tan(Teta_ta) + CotgAlfa) * Sin(Alfa_ta)
                Vrsd_y = 0.9 * Hu_y * Asw_tay / Pst_ta * fyd * (1 / Tan(Teta_ta) + CotgAlfa) * Sin(Alfa_ta)
                'resistenza FRP
                If RinfFRP Then
                    If Round(Alfa_ta_frp, 6) = Round(PiGreco / 2, 6) Then
                        CotgAlfa = 0
                    Else
                        CotgAlfa = 1 / Tan(Alfa_ta_frp)
                    End If
                    'lungo z
                    'calcolo lunghezza ottimale di ancoraggio Led, resistenza ffdd per distacco di estremità e ffed
                    If ContinuitàFRP = "discontinuo" Then
                        Rapp = B_f / p_f
                    ElseIf ContinuitàFRP = "continuo o strisce adiacenti" Then
                        Rapp = B_f / (Application.Min(0.9 * Hu_z, Perc_H * H) * Sin(Teta_ta + Alfa_ta_frp) / Sin(Teta_ta))
                    End If
                    If Rapp < 0.25 Then Rapp = 0.25
                    Kb = ((2 - Rapp) / (1 + Rapp)) ^ 0.5
                    If Kb < 1 Then Kb = 1
                    If TipoFRP = "composito preformato" Then
                        Kg = 0.023 / fc3
                    ElseIf TipoFRP = "composito impregnato in situ" Then
                        Kg = 0.037 / fc3
                    End If
                    LamdaFd = (Kb * Kg / FC) * (fcm * fctm) ^ 0.5
                    fbd = 2 * LamdaFd / (0.25 / fc3)
                    Led1 = (1 / (1.25 * fbd)) * (PiGreco ^ 2 * E_frp * t_f * LamdaFd / 2) ^ 0.5
                    Led = Application.Max(200 / fc3, Led1)
                    ffdd = (1 / Gammaf_dist) * (2 * E_frp * LamdaFd / t_f) ^ 0.5
                    H1 = Application.Min(0.9 * Hu_z, Perc_H * H)
                    If DisposizFRP = "ad U" Then
                        ffed = ffdd * (1 - 1 / 3 * Led * Sin(Alfa_ta_frp) / H1)
                    ElseIf DisposizFRP = "in avvolgimento" Then
                        Rapp = rc / B
                        If Rapp > 0.5 Then Rapp = 0.5
                        FiR = 0.2 + 1.6 * Rapp
                        SecondoTermine = 0.5 * (FiR * fpd - ffdd) * (1 - Led * Sin(Alfa_ta_frp) / H1)
                        If SecondoTermine < 0 Then SecondoTermine = 0
                        ffed = ffdd * (1 - 1 / 6 * Led * Sin(Alfa_ta_frp) / H1) + SecondoTermine
                    End If
                    Vrpd_z = (1 / 1.2) * 0.9 * Hu_z * B_f / p_f * ffed * 2 * t_f * (1 / Tan(Teta_ta) + CotgAlfa)
                    'lungo y
                    'calcolo lunghezza ottimale di ancoraggio Led, resistenza ffdd per distacco di estremità e ffed
                    If ContinuitàFRP = "discontinuo" Then
                        Rapp = B_f / p_f
                    ElseIf ContinuitàFRP = "continuo o strisce adiacenti" Then
                        Rapp = B_f / (Application.Min(0.9 * Hu_y, Perc_H * B) * Sin(Teta_ta + Alfa_ta_frp) / Sin(Teta_ta))
                    End If
                    If Rapp < 0.25 Then Rapp = 0.25
                    Kb = ((2 - Rapp) / (1 + Rapp)) ^ 0.5
                    If Kb < 1 Then Kb = 1
                    If TipoFRP = "composito preformato" Then
                        Kg = 0.023 / fc3
                    ElseIf TipoFRP = "composito impregnato in situ" Then
                        Kg = 0.037 / fc3
                    End If
                    LamdaFd = (Kb * Kg / FC) * (fcm * fctm) ^ 0.5
                    fbd = 2 * LamdaFd / (0.25 / fc3)
                    Led1 = (1 / (1.25 * fbd)) * (PiGreco ^ 2 * E_frp * t_f * LamdaFd / 2) ^ 0.5
                    Led = Application.Max(200 / fc3, Led1)
                    ffdd = (1 / Gammaf_dist) * (2 * E_frp * LamdaFd / t_f) ^ 0.5
                    H1 = Application.Min(0.9 * Hu_y, Perc_H * B)
                    If DisposizFRP = "ad U" Then
                        ffed = ffdd * (1 - 1 / 3 * Led * Sin(Alfa_ta_frp) / H1)
                    ElseIf DisposizFRP = "in avvolgimento" Then
                        Rapp = rc / H
                        If Rapp > 0.5 Then Rapp = 0.5
                        FiR = 0.2 + 1.6 * Rapp
                        SecondoTermine = 0.5 * (FiR * fpd - ffdd) * (1 - Led * Sin(Alfa_ta_frp) / H1)
                        If SecondoTermine < 0 Then SecondoTermine = 0
                        ffed = ffdd * (1 - 1 / 6 * Led * Sin(Alfa_ta_frp) / H1) + SecondoTermine
                    End If
                    Vrpd_y = (1 / 1.2) * 0.9 * Hu_y * B_f / p_f * ffed * 2 * t_f * (1 / Tan(Teta_ta) + CotgAlfa)
                Else
                    Vrpd_z = 0
                    Vrpd_y = 0
                End If
                'resistenza camicie acciaio
                If RinfCamicieAcc Then
                    Vrj_z = 0.5 * 0.9 * Hu_z * Bf_ / pf_ * fyd_a * 2 * tf_ * (1 / Tan(Teta_ta))
                    Vrj_y = 0.5 * 0.9 * Hu_y * Bf_ / pf_ * fyd_a * 2 * tf_ * (1 / Tan(Teta_ta))
                Else
                    Vrj_z = 0
                    Vrj_y = 0
                End If
                'resistenze a taglio nelle due direzioni
                If RinfCamicieCA Then
                    Vrd_z = 0.9 * Application.Min(Vrsd_z, Vrcd_z)
                    Vrd_y = 0.9 * Application.Min(Vrsd_y, Vrcd_y)
                Else
                    Vrd_z = Application.Min(Vrsd_z + Vrpd_z, Vrcd_z) + Vrj_z
                    Vrd_y = Application.Min(Vrsd_y + Vrpd_y, Vrcd_y) + Vrj_y
                End If
            Else 'calcolo progetto
                If Vrcd_z < Abs(Tz) Or Vrcd_y < Abs(Ty) Then
                    With Foglio1
                        .Range(.Cells(iF1, 1), .Cells(iF1 + 1, 1)).Select
                        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                        .Cells(iF1, 1) = "Taglio sollecitante che supera le resistenze al taglio: occorre riprogettare la sezione"
                        .Cells(iF1 + 1, 1) = "variando le dimensioni e/o la forma e/o la classe del cls."
                        iF1 = iF1 + 3
                        End
                    End With
                Else
                    'calcolo passo da sollecitazione agente
                    If Tz <> 0 Then
                        Pst_ta_z = 0.9 * Hu_z * Asw_taz * fyd * (1 / Tan(Teta_ta) + CotgAlfa) * Sin(Alfa_ta) / Abs(Tz)
                    Else
                        Pst_ta_z = Pst_r
                    End If
                    If Ty <> 0 Then
                        Pst_ta_y = 0.9 * Hu_y * Asw_tay * fyd * (1 / Tan(Teta_ta) + CotgAlfa) * Sin(Alfa_ta) / Abs(Ty)
                    Else
                        Pst_ta_y = Pst_r
                    End If
                    Pst_ta = Application.Min(Pst_ta_z, Pst_ta_y)
                    If Pst_ta > Pst_r Then Pst_ta = Pst_r
                    Vrsd_z = 0.9 * Hu_z * Asw_taz / Pst_ta * fyd * (1 / Tan(Teta_ta) + CotgAlfa) * Sin(Alfa_ta)
                    Vrsd_y = 0.9 * Hu_y * Asw_tay / Pst_ta * fyd * (1 / Tan(Teta_ta) + CotgAlfa) * Sin(Alfa_ta)
                    Vrd_z = Application.Min(Vrsd_z, Vrcd_z)
                    Vrd_y = Application.Min(Vrsd_y, Vrcd_y)
                End If
            End If
            '3)OUTPUT utente metodo stati limite
            With Foglio1
                .Cells(iF1, 1) = "resistenza a taglio dovuta al solo cls lungo z,   Tcls_z=" & FormatNumber(Tcls_z / fmF, 1, , , vbTrue) & umForze
                .Cells(iF1 + 1, 1) = "resistenza a taglio dovuta al solo cls lungo y,   Tcls_y=" & FormatNumber(Tcls_y / fmF, 1) & umForze
                '.Cells(iF1 + 2, 1) = "resistenza a ""taglio-compressione"" lungo z (bielle di cls),   Vrcd_z=" & FormatNumber(Vrcd_z / fmF, 1, , , vbTrue) & umForze
                '.Cells(iF1 + 3, 1) = "resistenza a ""taglio-compressione"" lungo y (bielle di cls),   Vrcd_y=" & FormatNumber(Vrcd_y / fmF, 1, , , vbTrue) & umForze
                iF1 = iF1 + 2
'                If CalcVerif Then
'                    .Cells(iF1, 1) = "resistenza a ""taglio-trazione"" lungo z (armatura trasversale),   Vrsd_z=" & FormatNumber(Vrsd_z / fmF, 1, , , vbTrue) & umForze
'                    .Cells(iF1 + 1, 1) = "resistenza a ""taglio-trazione"" lungo y (armatura trasversale),   Vrsd_y=" & FormatNumber(Vrsd_y / fmF, 1, , , vbTrue) & umForze
'                    iF1 = iF1 + 2
'                    If RinfFRP Then
'                        .Cells(iF1, 1) = "resistenza a ""taglio-trazione"" lungo z (composito FRP),   Vrpd_z=" & FormatNumber(Vrpd_z / fmF, 1, , , vbTrue) & umForze
'                        .Cells(iF1 + 1, 1) = "resistenza a ""taglio-trazione"" lungo y (composito FRP),   Vrpd_y=" & FormatNumber(Vrpd_y / fmF, 1, , , vbTrue) & umForze
'                        iF1 = iF1 + 2
'                    ElseIf RinfCamicieAcc Then
'                        .Cells(iF1, 1) = "resistenza aggiuntiva camicie acciaio lungo z,   Vrj_z=" & FormatNumber(Vrj_z / fmF, 1, , , vbTrue) & umForze
'                        .Cells(iF1 + 1, 1) = "resistenza aggiuntiva camicie acciaio lungo y,   Vrj_y=" & FormatNumber(Vrj_y / fmF, 1, , , vbTrue) & umForze
'                        iF1 = iF1 + 2
'                    End If
'                    .Cells(iF1, 1) = "resistenza a taglio lungo z,   Vrd_z=" & FormatNumber(Vrd_z / fmF, 1, , , vbTrue) & umForze
'                    .Cells(iF1 + 1, 1) = "resistenza a taglio lungo y,   Vrd_y=" & FormatNumber(Vrd_y / fmF, 1, , , vbTrue) & umForze
'                    iF1 = iF1 + 2
'                End If
                If Abs(Tz) <= Tcls_z And Abs(Ty) <= Tcls_y Then
                    .Cells(iF1, 1) = "essendo Tz<=Tcls_z e Ty<=Tcls_y non occorre specifica armatura a taglio (è sufficiente l'armatura"
                    .Cells(iF1 + 1, 1) = "trasversale minima regolamentare)"
                    .Cells(iF1 + 2, 1) = "passo massimo delle armature trasversali da prescrizione regolamentari,   p_r=" & Round(Pst_r / fmL, 1) & umL
                    iF1 = iF1 + 4
                Else
                    .Cells(iF1, 1) = "essendo Tz>Tcls_z o Ty>Tcls_y occorre specifica armatura a taglio"
                    .Cells(iF1 + 1, 1) = "resistenza a ""taglio-compressione"" lungo z (bielle di cls),   Vrcd_z=" & FormatNumber(Vrcd_z / fmF, 1, , , vbTrue) & umForze
                    .Cells(iF1 + 2, 1) = "resistenza a ""taglio-compressione"" lungo y (bielle di cls),   Vrcd_y=" & FormatNumber(Vrcd_y / fmF, 1, , , vbTrue) & umForze
                    iF1 = iF1 + 3
                    If CalcVerif Then
                        .Cells(iF1, 1) = "resistenza a ""taglio-trazione"" lungo z (armatura trasversale),   Vrsd_z=" & FormatNumber(Vrsd_z / fmF, 1, , , vbTrue) & umForze
                        .Cells(iF1 + 1, 1) = "resistenza a ""taglio-trazione"" lungo y (armatura trasversale),   Vrsd_y=" & FormatNumber(Vrsd_y / fmF, 1, , , vbTrue) & umForze
                        iF1 = iF1 + 2
                        If RinfFRP Then
                            .Cells(iF1, 1) = "resistenza a ""taglio-trazione"" lungo z (composito FRP),   Vrpd_z=" & FormatNumber(Vrpd_z / fmF, 1, , , vbTrue) & umForze
                            .Cells(iF1 + 1, 1) = "resistenza a ""taglio-trazione"" lungo y (composito FRP),   Vrpd_y=" & FormatNumber(Vrpd_y / fmF, 1, , , vbTrue) & umForze
                            iF1 = iF1 + 2
                        ElseIf RinfCamicieAcc Then
                            .Cells(iF1, 1) = "resistenza aggiuntiva camicie acciaio lungo z,   Vrj_z=" & FormatNumber(Vrj_z / fmF, 1, , , vbTrue) & umForze
                            .Cells(iF1 + 1, 1) = "resistenza aggiuntiva camicie acciaio lungo y,   Vrj_y=" & FormatNumber(Vrj_y / fmF, 1, , , vbTrue) & umForze
                            iF1 = iF1 + 2
                        End If
                        .Cells(iF1, 1) = "resistenza a taglio lungo z,   Vrd_z=" & FormatNumber(Vrd_z / fmF, 1, , , vbTrue) & umForze
                        .Cells(iF1 + 1, 1) = "resistenza a taglio lungo y,   Vrd_y=" & FormatNumber(Vrd_y / fmF, 1, , , vbTrue) & umForze
                        iF1 = iF1 + 2
                        If RinfCamicieCA Then
                            .Cells(iF1, 1) = "N.B. Le risistenze a taglio della sezione rinforzata con camicia in C.A. sono ridotti del 10%"
                            .Cells(iF1 + 1, 1) = "    come da normativa di riferimento (v. paragrafo C8.7.4.2 Circolare n. 7/2019)"
                            iF1 = iF1 + 2
                        End If
                        If Abs(Tz) <= Vrd_z And Abs(Ty) <= Vrd_y Then
                            .Cells(iF1, 1) = "essendo Tz<=Vrd_z e Ty<=Vrd_y la verifica a taglio è soddisfatta"
                        Else
                            .Cells(iF1, 1).Select
                            FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                            .Cells(iF1, 1) = "essendo Tz>Vrd_z e/o Ty>Vrd_y la verifica a taglio non è soddisfatta"
                        End If
                        iF1 = iF1 + 2
                    Else
                        .Cells(iF1, 1) = "passo massimo delle armature trasversali da prescrizione regolamentari,   p_r=" & Round(Pst_r / fmL, 1) & umL
                        .Cells(iF1 + 1, 1) = "passo adottato per le armature trasversali,   p=" & Round(Pst_ta / fmL, 1) & umL
                        .Cells(iF1 + 2, 1) = "resistenza a ""taglio-trazione"" lungo z (armatura trasversale),   Vrsd_z=" & FormatNumber(Vrsd_z / fmF, 1, , , vbTrue) & umForze
                        .Cells(iF1 + 3, 1) = "resistenza a ""taglio-trazione"" lungo y (armatura trasversale),   Vrsd_y=" & FormatNumber(Vrsd_y / fmF, 1, , , vbTrue) & umForze
                        .Cells(iF1 + 4, 1) = "resistenza a taglio lungo z,   Vrd_z=" & FormatNumber(Vrd_z / fmF, 1, , , vbTrue) & umForze
                        .Cells(iF1 + 5, 1) = "resistenza a taglio lungo y,   Vrd_y=" & FormatNumber(Vrd_y / fmF, 1, , , vbTrue) & umForze
                        iF1 = iF1 + 7
                    End If
                End If
            End With
        End If
    Else 'sezione generica
        With Foglio1
            .Cells(iF1, 1) = "Calcolo non implementato per sezioni di forma ""Generica"""
            iF1 = iF1 + 2
        End With
    End If
End If
End Sub

Sub Torsione() '7.
'con il metodo alle t.a., calcola la tensione tangenziale max; con gli SLU calcola la resistenza ultima a torsione della sezione
'calcola o verifica l'armatura a torsione con entrambi i metodi
'si esclude la forma sezione Generica
Dim A#, aa#, a1#, a2#, aM#
Dim bb#, b1#, b2#, bmax#, Bo1#
Dim D1#
Dim H1#
Dim Mtu1#, Mtu2#, Mtu3#, Mtu#
Dim Ntond#
Dim p#, Psi#
Dim Ri#, Re#
Dim s1#, smin#, Sigf_l#, Sigf_st#
Dim Taux_max#, TauC1_t#
Dim t#
If Mx <> 0 Then
    If MetodoTA Then
        If Ty <> 0 Or Tz <> 0 Then
            TauC1_t = TauC1 * 1.1
        Else
            TauC1_t = TauC1
        End If
    End If
    With Foglio1
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        If CalcVerif Then
            .Cells(iF1, 1) = "VERIFICA A TORSIONE (stato limite di resistenza)"
        Else
            .Cells(iF1, 1) = "PROGETTO A TORSIONE (stato limite di resistenza)"
        End If
        iF1 = iF1 + 1
    End With
    If FormSez = "Rettangolare" Or FormSez = "a T" Or FormSez = "a T rovescia" Or FormSez = "a doppio T" Or FormSez = "Circolare piena o cava" Or FormSez = "Scatolare" Then
        Df = Application.Max(Db())
        Delta = Cf + Df / 2
        Af1t = PiGreco * Df ^ 2 / 4
        '1. Calcolo Taux_max, area A e perimetro p del tubolare resistente
        If FormSez = "Circolare piena o cava" Then
            If MetodoTA Then
                Ri = Di / 2
                Re = D / 2
                Taux_max = 2 * Abs(Mx) * Re / (PiGreco * (Re ^ 4 - Ri ^ 4))
            End If
            'calcolo A e p
            D1 = D - 2 * Delta
            A = PiGreco * D1 ^ 2 / 4
            p = PiGreco * D1
        ElseIf FormSez = "Rettangolare" Then
            If MetodoTA Then
                If B <= H Then
                    aa = H
                    bb = B
                Else
                    aa = B
                    bb = H
                End If
                Psi = 3 + 2.6 / (0.45 + aa / bb)
                Taux_max = Psi * Abs(Mx) / (aa * bb ^ 2)
            End If
            'calcolo A e p
            b1 = B - 2 * Delta
            H1 = H - 2 * Delta
            A = b1 * H1
            p = 2 * b1 + 2 * H1
        ElseIf FormSez = "a T" Or FormSez = "a T rovescia" Then
            If MetodoTA Then
                If S <= B Then
                    a1 = B
                    b1 = S
                Else
                    a1 = S
                    b1 = B
                End If
                If Bo <= H - S Then
                    a2 = H - S
                    b2 = Bo
                Else
                    a2 = Bo
                    b2 = H - S
                End If
                If b1 <= b2 Then
                    bmax = b2
                Else
                    bmax = b1
                End If
                Taux_max = 3 * Abs(Mx) * bmax / (a1 * b1 ^ 3 + a2 * b2 ^ 3)
            End If
            'calcolo A e p
            b1 = B - 2 * Delta
            s1 = S - 2 * Delta
            Bo1 = Bo - 2 * Delta
            A = b1 * s1 + Bo1 * (H - S)
            p = b1 + 2 * s1 + Bo1 + 2 * (H - S) + (B - Bo)
        ElseIf FormSez = "a doppio T" Then
            If MetodoTA Then
                If S <= B Then
                    a1 = B
                    b1 = S
                Else
                    a1 = S
                    b1 = B
                End If
                If Bo <= H - 2 * S Then
                    a2 = H - 2 * S
                    b2 = Bo
                Else
                    a2 = Bo
                    b2 = H - 2 * S
                End If
                If b1 <= b2 Then
                    bmax = b2
                Else
                    bmax = b1
                End If
                Taux_max = 3 * Abs(Mx) * bmax / (2 * a1 * b1 ^ 3 + a2 * b2 ^ 3)
            End If
            'calcolo A e p
            b1 = B - 2 * Delta
            s1 = S - 2 * Delta
            Bo1 = Bo - 2 * Delta
            A = 2 * b1 * s1 + Bo1 * (H - 2 * S + 2 * Delta)
            p = 2 * b1 + 4 * s1 + 2 * (H - 2 * S + 2 * Delta) + 2 * (B - Bo)
        ElseIf FormSez = "Scatolare" Then
            If MetodoTA Then
                aM = (B - S) * (H - S)
                smin = S
                Taux_max = Abs(Mx) / (2 * aM * smin)
            End If
            'calcolo A e p
            b1 = B - 2 * Delta
            H1 = H - 2 * Delta
            A = b1 * H1
            p = 2 * b1 + 2 * H1
        End If
        '2. Verifica armatura o calcolo armatura longitudinale e trasversale a torsione
        If MetodoTA Then
            If Taux_max <= TauC1_t And Taux_max > TauC0 Then
                If CalcVerif Then
                    Sigf_l = Abs(Mx) * p / (2 * A * Al_to * Tan(Teta_to))
                    Sigf_st = Abs(Mx) * Pst_to / (2 * A * Asw_to * Sin(PiGreco - Teta_to - Alfa_to))
                Else
                    Al_to = Abs(Mx) * p / (2 * A * Sigfa * Tan(Teta_to))
                    Pst_to = 2 * A * Asw_to * Sigfa * Sin(PiGreco - Teta_to - Alfa_to) / Abs(Mx)
                End If
            End If
        ElseIf MetodoSL08 Or MetodoSL18 Then
            t = Asez / Psez
            If t < 2 * Delta Then t = 2 * Delta
            Mtu3 = 2 * A * t * (0.5 * fcd) * Sin(Teta_to) * Cos(Teta_to)
            If CalcVerif Then
                Mtu1 = 2 * Al_to * fyd * A / p * Tan(Teta_to)
                Mtu2 = 2 * Asw_to * fyd * A * Sin(PiGreco - Teta_to - Alfa_to) / (Pst_to * Sin(Teta_to))
                Mtu = Application.Min(Mtu1, Mtu2, Mtu3)
            Else
                Al_to = Abs(Mx) * p / (2 * fyd * A * Tan(Teta_to))
                Pst_to = 2 * Asw_to * fyd * A * Sin(PiGreco - Teta_to - Alfa_to) / (Abs(Mx) * Sin(Teta_to))
            End If
        End If
        If Al_to / Af1t - Int(Al_to / Af1t) > 0 Then Ntond = Int(Al_to / Af1t) + 1 Else Ntond = Int(Al_to / Af1t)
        '3. Output
        With Foglio1
            If MetodoTA Then
                .Cells(iF1, 1) = "Tensione tangenziale massima,   tx_max=" & Round(Taux_max / fmFL_2, 2) & umTens
                If Taux_max <= TauC0 Then
                    .Cells(iF1 + 1, 1) = "Non occorre specifica armatura a torsione"
                    iF1 = iF1 + 3
                ElseIf Taux_max <= TauC1_t Then
                    .Cells(iF1 + 1, 1) = "Occorre specifica armatura a torsione"
                    iF1 = iF1 + 2
                    If CalcVerif Then
                        .Cells(iF1, 1).Select
                        FormattaCella False, TipoCaratt, Hcaratt, True, True, 0, False, False
                        .Cells(iF1, 1) = "Verifica dell'armatura a torsione"
                        .Cells(iF1 + 1, 1) = "tensione normale nell'armatura longitudinale dedicata = " & FormatNumber(Sigf_l / fmFL_2, 2, , , vbTrue) & umTens
                        .Cells(iF1 + 2, 1) = "tensione normale nell'armatura trasversale dedicata = " & FormatNumber(Sigf_st / fmFL_2, 2, , , vbTrue) & umTens
                        If Sigf_l <= Sigfa And Sigf_st <= Sigfa Then
                            .Cells(iF1 + 3, 1) = "Verifica soddisfatta!"
                        Else
                            .Cells(iF1 + 3, 1).Select
                            FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                            .Cells(iF1 + 3, 1) = "Verifica non soddisfatta!"
                        End If
                        iF1 = iF1 + 5
                    Else
                        .Cells(iF1, 1).Select
                        FormattaCella False, TipoCaratt, Hcaratt, True, True, 0, False, False
                        .Cells(iF1, 1) = "Armatura a torsione"
                        .Cells(iF1 + 1, 1) = "armatura longitudinale minima dedicata,   Al=" & Round(Al_to / fmL2, 2) & umL2 & " (" & Ntond & " fi " & dfp / fmDiamTond & "=" & Round(Ntond * Af1t, 2) & umL2 & ")"
                        .Cells(iF1 + 2, 1) = "passo massimo armatura trasversale dedicata,   p=" & Int(Pst_to / fmL) & umL
                        iF1 = iF1 + 4
                    End If
                ElseIf Taux_max > TauC1_t Then
                    .Cells(iF1 + 1, 1).Select
                    FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                    .Cells(iF1 + 1, 1) = "Occorre riprogettare la sezione: tensioni tangenziali da torsione molto elevate"
                    iF1 = iF1 + 3
                End If
            ElseIf MetodoSL08 Or MetodoSL18 Then
                If CalcVerif Then
                    .Cells(iF1, 1) = "resistenza a torsione dovuta alle bielle in cls compresse,   Trcd=" & FormatNumber(Mtu3 / fmFL, 2, , , vbTrue) & umMomenti
                    .Cells(iF1 + 1, 1) = "resistenza a torsione dovuta all'armatura longitudinale dedicata,   Trld=" & FormatNumber(Mtu1 / fmFL, 2, , , vbTrue) & umMomenti
                    .Cells(iF1 + 2, 1) = "resistenza a torsione dovuta all'armatura trasversale dedicata,   Trsd=" & FormatNumber(Mtu2 / fmFL, 2, , , vbTrue) & umMomenti
                    .Cells(iF1 + 3, 1) = "resistenza a torsione dell'asta,   Trd=" & FormatNumber(Mtu / fmFL, 2, , , vbTrue) & umMomenti
                    If Abs(Mx) <= Mtu Then
                        .Cells(iF1 + 4, 1) = "essendo Mx<=Trd la verifica a torsione è soddisfatta"
                    Else
                        .Cells(iF1 + 4, 1).Select
                        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                        .Cells(iF1 + 4, 1) = "essendo Mx>Trd la verifica a torsione non è soddisfatta"
                    End If
                    iF1 = iF1 + 6
                Else 'calcolo di progetto
                    If Abs(Mx) <= Mtu3 Then
                        .Cells(iF1, 1).Select
                        FormattaCella False, TipoCaratt, Hcaratt, True, True, 0, False, False
                        .Cells(iF1, 1) = "Armatura a torsione"
                        .Cells(iF1 + 1, 1) = "armatura longitudinale minima dedicata,   Al=" & Round(Al_to / fmL2, 2) & umL2 & " (" & Ntond & " fi " & dfp / fmDiamTond & "=" & Round(Ntond * Af1t, 2) & umL2 & ")"
                        .Cells(iF1 + 2, 1) = "passo massimo armatura trasversale dedicata,   p=" & Int(Pst_to / fmL) & umL
                        iF1 = iF1 + 4
                    Else
                        .Range(.Cells(iF1, 1), .Cells(iF1 + 1, 1)).Select
                        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                        .Cells(iF1, 1) = "Verifica a torsione non soddisfatta per rottura bielle cls compresse: riprogettare variando"
                        .Cells(iF1 + 1, 1) = "        forma e/o dimensioni della sezione e/o classe del cls"
                        iF1 = iF1 + 3
                    End If
                End If
            End If
        End With
    Else 'sezione di forma generica
        With Foglio1
            .Cells(iF1, 1) = "Calcolo a torsione non eseguibile per sezioni di forma ""Generica"""
            iF1 = iF1 + 2
        End With
    End If
End If
End Sub

Sub VerifStabilitàAstaCA() '8.
'effettua le verifiche di stabilità (carico di punta) per i Pilastri in C.A., sia con approccio alle T.A. che con approccio SLU
Dim c#, Curvat#
Dim k2#, k1#
Dim e2#, e0#, e01#
Dim L0_y#, L0_z#, Lamda_y#, Lamda_z#, Lamda#
Dim My_pr#, Mz_pr#
Dim Nx_pr#
Dim Pcr_y#, Pcr_z#, Pcr#
Dim rm#
Dim SnellLim#
Dim Sigc_1#, Sig1f_1#, Sigc_2#, Sigf_2#, Sigc_3#, Sigf_3#
Dim VerifStab As Boolean, VerifStab1 As Boolean, VerifStab2 As Boolean, VerifStab3 As Boolean
'1. titolo su Fg1
With Foglio1
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "VERIFICHE DI STABILITA' DELL'ASTA NEL SUO COMPLESSO"
    .Cells(iF1 + 1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1 + 1, 1) = "(carico di punta con o senza eccentricità)"
    iF1 = iF1 + 2
End With
'2. procedi
If Nr < 0 Then
    'parcheggia provvisoriamente sollecitazioni agenti sulla sezione
    Nx_pr = Nx
    My_pr = My
    Mz_pr = Mz
    'snellezza asta
    L0_y = Beta_y * L
    L0_z = Beta_z * L
    Lamda_y = L0_y / ryp
    Lamda_z = L0_z / rzp
    Lamda = Application.Max(Lamda_y, Lamda_z)
    'carico critico
    Pcr_y = PiGreco ^ 2 * (0.4 * Ec) * Iyp / (L0_y ^ 2)
    Pcr_z = PiGreco ^ 2 * (0.4 * Ec) * Izp / (L0_z ^ 2)
    Pcr = Application.Min(Pcr_y, Pcr_z)
    If MetodoTA Then
        Aci = Asez + n * Aft
        SigCR = Pcr / Aci
        Omega = f_OmegaCA(Lamda) '8.1
        If Mr = 0 Then
            Sigc_1 = Omega * Nr / Aci
            Sig1f_1 = n * Sigc_1
            If Abs(Sigc_1) <= Sigcar And Abs(Sig1f_1) <= Sigfa Then
                VerifStab = True
            Else
                VerifStab = False
            End If
        ElseIf Mr <> 0 Then
            aM = 1 / (1 - Abs(Nr) / Pcr_y)
            '1^ verifica
            Sigc_1 = Omega * Nr / Aci
            Sig1f_1 = n * Sigc_1
            If Abs(Sigc_1) <= Sigcar And Abs(Sig1f_1) <= Sigfa Then
                VerifStab1 = True
            Else
                VerifStab1 = False
            End If
            '2^ verifica
            CalcVerif = False 'per non avere output di CalcoloTensNormali
            CalcoloTensNormali Omega * Nr, aM * Mr, 0, True '4.3
            VerifResistCA_TA '4.5
            Sigc_2 = Sigc
            Sigf_2 = Sigf
            VerifStab2 = VerifResist
            '3^ verifica
            CalcoloTensNormali Nr, aM * Mr, 0, True '4.3
            VerifResistCA_TA '4.5
            Sigc_3 = Sigc
            Sigf_3 = Sigf
            VerifStab3 = VerifResist
            'verifica complessiva
            If VerifStab1 And VerifStab2 And VerifStab3 Then
                VerifStab = True
            Else
                VerifStab = False
            End If
        End If
    ElseIf MetodoSL08 Or MetodoSL18 Then
        'calcola snellezza limite
        If MetodoSL08 Then
            If Mi = 0 And Mk = 0 Then
                rm = 0
            ElseIf Abs(Mi) >= Abs(Mk) Then
                rm = Mk / Mi
            Else
                rm = Mi / Mk
            End If
            c = 1.7 - rm
            SnellLim = 15.4 * c / ((Abs(Nr) / (Asez * fcd)) ^ 0.5)
        ElseIf MetodoSL18 Then
            SnellLim = 25 / ((Abs(Nr) / (Asez * fcd)) ^ 0.5)
        End If
        If Lamda > SnellLim Then 'fai verifica
            'calcolo e0 e e2
            k2 = 1
            Hu = H - (Cf + Db(1) / 2)
            Curvat = 2 * k2 * Eps_yd / (0.9 * Hu)
            Select Case Lamda
                Case Is > 35
                    k1 = 1
                Case Is > 15
                    k1 = Lamda / 20 - 0.75
                Case Else
                    k1 = 0
            End Select
            e2 = k1 * L0_y ^ 2 / 10 * Curvat
            e0 = L / 300
            If Mr < 0 Then
                My = Mr + Nr * (e2 + e0)
            ElseIf Mr > 0 Then
                My = Mr - Nr * (e2 + e0)
            ElseIf Mr = 0 Then
                e01 = 0.05 * H
                If e01 > e0 Then e0 = e01
                If e0 < 2 * fmL Then e0 = 2 * fmL
                My = -Nr * (e2 + e0) 'positivo
            End If
            'verifica con My e Nx=Nr
            Nx = Nr
            Mz = 0
            VerifResistCA_SLU_TensNorm_xCarPunta '8.2
            VerifStab = VerifResist
        End If
    End If
    'OUTPUT
    With Foglio1
        .Cells(iF1, 1) = "lunghezza libera di inflessione nel piano xz,   Lo_y=" & Round(L0_y / fmL, 1) & umL
        .Cells(iF1 + 1, 1) = "lunghezza libera di inflessione nel piano xy,   Lo_z=" & Round(L0_z / fmL, 1) & umL
        .Cells(iF1 + 2, 1) = "snellezza asta,   Lamda=" & Round(Lamda, 1)
        .Cells(iF1 + 3, 1) = "carico critico Euleriano,   Pcr=" & FormatNumber(Pcr / fmF, 2, , , vbTrue) & umForze
        iF1 = iF1 + 4
        If MetodoTA Then
            If Lamda > 100 Then
                .Cells(iF1, 1).Select
                FormattaCella False, TipoCaratt, Hcaratt, False, False, 3, False, False
                .Cells(iF1, 1) = "Attenzione: snellezza asta superiore al valore 100 (limite che è opportuno non superare)"
                iF1 = iF1 + 1
            End If
            .Cells(iF1, 1) = "tensione critica Euleriana,   SigCR=" & FormatNumber(SigCR / fmFL_2, 2, , , vbTrue) & umTens
            .Cells(iF1 + 1, 1) = "coefficiente    omega=" & Round(Omega, 2)
            If Mr = 0 Then
                .Cells(iF1 + 2, 1) = "tensione massima di compressione nel cls = " & FormatNumber(Sigc_1 / fmFL_2, 2, , , vbTrue) & umTens
                .Cells(iF1 + 3, 1) = "tensione massima acciaio compresso = " & FormatNumber(Sig1f_1 / fmFL_2, 2, , , vbTrue) & umTens
                iF1 = iF1 + 4
            Else
                .Cells(iF1 + 2, 1) = "coeff. di amplificaz. momento flettente,   aM=" & Round(aM, 4)
                .Cells(iF1 + 3, 1) = "1^ verifica: sforzo normale amplificato"
                .Cells(iF1 + 4, 1) = "   tensione massima di compressione nel cls = " & FormatNumber(Sigc_1 / fmFL_2, 2, , , vbTrue) & umTens
                .Cells(iF1 + 5, 1) = "   tensione massima acciaio compresso = " & FormatNumber(Sig1f_1 / fmFL_2, 2, , , vbTrue) & umTens
                .Cells(iF1 + 6, 1) = "2^ verifica: momento e sforzo normale amplificati"
                .Cells(iF1 + 7, 1) = "   tensione massima di compressione nel cls =" & FormatNumber(Sigc_2 / fmFL_2, 2, , , vbTrue) & umTens
                .Cells(iF1 + 8, 1) = "   tensione massima nell'acciaio = " & FormatNumber(Sigf_2 / fmFL_2, 2, , , vbTrue) & umTens
                .Cells(iF1 + 9, 1) = "3^ verifica: momento amplificato e sforzo normale non amplificato"
                .Cells(iF1 + 10, 1) = "   tensione massima di compressione nel cls =" & FormatNumber(Sigc_3 / fmFL_2, 2, , , vbTrue) & umTens
                .Cells(iF1 + 11, 1) = "   tensione massima nell'acciaio = " & FormatNumber(Sigf_3 / fmFL_2, 2, , , vbTrue) & umTens
                iF1 = iF1 + 12
            End If
            If VerifStab Then
                .Cells(iF1, 1) = "verifica a carico di punta soddisfatta"
            Else
                .Cells(iF1, 1).Select
                FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                .Cells(iF1, 1) = "Non verifica a carico di punta"
            End If
            iF1 = iF1 + 2
        ElseIf MetodoSL08 Or MetodoSL18 Then
            .Cells(iF1, 1) = "snellezza limite = " & Round(SnellLim, 2)
            If Lamda > SnellLim Then
                .Cells(iF1 + 1, 1) = "eccentricità   e0=" & Round(e0 / fmL, 2) & umL
                .Cells(iF1 + 2, 1) = "eccentricità   e2=" & Round(e2 / fmL, 2) & umL
                .Cells(iF1 + 3, 1) = "momento flettente di riferimento amplificato = " & FormatNumber(My / fmFL, 2, , , vbTrue) & umMomenti
                If VerifStab Then
                    .Cells(iF1 + 4, 1) = "verifica a carico di punta soddisfatta (v. dominio di rottura My-Nx)"
                Else
                    .Cells(iF1 + 4, 1).Select
                    FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                    .Cells(iF1 + 4, 1) = "Non verifica a carico di punta (v. dominio di rottura My-Nx)"
                End If
                .Cells(iF1 + 5, 1) = "momenti ultimi o resistenti della sezione soggetta a presso-flessione retta (corrispondenti a Nr)"
                .Cells(iF1 + 6, 1) = "    Myu_s=" & FormatNumber(Myu_s / fmFL, 1, , , vbTrue) & umMomenti
                .Cells(iF1 + 7, 1) = "    Myu_i=" & FormatNumber(Myu_i / fmFL, 1, , , vbTrue) & umMomenti
                iF1 = iF1 + 9
            Else
                .Cells(iF1 + 1, 1) = "essendo la snellezza dell'asta minore della snellezza limite gli effetti di instabilità si possono trascurare"
                iF1 = iF1 + 3
            End If
        End If
    End With
    'riprendi sollecitazioni agenti sulla sezione
    Nx = Nx_pr
    My = My_pr
    Mz = Mz_pr
ElseIf Nr >= 0 Then
    'non occorre fare la verifiche di stabilità
    With Foglio1
        .Cells(iF1, 1) = "verifica a carico di punta non necessaria (asta non compressa)"
        iF1 = iF1 + 2
    End With
End If
End Sub

Function f_Sigcar()
Dim A#
A = Application.Min(B, H)
If A / fmL < 25 Then
    f_Sigcar = 0.7 * Sigca * (1 - 0.03 * (25 - A / fmL))
Else
    f_Sigcar = 0.7 * Sigca
End If
End Function

Function f_OmegaCA#(Lam)  '8.1
If Lam <= 50 Then
    f_OmegaCA = 1
ElseIf Lam <= 70 Then
    f_OmegaCA = 1 + (1.08 - 1) * (Lam - 50) / (70 - 50)
ElseIf Lam <= 85 Then
    f_OmegaCA = 1.08 + (1.32 - 1.08) * (Lam - 70) / (85 - 70)
ElseIf Lam <= 100 Then
    f_OmegaCA = 1.32 + (1.62 - 1.32) * (Lam - 85) / (100 - 85)
ElseIf Lam <= 120 Then
    f_OmegaCA = 1.62 + (2.28 - 1.62) * (Lam - 100) / (120 - 100)
ElseIf Lam <= 140 Then
    f_OmegaCA = 2.28 + (3 - 2.28) * (Lam - 120) / (140 - 120)
Else
    f_OmegaCA = 10
End If
End Function

Sub ControlloDati() '2.
'1. DATI GENRALI
'1.2 Confinamento
If RinfFRP Then
    If blnConfinNessuno = False And blnConfinStaffe = False And blnConfinFRP = False Then
        MsgBox "Specifica se considerare o meno confinamento del cls (DATI GENERALI)", vbCritical, VersioneSw
        End
    End If
ElseIf RinfCamicieAcc Then
    If blnConfinNessuno = False And blnConfinCamicieAcc = False Then
        MsgBox "Specifica se considerare o meno confinamento del cls (DATI GENERALI)", vbCritical, VersioneSw
        End
    End If
ElseIf RinfCamicieCA Then
    If blnConfinNessuno = False And blnConfinStaffe = False Then
        MsgBox "Specifica se considerare o meno confinamento del cls (DATI GENERALI)", vbCritical, VersioneSw
        End
    End If
End If
'2. GEOMETRIA
'2.1 Sezione
If FormSez = "Rettangolare" Or FormSez = "a T" Or FormSez = "a T rovescia" Or FormSez = "a doppio T" Or FormSez = "Scatolare" Then
    If B <= 0 Or H <= 0 Then
        MsgBox "Inserire/correggere dimensioni B, H (GEOMETRIA>Sezione). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Cf < 0 Then
        MsgBox "Inserire/correggere copriferro (GEOMETRIA>Sezione). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If FormSez = "a T" Or FormSez = "a T rovescia" Then
        If Bo <= 0 Or Bo >= B Or S <= 0 Or S >= H Then
            MsgBox "Inserire/correggere dimensioni Bo, S (GEOMETRIA>Sezione). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    ElseIf FormSez = "a doppio T" Then
        If Bo <= 0 Or Bo >= B Or S <= 0 Or S >= H / 2 Then
            MsgBox "Inserire/correggere dimensioni Bo, S (GEOMETRIA>Sezione). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    ElseIf FormSez = "Scatolare" Then
        If S < 3 * Cf Or S >= Application.Min(B / 2, H / 2) Then
            MsgBox "Inserire/correggere dimensioni spessore sezione (GEOMETRIA>Sezione): non deve essere inferiore a tre volte il copriferro. Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
ElseIf FormSez = "Circolare piena o cava" Then
    If D <= 0 Or Di < 0 Or Di > D - 6 * Cf Then
        MsgBox "Inserire/correggere dimensioni D, Di (GEOMETRIA>Sezione). Di deve essere inferiore a D diminuito di 6 volte il copriferro. Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Cf < 0 Then
        MsgBox "Inserire/correggere copriferro (GEOMETRIA>Sezione). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'armature
'If CalcVerif And Nbar <= 0 Then
    'MsgBox "Inserire armature metalliche (GEOMETRIA>Sezione). Il calcolo verrà arrestato.", vbCritical, VersioneSw
    'End
'End If
'2.2 Composito FRP
If RinfFRP Then
    If B_frp <= 0 Or H_frp < 0 Then
        MsgBox "Inserire/correggere dimensioni del composito fibrorinforzato (GEOMETRIA>Rinforzi a flessione e/o taglio con FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Ty <> 0 Or Tz <> 0 Then
        If t_f < 0 Or B_f <= 0 Or p_f < B_f Then
            MsgBox "Inserire/correggere dimensioni del composito fibrorinforzato (GEOMETRIA>Rinforzi a flessione e/o taglio con FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
        If Alfa_ta_frp <= 0 Or Alfa_ta_frp >= PiGreco Then
            MsgBox "Inserire/correggere angolo di inclinazione strisce rispetto all'asse dell'asta (GEOMETRIA>Rinforzi a flessione e/o taglio con FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
        If Perc_H <= 0 Or Alfa_ta_frp > 100 Then
            MsgBox "Inserire/correggere percentuale altezza trave impegnata dal rinforzo (GEOMETRIA>Rinforzi a flessione e/o taglio con FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
        If rc < 0 Then
            MsgBox "Inserire/correggere raggio arrotondomento spigoli sezione (GEOMETRIA>Rinforzi a flessione e/o taglio con FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
End If
'2.3 Confinamento con FRP
If blnConfinFRP Then
    If tf_ <= 0 Or Bf_ <= 0 Then
        MsgBox "Inserire/correggere dimensioni strisce FRP (GEOMETRIA>Confinamento con compositi FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If TipoConfinFRP = "discontinuo" And pf_ < Bf_ Then
        MsgBox "Inserire/correggere passo strisce FRP (GEOMETRIA>Confinamento con compositi FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Alfa_fib < 0 Or Alfa_fib >= PiGreco / 2 Then 'angolo alfa
        MsgBox "Inserire/correggere angolo di inclinazione fibre rispetto alla normale all'asse dell'asta (GEOMETRIA>Confinamento con compositi FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If rc_ < 0 Then
        MsgBox "Inserire/correggere raggio arrotondomento spigoli sezione (GEOMETRIA>Confinamento con compositi FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'2.4 rinforzo a taglio con calastrelli
'If RinfCamicieAcc Then
    'If Ty <> 0 Or Tz <> 0 Then
        'If tj <= 0 Or Bj <= 0 Then
            'MsgBox "Inserire/correggere dimensioni calastrelli (GEOMETRIA>Rinforzo a taglio con camicie di acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            'End
        'End If
        'If TipoConfinCamicieAcc = "discontinuo" And pj < Bj Then
            'MsgBox "Inserire/correggere passo calastrelli (GEOMETRIA>Rinforzo a taglio con camicie di acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            'End
        'End If
    'End If
'End If
'2.5 Confinamento con calastrelli
If RinfCamicieAcc Or blnConfinCamicieAcc Then
    If tf_ <= 0 Or Bf_ <= 0 Then
        MsgBox "Inserire/correggere dimensioni calastrelli (GEOMETRIA>Confinamento e rinforzo a taglio con camicie di acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If TipoConfinCamicieAcc2 = "discontinuo" And pf_ < Bf_ Then
        MsgBox "Inserire/correggere passo calastrelli (GEOMETRIA>Confinamento e rinforzo a taglio con camicie di acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If rc_ < 0 Then
        MsgBox "Inserire/correggere raggio arrotondomento spigoli sezione (GEOMETRIA>Confinamento e rinforzo a taglio con camicie di acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'3. MATERIALI
'3.1 Cls e acciaio
If Rck < 100 / fcUM Or Rck > 1050 / fcUM Then
    MsgBox "Inserire valore corretto per Rck calcestruzzo (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
    End
End If
If Ec < 100000 / fcUM Or Ec > 1000000 / fcUM Then
    MsgBox "Inserire valore corretto per modulo elastico Ec calcestruzzo (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
    End
End If
If Es < 1000000 / fcUM Or Es > 3000000 / fcUM Then
    MsgBox "Inserire valore corretto per modulo elastico Es acciaio (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
    End
End If
If n <= 0 Or n > 30 Then
    MsgBox "Correggere il valore del coeff. di omogeneizzazione n (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
    End
End If
If CemArmOrd Then
    If MetodoTA Then
        If TipoAcciaioCA <> "Fe B 22 k" And TipoAcciaioCA <> "Fe B 32 k" And TipoAcciaioCA <> "Fe B 38 k" And TipoAcciaioCA <> "Fe B 44 k" Then
            MsgBox "Specificare correttamente il tipo di acciaio dal menù MATERIALI. Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    ElseIf MetodoSL08 Or MetodoSL18 Then
        If TipoAcciaioCA <> "B450C" Then
            MsgBox "Specificare correttamente il tipo di acciaio dal menù MATERIALI. Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
End If
If MetodoTA Then
    If Sigca < 40 / fcUM Or Sigca > 200 / fcUM Then
        MsgBox "Valore delle tensione ammissibile nel cls non corretto (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If CemArmOrd Then
        If Sigfa < 1000 / fcUM Or Sigfa > 4000 / fcUM Then
            MsgBox "Valore della tensione ammissibile dell'acciaio non corretto (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    ElseIf CemCAP Then
        If Sigfa < 1000 / fcUM Or Sigfa > 20000 / fcUM Then
            MsgBox "Valore della tensione ammissibile dell'acciaio non corretto (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
ElseIf MetodoSL08 Or MetodoSL18 Then
    If fcd < 40 / fcUM Or fcd > 500 / fcUM Then
        MsgBox "Valore della resistenza fcd del cls non corretto (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If CemArmOrd Then
        If fyd < 1000 / fcUM Or fyd > 5000 / fcUM Then
            MsgBox "Valore della resistenza fyd dell'acciaio non corretto (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    ElseIf CemCAP Then
        If fyd < 1000 / fcUM Or fyd > 20000 / fcUM Then
            MsgBox "Valore della resistenza fyd dell'acciaio non corretto (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
    If Eps_c2 <= 0 Or Eps_c2 > 0.0035 Or Eps_c3 <= 0 Or Eps_c3 > 0.0035 Or Eps_c4 <= 0 Or Eps_c4 > 0.0035 Then
        MsgBox "Inserire valore corretto delle deformazioni di calcolo del cls (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Eps_cu <= 0 Or Eps_cu > 0.02 Then
        MsgBox "Inserire valore corretto della deformazione di rottura del cls (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Eps_su <= 0 Or Eps_su > 0.1 Then
        MsgBox "Inserire valore corretto della deformazione di rottura dell'acciaio (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If blnBilineare And (Kincr < 1 Or Kincr > 1.35) Then
        MsgBox "Inserire valore corretto del rapporto di sovra.resistenza k (MATERIALI>Calcestruzzo e acciaio). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'3.2 acciaio esistente
If RinfCamicieCA Then
    If Gammas_e < 1 Or Gammas_e > 1.5 Then
        MsgBox "Controlla valore coefficiente parziali di sicurezza acciaio (MATERIALI>Acciaio esistente). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If FC < 1 Or FC > 1.35 Then
        MsgBox "Il fattore di confidenza FC deve essere compreso tra 1 e 1,35 (MATERIALI>Acciaio esistente). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If fym < 1000 / fcUM Or fym > 10000 / fcUM Then
        MsgBox "Valore della resistenza fym dell'acciaio non corretto (MATERIALI>Acciaio esistente). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If fyd_e < 1000 / fcUM Or fyd_e > 10000 / fcUM Then
        MsgBox "Valore della resistenza fyd dell'acciaio non corretto (MATERIALI>Acciaio esistente). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'3.3 Calcestruzzo fibrorinforzato
If CemFRC Then
    If blnLineareIncrud Then
        If Eps_Fs < 0 Or Eps_Fs > 0.01 Or Eps_Fu < 0 Or Eps_Fu < Eps_Fs Or Eps_Fu > 0.02 Then
            MsgBox "Inserire valori corretti delle deformazioni di calcolo del cls fibrorinforzato (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
        If fFts < 0.5 * fctd Or fFtu < fFts Then
            MsgBox "Valori delle resistenze a trazione residue del cls fibrorinforzato non corretti (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    ElseIf blnLineareDegrad Then
        If Eps_Fs < 0 Or Eps_Fs > 0.01 Or Eps_Fu < 0 Or Eps_Fu < Eps_Fs Or Eps_Fu > 0.03 Then
            MsgBox "Inserire valori corretti delle deformazioni di calcolo del cls fibrorinforzato (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
        If fFts < 1 * fctd Or fFtu > fFts Then
            MsgBox "Valori delle resistenze a trazione residue del cls fibrorinforzato non corretti (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    ElseIf blnRigidoPlastico Then
        If Eps_Fu < 0 Or Eps_Fu > 0.03 Then
            MsgBox "Inserire valore corretto della deformazioni di progetto del cls fibrorinforzato (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
        If fFtu < 1 * fctd Then
            MsgBox "Valore della resistenza a trazione residua del cls fibrorinforzato non corretto (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
End If
'3.4 Composito FRP
If RinfFRP Or blnConfinFRP Then
    If E_frp < 1000000 / fcUM Or E_frp > 5000000 / fcUM Then
        MsgBox "Inserire valore corretto per modulo elastico composito FRP (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If fpk < 500 / fcUM Or fpk > 50000 / fcUM Then
        MsgBox "Valore della resistenza fpk del composito FRP non corretto (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Gammaf < 1 Or Gammaf > 1.5 Or Gammaf_dist < 1.2 Or Gammaf_dist > 1.5 Then
        MsgBox "Controlla valori coefficienti parziali di sicurezza del composito FRP (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Eta_a < 0.5 Or Eta_a > 0.95 Or Eta1 < 0.3 Or Eta1 > 0.8 Then
        MsgBox "Controlla valori fattori di conversione per il composito FRP (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If FC < 1 Or FC > 1.35 Then
        MsgBox "Il fattore di confidenza FC deve essere compreso tra 1 e 1,35 (MATERIALI>Compositi fibrorinforzati FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If fpd < 500 / fcUM Or fpd > 50000 / fcUM Or fpd_sle < 500 / fcUM Or fpd_sle > 50000 / fcUM Then
        MsgBox "Valori della resistenza fpd del composito FRP non corretto (MATERIALI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Eps_pu <= 0 Or Eps_pu > 5 Or Eps_pk <= 0 Or Eps_pk > 5 Then
        MsgBox "Inserire valori corretti della deformazione caratteristica e/o di progetto a rottura (MATERIALI>Compositi fibrorinforzati FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Eps0f < 0 Or Eps0f > 10 Then
        MsgBox "Inserire valore corretto della deformazione nel lembo teso preesistente all'applicazione del FRP (MATERIALI>Compositi fibrorinforzati FRP). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'3.5 Acciaio angolari e calastrelli
If RinfCamicieAcc Or blnConfinCamicieAcc Then
    If Es_a < 1000000 / fcUM Or Es_a > 3000000 / fcUM Then
        MsgBox "Inserire valore corretto per modulo elastico Es acciaio (MATERIALI>Acciaio angolari e calastrelli). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If ftk_a < 1000 / fcUM Or ftk_a > 10000 / fcUM Or fyk_a < 1000 / fcUM Or fyk_a > 10000 / fcUM Or fyd_a < 1000 / fcUM Or fyd_a > 10000 / fcUM Then
        MsgBox "Valore delle resistenze dell'acciaio non corretti (MATERIALI>Acciaio angolari e calastrelli). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Gammas_a < 1 Or Gammas_a > 1.5 Then
        MsgBox "Controlla valore coefficiente parziali di sicurezza (MATERIALI>Acciaio angolari e calastrelli). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'5. CARICO DI PUNTA
If blnVerifCarPunta Then
    If L <= 0 Then
        MsgBox "Inserire lunghezza asta (STABILITA' ASTA). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Beta_y <= 0 Or Beta_y > 2 Or Beta_z <= 0 Or Beta_z > 2 Then
        MsgBox "Correggere o inserire coefficienti beta (STABILITA' ASTA). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'6. ALTRI DATI
'progetto armatura a flessione
If CalcVerif = False Then
    If dfp <= 0 Or dfp > 100 * fmDiamTond Then
        MsgBox "Inserire/correggere diametro tondini (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If (Pmax <= 3 * fmL Or Pmax > 200 * fmL) Then
        MsgBox "Inserire/correggere interasse massimo tra le armature (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If (Mu_ < 0 Or Mu_ > 1) Then
        MsgBox "Inserire/correggere rappoarto armature A'f/Af (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If (sLmin <= 0 Or sLmin > 200 * fmL) Then
        MsgBox "Inserire/correggere spazio minimo tra le barre di armatura (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'armatura a taglio
If Ty <> 0 Or Tz <> 0 Or blnConfinStaffe Then
    If Alfa_ta <= 0 Or Alfa_ta > PiGreco / 2 Then 'angolo alfa
        MsgBox "Inserire/correggere angolo di inclinazione armatura trasversale a taglio (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If (Teta_ta * 180 / PiGreco) > 45 Or (Teta_ta * 180 / PiGreco) < 21.8 Then
        MsgBox "L'angolo teta di inclinazione delle fessure nel calcolo a taglio deve essere compreso tra 21,8° e 45° (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Dst_ta <= 0 Or Dst_ta > 14 * fmDiamTond Then
        MsgBox "Inserire/correggere diametro armatura trasversale a taglio (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If CalcVerif Then
        If Pst_ta <= 0 Then
            MsgBox "Inserire/correggere interasse armatura trasversale a taglio (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
    If FormSez <> "Circolare piena o cava" Then
        If Nbrz < 0 Or Nbry < 0 Then
            MsgBox "Inserire/correggere numero braccia staffe a taglio (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
End If
'armatura a torsione
If Mx <> 0 Then
    If Alfa_to <= 0 Or Alfa_to > PiGreco / 2 Then 'angolo alfa
        MsgBox "Inserire/correggere angolo di inclinazione armatura trasversale a torsione (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If (Teta_to * 180 / PiGreco) > 45 Or (Teta_to * 180 / PiGreco) < 21.8 Then
        MsgBox "L'angolo teta di inclinazione delle fessure nel calcolo a torsione deve essere compreso tra 21,8° e 45° (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Dst_to <= 0 Or Dst_to > 14 * fmDiamTond Then
        MsgBox "Inserire/correggere diametro armatura trasversale a torsione (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If CalcVerif Then
        If Al_to <= 0 Then
            MsgBox "Inserire/correggere armatura longitudinale a torsione (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
        If Pst_to <= 0 Then
            MsgBox "Inserire/correggere interasse armatura trasversale a torsione (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
            End
        End If
    End If
End If
'diagramma momenti-curvatura
If CalcVerif And MetodoSL18 And blnVerifDuttilità And SollecPiane Then
    If Foglio2.Cells(27, 12) = "" Or Foglio2.Cells(27, 12) <= 0 Then 'Npx
        MsgBox "Inserire/correggere n° posizioni asse neutro per la costruzione del diagramma momenti-curvature (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    'If Foglio2.Cells(28, 12) = "" Or Foglio2.Cells(28, 12) <= 0 Then
        'MsgBox "Inserire/correggere incremento deformazioni per la costruzione del diagramma momenti-curvature (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        'End
    'End If
    If Foglio2.Cells(29, 12) = "" Or Foglio2.Cells(29, 12) <= 0 Then 'Deltaz
        MsgBox "Inserire/correggere altezza striscia elementare cls per la costruzione del diagramma momenti-curvature (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Foglio2.Cells(30, 12) = "" Or Foglio2.Cells(31, 12) = "" Or Foglio2.Cells(30, 12) = Foglio2.Cells(31, 12) Then 'x1 e x2
        MsgBox "Inserire/correggere intervallo variazione asse neutro per la costruzione del diagramma momenti-curvature (ALTRI DATI). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
'7. VERIFICHE SLE
If blnVerifSLE Then
    If Perc_cls_c <= 0 Or Perc_cls_c >= 100 Then
        MsgBox "Inserire valore corretto della % per il calcolo della tensione ammissibile nel cls per la combinazione caratteristica (VERIF. S.L.E). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Perc_cls_qp <= 0 Or Perc_cls_qp >= 100 Then
        MsgBox "Inserire valore corretto della % per il calcolo della tensione ammissibile nel cls per la combinazione quasi permanente (VERIF. S.L.E). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If Perc_acc_c <= 0 Or Perc_acc_c >= 100 Then
        MsgBox "Inserire valore corretto della % per il calcolo della tensione ammissibile nel'acciaio per la combinazione caratteristica (VERIF. S.L.E). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
    If KK < 0.4 Or KK > 1.5 Then
        MsgBox "Inserire valore corretto del coefficiente K (VERIF. S.L.E). Il calcolo verrà arrestato.", vbCritical, VersioneSw
        End
    End If
End If
End Sub

Sub OutInput() '3.
Dim My_c#, My_f#, My_qp#, Mz_c#, Mz_f#, Mz_qp#
Dim Nx_c#, Nx_f#, Nx_qp#
Dim Np_max%
With Foglio1
    '1.DATI GENERALI
    .Activate
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, False, 0, False, False
    .Cells(iF1, 1) = "PROGETTO/LAVORI"
    .Range(Cells(iF1 + 1, 1), Cells(iF1 + 1, 9)).Select
    FormattaCella False, TipoCaratt, Hcaratt, False, False, 0, True, True
    .Cells(iF1 + 1, 1) = Foglio2.Cells(13, 4)
    iF1 = iF1 + 3
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, False, 0, False, False
    .Cells(iF1, 1) = "COMMITTENTE"
    .Range(Cells(iF1 + 1, 1), Cells(iF1 + 1, 9)).Select
    FormattaCella False, TipoCaratt, Hcaratt, False, False, 0, True, True
    .Cells(iF1 + 1, 1) = Foglio2.Cells(14, 4)
    .Cells(iF1 + 3, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, False, 0, False, False
    .Cells(iF1 + 3, 1) = "COMUNE"
    .Range(Cells(iF1 + 4, 1), Cells(iF1 + 4, 9)).Select
    FormattaCella False, TipoCaratt, Hcaratt + 2, False, False, 0, True, True
    .Cells(iF1 + 4, 1) = Foglio2.Cells(15, 4)
    iF1 = iF1 + 6
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, False, 0, False, False
    .Cells(iF1, 1) = "LUOGO E DATA DI ESECUZIONE DEL CALCOLO"
    .Range(Cells(iF1 + 1, 1), Cells(iF1 + 1, 9)).Select
    FormattaCella False, TipoCaratt, Hcaratt, False, False, 0, True, True
    .Cells(iF1 + 1, 1) = Foglio2.Cells(18, 4)
    iF1 = iF1 + 3
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, False, 0, False, False
    .Cells(iF1, 1) = "ANNOTAZIONI"
    .Range(Cells(iF1 + 1, 1), Cells(iF1 + 1, 9)).Select
    FormattaCella False, TipoCaratt, Hcaratt, False, False, 0, True, True
    .Cells(iF1 + 1, 1) = Foglio2.Cells(17, 4)
    iF1 = iF1 + 3
    'Campo di applicazione del software
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "CAMPO DI APPLICAZIONE DEL SOFTWARE"
    .Cells(iF1 + 1, 1) = "Sezioni in cemento armato ordinario e precompresso"
    .Cells(iF1 + 2, 1) = "Calcestruzzo fibrorinforzato FRC"
    .Cells(iF1 + 3, 1) = "Calcolo di progetto e di verifica"
    .Cells(iF1 + 4, 1) = "Sezioni di forma geometrica qualunque, anche pluriconnessa"
    .Cells(iF1 + 5, 1) = "Stato di sollecitazione piano e spaziale"
    .Cells(iF1 + 6, 1) = "Calcolo alle tensioni normali, a taglio e torsione"
    .Cells(iF1 + 7, 1) = "Verifiche di resistenza e di stabilità (SLU)"
    .Cells(iF1 + 8, 1) = "Verifiche SLE: deformazioni, fessurazione, tensioni di esercizio"
    .Cells(iF1 + 9, 1) = "Calcestruzzo confinato da staffe chiuse (paragr. 4.1.2.1.2.1 DM 17/01/2018)"
    .Cells(iF1 + 10, 1) = "Calcestruzzo confinato con compositi fibrorinforzati a matrice polimerica FRP"
    .Cells(iF1 + 11, 1) = "Calcestruzzo confinato con camicie di acciaio (angolari a calastrelli)"
    .Cells(iF1 + 12, 1) = "Verifiche di duttilità ex DM 17/01/2018"
    .Cells(iF1 + 13, 1) = "Rinforzi strutture esistenti con compositi fibrorinforzati a matrice polimerica FRP"
    .Cells(iF1 + 14, 1) = "Rinforzi strutture esistenti con camicie di acciaio (angolari a calastrelli)"
    .Cells(iF1 + 15, 1) = "Rinforzi strutture esistenti con camicie in C.A."
    .Cells(iF1 + 16, 1) = "Normative applicabili: DM 11/02/1992 (Metodo alle Tensioni Ammissibili) -"
    .Cells(iF1 + 17, 1) = "     DM 14/01/2008 (Metodo agli Stati Limite) - DM 17/01/2018 (Metodo agli Stati Limite)"
    iF1 = iF1 + 19
    .Cells(iF1, 4).Select
    FormattaCella True, TipoCaratt, Hcaratt + 4, False, False, 0, False, False
    .Cells(iF1, 4) = "DATI DI INPUT"
    .Cells(iF1 + 2, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1 + 2, 1) = "TIPO DI SEZIONE IN C.A."
    If CemArmOrd Then
        .Cells(iF1 + 3, 1) = "Sezione in Cemento Armato Ordinario (CA)"
    ElseIf CemCAP Then
        .Cells(iF1 + 3, 1) = "Sezione in Cemento Armato Precompresso (CAP)"
    End If
    iF1 = iF1 + 4
    If CemFRC Then
        .Cells(iF1, 1) = "Calcestruzzo fibrorinforzato (FRC)"
        iF1 = iF1 + 1
    End If
    iF1 = iF1 + 1
    If RinfFRP Or RinfCamicieAcc Or RinfCamicieCA Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "RINFORZO COSTRUZIONI ESISTENTI"
        If RinfFRP Then
            .Cells(iF1 + 1, 1) = "Rinforzo a flessione e/o taglio con compositi fibrorinforzati a matrice polimerica (FRP)"
        ElseIf RinfCamicieAcc Then
            .Cells(iF1 + 1, 1) = "Rinforzo a taglio con camicie di acciaio (angolari e calastrelli)"
        ElseIf RinfCamicieCA Then
            .Cells(iF1 + 1, 1) = "Rinforzo con camicie in C.A."
        End If
        iF1 = iF1 + 3
    End If
    'unità di misura
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "UNITA' DI MISURA"
    .Cells(iF1 + 1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    If SistemaTecnico Then
        .Cells(iF1 + 1, 1) = "Sistema Tecnico"
    Else
        .Cells(iF1 + 1, 1) = "Sistema Internazionale"
    End If
    .Cells(iF1 + 2, 1) = "lunghezze (dimensioni, coordinate, copriferro, interferro, ...): " & umL
    .Cells(iF1 + 3, 1) = "aree sezioni: " & umL2
    .Cells(iF1 + 4, 1) = "volumi: " & umL3
    .Cells(iF1 + 5, 1) = "momenti statici sezioni: " & umL3
    .Cells(iF1 + 6, 1) = "momenti di inerzia sezioni: " & umL4
    .Cells(iF1 + 7, 1) = "forze, Sforzo normale, Taglio: " & umForze
    .Cells(iF1 + 8, 1) = "momenti flettenti e torcente: " & umMomenti
    .Cells(iF1 + 9, 1) = "tensioni/pressioni, moduli elastici, resistenze materiali: " & umTens
    .Cells(iF1 + 10, 1) = "diametri tondini, trefoli, barre, staffe e spirali: " & umDiamTond
    iF1 = iF1 + 12
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "NORMATIVA DI RIFERIMENTO"
    If MetodoTA Then
        .Cells(iF1 + 1, 1) = "D.M. 11/02/1992 (Metodo alle Tensioni Ammissibili)"
    ElseIf MetodoSL08 Then
        .Cells(iF1 + 1, 1) = "D.M. 14/01/2008 (Metodo agli Stati Limite)"
    ElseIf MetodoSL18 Then
        .Cells(iF1 + 1, 1) = "D.M. 17/01/2018 (Metodo agli Stati Limite)"
    End If
    iF1 = iF1 + 3
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "TIPO DI CALCOLO"
    If CalcVerif = False Then
        If Pilastro Then
            .Cells(iF1 + 1, 1) = "Progetto di un pilastro"
        ElseIf Trave Then
            .Cells(iF1 + 1, 1) = "Progetto di una trave"
        ElseIf TraveFondaz Then
            .Cells(iF1 + 1, 1) = "Progetto di una trave di fondazione"
        End If
    Else
        If Pilastro Then
            .Cells(iF1 + 1, 1) = "Verifica di un pilastro"
        ElseIf Trave Then
            .Cells(iF1 + 1, 1) = "Verifica di una trave"
        ElseIf TraveFondaz Then
            .Cells(iF1 + 1, 1) = "Verifica di una trave di fondazione"
        End If
    End If
    iF1 = iF1 + 3
    If MetodoSL18 And CalcVerif And (FormSez = "Rettangolare" Or FormSez = "Circolare piena o cava") Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "TIPO DI CONFINAMENTO DEL CALCESTRUZZO"
        If blnConfinNessuno Then
            .Cells(iF1 + 1, 1) = "nessun confinamento"
        ElseIf blnConfinStaffe Then
            .Cells(iF1 + 1, 1) = "confinamento dovuto alle staffe chiuse e legature"
        ElseIf blnConfinFRP Then
            .Cells(iF1 + 1, 1) = "confinamento ottenuto con compositi FRP"
        ElseIf blnConfinCamicieAcc Then
            .Cells(iF1 + 1, 1) = "confinamento ottenuto con camicie di acciaio (angolari e calastrelli)"
        End If
        iF1 = iF1 + 3
    End If
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "FORMA SEZIONE"
    .Cells(iF1 + 1, 1) = FormSez
    iF1 = iF1 + 2
    If FormSez = "Generica" Then
        .Cells(iF1, 1) = "n° di poligonali che compongono la sezione,   Npolig=" & Npolig
        iF1 = iF1 + 1
    End If
    iF1 = iF1 + 1
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "STATO DI SOLLECITAZIONE CHE AGISCE SULLA SEZIONE"
    If SollecPiane Then
        .Cells(iF1 + 1, 1) = "Stato di sollecitazione piano Nx, Tz, My"
    Else
        .Cells(iF1 + 1, 1) = "Stato di sollecitazione spaziale Nx, Ty, Tz, Mx, My, Mz"
    End If
    iF1 = iF1 + 3
    '2. GEOMETRIA
    '2.1 Sezione e armatura
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "GEOMETRIA SEZIONE"
    .Cells(iF1 + 1, 1) = "forma: " & FormSez
    If FormSez = "Rettangolare" Or FormSez = "a T" Or FormSez = "a doppio T" Or FormSez = "a T rovescia" Or FormSez = "Scatolare" Then
        .Cells(iF1 + 2, 1) = "base,   B=" & B / fmL & umL
        .Cells(iF1 + 3, 1) = "altezza,   H=" & H / fmL & umL
        iF1 = iF1 + 4
        If FormSez = "a T" Or FormSez = "a doppio T" Or FormSez = "a T rovescia" Then
            .Cells(iF1, 1) = "spessore ali,   s=" & S / fmL & umL
            .Cells(iF1 + 1, 1) = "spessore anima,   Bo=" & Bo / fmL & umL
            iF1 = iF1 + 2
        ElseIf FormSez = "Scatolare" Then
            .Cells(iF1, 1) = "spessore pareti,   S=" & S / fmL & umL
            iF1 = iF1 + 1
        End If
        .Cells(iF1, 1) = "copriferro,   Cf=" & Cf / fmL & umL
        iF1 = iF1 + 1
        If CalcVerif Then
            .Cells(iF1, 1).Select
            FormattaCella False, TipoCaratt, Hcaratt, False, True, 0, False, False
            If Armat2Lembi Then
                .Cells(iF1, 1) = "Barre di armature presenti ai lembi superiore e inferiore della sezione"
                .Cells(iF1 + 1, 1) = "diametro barre superiori,   dsup=" & dsup / fmDiamTond & umDiamTond
                .Cells(iF1 + 2, 1) = "n° barre superiori,   Nbs=" & Nbs
                .Cells(iF1 + 3, 1) = "area metallica lembo superiore,   Asup=" & Round(Asup / fmL2, 2) & umL2
                .Cells(iF1 + 4, 1) = "diametro barre inferiori,   dinf=" & dinf / fmDiamTond & umDiamTond
                .Cells(iF1 + 5, 1) = "n° barre inferiori,   Nbi=" & Nbi
                .Cells(iF1 + 6, 1) = "area metallica lembo inferiore,   Ainf=" & Round(Ainf / fmL2, 2) & umL2
                iF1 = iF1 + 7
            Else
                .Cells(iF1, 1) = "Coordinate ferri d'armatura longitudinali e diametri"
                .Cells(iF1 + 1, 1) = "n."
                .Cells(iF1 + 1, 2) = "y' (cm)"
                .Cells(iF1 + 1, 3) = "z' (cm)"
                .Cells(iF1 + 1, 4) = "D (mm)"
                iF1 = iF1 + 2
                For i = 1 To Nbar
                    .Cells(iF1, 1) = i
                    .Cells(iF1, 2) = Round(Yb_pr(i) / fmL, 1)
                    .Cells(iF1, 3) = Round(Zb_pr(i) / fmL, 1)
                    .Cells(iF1, 4) = Round(Db(i) / fmDiamTond, 0)
                    iF1 = iF1 + 1
                Next i
            End If
        End If
    ElseIf FormSez = "Circolare piena o cava" Then
        .Cells(iF1 + 2, 1) = "copriferro,   Cf=" & Cf / fmL & umL
        .Cells(iF1 + 3, 1) = "diametro esterno,   D=" & D / fmL & umL
        .Cells(iF1 + 4, 1) = "diametro interno,   Di=" & Di / fmL & umL
        iF1 = iF1 + 5
        If CalcVerif Then
            .Cells(iF1, 1) = "diametro barre,   D=" & Df / fmDiamTond & " mm"
            .Cells(iF1 + 1, 1) = "n° barre = " & Nbar
            iF1 = iF1 + 2
        End If
    ElseIf FormSez = "Generica" Then
        .Cells(iF1 + 2, 1).Select
        FormattaCella False, TipoCaratt, Hcaratt, False, True, 0, False, False
        .Cells(iF1 + 2, 1) = "coordinate vertici sezione"
        iF1 = iF1 + 3
        Np_max = 0
        For j = 1 To Npolig Step 1
            .Cells(iF1, 3 * j - 2) = "vert."
            .Cells(iF1, 3 * j - 1) = "y' (cm)"
            .Cells(iF1, 3 * j) = "z' (m)"
            'carica coordinate poligonale j
            CaricaDaFg2CoordPolig j '1.2
            If Np > Np_max Then Np_max = Np
            For i = 1 To Np Step 1
                .Cells(iF1 + i, 3 * j - 2) = i
                .Cells(iF1 + i, 3 * j - 1) = Ys_pr(i) / fmL
                .Cells(iF1 + i, 3 * j - 0) = Zs_pr(i) / fmL
            Next i
        Next j
        iF1 = iF1 + Np_max + 1
        .Cells(iF1 + 1, 1).Select
        FormattaCella False, TipoCaratt, Hcaratt, False, True, 0, False, False
        .Cells(iF1 + 1, 1) = "Coordinate ferri d'armatura longitudinali e diametri"
        .Cells(iF1 + 2, 1) = "n."
        .Cells(iF1 + 2, 2) = "y' (cm)"
        .Cells(iF1 + 2, 3) = "z' (cm)"
        .Cells(iF1 + 2, 4) = "D (mm)"
        iF1 = iF1 + 3
        For i = 1 To Nbar
            .Cells(iF1, 1) = i
            .Cells(iF1, 2) = Round(Yb_pr(i) / fmL, 1)
            .Cells(iF1, 3) = Round(Zb_pr(i) / fmL, 1)
            .Cells(iF1, 4) = Round(Db(i) / fmDiamTond, 0)
            iF1 = iF1 + 1
        Next i
    End If
    iF1 = iF1 + 1
    '2.2 Composito fibrorinforzato x rinforzo a flessione e taglio
    If RinfFRP Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "GEOMETRIA COMPOSITO DI RINFORZO A FLESSIONE E/O TAGLIO (FRP) "
        .Cells(iF1 + 1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1 + 1, 1) = "Rinforzo a flessione"
        .Cells(iF1 + 2, 1) = "larghezza,   Bf=" & B_frp / fmL & umL
        .Cells(iF1 + 3, 1) = "spessore,   Hf=" & H_frp / fmL & umL
        iF1 = iF1 + 4
        If Ty <> 0 Or Tz <> 0 Then
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
            .Cells(iF1, 1) = "Rinforzo a taglio"
            .Cells(iF1 + 1, 1) = "disposizione strisce: " & DisposizFRP
            .Cells(iF1 + 2, 1) = "continuità sistema di rinforzo: " & DisposizFRP
            .Cells(iF1 + 3, 1) = "larghezza strisce,   Bf=" & B_f / fmL & umL
            .Cells(iF1 + 4, 1) = "spessore strisce,   tf=" & t_f / fmL & umL
            .Cells(iF1 + 5, 1) = "passo strisce,   pf=" & p_f / fmL & umL
            .Cells(iF1 + 6, 1) = "angolo inclinazione strisce rispetto l'asse dell'asta,  Alfa_ta=" & Round(Alfa_ta_frp * 180 / PiGreco, 2) & "°"
            .Cells(iF1 + 7, 1) = "percentuale dell'altezza trave interessata dal rinforzo = " & Perc_H * 100 & "%"
            .Cells(iF1 + 8, 1) = "raggio arrotondamento spigoli sezione,   rc=" & rc / fmL & umL
            iF1 = iF1 + 9
        End If
        iF1 = iF1 + 1
    End If
    '2.3 Confinamento con fibrorinforzati FRP
    If blnConfinFRP Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "GEOMETRIA COMPOSITI FIBRORINFORZATI (FRP) PER CONFINAMENTO"
        .Cells(iF1 + 1, 1) = "tipo di confinamento: " & TipoConfinFRP
        .Cells(iF1 + 2, 1) = "larghezza strisce,   bf=" & Bf_ / fmL & umL
        .Cells(iF1 + 3, 1) = "spessore strisce,   tf=" & tf_ / fmL & umL
        .Cells(iF1 + 4, 1) = "passo strisce,   pf=" & pf_ / fmL & umL
        .Cells(iF1 + 5, 1) = "angolo inclinazione fibre rispetto alla normale all'asse dell'asta,  Alfa_f=" & Round(Alfa_fib * 180 / PiGreco, 2) & "°"
        .Cells(iF1 + 6, 1) = "raggio arrotondamento spigoli sezione,   rc=" & rc_ / fmL & umL
        iF1 = iF1 + 8
    End If
    '2.4 Rinforzo a taglio con calastrelli
    'If RinfCamicieAcc Then
        '.Cells(iF1, 1).Select
        'FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        '.Cells(iF1, 1) = "GEOMETRIA CAMICIE DI ACCIAIO DI RINFORZO A TAGLIO"
        '.Cells(iF1 + 1, 1) = "tipo di rinforzo: " & TipoConfinCamicieAcc
        '.Cells(iF1 + 2, 1) = "larghezza delle bande,   b=" & Bj / fmL & umL
        '.Cells(iF1 + 3, 1) = "spessore delle bande,   t=" & tj / fmL & umL
        '.Cells(iF1 + 4, 1) = "passo delle bande,   p=" & pj / fmL & umL
        'iF1 = iF1 + 6
    'End If
    '2.5 Confinamento con calastrelli
    If RinfCamicieAcc Or blnConfinCamicieAcc Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "GEOMETRIA CAMICIE DI ACCIAIO DI CONFINAMENTO"
        .Cells(iF1 + 1, 1) = "tipo di confinamento: " & TipoConfinCamicieAcc2
        .Cells(iF1 + 2, 1) = "larghezza delle bande,   b=" & Bf_ / fmL & umL
        .Cells(iF1 + 3, 1) = "spessore delle bande,   t=" & tf_ / fmL & umL
        .Cells(iF1 + 4, 1) = "passo delle bande,   p=" & pf_ / fmL & umL
        .Cells(iF1 + 5, 1) = "raggio arrotondamento spigoli sezione,   rc=" & rc_ / fmL & umL
        iF1 = iF1 + 7
    End If
    '3. MATERIALI
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "MATERIALE CALCESTRUZZO E ACCIAIO PER C.A."
    '3.1 Cls e acciaio
    .Cells(iF1 + 1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1 + 1, 1) = "Calcestruzzo"
    .Cells(iF1 + 2, 1) = "resistenza caratteristica cubica a compressione,   Rck=" & Rck / fmFL_2 & umTens
    .Cells(iF1 + 3, 1) = "modulo di elasticità longitudinale,   Ec=" & FormatNumber(Ec / fmFL_2, 0, , , vbTrue) & umTens
    If MetodoTA Then
        .Cells(iF1 + 4, 1) = "tensione ammissibile di compressione (ridotta),   scar=" & FormatNumber(Sigcar / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 5, 1) = "tensione ammissibile di compressione,   sca=" & FormatNumber(Sigca / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 6, 1) = "tensione tangenziale ammissibile in assenza di specifica armatura a taglio,   tc0=" & FormatNumber(TauC0 / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 7, 1) = "tensione tangenziale ammissibile in presenza di specifica armatura a taglio,   tc1=" & FormatNumber(TauC1 / fmFL_2, 2, , , vbTrue) & umTens
        iF1 = iF1 + 8
    ElseIf MetodoSL08 Or MetodoSL18 Then
        .Cells(iF1 + 4, 1) = "coeff. parziale di sicurezza,   gc=" & Gammac
        If blnParabRettang Then
            .Cells(iF1 + 5, 1) = "diagramma di calcolo tensione-deformazione: parabola-rettangolo"
        ElseIf blnTriangRettang Then
            .Cells(iF1 + 5, 1) = "diagramma di calcolo tensione-deformazione: triangolo-rettangolo"
        ElseIf blnStressBlock Then
            .Cells(iF1 + 5, 1) = "diagramma di calcolo tensione-deformazione: rettangolo (Stress Block)"
        End If
        .Cells(iF1 + 6, 1) = "deformazione    ec2=" & Eps_c2 * 100 & "%"
        .Cells(iF1 + 7, 1) = "deformazione    ec3=" & Eps_c3 * 100 & "%"
        .Cells(iF1 + 8, 1) = "deformazione    ec4=" & Eps_c4 * 100 & "%"
        .Cells(iF1 + 9, 1) = "deformazione di rottura o ultima,   ecu=" & Eps_cu * 100 & "%"
        .Cells(iF1 + 10, 1) = "resistenza media a compress. cilindrica,   fcm=" & Round(fcm / fmFL_2, 2) & umTens
        .Cells(iF1 + 11, 1) = "resistenza caratteristica a compress. cilindrica a 28 gg,   fck=" & Round(fck / fmFL_2, 2) & umTens
        .Cells(iF1 + 12, 1) = "resistenza di progetto a compressione,   fcd=" & Round(fcd / fmFL_2, 2) & umTens
        .Cells(iF1 + 13, 1) = "resistenza media a trazione,   fctm=" & Round(fctm / fmFL_2, 2) & umTens
        .Cells(iF1 + 14, 1) = "resistenza caratteristica a trazione,   fctk=" & Round(fctk / fmFL_2, 2) & umTens
        .Cells(iF1 + 15, 1) = "resistenza di progetto a trazione,   fctd=" & Round(fctd / fmFL_2, 2) & umTens
        iF1 = iF1 + 16
    End If
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1, 1) = "Acciaio"
    .Cells(iF1 + 1, 1) = "tipo di acciaio: " & TipoAcciaioCA
    .Cells(iF1 + 2, 1) = "modulo di elasticità longitudinale,   Es=" & FormatNumber(Es / fmFL_2, 0, , , vbTrue) & umTens
    .Cells(iF1 + 3, 1) = "coefficiente di omogeneizzazione,   n=" & n
    If MetodoTA Then
        .Cells(iF1 + 4, 1) = "tensione ammissibile a compressione/trazione,   sfa=" & FormatNumber(Sigfa / fmFL_2, 0, , , vbTrue) & umTens
        .Cells(iF1 + 5, 1) = "tensione ammissibile convenzionale a compressione/trazione,   sfac=" & FormatNumber(Sigfac / fmFL_2, 0, , , vbTrue) & umTens
        iF1 = iF1 + 7
    ElseIf MetodoSL08 Or MetodoSL18 Then
        .Cells(iF1 + 4, 1) = "coeff. parziale di sicurezza,   gs=" & Gammas
        If blnElastPerfettPlastico Then
            .Cells(iF1 + 5, 1) = "diagramma di calcolo tensione-deformazione: elastico-perfettamente plastico"
            iF1 = iF1 + 6
        ElseIf blnTriangRettang Then
            .Cells(iF1 + 5, 1) = "diagramma di calcolo tensione-deformazione: bilineare"
            .Cells(iF1 + 6, 1) = "rapporto di sovraresistenza,   k=" & Kincr
            iF1 = iF1 + 7
        End If
        If CemArmOrd Then
            .Cells(iF1, 1) = "deformazione di snervamento,   eyd=" & Round(Eps_yd * 100, 3) & "%"
            .Cells(iF1 + 1, 1) = "deformazione a rottura,   esu=" & Eps_su * 100 & "%"
            .Cells(iF1 + 2, 1) = "tensione caratteristica di snervamento,   fyk=" & FormatNumber(fyk / fmFL_2, 2, , , vbTrue) & umTens
            .Cells(iF1 + 3, 1) = "resistenza di progetto dell'acciaio,   fyd=" & FormatNumber(fyd / fmFL_2, 2, , , vbTrue) & umTens
            iF1 = iF1 + 5
        ElseIf CemCAP Then
            .Cells(iF1, 1) = "dati sull'acciaio armonico da precompressione"
            .Cells(iF1 + 1, 1) = "   deformazione alla tensione convenzionale caratt. di snervamento,   Eps_yd=" & Round(Eps_yd * 100, 3) & "%"
            .Cells(iF1 + 2, 1) = "   deformazione a rottura,   Eps_su=" & Eps_su * 100 & "%"
            .Cells(iF1 + 3, 1) = "   tensione convenzionale caratteristica di snervamento,   fyk=" & FormatNumber(fyk / fmFL_2, 2, , , vbTrue) & umTens
            .Cells(iF1 + 4, 1) = "   resistenza di progetto dell'acciaio,   fyd=" & FormatNumber(fyd / fmFL_2, 2, , , vbTrue) & umTens
            iF1 = iF1 + 5
            .Cells(iF1, 1) = "dati sull'acciaio ordinario eventualmente presente nella trave in C.A.P."
            .Cells(iF1 + 1, 1) = "   tensione caratteristica di snervamento,   fyk=" & fyk2 & umTens
            .Cells(iF1 + 2, 1) = "   resistenza di progetto,   fyd=" & Round(fyk2 / Gammas, 2) & umTens
            iF1 = iF1 + 4
        End If
    End If
    '3.2 acciaio esistente
    If RinfCamicieCA Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "MATERIALE ACCIAIO ESISTENTE (nelle camicie in C.A.)"
        .Cells(iF1 + 1, 1) = "coeff. parziale di sicurezza,   gs=" & Gammas_e
        .Cells(iF1 + 2, 1) = "fattore di confidenza,   FC=" & FC
        .Cells(iF1 + 3, 1) = "tensione media di rottura,   fym=" & FormatNumber(fym / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 4, 1) = "resistenza di progetto dell'acciaio,   fyd=" & FormatNumber(fyd_e / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 5, 1) = "deformazione di progetto di snervamento,   eyd=" & Round(Eps_yd_e * 100, 3) & "%"
        iF1 = iF1 + 7
    End If
    '3.3 calcestruzzo fibrorinforato
    If CemFRC Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "MATERIALE CALCESTRUZZO FIBRORINFORZATO - FRC (resistente a trazione)"
        If blnLineareIncrud Then
            .Cells(iF1 + 1, 1) = "diagramma tensione-deformazione a trazione: Lineare incrudente"
        ElseIf blnLineareDegrad Then
            .Cells(iF1 + 1, 1) = "diagramma tensione-deformazione a trazione: Lineare degradante"
        ElseIf blnRigidoPlastico Then
            .Cells(iF1 + 1, 1) = "diagramma tensione-deformazione a trazione: Rigido-plastico"
        End If
        If blnLineareIncrud Or blnLineareDegrad Then
            .Cells(iF1 + 2, 1) = "deformazione di picco,   eFs=" & Eps_Fs * 100 & "%"
            .Cells(iF1 + 3, 1) = "deformazione di rottura a trazione,   eFu=" & Eps_Fu * 100 & "%"
            .Cells(iF1 + 4, 1) = "resistenza di progetto a trazione residua di esercizio,   fFts=" & Round(fFts / fmFL_2, 2) & umTens
            .Cells(iF1 + 5, 1) = "resistenza di progetto a trazione residua ultima,   fFtu=" & Round(fFtu / fmFL_2, 2) & umTens
            iF1 = iF1 + 7
        ElseIf blnRigidoPlastico Then
            .Cells(iF1 + 2, 1) = "deformazione di rottura a trazione    eFu=" & Eps_Fu * 100 & "%"
            .Cells(iF1 + 3, 1) = "resistenza di progetto a trazione residua ultima,   fFtu=" & Round(fFtu / fmFL_2, 2) & umTens
            iF1 = iF1 + 5
        End If
    End If
    '3.4 compositi fibrorinforati polimerici (FRP)
    If RinfFRP Or blnConfinFRP Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "MATERIALE COMPOSITI FIBRORINFORZATI a matrice polimerica FRP (resist. a trazione)"
        .Cells(iF1 + 1, 1) = "classe di rigidezza composito: " & RigidezzaFRP
        .Cells(iF1 + 2, 1) = "tipo di composito: " & TipoFRP
        .Cells(iF1 + 3, 1) = "modulo di elasticità longitudinale,   Ef=" & FormatNumber(E_frp / fmFL_2, 0, , , vbTrue) & umTens
        .Cells(iF1 + 4, 1) = "tensione caratteristica di rottura,   fpk=" & Round(fpk / fmFL_2, 2) & umTens
        .Cells(iF1 + 5, 1) = "coeff. parziale di sicurezza per i SLU,   gf=" & Gammaf
        .Cells(iF1 + 6, 1) = "coeff. parziale di sicurezza per il SLU di distacco dal supporto,   gfd=" & Gammaf_dist
        .Cells(iF1 + 7, 1) = "fattore di conversione ambientale,   Eta_a=" & Eta_a
        .Cells(iF1 + 8, 1) = "fattore di conversione per effetti di lunga durata,   Eta1=" & Eta1
        .Cells(iF1 + 9, 1) = "fattore di confidenza,   FC=" & FC
        .Cells(iF1 + 10, 1) = "resistenza di progetto per gli SLU,   fpd=" & Round(fpd / fmFL_2, 2) & umTens
        .Cells(iF1 + 11, 1) = "resistenza di progetto per gli SLE,   fpd_sle=" & Round(fpd_sle / fmFL_2, 2) & umTens
        .Cells(iF1 + 12, 1) = "deformazione caratteristica a rottura per trazione,   epk=" & Eps_pk * 100 & "%"
        .Cells(iF1 + 13, 1) = "deformazione di progetto a rottura per trazione,   epu=" & Eps_pu * 100 & "%"
        .Cells(iF1 + 14, 1) = "deformazione nel lembo teso preesistente all'pllicazione del rinforzo,   e0=" & Eps0f * 100 & "%"
        iF1 = iF1 + 16
    End If
    '3.5 acciaio angolari e calastrelli
    If RinfCamicieAcc Or blnConfinCamicieAcc Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "MATERIALE ACCIAIO ANGOLARI E CALASTRELLI"
        .Cells(iF1 + 1, 1) = "tipo di acciaio: " & TipoAcciaio
        .Cells(iF1 + 2, 1) = "modulo di elasticità longitudinale,   Es=" & FormatNumber(Es_a / fmFL_2, 0, , , vbTrue) & umTens
        .Cells(iF1 + 3, 1) = "tensione caratteristica di rottura,   ftk=" & FormatNumber(ftk_a / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 4, 1) = "tensione caratteristica di snervamento,   fyk=" & FormatNumber(fyk_a / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 5, 1) = "coeff. parziale di sicurezza,   gs=" & Gammas_a
        .Cells(iF1 + 6, 1) = "resistenza di progetto dell'acciaio,   fyd=" & FormatNumber(fyd_a / fmFL_2, 2, , , vbTrue) & umTens
        iF1 = iF1 + 8
    End If
    '4.SOLLECITAZIONI
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "CARATTERISTICHE DI SOLLECITAZIONI AGENTI SULLA SEZIONE"
    iF1 = iF1 + 1
    If MetodoTA = False And blnVerifSLE Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "Combinazione di carico per verifiche allo S.L.U."
        iF1 = iF1 + 1
    End If
    If SollecPiane Then
        .Cells(iF1, 1) = "sforzo normale,   Nx=" & Nx / fmF & umForze
        .Cells(iF1 + 1, 1) = "sforzo di taglio,   Tz=" & Tz / fmF & umForze
        .Cells(iF1 + 2, 1) = "momento flettente,   My=" & My / fmFL & umMomenti
        iF1 = iF1 + 3
    Else
        .Cells(iF1, 1) = "sforzo normale,   Nx=" & Nx / fmF & umForze
        .Cells(iF1 + 1, 1) = "sforzo di taglio,   Ty=" & Ty / fmF & umForze
        .Cells(iF1 + 2, 1) = "sforzo di taglio,   Tz=" & Tz / fmF & umForze
        .Cells(iF1 + 3, 1) = "momento torcente,   Mx=" & Mx / fmFL & umMomenti
        .Cells(iF1 + 4, 1) = "momento flettente,   My=" & My / fmFL & umMomenti
        .Cells(iF1 + 5, 1) = "momento flettente,   Mz=" & Mz / fmFL & umMomenti
        iF1 = iF1 + 6
    End If
    If MetodoTA = False And blnVerifSLE Then
        If Foglio2.Cells(34, 7) = "" Then Nx_c = 0 Else Nx_c = Foglio2.Cells(34, 7)  'caratteristica
        If Foglio2.Cells(35, 7) = "" Then My_c = 0 Else My_c = Foglio2.Cells(35, 7)
        If Foglio2.Cells(36, 7) = "" Then Mz_c = 0 Else Mz_c = Foglio2.Cells(36, 7)
        If Foglio2.Cells(34, 8) = "" Then Nx_f = 0 Else Nx_f = Foglio2.Cells(34, 8)  'frequente
        If Foglio2.Cells(35, 8) = "" Then My_f = 0 Else My_f = Foglio2.Cells(35, 8)
        If Foglio2.Cells(36, 8) = "" Then Mz_f = 0 Else Mz_f = Foglio2.Cells(36, 8)
        If Foglio2.Cells(34, 9) = "" Then Nx_qp = 0 Else Nx_qp = Foglio2.Cells(34, 9)  'quasi perman
        If Foglio2.Cells(35, 9) = "" Then My_qp = 0 Else My_qp = Foglio2.Cells(35, 9)
        If Foglio2.Cells(36, 9) = "" Then Mz_qp = 0 Else Mz_qp = Foglio2.Cells(36, 9)
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "Combinazione di carico caratteristica o rara (verifica agli S.L.E.)"
        .Cells(iF1 + 1, 1) = "sforzo normale,   Nx=" & Nx_c & umForze
        .Cells(iF1 + 2, 1) = "momento flettente,   My=" & My_c & umMomenti
        iF1 = iF1 + 3
        If SollecPiane = False Then
            .Cells(iF1, 1) = "momento flettente,   Mz=" & Mz_c & umMomenti
            iF1 = iF1 + 1
        End If
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "Combinazione di carico frequente (verifica agli S.L.E.)"
        .Cells(iF1 + 1, 1) = "sforzo normale,   Nx=" & Nx_f & umForze
        .Cells(iF1 + 2, 1) = "momento flettente,   My=" & My_f & umMomenti
        iF1 = iF1 + 3
        If SollecPiane = False Then
            .Cells(iF1, 1) = "momento flettente,   Mz=" & Mz_f & umMomenti
            iF1 = iF1 + 1
        End If
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "Combinazione di carico quasi permanente (verifica agli S.L.E.)"
        .Cells(iF1 + 1, 1) = "sforzo normale,   Nx=" & Nx_qp & umForze
        .Cells(iF1 + 2, 1) = "momento flettente,   My=" & My_qp & umMomenti
        iF1 = iF1 + 3
        If SollecPiane = False Then
            .Cells(iF1, 1) = "momento flettente,   Mz=" & Mz_qp & umMomenti
            iF1 = iF1 + 1
        End If
    End If
    iF1 = iF1 + 1
    '5.GEOMETRIA VERIFICHE DI STABILITA'
    If blnVerifCarPunta And Pilastro Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "DATI PER LA VERIFICA DI STABILITA' A CARICO DI PUNTA DELL'INTERA ASTA"
        .Cells(iF1 + 1, 1) = "lunghezza dell'asta,   L=" & L / fmL & umL
        .Cells(iF1 + 2, 1) = "sforzo normale di riferimento,   Nr=" & Nr / fmF & umForze
        .Cells(iF1 + 3, 1) = "momento flettente di riferimento,   Mr=" & Mr / fmFL & umMomenti
        iF1 = iF1 + 4
        If MetodoSL08 Then
            .Cells(iF1, 1) = "momento flettente all'estremo iniziale del pilastro,   Mi=" & Mi / fmFL & umMomenti
            .Cells(iF1 + 1, 1) = "momento flettente all'estremo finale del pilastro,   Mk=" & Mk / fmFL & umMomenti
            iF1 = iF1 + 2
        End If
        .Cells(iF1, 1) = "coefficiente beta nel piano di inflessione zx,   beta_y=" & Beta_y
        .Cells(iF1 + 1, 1) = "coefficiente beta nel piano di inflessione xy,   beta_z=" & Beta_z
        iF1 = iF1 + 3
    End If
    '6. ALTRI DATI
    If CalcVerif = False Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "DATI PROGETTO ARMATURA A FLESSIONE"
        iF1 = iF1 + 1
        If MetodoSL08 Or MetodoSL18 Then
            If ZonaSismStruttDissip Then
                .Cells(iF1, 1) = "Limitazioni di armatura per strutture a comportam. dissipativo in zona sismica (7.4.6.2 NTC)"
                If blnCDA Then
                    .Cells(iF1 + 1, 1) = "Classe Duttilità Alta (CD ""A"")"
                Else
                    .Cells(iF1 + 1, 1) = "Classe Duttilità Media (CD ""B"")"
                End If
                iF1 = iF1 + 2
            Else
                .Cells(iF1, 1) = "Limitazioni di armatura per strutture a comportam. non dissipativo o in zona non sismica (4.1.6.1 NTC)"
                iF1 = iF1 + 1
            End If
        End If
        .Cells(iF1, 1) = "diametro tondini,   dfp=" & dfp / fmDiamTond & " mm"
        .Cells(iF1 + 1, 1) = "spazio minimo tra le barre (interferro),   sLmin=" & sLmin / fmL & umL
        .Cells(iF1 + 2, 1) = "interasse massimo tra le barre,   Pmax=" & Pmax / fmL & umL
        .Cells(iF1 + 3, 1) = "rapporto armature,   Mu=A'f/Af=" & Mu_
        iF1 = iF1 + 5
    End If
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "ARMATURA TRASVERSALE"
    .Cells(iF1 + 1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1 + 1, 1) = "a Taglio"
    .Cells(iF1 + 2, 1) = "angolo di inclinazione dell'armat. trasvers. rispetto all'asse della trave,   Alfa=" & Alfa_ta * 180 / PiGreco & "°"
    .Cells(iF1 + 3, 1) = "angolo di inclinazione delle fessure,   Teta=" & Round(Teta_ta * 180 / PiGreco, 2) & "°"
    .Cells(iF1 + 4, 1) = "diametro armatura trasversale,   Dst_ta=" & Dst_ta / fmDiamTond & umDiamTond
    iF1 = iF1 + 5
    If CalcVerif Then
        .Cells(iF1, 1) = "interasse o passo tra due armature trasversali consecutive,   s=" & Pst_ta & umL
        iF1 = iF1 + 1
    End If
    If FormSez <> "Circolare piena o cava" Then
        .Cells(iF1, 1) = "n° di braccia (o ferri piegati) lungo z,   Nbr_z=" & Nbrz
        .Cells(iF1 + 1, 1) = "n° di braccia (o ferri piegati) lungo y,   Nbr_y=" & Nbry
        .Cells(iF1 + 2, 1) = "area armatura trasversale complessiva lungo y,   Asw_y=" & Round(Asw_tay / fmL2, 2) & umL2
        .Cells(iF1 + 3, 1) = "area armatura trasversale complessiva lungo z,   Asw_z=" & Round(Asw_taz / fmL2, 2) & umL2
        iF1 = iF1 + 4
    ElseIf FormSez = "Circolare piena o cava" Then
        If StaffeCircSingole Then
            .Cells(iF1, 1) = "staffe circolari singole"
        Else
            .Cells(iF1, 1) = "staffa a spirale"
        End If
        iF1 = iF1 + 1
    End If
    If SollecPiane = False Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "a Torsione"
        iF1 = iF1 + 1
        If CalcVerif Then
            .Cells(iF1, 1) = "armatura longitudinale dedicata,   Al_to=" & Al_to / fmL2 & umL2
            iF1 = iF1 + 1
        End If
        .Cells(iF1, 1) = "angolo di inclinazione dell'armat. trasvers. rispetto all'asse della trave,   Alfa=" & Alfa_to * 180 / PiGreco & "°"
        .Cells(iF1 + 1, 1) = "angolo di inclinazione delle fessure,   Teta=" & Round(Teta_to * 180 / PiGreco, 2) & "°"
        .Cells(iF1 + 2, 1) = "diametro armatura trasversale,   Dst_to=" & Dst_to / fmDiamTond & umDiamTond
        .Cells(iF1 + 3, 1) = "interasse o passo tra due armature trasversali consecutive,   s=" & Pst_to / fmL & umL
        iF1 = iF1 + 4
    End If
    iF1 = iF1 + 1
    If MetodoSL18 And CalcVerif And SollecPiane And blnVerifDuttilità Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "DATI PER LA COSTRUZIONE DEL DIAGRAMMA MOMENTI-CURVATURA"
        .Cells(iF1 + 1, 1) = "n. posizioni di asse neutro da analizzare = " & Foglio2.Cells(27, 12)
        '.Cells(iF1 + 2, 1) = "incremento deformazioni = " & Foglio2.Cells(28, 12)
        .Cells(iF1 + 2, 1) = "altezza striscia elementare cls = " & Foglio2.Cells(29, 12) & umL
        .Cells(iF1 + 3, 1) = "intervallo di variazione asse neutro,   x1=" & Foglio2.Cells(30, 12) & umL & ",   x2=" & Foglio2.Cells(31, 12) & umL
        iF1 = iF1 + 5
    End If
    If CemCAP And MetodoTA = False Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "ALTRI DATI"
        .Cells(iF1 + 1, 1) = "deformazione iniziale dovuta alla pretenzione delle armature,   Eps0=" & Foglio2.Cells(42, 1)
        iF1 = iF1 + 3
    End If
    '7. VERICHE SLE
    If blnVerifSLE Then
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "VERIFICHE ALLO S.L.E."
        If blnCarichiBrevi Then
            .Cells(iF1 + 1, 1) = "carichi di breve durata"
        Else
            .Cells(iF1 + 1, 1) = "carichi di lunga durata o ciclici"
        End If
        .Cells(iF1 + 2, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, True, 0, False, False
        .Cells(iF1 + 2, 1) = "Verifiche di fessurazione"
        .Cells(iF1 + 3, 1) = "condizioni ambientali: " & CondizAmb
        .Cells(iF1 + 4, 1) = "sensibilità armature alla corrosione: " & SensibArmat
        If MetodoFess1996 Then
            .Cells(iF1 + 5, 1) = "metodo di calcolo ampiezze fessure: DM 1996 e relativa circolare"
        ElseIf MetodoFess2008 Then
            .Cells(iF1 + 5, 1) = "metodo di calcolo ampiezze fessure: DM 14/01/08 e Circ. 2/2/09 n. 617"
        End If
        .Cells(iF1 + 6, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, True, 0, False, False
        .Cells(iF1 + 6, 1) = "Verifiche delle tensioni di esercizio"
        .Cells(iF1 + 7, 1) = "tens. ammiss. nel cls per la combinazione rara=" & Perc_cls_c & "% di fck=" & FormatNumber(Perc_cls_c / 100 * fck / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 8, 1) = "tens. ammiss. nel cls per la combinazione quasi permanente=" & Perc_cls_qp & "% di fck=" & FormatNumber(Perc_cls_qp / 100 * fck / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 9, 1) = "tens. ammiss. nell'acciaio per la combinazione rara=" & Perc_acc_c & "% di fyk=" & FormatNumber(Perc_acc_c / 100 * fyk / fmFL_2, 2, , , vbTrue) & umTens
        .Cells(iF1 + 10, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, True, 0, False, False
        .Cells(iF1 + 10, 1) = "Verifiche allo stato limite di deformazione"
        .Cells(iF1 + 11, 1) = "coeff. per il calcolo della snellezza limite (funzione dello schema strutturale),   K=" & KK
        iF1 = iF1 + 13
    End If
    'IMPOSTAZIONI ED IPOTESI DI CALCOLO
    '.Cells(iF1 + 1, 1).Select
    'FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    '.Cells(iF1 + 1, 1) = "IMPOSTAZIONI ED IPOTESI DI CALCOLO"
    'If ClsResistTraz Then
        '.Cells(iF1 + 2, 1) = "Calcestruzzo resistente a trazione"
    'Else
        '.Cells(iF1 + 2, 1) = "Calcestruzzo non resistente a trazione"
    'End If
    'iF1 = iF1 + 3
    'DATI DI OUTPUT
    .Cells(iF1 + 1, 4).Select
        FormattaCella True, TipoCaratt, Hcaratt + 4, False, False, 0, False, False
    .Cells(iF1 + 1, 4) = "DATI DI OUTPUT"
    iF1 = iF1 + 2
End With
End Sub

Sub OutDatiSezioneCA() '4.2
With Foglio1
    .Cells(iF1 + 1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1 + 1, 1) = "DATI SULLA SEZIONE"
    .Cells(iF1 + 2, 1).Select
    FormattaCella False, TipoCaratt, Hcaratt, True, True, 0, False, False
    .Cells(iF1 + 2, 1) = "Sistema di riferimento y'z'"
    If FormSez = "Generica" Then
        .Cells(iF1 + 3, 1) = "Il sistema di riferimento y'z' è definito dall'utente all'atto di inserimento delle coordinate dei vertici della sezione"
        .Cells(iF1 + 4, 1) = "lunghezza massima della sez. lungo l'asse y',   B=" & Round((Ymax_pr - Ymin_pr) / fmL, 2) & umL
        .Cells(iF1 + 5, 1) = "lunghezza massima della sez. lungo l'asse z',   H=" & Round((Zmax_pr - Zmin_pr) / fmL, 2) & umL
        iF1 = iF1 + 6
    Else
        .Cells(iF1 + 3, 1) = "Per le sezioni rettangolare, a T, a T rovescia, a doppio T e scatolare, l'origine è posta nel vertice"
        .Cells(iF1 + 4, 1) = "della sezione in alto a destra, l'asse y' è orizzontale verso sinistra, l'asse z' verticale verso il"
        .Cells(iF1 + 5, 1) = "basso; per la sezione circolare piena o cava l'origine è nel centro della sezione"
        iF1 = iF1 + 6
    End If
    .Cells(iF1, 1).Select
    FormattaCella False, TipoCaratt, Hcaratt, True, True, 0, False, False
    .Cells(iF1, 1) = "Sezione geometrica e area complessiva armatura"
    .Cells(iF1 + 1, 1) = "area,   Asez=" & Round(Asez / fmL2, 2) & umL2
    .Cells(iF1 + 2, 1) = "perimetro,   Psez=" & Round(Psez / fmL, 2) & umL
    .Cells(iF1 + 3, 1) = "area dell'armatura metallica,   Aft=" & Round(Aft / fmL2, 2) & umL2
    .Cells(iF1 + 4, 1) = "rapporto,   Aft/Asez=" & Round(Aft / Asez * 100, 2) & "%"
    .Cells(iF1 + 5, 1) = "area cls ideale,   Aci=" & FormatNumber(Aci / fmL2, 2, , , vbTrue) & umL2
    .Cells(iF1 + 6, 1).Select
    FormattaCella False, TipoCaratt, Hcaratt, True, True, 0, False, False
    .Cells(iF1 + 6, 1) = "Sezione omogeneizzata"
    .Cells(iF1 + 7, 1) = "momento statico rispetto all'asse y',   Sy'=" & FormatNumber(Sy_pr / fmL3, 1, , , vbTrue) & umL3
    .Cells(iF1 + 8, 1) = "momento statico rispetto all'asse z',   Sz'=" & FormatNumber(Sz_pr / fmL3, 1, , , vbTrue) & umL3
    .Cells(iF1 + 9, 1) = "momento d'inerzia rispetto all'asse y',   Iy'=" & FormatNumber(Iy_pr / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 10, 1) = "momento d'inerzia rispetto all'asse z',   Iz'=" & FormatNumber(Iz_pr / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 11, 1) = "momento d'inerzia centrifugo rispetto agli assi y' z',   Iy'z'=" & FormatNumber(Iyz_pr / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 12, 1) = "distanza del baricentro G rispetto all'asse y',   z'G=" & FormatNumber(zG_pr / fmL, 1, , , vbTrue) & umL
    .Cells(iF1 + 13, 1) = "distanza del baricentro G rispetto all'asse z',   y'G=" & FormatNumber(yG_pr / fmL, 1, , , vbTrue) & umL
    .Cells(iF1 + 14, 1) = "momento d'inerzia rispetto all'asse y passante per il baric. G,   Iy=" & FormatNumber(Iy / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 15, 1) = "momento d'inerzia rispetto all'asse z passante per il baric. G,   Iz=" & FormatNumber(Iz / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 16, 1) = "momento d'inerzia centrifugo rispetto agli assi yz,   Iyz=" & FormatNumber(Iyz / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 17, 1) = "momento d'inerzia rispetto all'asse principale yp,   Iyp=" & FormatNumber(Iyp / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 18, 1) = "momento d'inerzia rispetto all'asse principale zp,   Izp=" & FormatNumber(Izp / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 19, 1) = "raggio giratore d'inerzia rispetto a yp,   r_yp=" & FormatNumber(ryp / fmL, 1, , , vbTrue) & umL
    .Cells(iF1 + 20, 1) = "raggio giratore d'inerzia rispetto a zp,   r_zp=" & FormatNumber(rzp / fmL, 1, , , vbTrue) & umL
    iF1 = iF1 + 22
End With
End Sub

Sub OutCalcoloTensNormali() '4.4
Dim Np_max%
With Foglio1
    'iF1 = iF1 + 1
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "TENSIONI NORMALI AGENTI SULLA SEZIONE"
    .Cells(iF1 + 1, 1) = "area del cls compresso,   Ac=" & Round(Ac / fmL2, 1) & umL2
    .Cells(iF1 + 2, 1) = "area ideale del cls,   Aci=" & Round(Aci / fmL2, 1) & umL2
    .Cells(iF1 + 3, 1) = "momento statico della sez. reagente rispetto all'asse y',   Sy'=" & FormatNumber(Sy_pr / fmL3, 1, , , vbTrue) & umL3
    .Cells(iF1 + 4, 1) = "momento statico della sez. reagente rispetto all'asse z',   Sz'=" & FormatNumber(Sz_pr / fmL3, 1, , , vbTrue) & umL3
    .Cells(iF1 + 5, 1) = "momento d'inerzia della sez. reagente rispetto all'asse y',   Iy'=" & FormatNumber(Iy_pr / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 6, 1) = "momento d'inerzia della sez. reagente rispetto all'asse z',   Iz'=" & FormatNumber(Iz_pr / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 7, 1) = "distanza del baricentro Gr della sez. reagente rispetto all'asse y',   z'Gr=" & FormatNumber(zGr_pr / fmL, 1, , , vbTrue) & umL
    .Cells(iF1 + 8, 1) = "distanza del baricentro Gr della sez. reagente rispetto all'asse z',   y'Gr=" & FormatNumber(yGr_pr / fmL, 1, , , vbTrue) & umL
    .Cells(iF1 + 9, 1) = "momento d'inerzia della sez. reagente rispetto all'asse yr passante per il baric. Gr,   Iyr=" & FormatNumber(Iy / fmL4, 1, , , vbTrue) & umL4
    .Cells(iF1 + 10, 1) = "momento d'inerzia della sez. reagente rispetto all'asse zr passante per il baric. Gr,   Izr=" & FormatNumber(Iz / fmL4, 1, , , vbTrue) & umL4
    iF1 = iF1 + 11
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1, 1) = "coordinate vertici sezione parzializzata"
    Np_max = 0
    For j = 1 To Npolig_ns Step 1
        .Cells(iF1 + 1, 3 * j - 2) = "vert."
        .Cells(iF1 + 1, 3 * j - 1) = "y' (cm)"
        .Cells(iF1 + 1, 3 * j) = "z' (cm)"
        Np = Foglio2.Cells(107, 22 + 2 * j)
        If Np > Np_max Then Np_max = Np
        For i = 1 To Np Step 1
            .Cells(iF1 + 1 + i, 3 * j - 2) = i
            .Cells(iF1 + 1 + i, 3 * j - 1) = Round(Foglio2.Cells(108 + i, 21 + 2 * j), 2)
            .Cells(iF1 + 1 + i, 3 * j) = Round(Foglio2.Cells(108 + i, 22 + 2 * j), 2)
        Next i
    Next j
    iF1 = iF1 + 1 + Np_max + 1
    'tensioni normali nel cls in corrispondenza dei vertici della sezione
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1, 1) = "Tensioni normali nel cls in corrispondenza dei vertici della sezione"
    Np_max = 0
    For j = 1 To Npolig Step 1
        .Cells(iF1 + 1, 3 * j - 2) = "vert."
        .Cells(iF1 + 1, 3 * j - 1) = "sig_c"
        .Cells(iF1 + 1, 3 * j) = "eps_c (%)"
        Np = Foglio2.Cells(4, 22 + 2 * j)
        If Np > Np_max Then Np_max = Np
        For i = 1 To Np Step 1
            SigVert(i) = Foglio2.Cells(5 + i, 50 + j) * fmFL_2
            EpsVert(i) = Foglio2.Cells(5 + i, 55 + j)
            .Cells(iF1 + 1 + i, 3 * j - 2) = i
            If ClsResistTraz = False Then
                If SigVert(i) < 0 Then
                    .Cells(iF1 + 1 + i, 3 * j - 1) = Round(SigVert(i), 1)
                Else
                    .Cells(iF1 + 1 + i, 3 * j - 1) = 0
                End If
            Else
                .Cells(iF1 + 1 + i, 3 * j - 1) = Round(SigVert(i), 1)
            End If
            .Cells(iF1 + 1 + i, 3 * j) = Round(EpsVert(i) * 100, 4)
        Next i
    Next j
    iF1 = iF1 + 1 + Np_max + 1
    If ClsResistTraz Then
        .Cells(iF1, 1) = "tensione più alta (con segno) nel cls = " & Round(Sigc_max / fmFL_2, 2) & umTens
        .Cells(iF1 + 1, 1) = "tensione più bassa (con segno) nel cls = " & Round(Sigc_min / fmFL_2, 2) & umTens
        iF1 = iF1 + 2
        If Sigc_pos > 0 Then
            .Cells(iF1, 1) = "tensione massima di trazione nel cls = " & Round(Sigc_pos / fmFL_2, 2) & umTens
            iF1 = iF1 + 1
        End If
        If Sigc < 0 Then
            .Cells(iF1, 1) = "tensione massima di compressione nel cls = " & Round(Sigc / fmFL_2, 2) & umTens
            iF1 = iF1 + 1
        End If
    Else
        .Cells(iF1, 1) = "tensione massima di compressione nel cls = " & Round(Sigc / fmFL_2, 2) & umTens
        iF1 = iF1 + 1
        If Nx < 0 Then
            .Cells(iF1, 1) = "tensione media (da sforzo normale Nx) di compressione nel cls = " & Round(SigMed / fmFL_2, 2) & umTens
            iF1 = iF1 + 1
        End If
    End If
    'tensioni nelle armature
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1, 1) = "Tensioni normali in corrispondenza delle armature"
    .Cells(iF1 + 1, 1) = "tond."
    .Cells(iF1 + 1, 2) = "sig_f"
    iF1 = iF1 + 1
    For i = 1 To Nbar Step 1
        .Cells(iF1 + i, 1) = i
        .Cells(iF1 + i, 2) = Round(Sig_fi(i), 2)
    Next i
    iF1 = iF1 + Nbar + 1
    .Cells(iF1, 1) = "tensione massima nelle armature = " & FormatNumber(Sigf / fmFL_2, 2, , , vbTrue) & umTens
    iF1 = iF1 + 2
End With
With Foglio2 'coordinate baricentro sezione reagente
    .Cells(17, 11) = yGr_pr / fmL
    .Cells(18, 11) = zGr_pr / fmL
End With
End Sub

Sub OutNoProg() '5.1
With Foglio1
    .Range(Cells(iF1, 1), Cells(iF1 + 2, 1)).Select
     FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
    .Cells(iF1, 1) = "Calcolo di progetto non possibile: l'armatura necessaria supera il massimo consentito dalla"
    .Cells(iF1 + 1, 1) = "normativa in rapporto all'area del cls. Occorre variare i dati di progetto (forma e/o"
    .Cells(iF1 + 2, 1) = "dimensioni sezione, materiali, diametro tondini, interferro, spazio libero tra le barre ecc.)"
    iF1 = iF1 + 3
End With
End Sub
