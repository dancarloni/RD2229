VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmPacchettiArmat 
   Caption         =   "Pacchetti di armatura presenti nella sezione"
   ClientHeight    =   3405
   ClientLeft      =   96
   ClientTop       =   588
   ClientWidth     =   17868
   OleObjectBlob   =   "frmPacchettiArmat.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmPacchettiArmat"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttCarica2_Click()
Dim Nb As Byte, Db#
If txtNb = "" Then Nb = 0 Else Nb = txtNb
If txtDb = "" Then Db = 0 Else Db = CDbl(txtDb)
If Nb > 0 And Db > 0 Then
    lstBarre.AddItem lstBarre.ListCount + 1 'aggiunge in coda una nuova riga
    lstBarre.List(lstBarre.ListCount - 1, 1) = txtYin.Text
    lstBarre.List(lstBarre.ListCount - 1, 2) = txtZin.Text
    lstBarre.List(lstBarre.ListCount - 1, 3) = txtYfi.Text
    lstBarre.List(lstBarre.ListCount - 1, 4) = txtZfi.Text
    lstBarre.List(lstBarre.ListCount - 1, 5) = txtNb.Text
    lstBarre.List(lstBarre.ListCount - 1, 6) = txtDb.Text
    lstBarre.List(lstBarre.ListCount - 1, 7) = cmbArm.Text
    lstBarre.List(lstBarre.ListCount - 1, 8) = cmbArmNuova.Text
    txtYin = ""
    txtZin = ""
    txtYfi = ""
    txtZfi = ""
    txtNb = ""
    txtDb = ""
    cmbArm = ""
    'cmbArmNuova = ""
    txtYin.SetFocus
Else
    MsgBox "Inserire dati obbligatori!", vbCritical, VersioneSw
End If
End Sub

Private Sub bttChiudi_Click()
Unload Me
End Sub

Private Sub bttElimina2_Click()
Dim Risp%
If lstBarre.ListIndex >= 0 Then 'verifica che è stato selezionato un elemento
    Risp = MsgBox("Confermi l'eliminazione del pacchetto selezionato", vbYesNo, VersioneSw)
    If Risp = vbYes Then
        lstBarre.RemoveItem lstBarre.ListIndex
    End If
Else
    MsgBox "Selezionare pacchetto da eliminare", vbOKOnly, VersioneSw
End If
End Sub

Private Sub bttModifica2_Click()
If lstBarre.ListIndex >= 0 Then
    If bttModifica2.Caption = "Modifica" Then
        txtYin.Text = lstBarre.List(lstBarre.ListIndex, 1)
        txtZin.Text = lstBarre.List(lstBarre.ListIndex, 2)
        txtYfi.Text = lstBarre.List(lstBarre.ListIndex, 3)
        txtZfi.Text = lstBarre.List(lstBarre.ListIndex, 4)
        txtNb.Text = lstBarre.List(lstBarre.ListIndex, 5)
        txtDb.Text = lstBarre.List(lstBarre.ListIndex, 6)
        cmbArm.Text = lstBarre.List(lstBarre.ListIndex, 7)
        cmbArmNuova.Text = lstBarre.List(lstBarre.ListIndex, 8)
        lstBarre.Locked = True
        bttElimina2.Enabled = False
        bttCarica2.Enabled = False
        bttModifica2.Caption = "Carica modif"
        bttSalvaPacch.Enabled = False
    Else 'carica le modifiche
        lstBarre.List(lstBarre.ListIndex, 1) = txtYin.Text
        lstBarre.List(lstBarre.ListIndex, 2) = txtZin.Text
        lstBarre.List(lstBarre.ListIndex, 3) = txtYfi.Text
        lstBarre.List(lstBarre.ListIndex, 4) = txtZfi.Text
        lstBarre.List(lstBarre.ListIndex, 5) = txtNb.Text
        lstBarre.List(lstBarre.ListIndex, 6) = txtDb.Text
        lstBarre.List(lstBarre.ListIndex, 7) = cmbArm.Text
        lstBarre.List(lstBarre.ListIndex, 8) = cmbArmNuova.Text
        txtYin = ""
        txtZin = ""
        txtYfi = ""
        txtZfi = ""
        txtNb = ""
        txtDb = ""
        cmbArm = ""
        'cmbArmNuova = ""
        lstBarre.Locked = False
        bttElimina2.Enabled = True
        bttCarica2.Enabled = True
        bttModifica2.Caption = "Modifica"
        bttSalvaPacch.Enabled = True
        lstBarre.ListIndex = -1
    End If
