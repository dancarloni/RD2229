VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmGeomFRPconfin 
   Caption         =   "CONFINAMENTO CON COMPOSITI FIBRORINFORZATI FRP"
   ClientHeight    =   4275
   ClientLeft      =   96
   ClientTop       =   576
   ClientWidth     =   11316
   OleObjectBlob   =   "frmGeomFRPconfin.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmGeomFRPconfin"
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
    .Cells(101, 1) = txt_tf
    .Cells(102, 1) = txtBf
    .Cells(103, 1) = txtPf
    .Cells(104, 1) = txtAlfa
    .Cells(105, 1) = cmbTipoConfin
    .Cells(106, 1) = txtRc
End With
Unload Me
End Sub

Private Sub cmbTipoConfin_Change()
If cmbTipoConfin = "continuo" Then
    txtPf.Enabled = False
    txtPf = ""
    lblPf.Enabled = False
Else
    txtPf.Enabled = True
    lblPf.Enabled = True
End If
End Sub

Private Sub txt_tf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtAlfa_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtBf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtPf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtRc_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
cmbTipoConfin.AddItem "continuo"
cmbTipoConfin.AddItem "discontinuo"
With Me
    .txt_tf = Foglio2.Cells(101, 1)
    .txtBf = Foglio2.Cells(102, 1)
    .txtPf = Foglio2.Cells(103, 1)
    .txtAlfa = Foglio2.Cells(104, 1)
    .cmbTipoConfin = Foglio2.Cells(105, 1)
    .txtRc = Foglio2.Cells(106, 1)
End With
End Sub
