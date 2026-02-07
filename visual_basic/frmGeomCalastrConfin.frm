VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmGeomCalastrConfin 
   Caption         =   "CONFINAMENTO E RINFORZO A TAGLIO CON CAMICIE IN ACCIAIO - ANGOLARI E CALASTRELLI O CAM"
   ClientHeight    =   3555
   ClientLeft      =   84
   ClientTop       =   576
   ClientWidth     =   14364
   OleObjectBlob   =   "frmGeomCalastrConfin.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmGeomCalastrConfin"
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
    .Cells(101, 5) = txt_tf
    .Cells(102, 5) = txtBf
    .Cells(103, 5) = txtPf
    .Cells(105, 5) = cmbTipoConfin
    .Cells(106, 5) = txtRc
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
    .txt_tf = Foglio2.Cells(101, 5)
    .txtBf = Foglio2.Cells(102, 5)
    .txtPf = Foglio2.Cells(103, 5)
    .cmbTipoConfin = Foglio2.Cells(105, 5)
    .txtRc = Foglio2.Cells(106, 5)
End With
End Sub
