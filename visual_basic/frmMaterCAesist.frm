VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmMaterCAesist 
   Caption         =   "INCAMICIATURA IN C.A. - ACCIAIO ESISTENTE"
   ClientHeight    =   3360
   ClientLeft      =   96
   ClientTop       =   588
   ClientWidth     =   8340.001
   OleObjectBlob   =   "frmMaterCAesist.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmMaterCAesist"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttCalcola_Click()
Dim FC#, fym#
If txtFC = "" Then FC = 0 Else FC = txtFC
If txtFym = "" Then fym = 0 Else fym = txtFym
If FC = 0 Or fym = 0 Then
    MsgBox "Inserire fattore di confidenza e/o fym", vbInformation, VersioneSw
    Exit Sub
End If
txtFyd = Round(fym / txtFC, 2)
End Sub

Private Sub bttImpostaParam_Click()
txtGammas = 1.15
End Sub

Private Sub bttSalvaChiudi_Click()
With Foglio2
    .Cells(72, 10) = txtGammas
    .Cells(73, 10) = txtFC
    .Cells(74, 10) = txtFym
    .Cells(75, 10) = txtFyd
End With
Unload Me
End Sub

Private Sub txtFC_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFyd_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtFym_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtGammas_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
lblFym = "tensione media di snervam. acciaio fym  (" & umTens & ")"
lblFyd = "resistenza di progetto acciaio fyd (" & umTens & ")"
With Me
    .txtGammas = Foglio2.Cells(72, 10)
    .txtFC = Foglio2.Cells(73, 10)
    .txtFym = Foglio2.Cells(74, 10)
    .txtFyd = Foglio2.Cells(75, 10)
End With
End Sub
