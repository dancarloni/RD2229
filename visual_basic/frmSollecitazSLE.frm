VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmSollecitazSLE 
   Caption         =   "SOLLECITAZ. AGENTI PER LE COMBINAZ. DI CARICO S.L.E."
   ClientHeight    =   5970
   ClientLeft      =   84
   ClientTop       =   552
   ClientWidth     =   7836
   OleObjectBlob   =   "frmSollecitazSLE.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmSollecitazSLE"
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
    .Cells(34, 7) = txtNx_c
    .Cells(35, 7) = txtMy_c
    .Cells(36, 7) = txtMz_c
    .Cells(34, 8) = txtNx_f
    .Cells(35, 8) = txtMy_f
    .Cells(36, 8) = txtMz_f
    .Cells(34, 9) = txtNx_qp
    .Cells(35, 9) = txtMy_qp
    .Cells(36, 9) = txtMz_qp
End With
Unload Me
End Sub

Private Sub txtMy_c_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMy_f_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMy_qp_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMz_c_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMz_f_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtMz_qp_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNx_c_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNx_f_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNx_qp_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
'input
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
SollecPiane = Foglio2.Cells(28, 1)
'esecuz
lblNx_c = "sforzo normale Nx (" & umForze & ")"
lblMy_c = "momento flettente My (" & umMomenti & ")"
lblMz_c = "momento flettente Mz (" & umMomenti & ")"
lblNx_f = "sforzo normale Nx (" & umForze & ")"
lblMy_f = "momento flettente My (" & umMomenti & ")"
lblMz_f = "momento flettente Mz (" & umMomenti & ")"
lblNx_qp = "sforzo normale Nx (" & umForze & ")"
lblMy_qp = "momento flettente My (" & umMomenti & ")"
lblMz_qp = "momento flettente Mz (" & umMomenti & ")"
With Me
    .txtNx_c = Foglio2.Cells(34, 7)
    .txtMy_c = Foglio2.Cells(35, 7)
    .txtMz_c = Foglio2.Cells(36, 7)
    .txtNx_f = Foglio2.Cells(34, 8)
    .txtMy_f = Foglio2.Cells(35, 8)
    .txtMz_f = Foglio2.Cells(36, 8)
    .txtNx_qp = Foglio2.Cells(34, 9)
    .txtMy_qp = Foglio2.Cells(35, 9)
    .txtMz_qp = Foglio2.Cells(36, 9)
End With
If SollecPiane Then
    lblMz_c.Enabled = False
    txtMz_c.Enabled = False
    lblMz_f.Enabled = False
    txtMz_f.Enabled = False
    lblMz_qp.Enabled = False
    txtMz_qp.Enabled = False
End If
End Sub
