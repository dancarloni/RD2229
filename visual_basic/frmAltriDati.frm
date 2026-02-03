VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmAltriDati 
   Caption         =   "ALTRI DATI"
   ClientHeight    =   8790.001
   ClientLeft      =   84
   ClientTop       =   612
   ClientWidth     =   12204
   OleObjectBlob   =   "frmAltriDati.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmAltriDati"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttDuttilit‡Param_Click()
If Foglio2.Cells(31, 1) = "" Then Nx = 0 Else Nx = Foglio2.Cells(31, 1) * fmF
txtNpx = 100
'txtDeltaEps = 0.00001
txtDeltaZ1 = 2
If Nx = 0 Then
    txtX1 = 0.2
    txtX2 = H / fmL
ElseIf Nx > 0 Then
    txtX1 = -H / fmL
    txtX2 = H / fmL
ElseIf Nx < 0 Then
    txtX1 = 0.2
    txtX2 = 2 * H / fmL
End If
End Sub

Private Sub bttSalvaChiudi_Click()
With Foglio2
    .Cells(35, 1) = cmbDfp
    .Cells(10, 11) = cmbDfp
    .Cells(34, 1) = txtIntmax
    .Cells(40, 1) = txtsLmin
    .Cells(41, 1) = txtMu
    .Cells(14, 14) = cmbDst_ta
    .Cells(13, 14) = txtTeta_ta
    .Cells(17, 14) = cmbNbrz
    .Cells(18, 14) = cmbNbry
    .Cells(17, 18) = optStaffeCircSingole
    .Cells(18, 18) = optStaffeSpirale
    .Cells(15, 14) = txtPsTag
    .Cells(16, 14) = txtAlfaTag
    .Cells(20, 14) = txtAlTor
    .Cells(22, 14) = txtPsTor
    .Cells(21, 14) = cmbDst_tor
    .Cells(23, 14) = txtAlfaTor
    .Cells(9, 14) = optSism
    .Cells(10, 14) = optNoSism
    .Cells(11, 14) = optCDA
    .Cells(11, 16) = optCDB
    .Cells(42, 1) = txtEps0
    .Cells(27, 12) = txtNpx
    '.Cells(28, 12) = txtDeltaEps
    .Cells(29, 12) = txtDeltaZ1
    .Cells(30, 12) = txtX1
    .Cells(31, 12) = txtX2
End With
Unload Me
End Sub

Private Sub cmbDfp_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub cmbDst_ta_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub cmbDst_tor_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub cmbNbry_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub cmbNbrz_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub optNoSism_Click()
If optNoSism Then
    optCDA.Enabled = False
    optCDB.Enabled = False
Else
    optCDA.Enabled = True
    optCDB.Enabled = True
End If
End Sub

Private Sub optSism_Click()
optNoSism_Click
End Sub

Private Sub txtAlfaTag_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtAlfaTor_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtAlTor_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtDeltaEps_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtDeltaZ1_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
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

Private Sub txtIntmax_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMu_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNpx_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtPsTag_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtPsTor_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtsLmin_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtTeta_ta_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtX1_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtX2_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
CalcVerif = Foglio2.Cells(25, 1)
Pilastro = Foglio2.Cells(36, 1)
Trave = Foglio2.Cells(37, 1)
TraveFondaz = Foglio2.Cells(38, 1)
blnVerifDuttilit‡ = Foglio2.Cells(22, 1)
FormSez = Foglio2.Cells(54, 1)
MetodoTA = Foglio2.Cells(57, 1)
MetodoSL08 = Foglio2.Cells(58, 1)
MetodoSL18 = Foglio2.Cells(59, 1)
SollecPiane = Foglio2.Cells(28, 1)
CemArmOrd = Foglio2.Cells(20, 1)
CemCAP = Foglio2.Cells(21, 1)
CemFRC = Foglio2.Cells(26, 1)
If FormSez <> "Generica" Then
    If Foglio2.Cells(10, 1) = "" Then H = 0 Else H = Foglio2.Cells(10, 1) * fmL
    If FormSez = "Circolare piena o cava" Then
        If Foglio2.Cells(9, 11) = "" Then H = 0 Else H = Foglio2.Cells(9, 11) * fmL
    End If
