VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmStabilit‡ 
   Caption         =   "VERIFICHE DI STABILITA' (Carico di Punta nei pilastri)"
   ClientHeight    =   3315
   ClientLeft      =   96
   ClientTop       =   612
   ClientWidth     =   9180.001
   OleObjectBlob   =   "frmStabilit‡.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmStabilit‡"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttSalvaChiudi_Click()
'CONTROLLO DATI
If txtL = "" Then
    MsgBox "Inserire lunghezza asta", vbInformation, VersioneSw
    Exit Sub
End If
If cmbBetay = "" Or cmbBetaz = "" Or cmbBetay <= 0 Or cmbBetay > 2 Or cmbBetaz <= 0 Or cmbBetaz > 2 Then
    MsgBox "Correggere coefficienti beta", vbInformation, VersioneSw
    Exit Sub
End If
'SALVA DATI
With Foglio2
    .Cells(39, 1) = txtL
    .Cells(47, 1) = cmbBetay
    .Cells(48, 1) = cmbBetaz
    .Cells(51, 1) = txtNr
    .Cells(52, 1) = txtMr
    .Cells(51, 3) = txtMi
    .Cells(52, 3) = txtMk
End With
Unload Me
End Sub

Private Sub cmbBetay_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub cmbBetaz_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMi_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMk_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMr_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNr_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtL_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
'input
blnVerifCarPunta = Foglio2.Cells(46, 1)
SistemaTecnico = Foglio2.Cells(68, 1)
MetodoTA = Foglio2.Cells(57, 1)
MetodoSL08 = Foglio2.Cells(58, 1)
MetodoSL18 = Foglio2.Cells(59, 1)
DefinisciUnit‡Misura
With cmbBetay
    .AddItem 0.5
    .AddItem 0.707
    .AddItem 1
    .AddItem 2
End With
With cmbBetaz
    .AddItem 0.5
    .AddItem 0.707
    .AddItem 1
    .AddItem 2
End With
'esecuz
lblNr = "sforzo normale di riferimento Nr (" & umForze & ")"
lblMr = "momento flettente di riferimento Mr (" & umMomenti & ")"
lblMi = "momento all'estremo iniziale del pilastro (" & umMomenti & ")"
lblMk = "momento all'estremo finale del pilastro (" & umMomenti & ")"
With Me
    .txtL = Foglio2.Cells(39, 1)
    .cmbBetay = Foglio2.Cells(47, 1)
    .cmbBetaz = Foglio2.Cells(48, 1)
    .txtNr = Foglio2.Cells(51, 1)
    .txtMr = Foglio2.Cells(52, 1)
    .txtMi = Foglio2.Cells(51, 3)
    .txtMk = Foglio2.Cells(52, 3)
End With
If MetodoTA Or MetodoSL18 Then
    txtMi.Enabled = False
    lblMi.Enabled = False
    txtMk.Enabled = False
    lblMk.Enabled = False
End If
End Sub
