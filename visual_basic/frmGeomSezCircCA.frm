VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmGeomSezCircCA 
   Caption         =   "SEZIONE CIRCOLARE PIENA O CAVA IN C.A."
   ClientHeight    =   6900
   ClientLeft      =   96
   ClientTop       =   612
   ClientWidth     =   16572
   OleObjectBlob   =   "frmGeomSezCircCA.frx":0000
   ShowModal       =   0   'False
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmGeomSezCircCA"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Sub bttSalvaChiudi_Click()
Dim D#, Di#, Df#, Np%, Alfa0#, Alfa#, Nf#
'controllo dei dati
If txtD = "" Then D = 0 Else D = CDbl(txtD)
If txtDi = "" Then Di = 0 Else Di = CDbl(txtDi)
If txtCf = "" Then Cf = 0 Else Cf = CDbl(txtCf)
If cmbDf = "" Then Df = 0 Else Df = cmbDf
If txtNf = "" Then Nf = 0 Else Nf = CDbl(txtNf)
If D <= 0 Or Di < 0 Or Cf <= 0 Or Df <= 0 Then
    MsgBox "Inserisci dati obbligatori!", vbCritical, VersioneSw
    Exit Sub
End If
If Di >= D Then
    MsgBox "Deve essere Di <= D - 6Cf", vbCritical, VersioneSw
    Exit Sub
End If
If CalcVerif Then
    If Nf <= 0 Then
        MsgBox "Inserisci numero di barre!", vbCritical, VersioneSw
        Exit Sub
    End If
End If
'salva dati
With Foglio2
    .Cells(9, 11) = txtD
    .Cells(10, 11) = cmbDf
    .Cells(11, 11) = txtNf
    .Cells(12, 11) = txtDi
    .Cells(16, 1) = txtCf
    'coordinate vertici sezione
    Np = 32
    Alfa0 = 2 * PiGreco / Np
    For i = 1 To Np Step 1 'poligonale esterna
        Alfa = Alfa0 * (i - 1)
        .Cells(5 + i, 23) = Round(D / 2 * Sin(Alfa), 2)
        .Cells(5 + i, 24) = Round(D / 2 * Cos(Alfa), 2)
    Next i
    If Di = 0 Then
        .Cells(3, 26) = 1 'Npolig
        .Cells(4, 24) = Np 'Nvertici
    ElseIf Di > 0 Then
        .Cells(3, 26) = 2 'Npolig
        .Cells(4, 24) = Np 'Nvertici
        .Cells(4, 26) = Np 'Nvertici
        For i = 1 To Np Step 1 'poligonale interna
            Alfa = -Alfa0 * (i - 1)
            .Cells(5 + i, 25) = Round(Di / 2 * Sin(Alfa), 2)
            .Cells(5 + i, 26) = Round(Di / 2 * Cos(Alfa), 2)
        Next i
    End If
End With
'CoordBaricentriTondini
Unload Me
End Sub

Private Sub cmbDf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtD_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtCf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtDi_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
'input
CalcVerif = Foglio2.Cells(25, 1)
'esecuz
cmbDf.RowSource = "Foglio3!a5:a19"
With Me
    .txtD = Foglio2.Cells(9, 11)
    .cmbDf = Foglio2.Cells(10, 11)
    .txtNf = Foglio2.Cells(11, 11)
    .txtCf = Foglio2.Cells(16, 1)
    .txtDi = Foglio2.Cells(12, 11)
End With
If CalcVerif = False Then
    lblDf.Enabled = False
    cmbDf.Enabled = False
    txtNf.Enabled = False
    lblNf.Enabled = False
Else
    lblDf.Enabled = True
    cmbDf.Enabled = True
    txtNf.Enabled = True
    lblNf.Enabled = True
End If
End Sub
