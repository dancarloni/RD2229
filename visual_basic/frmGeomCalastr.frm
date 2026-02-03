VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmGeomCalastr 
   Caption         =   "RINFORZO A TAGLIO CON CAMICIE IN ACCIAIO - ANGOLARI E CALASTRELLI"
   ClientHeight    =   4515
   ClientLeft      =   96
   ClientTop       =   576
   ClientWidth     =   10896
   OleObjectBlob   =   "frmGeomCalastr.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmGeomCalastr"
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
    .Cells(101, 10) = txt_tf
    .Cells(102, 10) = txtBf
    .Cells(103, 10) = txtPf
    .Cells(105, 10) = cmbTipoConfin
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

Private Sub UserForm_Initialize()
cmbTipoConfin.AddItem "continuo"
cmbTipoConfin.AddItem "discontinuo"
With Me
    .txt_tf = Foglio2.Cells(101, 10)
    .txtBf = Foglio2.Cells(102, 10)
    .txtPf = Foglio2.Cells(103, 10)
    .cmbTipoConfin = Foglio2.Cells(105, 10)
End With
End Sub
