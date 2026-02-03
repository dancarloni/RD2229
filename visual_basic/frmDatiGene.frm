VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmDatiGene 
   Caption         =   "DATI GENERALI"
   ClientHeight    =   7755
   ClientLeft      =   84
   ClientTop       =   612
   ClientWidth     =   13356
   OleObjectBlob   =   "frmDatiGene.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmDatiGene"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttSalvaChiudi_Click()
If cmbFormSez = "" Then
    MsgBox "Inserisci dati obbligatori!", vbCritical, VersioneSw
    Exit Sub
End If
With Foglio2
    .Cells(24, 1) = optCalcProg
    .Cells(25, 1) = optCalcVerif
    .Cells(54, 1) = cmbFormSez
    .Cells(3, 26) = cmbNpolig
    .Cells(46, 1) = chkVerifCarPunta
    .Cells(57, 1) = optMetodoTA
    .Cells(58, 1) = optMetodoSL08
    .Cells(59, 1) = optMetodoSL18
    .Cells(68, 1) = optSistemaTecnico
    .Cells(69, 1) = optSistemaInternaz
    .Cells(13, 4) = txtProgetto
    .Cells(14, 4) = txtCommitt
    .Cells(15, 4) = txtComune
    .Cells(16, 4) = txtTecnico
    .Cells(18, 4) = txtDataLuogo
    .Cells(17, 4) = txtAnnotazioni
    .Cells(32, 6) = chkVerifSLE
    .Cells(22, 1) = chkVerificheDuttilità
    .Cells(28, 1) = optSollPiane
    .Cells(29, 1) = optSollSpaz
    .Cells(20, 1) = optCAO
    .Cells(21, 1) = optCAP
    '.Cells(20, 4) = optCostruzNuova
    '.Cells(21, 4) = optCostruzEsist
    .Cells(22, 4) = chkCamicieAcc
    .Cells(23, 4) = chkCamicieCA
    .Cells(26, 1) = chkFRC
    .Cells(81, 1) = chkFRP
    .Cells(36, 1) = optPilastro
    .Cells(37, 1) = optTrave
    .Cells(38, 1) = optTraveFondaz
End With
'Ricrea la barra strumenti in modo da disattivare menù
Application.CommandBars("PERS").Delete
CreaBarraProgramma
Unload Me
End Sub

Private Sub chkCamicieAcc_Click()
If chkCamicieAcc Then
    chkFRP = False
    chkFRP.Enabled = False
    chkCamicieCA = False
    chkCamicieCA.Enabled = False
    optMetodoTA.Enabled = False
    optMetodoSL08.Enabled = False
    optMetodoSL18.Enabled = True
    optCalcProg = False
    optCalcVerif = True
    optCalcProg.Enabled = False
    optCalcVerif.Enabled = False
Else
    chkFRP.Enabled = True
    chkCamicieCA.Enabled = True
    optMetodoTA.Enabled = True
    optMetodoSL08.Enabled = True
    optMetodoSL18.Enabled = True
    optCalcProg.Enabled = True
    optCalcVerif.Enabled = True
End If
End Sub

Private Sub chkCamicieCA_Click()
If chkCamicieCA Then
    chkFRP = False
    chkFRP.Enabled = False
    chkCamicieAcc = False
    chkCamicieAcc.Enabled = False
    optMetodoTA.Enabled = False
    optMetodoSL08.Enabled = False
    optMetodoSL18.Enabled = True
    optCalcProg = False
    optCalcVerif = True
    optCalcProg.Enabled = False
    optCalcVerif.Enabled = False
Else
    chkFRP.Enabled = True
    chkCamicieAcc.Enabled = True
    optMetodoTA.Enabled = True
    optMetodoSL08.Enabled = True
    optMetodoSL18.Enabled = True
    optCalcProg.Enabled = True
    optCalcVerif.Enabled = True
End If
End Sub

Private Sub chkFRC_Click()
If chkFRC Then
    optMetodoSL18 = True
    optMetodoSL08.Enabled = False
    optMetodoTA.Enabled = False
Else
    optMetodoSL18.Enabled = True
    optMetodoTA.Enabled = True
    optMetodoSL08.Enabled = True
End If
End Sub

Private Sub chkFRP_Click()
If chkFRP Then
    chkCamicieAcc = False
    chkCamicieAcc.Enabled = False
    chkCamicieCA = False
    chkCamicieCA.Enabled = False
    optMetodoTA.Enabled = False
    optMetodoSL08.Enabled = False
    optMetodoSL18.Enabled = True
    optCalcProg = False
    optCalcVerif = True
    optCalcProg.Enabled = False
    optCalcVerif.Enabled = False
