VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmMaterCA 
   Caption         =   "DATI MATERIALI"
   ClientHeight    =   8475.001
   ClientLeft      =   96
   ClientTop       =   624
   ClientWidth     =   18876
   OleObjectBlob   =   "frmMaterCA.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmMaterCA"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttCalcolaParam_Click()
Dim Rck#, fck#, fcd#, fcm#, fctm#, fctk#, fctd#, fyk#, fyd#, fyk2#
Dim Gammac#, Gammas#
Dim Sigca#, TauC0#, TauC1#, Sigfa#, Sigfac#
Dim Epsc2#, Epscu#, Epsc3#, Epsc4#
If cmbRck = "" Or cmbTipoAcciaioCA = "" Then
    MsgBox "Specificare Rck e/o il tipo di acciaio", vbInformation, VersioneSw
    Exit Sub
End If
If txtGammac = "" Or txtGammas = "" Then
    MsgBox "Specificare coefficienti parziali di sicurezza cls e acciaio (premi su imposta parametri)", vbInformation, VersioneSw
    Exit Sub
End If
If txtFyk = "" Then
    MsgBox "Specificare tensione caratt. di snervam. acciaio (premi su imposta parametri)", vbInformation, VersioneSw
    Exit Sub
End If
Rck = cmbRck
If MetodoTA Then
    If SistemaTecnico Then
        If CemArmOrd Then
            Sigca = Round(60 + (Rck - 150) / 4, 2)
            Select Case cmbTipoAcciaioCA
                Case "Fe B 22 k"
                    Sigfa = 1200
                Case "Fe B 32 k"
                    Sigfa = 1600
                Case "Fe B 38 k"
                    Sigfa = 2200
                Case "Fe B 44 k"
                    Sigfa = 2600
                'Case Else
                    'MsgBox "Specificare tipo di acciaio.", vbCritical, VersioneSw
            End Select
            If cmbTipoAcciaioCA = "Fe B 38 k" Or cmbTipoAcciaioCA = "Fe B 44 k" Then
                Sigfac = 1800 'barre ad aderenza migliorata
            Else
                Sigfac = 1200
            End If
        ElseIf CemCAP Then
            Sigca = Round(0.38 * Rck, 2)
            Sigfa = Round(0.85 * 16700, 2)
            Sigfac = Round(0.75 * Sigfa, 2)
        End If
        TauC0 = Round(4 + (Rck - 150) / 75, 2)
        TauC1 = Round(14 + (Rck - 150) / 35, 2)
        txtEs_ca = 2100000
        txtEc = Round(18000 * Rck ^ 0.5, 0)
    Else
        If CemArmOrd Then
            Sigca = Round(6 + (Rck - 15) / 4, 2)
            Select Case cmbTipoAcciaioCA
                Case "Fe B 22 k"
                    Sigfa = 115
                Case "Fe B 32 k"
                    Sigfa = 155
                Case "Fe B 38 k"
                    Sigfa = 215
                Case "Fe B 44 k"
                    Sigfa = 255
                'Case Else
                    'MsgBox "Specificare tipo di acciaio.", vbCritical, VersioneSw
            End Select
            If cmbTipoAcciaioCA = "Fe B 38 k" Or cmbTipoAcciaioCA = "Fe B 44 k" Then
                Sigfac = 175
            Else
                Sigfac = 115
            End If
        ElseIf CemCAP Then
            Sigca = Round(0.38 * Rck, 2)
            Sigfa = Round(0.85 * 1670, 2)
            Sigfac = Round(0.75 * Sigfa, 2)
        End If
        TauC0 = Round(0.4 + (Rck - 15) / 75, 2)
        TauC1 = Round(1.4 + (Rck - 15) / 35, 2)
        txtEs_ca = 206000
        txtEc = Round(5700 * Rck ^ 0.5, 0)
    End If
    txtSigca = Sigca
    txtTauc0 = TauC0
    txtTauc1 = TauC1
    txtSigfa = Sigfa
    txtSigfac = Sigfac
    txtN = 15
