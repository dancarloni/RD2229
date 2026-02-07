VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmMaterFRP 
   Caption         =   "DATI MATERIALE COMPOSITO A MATRICE POLIMERICA FRP"
   ClientHeight    =   6435
   ClientLeft      =   84
   ClientTop       =   576
   ClientWidth     =   11004
   OleObjectBlob   =   "frmMaterFRP.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmMaterFRP"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttCalcolaParam_Click()
Dim Ep#, Epspu#, Epspk#, fpk#, fpd#, fpd2#, Gammap#, Eta_a#, Eta1#
'1. input
If txtEp = "" Then Ep = 0 Else Ep = txtEp
If txtfpk = "" Then fpk = 0 Else fpk = txtfpk
If txtGammap = "" Then Gammap = 0 Else Gammap = txtGammap
If txtEta_a = "" Then Eta_a = 0 Else Eta_a = txtEta_a
If txtEta1 = "" Then Eta1 = 0 Else Eta1 = txtEta1
'2. controllo fati
If Gammap <= 0 Then
    MsgBox "Specificare coefficiente parziale di sicurezza (premi su imposta parametri)", vbInformation, VersioneSw
    Exit Sub
End If
If Eta_a < 0.5 Or Eta_a > 0.95 Then
    MsgBox "Inserire/correggere fattore di conversione ambientale", vbInformation, VersioneSw
    Exit Sub
End If
If Eta1 < 0.3 Or Eta1 > 0.8 Then
    MsgBox "Inserire/correggere fattore di conversione per effetti di lunga durata", vbInformation, VersioneSw
    Exit Sub
End If
'3. calcoli ed output
fpd = fpk * Eta_a / Gammap
fpd2 = fpk * Eta_a * Eta1 / Gammap
Epspk = fpk / Ep * 100
Epspu = fpd / Ep * 100
txtfpd = Round(fpd, 0)
txtfpd2 = Round(fpd2, 0)
txtEpspk = Round(Epspk, 2)
txtEpspu = Round(Epspu, 2)
End Sub

Private Sub bttCancella_Click()
txtEp = ""
txtEpspk = ""
txtEpspu = ""
txtGammap = ""
txtGammaDist = ""
txtEta_a = ""
txtEta1 = ""
txtfpk = ""
txtfpd = ""
txtfpd2 = ""
End Sub

Private Sub bttImpostaParam_Click()
If cmbRigidezzaFRP = "basso modulo E" Then
    txtEp = Round(160000 / fc1, 0)
    'txtEpspu = 1.6
    txtfpk = Round(2800 / fc1, 0)
ElseIf cmbRigidezzaFRP = "alto modulo E" Then
    txtEp = Round(300000 / fc1, 0)
    'txtEpspu = 0.5
    txtfpk = Round(1500 / fc1, 0)
End If
txtGammap = 1.1
txtGammaDist = 1.35
txtEta_a = 0.95
txtEta1 = 0.8
End Sub

Private Sub bttSalvaChiudi_Click()
With Foglio2
    .Cells(82, 5) = cmbTipoFRP
    .Cells(83, 5) = cmbRigidezzaFRP
    .Cells(83, 1) = txtEp
    .Cells(84, 5) = txtfpk
    .Cells(86, 5) = txtGammap
    .Cells(87, 5) = txtGammaDist
    .Cells(89, 5) = txtEta_a
    .Cells(90, 5) = txtEta1
    .Cells(91, 5) = txtFC
    .Cells(85, 5) = txtfpd
    .Cells(88, 5) = txtfpd2
    .Cells(93, 5) = txtEpspk
    .Cells(84, 1) = txtEpspu
    .Cells(85, 1) = txtEps0
End With
Unload Me
End Sub

Private Sub txtEp_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEps0_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEpspk_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEpspu_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEta_a_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtEta1_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFC_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtfpd_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtfpd2_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtfpk_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtGammaDist_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtGammap_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
'1. input
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
'2. impostazioni
cmbTipoFRP.AddItem "composito preformato"
cmbTipoFRP.AddItem "composito impregnato in situ"
cmbRigidezzaFRP.AddItem "basso modulo E"
cmbRigidezzaFRP.AddItem "alto modulo E"
lblEp = "modulo elastico longitudinale Ep (" & umTens & ")"
lblfpk = "tensione caratteristica di rottura fpk (" & umTens & ")"
lblfpd = "resistenza di progetto fpd per SLU (" & umTens & ")"
lblfpd2 = "resistenza di progetto fpd per SLE (" & umTens & ")"
'3. preleva dati da Fg2
With Me
    .cmbTipoFRP = Foglio2.Cells(82, 5)
    .cmbRigidezzaFRP = Foglio2.Cells(83, 5)
    .txtEp = Foglio2.Cells(83, 1)
    .txtfpk = Foglio2.Cells(84, 5)
    .txtGammap = Foglio2.Cells(86, 5)
    .txtGammaDist = Foglio2.Cells(87, 5)
    .txtEta_a = Foglio2.Cells(89, 5)
    .txtEta1 = Foglio2.Cells(90, 5)
    .txtFC = Foglio2.Cells(91, 5)
    .txtfpd = Foglio2.Cells(85, 5)
    .txtfpd2 = Foglio2.Cells(88, 5)
    .txtEpspk = Foglio2.Cells(93, 5)
    .txtEpspu = Foglio2.Cells(84, 1)
    .txtEps0 = Foglio2.Cells(85, 1)
End With
End Sub