End If
cmbDfp.RowSource = "Foglio3!a5:a19"
cmbDst_ta.RowSource = "Foglio3!b5:b10"
cmbNbrz.RowSource = "Foglio3!c5:c9"
cmbNbry.RowSource = "Foglio3!c5:c9"
cmbDst_tor.RowSource = "Foglio3!b5:b10"
With Me
    .cmbDfp = Foglio2.Cells(35, 1)
    .txtsLmin = Foglio2.Cells(40, 1)
    .txtMu = Foglio2.Cells(41, 1)
    .txtIntmax = Foglio2.Cells(34, 1)
    .cmbDst_ta = Foglio2.Cells(14, 14)
    .txtTeta_ta = Foglio2.Cells(13, 14)
    .cmbNbrz = Foglio2.Cells(17, 14)
    .cmbNbry = Foglio2.Cells(18, 14)
    .optStaffeCircSingole = Foglio2.Cells(17, 18)
    .optStaffeSpirale = Foglio2.Cells(18, 18)
    .txtPsTag = Foglio2.Cells(15, 14)
    .txtAlfaTag = Foglio2.Cells(16, 14)
    .txtAlTor = Foglio2.Cells(20, 14)
    .txtPsTor = Foglio2.Cells(22, 14)
    .cmbDst_tor = Foglio2.Cells(21, 14)
    .txtAlfaTor = Foglio2.Cells(23, 14)
    .optSism = Foglio2.Cells(9, 14)
    .optNoSism = Foglio2.Cells(10, 14)
    .optCDA = Foglio2.Cells(11, 14)
    .optCDB = Foglio2.Cells(11, 16)
    .txtEps0 = Foglio2.Cells(42, 1)
    .txtNpx = Foglio2.Cells(27, 12)
    '.txtDeltaEps = Foglio2.Cells(28, 12)
    .txtDeltaZ1 = Foglio2.Cells(29, 12)
    .txtX1 = Foglio2.Cells(30, 12)
    .txtX2 = Foglio2.Cells(31, 12)
End With
If CalcVerif Then
    Frame5.Enabled = False
    cmbDfp.Enabled = False
    lblDfp.Enabled = False
    lblsLmin.Enabled = False
    txtsLmin.Enabled = False
    lblIntmax.Enabled = False
    txtIntmax.Enabled = False
    lblMu.Enabled = False
    txtMu.Enabled = False
    'optSism.Enabled = False
    'optNoSism.Enabled = False
    'optCDA.Enabled = False
    'optCDB.Enabled = False
Else
    If FormSez = "Circolare piena o cava" Or Pilastro Then
        lblMu.Enabled = False
        txtMu.Enabled = False
    End If
    txtPsTag.Enabled = False
    lblPsTag.Enabled = False
    txtAlTor.Enabled = False
    lblAlTor.Enabled = False
    txtPsTor.Enabled = False
    lblPsTor.Enabled = False
End If
If MetodoTA Or TraveFondaz Then
    optSism.Enabled = False
    optNoSism.Enabled = False
    optNoSism = True
End If
If FormSez = "Circolare piena o cava" Then
    cmbNbrz.Enabled = False
    cmbNbry.Enabled = False
    lblNbrz.Enabled = False
    lblNbry.Enabled = False
Else
    optStaffeCircSingole.Enabled = False
    optStaffeSpirale.Enabled = False
End If
If SollecPiane Then
    Label2.Enabled = False
    txtAlTor.Enabled = False
    lblAlTor.Enabled = False
    txtPsTor.Enabled = False
    lblPsTor.Enabled = False
    cmbDst_tor.Enabled = False
    lblDst_tor.Enabled = False
    txtAlfaTor.Enabled = False
    lblAlfaTor.Enabled = False
End If
If CemArmOrd Or MetodoTA Then
    Frame3.Enabled = False
    txtEps0.Enabled = False
    lblEps0.Enabled = False
End If
If MetodoTA Or MetodoSL08 Or (MetodoSL18 And blnVerifDuttilit‡ = False) Then
    frmDuttilit‡.Enabled = False
    txtNpx.Enabled = False
    lblNpx.Enabled = False
    'txtDeltaEps.Enabled = False
    'lblDeltaEps.Enabled = False
    txtDeltaZ1.Enabled = False
    lblDeltaZ1.Enabled = False
    bttDuttilit‡Param.Enabled = False
    lblInterv.Enabled = False
    txtX1.Enabled = False
    lblX1.Enabled = False
    txtX2.Enabled = False
    lblX2.Enabled = False
End If
End Sub
