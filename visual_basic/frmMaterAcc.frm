VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmMaterAcc 
   Caption         =   "CAMICIE DI RINFORZO IN ACCIAIO - ANGOLARI E CALASTRELLI"
   ClientHeight    =   4044
   ClientLeft      =   84
   ClientTop       =   612
   ClientWidth     =   8880.001
   OleObjectBlob   =   "frmMaterAcc.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmMaterAcc"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttCalcolaCls_Click()
Dim Es#
Dim Pois#
If cmbTipoAcciaio = "" Then
    MsgBox "Specificare tipo di acciaio", vbInformation, VersioneSw
    Exit Sub
End If
If txtE = "" Or txtFyk = "" Then
    MsgBox "Inserisci dati obbligatori!", vbCritical, VersioneSw
    Exit Sub
End If
'Pois = txtPoisson
'Es = txtE
'txtG = Round(Es / (2 * (1 + Pois)), 0)
txtFyd = Round(txtFyk / txtgM0, 0)
End Sub

'Private Sub bttCancellaCls_Click()
'With Me
'    .txtG = ""
'    .txtFyd = ""
'End With
'End Sub

Private Sub bttSalvaChiudi_Click()
'controllo dati
If cmbTipoAcciaio = "" Then
    MsgBox "Inserisci tipo di acciaio", vbCritical, VersioneSw
    Exit Sub
End If
If txtE = "" Then
    MsgBox "Inserisci valore corretto per il modulo elastico E", vbCritical, VersioneSw
    Exit Sub
End If
If SistemaTecnico Then
    If txtE < 1000000 Or txtE > 3000000 Then
        MsgBox "Inserisci valore corretto per il modulo elastico longitudinale E", vbCritical, VersioneSw
        Exit Sub
    End If
Else
    If txtE < 100000 Or txtE > 300000 Then
        MsgBox "Inserisci valore corretto per il modulo elastico longitudinale E", vbCritical, VersioneSw
        Exit Sub
    End If
End If
If txtFyk = "" Or txtftk = "" Or txtgM0 = "" Or txtFyk = 0 Or txtftk = 0 Or txtgM0 = 0 Then
    MsgBox "Inserisci dati obbligatori!", vbCritical, VersioneSw
    Exit Sub
End If
'salva dati
With Foglio2
    .Cells(72, 5) = cmbTipoAcciaio
    .Cells(73, 5) = txtE
    .Cells(74, 5) = txtftk
    .Cells(75, 5) = txtFyk
    .Cells(76, 5) = txtgM0
    .Cells(77, 5) = txtFyd
End With
Unload Me
End Sub

Private Sub bttValoriNormat_Click()
Dim fyk#, ftk#
If SistemaTecnico Then
    txtE = Round(210000 * 10.1937, 0)
    Select Case cmbTipoAcciaio
        Case "S 235"
            fyk = Round(235 * 10.1937, 0) 'kg/cmq
            ftk = Round(360 * 10.1937, 0)
        Case "S 275"
            fyk = Round(275 * 10.1937, 0)
            ftk = Round(430 * 10.1937, 0) '4383
        Case "S 355"
            fyk = Round(355 * 10.1937, 0)
            ftk = Round(510 * 10.1937, 0)
        Case "S 420"
            fyk = Round(420 * 10.1937, 0)
            ftk = Round(520 * 10.1937, 0)
        Case "S 460"
            fyk = Round(460 * 10.1937, 0)
            ftk = Round(540 * 10.1937, 0)
        Case Else
            fyk = 0
            ftk = 0
    End Select
Else
    txtE = 210000
    Select Case cmbTipoAcciaio
        Case "S 235"
            fyk = 235  'N/mmq
            ftk = 360
        Case "S 275"
            fyk = 275
            ftk = 430
        Case "S 355"
            fyk = 355
            ftk = 510
        Case "S 420"
            fyk = 420
            ftk = 520
        Case "S 460"
            fyk = 460
            ftk = 540
        Case Else
            fyk = 0
            ftk = 0
    End Select
End If
txtFyk = fyk
txtftk = ftk
txtgM0 = 1.05
End Sub

Private Sub txtE_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtftk_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
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

Private Sub txtFyk_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtG_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtgM0_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtgM1_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtgM2_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtPesoSpecAcc_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtPoisson_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub txtSigfa_KeyPress(ByVal KeyAscii As MSForms.ReturnInteger)
If (KeyAscii < Asc("0") Or KeyAscii > Asc("9")) And KeyAscii <> Asc(",") Then
    KeyAscii = 0
    Beep
End If
End Sub

Private Sub UserForm_Initialize()
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
cmbTipoAcciaio.RowSource = "Foglio3!L10:L15"
lblE = "modulo elastico longitudinale E (" & umTens & ")"
'lblG = "modulo elastico tangenziale G (" & umTens & ")"
'lblPesoSpecAcc = "peso specifico dell'acciaio (" & umFL_3 & ")"
'lblSigfa = "tensione ammissibile (" & umTens & ")"
lblftk = "tensione caratteristica di rottura ftk (" & umTens & ")"
lblFyk = "tensione caratteristica di snervamento fyk (" & umTens & ")"
lblFyd = "resistenza di progetto acciaio fyd (" & umTens & ")"
'DisabilitaControlli
With Me
    .cmbTipoAcciaio = Foglio2.Cells(72, 5)
    .txtE = Foglio2.Cells(73, 5)
    .txtftk = Foglio2.Cells(74, 5)
    .txtFyk = Foglio2.Cells(75, 5)
    .txtgM0 = Foglio2.Cells(76, 5)
    .txtFyd = Foglio2.Cells(77, 5)
End With
End Sub

'Sub DisabilitaControlli()
'If MetodoTA Then
'    lblTA.Enabled = True
'    lblSigfa.Enabled = True
'    txtSigfa.Enabled = True
'    lblSLU.Enabled = False
'    lblgM0.Enabled = False
'    txtgM0.Enabled = False
'    lblgM1.Enabled = False
'    txtgM1.Enabled = False
'    lblgM2.Enabled = False
'    txtgM2.Enabled = False
'Else 'SLU
'    lblTA.Enabled = False
'    lblSigfa.Enabled = False
'    txtSigfa.Enabled = False
'    lblSLU.Enabled = True
'    lblgM0.Enabled = True
'    txtgM0.Enabled = True
'    lblgM1.Enabled = True
'    txtgM1.Enabled = True
'    lblgM2.Enabled = True
'    txtgM2.Enabled = True
'End If
'End Sub
