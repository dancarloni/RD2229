VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmVerifSLE 
   Caption         =   "DATI PER LE VERIFICHE AGLI S.L.E."
   ClientHeight    =   7065
   ClientLeft      =   48
   ClientTop       =   372
   ClientWidth     =   7524
   OleObjectBlob   =   "frmVerifSLE.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmVerifSLE"
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
    .Cells(37, 6) = cmbCondizAmb
    .Cells(38, 6) = cmbSensibArmat
    .Cells(39, 6) = txtPerc_c
    .Cells(40, 6) = txtPerc_qp
    .Cells(41, 6) = txtPerc_cs
    .Cells(42, 6) = optCarichiBrevi
    .Cells(43, 6) = optCarichiLunghi
    .Cells(44, 6) = opt1996
    .Cells(45, 6) = opt2008
    .Cells(46, 6) = txtK
End With
Unload Me
End Sub

Private Sub bttValNTC_Click()
txtPerc_c = 60
txtPerc_qp = 45
txtPerc_cs = 80
End Sub

Private Sub txtPerc_c_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
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

Private Sub txtPerc_cs_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtPerc_qp_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
cmbCondizAmb.AddItem "Ordinarie"
cmbCondizAmb.AddItem "Aggressive"
cmbCondizAmb.AddItem "Molto aggressive"
cmbSensibArmat.AddItem "Armature poco sensibili"
cmbSensibArmat.AddItem "Armature sensibili"
With Me
    .cmbCondizAmb = Foglio2.Cells(37, 6)
    .cmbSensibArmat = Foglio2.Cells(38, 6)
    .txtPerc_c = Foglio2.Cells(39, 6)
    .txtPerc_qp = Foglio2.Cells(40, 6)
    .txtPerc_cs = Foglio2.Cells(41, 6)
    .optCarichiBrevi = Foglio2.Cells(42, 6)
    .optCarichiLunghi = Foglio2.Cells(43, 6)
    .opt1996 = Foglio2.Cells(44, 6)
    .opt2008 = Foglio2.Cells(45, 6)
    .txtK = Foglio2.Cells(46, 6)
End With
End Sub