ElseIf MetodoSL08 Or MetodoSL18 Then
    '1.cls
    Gammac = txtGammac
    fck = 0.83 * Rck
    fcd = 0.85 * fck / Gammac
    If SistemaTecnico Then
        fcm = (fck * 9.81 / 100 + 8) * 100 / 9.81
        If Rck <= 600 Then
            fctm = (0.3 * (fck * 9.81 / 100) ^ (2 / 3)) * 100 / 9.81
        Else
            fctm = (2.12 * Log(1 + fcm / 10 * 9.81 / 100)) * 100 / 9.81
        End If
        txtEc = Round((22000 * (fcm * (9.81 / 100) / 10) ^ 0.3) * 100 / 9.81, 0)
        If Rck <= 600 Then 'calcolo Eps_c2,Eps_c3,Eps_c4 e Eps_cu
            Epscu = 0.35
            Epsc2 = 0.2
            Epsc3 = 0.175
            Epsc4 = 0.07
        Else
            Epscu = 0.26 + 3.5 * ((90 - fck * 0.0981) / 100) ^ 4 'fck deve essere in N/mm2
            Epsc2 = 0.2 + 0.0085 * (fck * 0.0981 - 50) ^ 0.53
            Epsc3 = 0.175 + 0.055 * (fck * 0.0981 - 50) / 40
            Epsc4 = 0.2 * Epscu
        End If
    Else
        fcm = fck + 8
        If Rck <= 600 Then
            fctm = 0.3 * fck ^ (2 / 3)
        Else
            fctm = 2.12 * Log(1 + fcm / 10)
        End If
        txtEc = Round(22000 * (fcm / 10) ^ 0.3, 0)
        If Rck <= 60 Then
            Epscu = 0.35
            Epsc2 = 0.2
            Epsc3 = 0.175
            Epsc4 = 0.07
        Else
            Epscu = 0.26 + 3.5 * ((90 - fck) / 100) ^ 4
            Epsc2 = 0.2 + 0.0085 * (fck - 50) ^ 0.53
            Epsc3 = 0.175 + 0.055 * (fck - 50) / 40
            Epsc4 = 0.2 * Epscu
        End If
    End If
    fctk = 0.7 * fctm
    fctd = fctk / Gammac
    txtFck = Round(fck, 2)
    txtFcd = Round(fcd, 2)
    txtFcm = Round(fcm, 2)
    txtFctm = Round(fctm, 2)
    txtFctk = Round(fctk, 2)
    txtFctd = Round(fctd, 2)
    txtEpsc2 = Round(Epsc2, 3)
    txtEpsc3 = Round(Epsc3, 3)
    txtEpsc4 = Round(Epsc4, 3)
    txtEpscu = Round(Epscu, 3)
    '2.acciaio
    Gammas = txtGammas
    'If CemArmOrd Then
        'fyk = 450 * fc3
    'Else
        'fyk = 1670 * fc3
        'fyk2 = 450 * fc3
    'End If
    txtEs_ca = 210000 * fc3
    fyk = txtFyk
    fyd = fyk / Gammas
    txtFyd = Round(fyd, 2)
    If CemCAP Then txtFyk2 = fyk2
    'coeff. omogeneizz
    txtN = 15 'Round(txtEs_ca / txtEc, 2)
End If
End Sub

Private Sub bttCancellaCls_Click()
With Me
    .txtEc = ""
    .txtEs_ca = ""
    .txtSigca = ""
    .txtTauc0 = ""
    .txtTauc1 = ""
    .txtSigfa = ""
    .txtSigfac = ""
    .txtFcm = ""
    .txtFck = ""
    .txtFcd = ""
    .txtFctm = ""
    .txtFctk = ""
    .txtFctd = ""
    .txtFyk = ""
    .txtFyd = ""
    .txtN = ""
    .txtEpssu = ""
    .txtK = ""
    .txtEpsc2 = ""
    .txtEpsc3 = ""
    .txtEpsc4 = ""
    .txtEpscu = ""
    .txtFyk2 = ""
    .txtGammac = ""
    .txtGammas = ""
End With
End Sub

Private Sub bttFRC_Click()
frmMaterFRC.Show
End Sub

Private Sub bttImpostaParam_Click()
'MetodoTA = Foglio2.Cells(57, 1)
'If MetodoTA Then txtN = 15
txtGammac = 1.5
txtGammas = 1.15
txtEpssu = 6.75
txtK = 1.2
If CemArmOrd Then
    txtFyk = 450 * fc3