Else
    chkCamicieAcc.Enabled = True
    chkCamicieCA.Enabled = True
    optMetodoTA.Enabled = True
    optMetodoSL08.Enabled = True
    optMetodoSL18.Enabled = True
    optCalcProg.Enabled = True
    optCalcVerif.Enabled = True
End If
End Sub

Private Sub cmbFormSez_Change()
If cmbFormSez <> "Generica" Then
    lblNpolig.Enabled = False
    cmbNpolig = 1
    cmbNpolig.Enabled = False
Else
    lblNpolig.Enabled = True
    cmbNpolig.Enabled = True
End If
End Sub

Private Sub cmbNpolig_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub optCalcProg_Click()
cmbFormSez = ""
If optCalcProg Then
    frmRinforzi.Enabled = False
    chkFRP = False
    chkCamicieAcc = False
    chkCamicieCA = False
    chkFRP.Enabled = False
    chkCamicieAcc.Enabled = False
    chkCamicieCA.Enabled = False
    cmbFormSez.RowSource = "Foglio3!n7:n12"
    chkVerificheDuttilità.Enabled = False
Else
    frmRinforzi.Enabled = True
    chkFRP.Enabled = True
    chkCamicieAcc.Enabled = True
    chkCamicieCA.Enabled = True
    cmbFormSez.RowSource = "Foglio3!n7:n13"
    chkVerificheDuttilità.Enabled = True
End If
cmbFormSez_Change
End Sub

Private Sub optCalcVerif_Click()
optCalcProg_Click
End Sub

Private Sub optCAO_Click()
optCAP_Click
End Sub

Private Sub optCAP_Click()
If optCAP Then
    Frame3.Enabled = False
    optCalcProg = False
    optCalcVerif = True
    optCalcProg.Enabled = False
    optCalcVerif.Enabled = False
    Frame6.Enabled = False
    cmbFormSez = "Generica"
    cmbFormSez.Enabled = False
    cmbNpolig = 1
    cmbNpolig.Enabled = False
    lblNpolig.Enabled = False
    optPilastro.Enabled = False
    optTrave.Enabled = False
    optTraveFondaz.Enabled = False
ElseIf optCAO Or chkFRC Then
    Frame3.Enabled = True
    optCalcProg.Enabled = True
    optCalcVerif.Enabled = True
    Frame6.Enabled = True
    cmbFormSez.Enabled = True
    cmbNpolig.Enabled = True
    lblNpolig.Enabled = True
    optPilastro.Enabled = True
    optTrave.Enabled = True
    optTraveFondaz.Enabled = True
End If
chkFRC_Click
End Sub

Private Sub optSLU_Click()
chkVerifSLE.Enabled = True
End Sub

Private Sub optTA_Click()
chkVerifSLE.Enabled = False
End Sub

Private Sub optFRC_Click()
optCAP_Click
End Sub

'Private Sub optCostruzEsist_Click()
'optCostruzNuova_Click
'End Sub

'Private Sub optCostruzNuova_Click()
'If optCostruzNuova Then
'    optMetodoTA.Enabled = True
'    optMetodoSL08.Enabled = True
'    optMetodoSL18.Enabled = True
'    If optMetodoSL18 Then
'        chkFRC.Enabled = True
'    Else
'        chkFRC.Enabled = False
'    End If
'    chkFRP = False
'    chkCamicieAcc = False
'    chkCamicieCA = False
'    chkFRP.Enabled = False
'    chkCamicieAcc.Enabled = False
'    chkCamicieCA.Enabled = False
'    optCalcProg.Enabled = True
'    optCalcVerif.Enabled = True
'ElseIf optCostruzEsist Then
'    optMetodoTA.Enabled = False
'    optMetodoSL08.Enabled = True
'    optMetodoSL18.Enabled = True
'    chkFRC = False
'    chkFRC.Enabled = False
'    chkFRP.Enabled = True
'    chkCamicieAcc.Enabled = True
'    chkCamicieCA.Enabled = True
'    optCalcProg = False
'    optCalcVerif = True
'    optCalcProg.Enabled = False
'    optCalcVerif.Enabled = False
'End If
'End Sub

Private Sub optMetodoSL08_Click()
optMetodoTA_Click
End Sub

