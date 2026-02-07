VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmGeomFRP 
   Caption         =   "GEOMETRIA COMPOSITO FRP"
   ClientHeight    =   8460.001
   ClientLeft      =   96
   ClientTop       =   576
   ClientWidth     =   14868
   OleObjectBlob   =   "frmGeomFRP.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmGeomFRP"
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
    .Cells(88, 1) = txtB
    .Cells(87, 1) = txtH
    .Cells(91, 1) = txt_tf
    .Cells(92, 1) = txtBf
    .Cells(93, 1) = txtPf
    .Cells(94, 1) = txtBeta
    .Cells(95, 1) = cmbDisposiz
    .Cells(96, 1) = txtPercH
    .Cells(97, 1) = txtRc
    .Cells(98, 1) = cmbContinuità
End With
Unload Me
End Sub

Private Sub txt_tf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtB_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtBeta_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
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

Private Sub txtH_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtPercH_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
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
cmbDisposiz.AddItem "ad U"
cmbDisposiz.AddItem "in avvolgimento"
cmbContinuità.AddItem "discontinuo"
cmbContinuità.AddItem "continuo o strisce adiacenti"
With Me
    .txtB = Foglio2.Cells(88, 1)
    .txtH = Foglio2.Cells(87, 1)
    .txt_tf = Foglio2.Cells(91, 1)
    .txtBf = Foglio2.Cells(92, 1)
    .txtPf = Foglio2.Cells(93, 1)
    .txtBeta = Foglio2.Cells(94, 1)
    .cmbDisposiz = Foglio2.Cells(95, 1)
    .txtPercH = Foglio2.Cells(96, 1)
    .txtRc = Foglio2.Cells(97, 1)
    .cmbContinuità = Foglio2.Cells(98, 1)
    .txtB.SetFocus
End With
End Sub