Else
    txtFyk = 1670 * fc3
    txtFyk2 = 450 * fc3
End If
End Sub

Private Sub bttSalvaChiudi_Click()
'If cmbRck <> "" And cmbTipoAcciaioCA <> "" Then
    If MetodoTA Then
        If txtSigca = "" Or txtTauc0 = "" Or txtTauc1 = "" Or txtSigfa = "" Or txtSigfac = "" Then
            MsgBox "Inserire tensioni ammissibili per il C.A.", vbInformation, VersioneSw
            Exit Sub
        End If
    ElseIf MetodoSL08 Or MetodoSL18 Then
        If txtFcm = "" Or txtFck = "" Or txtFcd = "" Or txtFctm = "" Or txtFctk = "" Or txtFctd = "" Or txtFyk = "" Or txtFyd = "" Or txtGammac = "" Or txtGammas = "" Then
            MsgBox "Inserire tutti i dati del C.A. per le verifiche agli S.L.U.", vbInformation, VersioneSw
            Exit Sub
        End If
    End If
'End If
With Foglio2
    .Cells(19, 1) = cmbRck
    .Cells(18, 1) = cmbTipoAcciaioCA
    .Cells(9, 8) = txtEc
    .Cells(62, 1) = txtEs_ca
    .Cells(60, 1) = txtGammac
    .Cells(61, 1) = txtGammas
    .Cells(10, 8) = txtSigca
    .Cells(11, 8) = txtTauc0
    .Cells(12, 8) = txtTauc1
    .Cells(13, 8) = txtSigfa
    .Cells(14, 8) = txtSigfac
    .Cells(15, 8) = txtFcm
    .Cells(16, 8) = txtFck
    .Cells(17, 8) = txtFcd
    .Cells(18, 8) = txtFctm
    .Cells(19, 8) = txtFctk
    .Cells(20, 8) = txtFctd
    .Cells(21, 8) = txtFyk
    .Cells(22, 8) = txtFyd
    .Cells(65, 1) = optParabRettang
    .Cells(66, 1) = optRettang
    .Cells(67, 1) = optTriang
    '.Cells(70, 1) = chkClsConfinato
    .Cells(23, 8) = txtN
    .Cells(64, 1) = txtEpsc2
    .Cells(63, 3) = txtEpsc3
    .Cells(64, 3) = txtEpsc4
    .Cells(63, 1) = txtEpscu
    .Cells(24, 8) = optElastPlastico
    .Cells(25, 8) = optBilineare
    .Cells(26, 8) = txtEpssu
    .Cells(27, 8) = txtK
    .Cells(29, 8) = txtFyk2
    .Cells(19, 3) = Foglio3.Cells(4 + cmbRck.ListIndex + 1, 10)
End With
Unload Me
End Sub

Private Sub cmbRck_Change()
If cmbRck.ListIndex >= 0 Then lblClasseRes = "Classe di resistenza: " & Foglio3.Cells(4 + cmbRck.ListIndex + 1, 10) Else lblClasseRes = ""
End Sub

Private Sub optBilineare_Click()
If optBilineare Then
    txtK.Enabled = True
    lblK.Enabled = True
Else
    txtK.Enabled = False
    lblK.Enabled = False
End If
End Sub

Private Sub optElastPlastico_Click()
optBilineare_Click
End Sub

Private Sub txtEc_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEpsc2_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEpsc3_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEpsc4_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEpscu_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEpssu_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEs_ca_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFcd_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFck_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFcm_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFctd_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFctk_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFctm_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFyd_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFyk_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFyk2_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtGammac_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtGammas_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtK_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtN_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtSigca_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtSigfa_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtSigfac_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtTauc0_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtTauc1_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
MetodoTA = Foglio2.Cells(57, 1)
MetodoSL08 = Foglio2.Cells(58, 1)
MetodoSL18 = Foglio2.Cells(59, 1)
FormSez = Foglio2.Cells(54, 1)
CalcVerif = Foglio2.Cells(25, 1)
CemArmOrd = Foglio2.Cells(20, 1)
CemCAP = Foglio2.Cells(21, 1)
CemFRC = Foglio2.Cells(26, 1)
If SistemaTecnico Then
    cmbRck.RowSource = "Foglio3!i5:i21"
