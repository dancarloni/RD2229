VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmInformaz 
   Caption         =   "Informazioni su SezioniCA.Az"
   ClientHeight    =   5025
   ClientLeft      =   96
   ClientTop       =   528
   ClientWidth     =   13212
   OleObjectBlob   =   "frmInformaz.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmInformaz"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAttivaSw_Click()
Foglio2.Cells(3, 4) = txtCH1
Foglio2.Cells(2, 4) = txtCH2
Foglio2.Cells(1, 4) = txtCH3
ActiveWorkbook.Save
fSwAttivato
If Foglio2.Cells(5, 4) Then 'è contenuta la varib SwAttivato
    lblSwAttivato = "Software attivato"
    bttAttivaSw.Enabled = False
    lblTitolare.Enabled = True
    txtTitolare.Enabled = True
Else
    lblSwAttivato = "Software non attivato"
    bttAttivaSw.Enabled = True
    lblTitolare.Enabled = False
    txtTitolare.Enabled = False
End If
Application.CommandBars("PERS").Delete
CreaBarraProgramma
End Sub

Private Sub bttChiudi_Click()
Unload Me
Foglio5.Protect PasswordMe 'dove ci sono le istruzioni
End Sub

Private Sub UserForm_Initialize()
lblNSsw = SerialeHD("C:")
txtCH1 = Foglio2.Cells(3, 4)
txtCH2 = Foglio2.Cells(2, 4)
txtCH3 = Foglio2.Cells(1, 4)
txtTitolare = Foglio2.Cells(6, 1)
fSwAttivato
If Foglio2.Cells(5, 4) Then 'è contenuta la varib SwAttivato
    lblSwAttivato = "Software attivato"
    bttAttivaSw.Enabled = False
    lblTitolare.Enabled = True
    txtTitolare.Enabled = True
Else
    lblSwAttivato = "Software non attivato"
    bttAttivaSw.Enabled = True
    lblTitolare.Enabled = False
    txtTitolare.Enabled = False
End If
End Sub

Private Sub bttSalva_Click()
Foglio2.Cells(3, 4) = txtCH1
Foglio2.Cells(2, 4) = txtCH2
Foglio2.Cells(1, 4) = txtCH3
Foglio2.Cells(6, 1) = txtTitolare
ActiveWorkbook.Save
'Unload Me
End Sub




