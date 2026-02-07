VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmRelazCalc 
   Caption         =   "RELAZIONE DI CALCOLO"
   ClientHeight    =   1875
   ClientLeft      =   96
   ClientTop       =   612
   ClientWidth     =   7308
   OleObjectBlob   =   "frmRelazCalc.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmRelazCalc"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttChiudi_Click()
Unload Me
End Sub

Private Sub bttElabora_Click()
'Crea Relazione di calcolo in Word
Dim Percorso As String
Dim wApp As Object
Dim wDoc As Object
'CONTROLLO DATI
If txtData = "" Then
    MsgBox "Inserire data emissione Relazione di calcolo", , VersioneSw
    txtData.SetFocus
    Exit Sub
End If
'SALVA DATI IN FG2
bttSalva_Click
'INPUT
MetodoTA = Foglio2.Cells(57, 1)
MetodoSL08 = Foglio2.Cells(58, 1)
MetodoSL18 = Foglio2.Cells(59, 1)
'ESECUZ
Set wApp = CreateObject("Word.Application")
wApp.Visible = True
Percorso = ActiveWorkbook.Path & "\Relazione di calcolo SezioniCA.Az.doc"
Set wDoc = wApp.Documents.Add(Percorso) 'crea una copia senza nome della relaz di calc
'IMPOSTA CAMPI NELLA COPERTINA, INTESTAZ E PIè PAGINA
wDoc.Bookmarks("Committ").Range.Text = Foglio2.Cells(14, 4)
wDoc.Bookmarks("TitoloProgetto").Range.Text = Foglio2.Cells(13, 4)
wDoc.Bookmarks("CodiceComm").Range.Text = Foglio2.Cells(4, 8)
wDoc.Bookmarks("CodiceElab").Range.Text = Foglio2.Cells(5, 8)
wDoc.Bookmarks("Progettista").Range.Text = Foglio2.Cells(16, 4)
wDoc.Bookmarks("Data").Range.Text = CDate(Foglio2.Cells(3, 8))
wDoc.Bookmarks("TitoloProgetto2").Range.Text = Foglio2.Cells(13, 4)
wDoc.Bookmarks("PièPagina").Range.Text = PièPagina & Foglio2.Cells(6, 1) & " (n° di serie: " & Foglio2.Cells(4, 4) & ")"
'IMPOSTA CAMPI NEL CORPO DELLA RELAZIONE E CANCELLA QUELLO NON NECESSARIO
wDoc.Bookmarks("ClasseCls").Range.Text = Foglio2.Cells(19, 3)
If MetodoSL08 Then
    wDoc.Bookmarks("Normativa").Range.Text = "Metodo agli Stati Limite di cui al D.M. 14/01/2008."
    wDoc.Bookmarks("NormativaSL2018").Range.Delete
    wDoc.Bookmarks("NormativaTA").Range.Delete
    wDoc.Bookmarks("MaterialiCA_TA").Range.Delete
    wDoc.Bookmarks("VerifResistCA_TA").Range.Delete
    wDoc.Bookmarks("DettagliCostruttCA_TA").Range.Delete
ElseIf MetodoSL18 Then
    wDoc.Bookmarks("Normativa").Range.Text = "Metodo agli Stati Limite di cui al D.M. 17/01/2018."
    wDoc.Bookmarks("NormativaSL2008").Range.Delete
    wDoc.Bookmarks("NormativaTA").Range.Delete
    wDoc.Bookmarks("MaterialiCA_TA").Range.Delete
    wDoc.Bookmarks("VerifResistCA_TA").Range.Delete
    wDoc.Bookmarks("DettagliCostruttCA_TA").Range.Delete
ElseIf MetodoTA Then
    wDoc.Bookmarks("Normativa").Range.Text = "Metodo alle Tensioni Ammissibili di cui al D.M. 11/03/1988 e D.M. 16/01/1996."
    wDoc.Bookmarks("NormativaSL2008").Range.Delete
    wDoc.Bookmarks("NormativaSL2018").Range.Delete
    wDoc.Bookmarks("MaterialiCA_SL").Range.Delete
    wDoc.Bookmarks("VerifResitCA_SL").Range.Delete
    wDoc.Bookmarks("VerifSLE_CA").Range.Delete
    wDoc.Bookmarks("DettagliCostruttCA_SL").Range.Delete
End If
'ultima parte della Relazione di calcolo
wDoc.Bookmarks("CodiceAttivazione").Range.Text = Foglio2.Cells(4, 4)
wDoc.Bookmarks("TitolareLicenza").Range.Text = Foglio2.Cells(6, 1)
wDoc.Bookmarks("TitolareLicenza2").Range.Text = Foglio2.Cells(6, 1)
'aggiorna sommario
wDoc.TablesOfContents(1).UpdatePageNumbers
End Sub

Private Sub bttSalva_Click()
With Foglio2
    .Cells(3, 8) = txtData
    .Cells(4, 8) = txtCommessa
    .Cells(5, 8) = txtCodElab
End With
End Sub

Private Sub UserForm_Initialize()
txtData = Foglio2.Cells(3, 8)
txtCommessa = Foglio2.Cells(4, 8)
txtCodElab = Foglio2.Cells(5, 8)
End Sub