Else
    MsgBox "Selezionare dati da modificare", vbOKOnly, VersioneSw
End If
End Sub

Private Sub bttSalvaPacch_Click()
Dim Npacch%
If lstBarre.ListCount > 0 Then
    With Foglio2
        Npacch = .Cells(3, 42)
        'cancella coord preced vertici sezione
        If Npacch > 0 Then
            .Range(.Cells(5, 38), .Cells(5 + Npacch - 1, 43)).ClearContents
        End If
        For i = 1 To lstBarre.ListCount
            .Cells(4 + i, 38) = lstBarre.List(i - 1, 1)
            .Cells(4 + i, 39) = lstBarre.List(i - 1, 2)
            .Cells(4 + i, 40) = lstBarre.List(i - 1, 3)
            .Cells(4 + i, 41) = lstBarre.List(i - 1, 4)
            .Cells(4 + i, 42) = lstBarre.List(i - 1, 5)
            .Cells(4 + i, 43) = lstBarre.List(i - 1, 6)
            .Cells(4 + i, 44) = lstBarre.List(i - 1, 7)
            .Cells(4 + i, 36) = lstBarre.List(i - 1, 8)
        Next i
        .Cells(3, 42) = lstBarre.ListCount 'Npacc armat
    End With
    Unload Me
Else
    MsgBox "Occorre definire almeno un pacchetto armatura", vbCritical, VersioneSw
End If
End Sub

Private Sub UserForm_Initialize()
Dim i As Integer
Dim Npacch%
CemArmOrd = Foglio2.Cells(20, 1)
CemCAP = Foglio2.Cells(21, 1)
CemFRC = Foglio2.Cells(26, 1)
RinfCamicieCA = Foglio2.Cells(23, 4)
cmbArm.AddItem "Si"
cmbArm.AddItem "No"
cmbArmNuova.AddItem "Si"
cmbArmNuova.AddItem "No"
Npacch = Foglio2.Cells(3, 42)
For i = 1 To Npacch
    lstBarre.AddItem lstBarre.ListCount + 1
    lstBarre.List(lstBarre.ListCount - 1, 1) = Foglio2.Cells(4 + i, 38)
    lstBarre.List(lstBarre.ListCount - 1, 2) = Foglio2.Cells(4 + i, 39)
    lstBarre.List(lstBarre.ListCount - 1, 3) = Foglio2.Cells(4 + i, 40)
    lstBarre.List(lstBarre.ListCount - 1, 4) = Foglio2.Cells(4 + i, 41)
    lstBarre.List(lstBarre.ListCount - 1, 5) = Foglio2.Cells(4 + i, 42)
    lstBarre.List(lstBarre.ListCount - 1, 6) = Foglio2.Cells(4 + i, 43)
    lstBarre.List(lstBarre.ListCount - 1, 7) = Foglio2.Cells(4 + i, 44)
    lstBarre.List(lstBarre.ListCount - 1, 8) = Foglio2.Cells(4 + i, 36)
Next
If CemArmOrd Then
    cmbArm.Enabled = False
    cmbArm.Text = ""
    lblArm.Enabled = False
    Label57.Enabled = False
End If
If RinfCamicieCA = False Then
    lblArmNuova.Enabled = False
    cmbArmNuova.Enabled = False
    cmbArmNuova.Text = "Si"
    Label58.Enabled = False
End If
End Sub

Private Sub txtYfi_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtYin_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtZfi_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtZin_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") And KeyAscii <> Asc("-") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub lstBarre_DblClick(ByVal Cancel As MSForms.ReturnBoolean)
bttModifica2_Click
End Sub

Private Sub txtDb_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtNb_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) Then
    KeyAscii = 0
    Beep
End If
End Sub
