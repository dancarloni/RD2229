VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmMaterFRC 
   Caption         =   "DATI RESISTENZA A TRAZIONE CLS FIBRORINFORZATO - FRC"
   ClientHeight    =   4875
   ClientLeft      =   84
   ClientTop       =   576
   ClientWidth     =   13836
   OleObjectBlob   =   "frmMaterFRC.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmMaterFRC"
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
    .Cells(76, 1) = optLineareIncrud
    .Cells(77, 1) = optLineareDegrad
    .Cells(78, 1) = optRigidoPlastico
    .Cells(72, 1) = txteFs
    .Cells(73, 1) = txteFu
    .Cells(74, 1) = txtfFts
    .Cells(75, 1) = txtfFtu
End With
Unload Me
End Sub

Private Sub bttValoriCons_Click()
Dim fctd#
If Foglio2.Cells(20, 8) = "" Then fctd = 0 Else fctd = Foglio2.Cells(20, 8)
If optLineareIncrud Then
    txteFs = 0.2 'mia ipotesi
    txteFu = 1
    txtfFts = fctd
    txtfFtu = 1.2 * fctd 'mia ipotesi
ElseIf optLineareDegrad Then
    txteFs = 0.2 'mia ipotesi
    txteFu = 2
    txtfFts = 2 * fctd 'mia ipotesi
    txtfFtu = 0.4 * fctd 'mia ipotesi
ElseIf optRigidoPlastico Then
    txteFu = 1.5 'mia ipotesi
    txtfFtu = 4 * fctd 'mia ipotesi
End If
End Sub

Private Sub optLineareDegrad_Click()
optRigidoPlastico_Click
End Sub

Private Sub optLineareIncrud_Click()
optRigidoPlastico_Click
End Sub

Private Sub optRigidoPlastico_Click()
If optRigidoPlastico Then
    txteFs = ""
    txteFs.Enabled = False
    lbleFs.Enabled = False
    txtfFts = ""
    txtfFts.Enabled = False
    lblfFts.Enabled = False
Else
    txteFs.Enabled = True
    lbleFs.Enabled = True
    txtfFts.Enabled = True
    lblfFts.Enabled = True
End If
End Sub

Private Sub txteFs_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txteFu_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtfFts_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtfFtu_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
SistemaTecnico = Foglio2.Cells(68, 1)
lblfFts = "resistenza di progetto a trazione residua di esercizio fFts (" & umTens & ")"
lblfFtu = "resistenza di progetto a trazione residua ultima fFtu (" & umTens & ")"
With Me
    .optLineareIncrud = Foglio2.Cells(76, 1)
    .optLineareDegrad = Foglio2.Cells(77, 1)
    .optRigidoPlastico = Foglio2.Cells(78, 1)
    .txteFs = Foglio2.Cells(72, 1)
    .txteFu = Foglio2.Cells(73, 1)
    .txtfFts = Foglio2.Cells(74, 1)
    .txtfFtu = Foglio2.Cells(75, 1)
End With
End Sub
