VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmDatiGene2 
   Caption         =   "CONFINAMENTO CALCESTRUZZO"
   ClientHeight    =   2610
   ClientLeft      =   96
   ClientTop       =   588
   ClientWidth     =   5976
   OleObjectBlob   =   "frmDatiGene2.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmdatiGene2"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttSalvaChiudi_Click()
'controlla dati
If RinfFRP Then
    If optConfinamNessuno = False And optConfinamStaffe = False And optConfinamFRP = False Then
        MsgBox "Specifica se considerare o meno confinamento del cls", vbCritical, VersioneSw
        Exit Sub
    End If
ElseIf RinfCamicieAcc Then
    If optConfinamNessuno = False And optConfinamCalastr = False Then
        MsgBox "Specifica se considerare o meno confinamento del cls", vbCritical, VersioneSw
        Exit Sub
    End If
ElseIf RinfCamicieCA Then
    If optConfinamNessuno = False And optConfinamStaffe = False Then
        MsgBox "Specifica se considerare o meno confinamento del cls", vbCritical, VersioneSw
        Exit Sub
    End If
End If
'salda dati
With Foglio2
    .Cells(66, 5) = optConfinamNessuno
    .Cells(67, 5) = optConfinamStaffe
    .Cells(68, 5) = optConfinamFRP
    .Cells(69, 5) = optConfinamCalastr
End With
'Ricrea la barra strumenti in modo da disattivare menù
Application.CommandBars("PERS").Delete
CreaBarraProgramma
Unload Me
End Sub

Private Sub UserForm_Initialize()
'CostruzNuova = Foglio2.Cells(20, 4)
'CostruzEsist = Foglio2.Cells(21, 4)
RinfFRP = Foglio2.Cells(81, 1)
RinfCamicieAcc = Foglio2.Cells(22, 4)
RinfCamicieCA = Foglio2.Cells(23, 4)
If RinfFRP Then
    optConfinamCalastr.Enabled = False
ElseIf RinfCamicieAcc Then
    optConfinamFRP.Enabled = False
    optConfinamStaffe.Enabled = False
ElseIf RinfCamicieCA Then
    optConfinamFRP.Enabled = False
    optConfinamCalastr.Enabled = False
End If
With Me
    .optConfinamNessuno = Foglio2.Cells(66, 5)
    .optConfinamStaffe = Foglio2.Cells(67, 5)
    .optConfinamFRP = Foglio2.Cells(68, 5)
    .optConfinamCalastr = Foglio2.Cells(69, 5)
End With
End Sub