Else
    cmbRck.RowSource = "Foglio3!h5:h21"
End If
If CemArmOrd Then
    If MetodoTA Then
        cmbTipoAcciaioCA.RowSource = "Foglio3!g5:g8"
    Else
        cmbTipoAcciaioCA.RowSource = "Foglio3!f5:f5"
    End If
ElseIf CemCAP Then
    cmbTipoAcciaioCA.AddItem "Armonico"
End If
lblRck = "resistenza caratt. cubica del cls, Rck (" & umTens & ")"
lblEc = "modulo elastico longit. cls Ec (" & umTens & ")"
lblEs_ca = "modulo elastico longit. acciaio Es (" & umTens & ")"
lblSigca = "tens. ammiss. di compressione nel cls (" & umTens & ")"
lblTauc0 = "tens. tang. ammiss. nel cls, tc0 (" & umTens & ")"
lblTauc1 = "tens. tang. ammiss. nel cls, tc1 (" & umTens & ")"
lblSigfa = "tens. ammiss. acciaio (" & umTens & ")"
lblSigfac = "tens. ammiss. convenzionale acciaio (" & umTens & ")"
lblFcm = "resist. media a compress. cilindrica, fcm (" & umTens & ")"
lblFck = "resist. caratt. a compress. cilindrica, fck (" & umTens & ")"
lblFcd = "resist. di progetto a compressione, fcd (" & umTens & ")"
lblFctm = "resist. media a trazione, fctm (" & umTens & ")"
lblFctk = "resist. caratteristica a trazione, fctk (" & umTens & ")"
lblFctd = "resist. di progetto a trazione, fctd (" & umTens & ")"
If CemArmOrd Then
    lblFyk = "tensione caratt. di snervam. acciaio, fyk (" & umTens & ")"
ElseIf CemCAP Then
    lblFyk = "tensione caratt. convenzionale di snervam. acciaio, fyk (" & umTens & ")"
End If
lblFyd = "resistenza di progetto acciaio, fyd (" & umTens & ")"
lblFyk2 = "tensione caratt. di snervam. acciaio ordinario, fyk (" & umTens & ")"
DisabilitaControlli
With Me
    .cmbRck = Foglio2.Cells(19, 1)
    .cmbTipoAcciaioCA = Foglio2.Cells(18, 1)
    .optParabRettang = Foglio2.Cells(65, 1)
    .optRettang = Foglio2.Cells(66, 1)
    .optTriang = Foglio2.Cells(67, 1)
    .optElastPlastico = Foglio2.Cells(24, 8)
    .optBilineare = Foglio2.Cells(25, 8)
    '.chkClsConfinato = Foglio2.Cells(70, 1)
    .txtEc = Foglio2.Cells(9, 8)
    .txtEs_ca = Foglio2.Cells(62, 1)
    .txtGammac = Foglio2.Cells(60, 1)
    .txtGammas = Foglio2.Cells(61, 1)
    .txtSigca = Foglio2.Cells(10, 8)
    .txtTauc0 = Foglio2.Cells(11, 8)
    .txtTauc1 = Foglio2.Cells(12, 8)
    .txtSigfa = Foglio2.Cells(13, 8)
    .txtSigfac = Foglio2.Cells(14, 8)
    .txtEpsc2 = Foglio2.Cells(64, 1)
    .txtEpsc3 = Foglio2.Cells(63, 3)
    .txtEpsc4 = Foglio2.Cells(64, 3)
    .txtEpscu = Foglio2.Cells(63, 1)
    .txtFcm = Foglio2.Cells(15, 8)
    .txtFck = Foglio2.Cells(16, 8)
    .txtFcd = Foglio2.Cells(17, 8)
    .txtFctm = Foglio2.Cells(18, 8)
    .txtFctk = Foglio2.Cells(19, 8)
    .txtFctd = Foglio2.Cells(20, 8)
    .txtFyk = Foglio2.Cells(21, 8)
    .txtFyd = Foglio2.Cells(22, 8)
    .txtN = Foglio2.Cells(23, 8)
    .txtEpssu = Foglio2.Cells(26, 8)
    .txtK = Foglio2.Cells(27, 8)
    .txtFyk2 = Foglio2.Cells(29, 8)
End With
End Sub

