VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmSollecitazSLU 
   Caption         =   "CARATTERISTICHE DI SOLLECITAZIONE AGENTI SULLA SEZIONE"
   ClientHeight    =   5610
   ClientLeft      =   84
   ClientTop       =   612
   ClientWidth     =   15372
   OleObjectBlob   =   "frmSollecitazSLU.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmSollecitazSLU"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttSalvaChiudi_Click()
With Foglio2
    .Cells(31, 1) = txtNx
    .Cells(27, 1) = txtTy
    .Cells(32, 1) = txtTz
    .Cells(30, 1) = txtMx
    .Cells(11, 1) = txtMy
    .Cells(17, 1) = txtMz
End With
Unload Me
End Sub

Private Sub txtMx_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMz_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNx_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtTy_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtTz_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMy_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
'input
FormSez = Foglio2.Cells(54, 1)
SistemaTecnico = Foglio2.Cells(68, 1)
SollecPiane = Foglio2.Cells(28, 1)
DefinisciUnit‡Misura
'esecuz
lblNx = "sforzo normale Nx (" & umForze & ")"
lblTy = "sforzo di taglio Ty (" & umForze & ")"
lblTz = "sforzo di taglio Tz (" & umForze & ")"
lblMx = "momento torcente Mx (" & umMomenti & ")"
lblMy = "momento flettente My (" & umMomenti & ")"
lblMz = "momento flettente Mz (" & umMomenti & ")"
With Me
    .txtNx = Foglio2.Cells(31, 1)
    .txtTz = Foglio2.Cells(32, 1)
    .txtMy = Foglio2.Cells(11, 1)
    .txtTy = Foglio2.Cells(27, 1)
    .txtMx = Foglio2.Cells(30, 1)
    .txtMz = Foglio2.Cells(17, 1)
End With
If SollecPiane Then
    lblTy.Enabled = False
    txtTy.Enabled = False
    lblMx.Enabled = False
    txtMx.Enabled = False
    lblMz.Enabled = False
    txtMz.Enabled = False
ElseIf FormSez = "Circolare piena o cava" Then
    lblMz.Enabled = False
    txtMz.Enabled = False
    lblTy.Enabled = False
    txtTy.Enabled = False
End If
End Sub

