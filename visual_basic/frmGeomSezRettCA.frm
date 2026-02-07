VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmGeomSezRettCA 
   Caption         =   "SEZIONE RETTANGOLARE IN C.A."
   ClientHeight    =   6336
   ClientLeft      =   96
   ClientTop       =   516
   ClientWidth     =   13704
   OleObjectBlob   =   "frmGeomSezRettCA.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmGeomSezRettCA"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttPacchettiArmat_Click()
frmPacchettiArmat.Show
End Sub

Sub bttSalvaChiudi_Click()
Dim DeltaSup#, DeltaInf#, B#, H#, Cf#, Dbs#, Dbi#
'controllo dei dati
If txtH = "" Then H = 0 Else H = CDbl(txtH)
If txtB = "" Then B = 0 Else B = CDbl(txtB)
If txtCf = "" Then Cf = 0 Else Cf = CDbl(txtCf)
If cmbDbs = "" Then Dbs = 0 Else Dbs = cmbDbs
If cmbDbi = "" Then Dbi = 0 Else Dbi = cmbDbi
DeltaSup = Cf + (Dbs / 10) / 2
DeltaInf = Cf + (Dbi / 10) / 2
If B <= 0 Or H <= 0 Or Cf < 0 Then
    MsgBox "Inserisci dati obbligatori!", vbCritical, VersioneSw
    Exit Sub
End If
'salva dati in Fg2
With Foglio2
    .Cells(9, 1) = txtB
    .Cells(10, 1) = txtH
    .Cells(12, 1) = cmbDbs
    .Cells(13, 1) = txtNbs
    .Cells(14, 1) = cmbDbi
    .Cells(15, 1) = txtNbi
    .Cells(16, 1) = txtCf
    .Cells(3, 26) = 1 'Npolig
    .Cells(4, 24) = 4 'Nvertici
    .Cells(6, 23) = 0 'coordinate 1° vertice
    .Cells(6, 24) = 0
    .Cells(7, 23) = 0 '2° vertice
    .Cells(7, 24) = H
    .Cells(8, 23) = B '3° vertice
    .Cells(8, 24) = H
    .Cells(9, 23) = B '4° vertice
    .Cells(9, 24) = 0
    If optDueLembi Then
        .Cells(3, 42) = 2 'Npacch
        .Cells(5, 38) = DeltaSup
        .Cells(5, 39) = DeltaSup
        .Cells(5, 40) = B - DeltaSup
        .Cells(5, 41) = DeltaSup
        .Cells(5, 42) = txtNbs
        .Cells(5, 43) = cmbDbs
        .Cells(6, 38) = B - DeltaInf 'y'iniz
        .Cells(6, 39) = H - DeltaInf 'z'iniz
        .Cells(6, 40) = DeltaInf 'y'fin
        .Cells(6, 41) = H - DeltaInf 'z'fin
        .Cells(6, 42) = txtNbi
        .Cells(6, 43) = cmbDbi
        .Cells(5, 36) = "Si" 'tondini nuovi
        .Cells(6, 36) = "Si" 'tondini nuovi
    End If
    .Cells(23, 1) = optDueLembi
End With
'CoordBaricentriTondini
Unload Me
End Sub

Private Sub cmbDbi_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub cmbDbs_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub optAltrove_Click()
optDueLembi_Click
End Sub

Private Sub optDueLembi_Click()
If optDueLembi Then
    lblDbs.Enabled = True
    cmbDbs.Enabled = True
    lblLemboSup.Enabled = True
    cmbDbi.Enabled = True
    txtNbi.Enabled = True
    txtNbs.Enabled = True
    lblLemboInf.Enabled = True
    lblNbs.Enabled = True
    bttPacchettiArmat.Enabled = False
Else
    lblDbs.Enabled = False
    cmbDbs.Enabled = False
    lblLemboSup.Enabled = False
    cmbDbi.Enabled = False
    txtNbi.Enabled = False
    txtNbs.Enabled = False
    lblLemboInf.Enabled = False
    lblNbs.Enabled = False
    bttPacchettiArmat.Enabled = True
End If
End Sub

Private Sub txtB_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
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

Private Sub txtCf_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNbi_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNbs_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
'input
CalcVerif = Foglio2.Cells(25, 1)
'esecuz
cmbDbs.RowSource = "Foglio3!a5:a19"
cmbDbi.RowSource = "Foglio3!a5:a19"
With Me
    .txtB = Foglio2.Cells(9, 1)
    .txtH = Foglio2.Cells(10, 1)
    .cmbDbs = Foglio2.Cells(12, 1)
    .txtNbs = Foglio2.Cells(13, 1)
    .cmbDbi = Foglio2.Cells(14, 1)
    .txtNbi = Foglio2.Cells(15, 1)
    .txtCf = Foglio2.Cells(16, 1)
    .optDueLembi = Foglio2.Cells(23, 1)
    .optAltrove = Not (Foglio2.Cells(23, 1))
End With
If CalcVerif = False Then
    Frame1.Enabled = False
    optDueLembi.Enabled = False
    optAltrove.Enabled = False
    lblDbs.Enabled = False
    cmbDbs.Enabled = False
    lblLemboSup.Enabled = False
    cmbDbi.Enabled = False
    txtNbi.Enabled = False
    txtNbs.Enabled = False
    lblLemboInf.Enabled = False
    lblNbs.Enabled = False
    bttPacchettiArmat.Enabled = False
End If
End Sub