Sub DisabilitaControlli()
If MetodoTA Then
    lblTA.Enabled = True
    lblSigca.Enabled = True
    txtSigca.Enabled = True
    lblTauc0.Enabled = True
    txtTauc0.Enabled = True
    lblTauc1.Enabled = True
    txtTauc1.Enabled = True
    lblSigfa.Enabled = True
    txtSigfa.Enabled = True
    lblSigfac.Enabled = True
    txtSigfac.Enabled = True
    'txtN.Enabled = True
    'lblN.Enabled = True
    lblSLU.Enabled = False
    lblFcm.Enabled = False
    txtFcm.Enabled = False
    lblFck.Enabled = False
    txtFck.Enabled = False
    lblFcd.Enabled = False
    txtFcd.Enabled = False
    lblFctm.Enabled = False
    txtFctm.Enabled = False
    lblFctk.Enabled = False
    txtFctk.Enabled = False
    lblFctd.Enabled = False
    txtFctd.Enabled = False
    lblGammas.Enabled = False
    txtGammas.Enabled = False
    lblGammac.Enabled = False
    txtGammac.Enabled = False
    lblFyk.Enabled = False
    txtFyk.Enabled = False
    lblFyd.Enabled = False
    txtFyd.Enabled = False
    Frame1.Enabled = False
    optParabRettang.Enabled = False
    optRettang.Enabled = False
    optTriang.Enabled = False
    optElastPlastico.Enabled = False
    optBilineare.Enabled = False
    txtEpsc2.Enabled = False
    lblEpsc2.Enabled = False
    txtEpsc3.Enabled = False
    lblEpsc3.Enabled = False
    txtEpsc4.Enabled = False
    lblEpsc4.Enabled = False
    txtEpscu.Enabled = False
    lblEpscu.Enabled = False
    Frame2.Enabled = False
    txtEpssu.Enabled = False
    lblEpssu.Enabled = False
    txtK.Enabled = False
    lblK.Enabled = False
    lblCAP.Enabled = False
    txtFyk2.Enabled = False
    lblFyk2.Enabled = False
Else 'SLU
    lblTA.Enabled = False
    lblSigca.Enabled = False
    txtSigca.Enabled = False
    lblTauc0.Enabled = False
    txtTauc0.Enabled = False
    lblTauc1.Enabled = False
    txtTauc1.Enabled = False
    lblSigfa.Enabled = False
    txtSigfa.Enabled = False
    lblSigfac.Enabled = False
    txtSigfac.Enabled = False
    'txtN.Enabled = False
    'lblN.Enabled = False
    lblSLU.Enabled = True
    lblFcm.Enabled = True
    txtFcm.Enabled = True
    lblFck.Enabled = True
    txtFck.Enabled = True
    lblFcd.Enabled = True
    txtFcd.Enabled = True
    lblFctm.Enabled = True
    txtFctm.Enabled = True
    lblFctk.Enabled = True
    txtFctk.Enabled = True
    lblFctd.Enabled = True
    txtFctd.Enabled = True
    lblGammas.Enabled = True
    txtGammas.Enabled = True
    lblGammac.Enabled = True
    txtGammac.Enabled = True
    lblFyk.Enabled = True
    txtFyk.Enabled = True
    lblFyd.Enabled = True
    txtFyd.Enabled = True
    Frame1.Enabled = True
    optParabRettang.Enabled = True
    optRettang.Enabled = True
    optTriang.Enabled = True
    optElastPlastico.Enabled = True
    optBilineare.Enabled = True
    txtEpsc2.Enabled = True
    lblEpsc2.Enabled = True
    txtEpsc3.Enabled = True
    lblEpsc3.Enabled = True
    txtEpsc4.Enabled = True
    lblEpsc4.Enabled = True
    txtEpscu.Enabled = True
    lblEpscu.Enabled = True
    Frame2.Enabled = True
    txtEpssu.Enabled = True
    lblEpssu.Enabled = True
    txtK.Enabled = True
    lblK.Enabled = True
    If CemArmOrd Then
        lblCAP.Enabled = False
        txtFyk2.Enabled = False
        lblFyk2.Enabled = False
    ElseIf CemCAP Then
        lblCAP.Enabled = True
        txtFyk2.Enabled = True
        lblFyk2.Enabled = True
    End If
End If
End Sub