Private Sub optMetodoSL18_Click()
optMetodoTA_Click
End Sub

Private Sub optMetodoTA_Click()
If optMetodoTA Then
    chkFRC = False
    chkFRC.Enabled = False
    frmRinforzi.Enabled = False
    chkFRP = False
    chkCamicieAcc = False
    chkCamicieCA = False
    chkFRP.Enabled = False
    chkCamicieAcc.Enabled = False
    chkCamicieCA.Enabled = False
    chkVerifSLE = False
    chkVerificheDuttilità = False
    chkVerifSLE.Enabled = False
    chkVerificheDuttilità.Enabled = False
Else
    chkVerifSLE.Enabled = True
    If optMetodoSL08 Then
        chkFRC = False
        chkFRC.Enabled = False
        frmRinforzi.Enabled = False
        chkFRP = False
        chkCamicieAcc = False
        chkCamicieCA = False
        chkFRP.Enabled = False
        chkCamicieAcc.Enabled = False
        chkCamicieCA.Enabled = False
        chkVerificheDuttilità = False
        chkVerificheDuttilità.Enabled = False
    ElseIf optMetodoSL18 Then
        chkFRC.Enabled = True
        frmRinforzi.Enabled = True
        chkFRP.Enabled = True
        chkCamicieAcc.Enabled = True
        chkCamicieCA.Enabled = True
        chkVerificheDuttilità.Enabled = True
    End If
End If
End Sub

Private Sub optPilastro_Click()
If optPilastro Then
    chkVerifCarPunta.Enabled = True
Else
    chkVerifCarPunta = False
    chkVerifCarPunta.Enabled = False
End If
End Sub

Private Sub optSollPiane_Click()
If optSollPiane Then
    chkVerificheDuttilità.Enabled = True
Else
    chkVerificheDuttilità = False
    chkVerificheDuttilità.Enabled = False
End If
End Sub

Private Sub optSollSpaz_Click()
optSollPiane_Click
End Sub

Private Sub optTrave_Click()
optPilastro_Click
End Sub

Private Sub optTraveFondaz_Click()
optPilastro_Click
End Sub

Private Sub UserForm_Initialize()
For i = 1 To 5
    cmbNpolig.AddItem i
Next i
With Me
    .optCalcProg = Foglio2.Cells(24, 1)
    .optCalcVerif = Foglio2.Cells(25, 1)
    .chkVerifCarPunta = Foglio2.Cells(46, 1)
    .optMetodoTA = Foglio2.Cells(57, 1)
    .optMetodoSL08 = Foglio2.Cells(58, 1)
    .optMetodoSL18 = Foglio2.Cells(59, 1)
    .optSistemaTecnico = Foglio2.Cells(68, 1)
    .optSistemaInternaz = Foglio2.Cells(69, 1)
    .txtProgetto = Foglio2.Cells(13, 4)
    .txtCommitt = Foglio2.Cells(14, 4)
    .txtComune = Foglio2.Cells(15, 4)
    .txtTecnico = Foglio2.Cells(16, 4)
    .txtDataLuogo = Foglio2.Cells(18, 4)
    .txtAnnotazioni = Foglio2.Cells(17, 4)
    .cmbFormSez = Foglio2.Cells(54, 1)
    .cmbNpolig = Foglio2.Cells(3, 26)
    .chkVerifSLE = Foglio2.Cells(32, 6)
    .chkVerificheDuttilità = Foglio2.Cells(22, 1)
    .optSollPiane = Foglio2.Cells(28, 1)
    .optSollSpaz = Foglio2.Cells(29, 1)
    .optCAO = Foglio2.Cells(20, 1)
    .optCAP = Foglio2.Cells(21, 1)
    '.optCostruzNuova = Foglio2.Cells(20, 4)
    '.optCostruzEsist = Foglio2.Cells(21, 4)
    .chkCamicieAcc = Foglio2.Cells(22, 4)
    .chkCamicieCA = Foglio2.Cells(23, 4)
    .chkFRC = Foglio2.Cells(26, 1)
    .chkFRP = Foglio2.Cells(81, 1)
    .optPilastro = Foglio2.Cells(36, 1)
    .optTrave = Foglio2.Cells(37, 1)
    .optTraveFondaz = Foglio2.Cells(38, 1)
End With
cmbFormSez_Change
If optCalcProg Then
    chkVerificheDuttilità.Enabled = False
Else
    chkVerificheDuttilità.Enabled = True
End If
End Sub
