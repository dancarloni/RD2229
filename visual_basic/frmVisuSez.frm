VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmVisuSez 
   Caption         =   "VISUALIZZA ESECUTIVO SEZIONE"
   ClientHeight    =   2730
   ClientLeft      =   48
   ClientTop       =   432
   ClientWidth     =   5172
   OleObjectBlob   =   "frmVisuSez.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmVisuSez"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit
Dim IDtondini As Boolean, IDvert As Boolean

Private Sub bttAnnulla_Click()
Unload Me
End Sub

Private Sub bttVisualizza_Click()
If optVisuDis Then
    Foglio6.Activate
ElseIf optAggiornaDis Then
    Foglio2.Cells(11, 4) = txtScalaDisSez
    IDtondini = chkIDtondini
    IDvert = chkIDvert
    DisegnaSezCA
End If
End Sub

Private Sub optAggiornaDis_Click()
optVisuDis_Click
End Sub

Private Sub optVisuDis_Click()
If optVisuDis Then
    txtScalaDisSez.Enabled = False
    chkIDtondini.Enabled = False
    chkIDvert.Enabled = False
Else
    txtScalaDisSez.Enabled = True
    chkIDtondini.Enabled = True
    chkIDvert.Enabled = True
End If
End Sub

Private Sub UserForm_Initialize()
txtScalaDisSez = Foglio2.Cells(11, 4)
optVisuDis = True
End Sub

Sub DisegnaSezCA()
Const Delt = 60 'distanza dai bordi del foglio
Const Puntixcm = 27
Dim Alfa_f#, Alfa#
Dim DenomScala%
Dim FsX#, FsY#
Dim i%, j%, i1%
'Dim Np%
Dim NuovoCalcolo As Boolean
Dim Np_ns%
Dim Rf#
Dim Xod#, Yod#
Dim Xid#, Yid#, Xi1d#, Yi1d#
'1.INPUT
DenomScala = Foglio2.Cells(11, 4)
NuovoCalcolo = Foglio2.Cells(1, 8)
FormSez = Foglio2.Cells(54, 1)
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
If Foglio2.Cells(9, 11) = "" Then D = 0 Else D = Foglio2.Cells(9, 11) * fmL
If Foglio2.Cells(12, 11) = "" Then Di = 0 Else Di = Foglio2.Cells(12, 11) * fmL
If Foglio2.Cells(9, 1) = "" Then B = 0 Else B = Foglio2.Cells(9, 1) * fmL
If Foglio2.Cells(10, 1) = "" Then H = 0 Else H = Foglio2.Cells(10, 1) * fmL
If Foglio2.Cells(14, 11) = "" Then Bo = 0 Else Bo = Foglio2.Cells(14, 11) * fmL
If Foglio2.Cells(15, 11) = "" Then S = 0 Else S = Foglio2.Cells(15, 11) * fmL
n = Foglio2.Cells(9, 14)
Npolig = Foglio2.Cells(3, 26)
MetodoTA = Foglio2.Cells(57, 1)
MetodoSL08 = Foglio2.Cells(58, 1)
MetodoSL18 = Foglio2.Cells(59, 1)
Npacch = Foglio2.Cells(3, 42)
If Foglio2.Cells(10, 11) = "" Then Df = 0 Else Df = Foglio2.Cells(10, 11) * fmDiamTond
If Foglio2.Cells(16, 1) = "" Then Cf = 0 Else Cf = Foglio2.Cells(16, 1) * fmL
'calcolo numero complessivo di barre presenti in sezione
If FormSez <> "Circolare piena o cava" Then
    Nbar = 0
    For j = 1 To Npacch Step 1
        If Foglio2.Cells(4 + j, 42) <> "" Then Nbar = Nbar + Foglio2.Cells(4 + j, 42)
    Next j
Else
    If Foglio2.Cells(11, 11) = "" Then Nbar = 0 Else Nbar = Foglio2.Cells(11, 11)
End If
'determina coordinate tondini
CoordBaricentriTondini '1.1
'carica coordinate barre di armatura
If Nbar > 0 Then
    ReDim Yb_pr#(1 To Nbar)
    ReDim Zb_pr#(1 To Nbar)
    ReDim Db#(1 To Nbar)
End If
For i = 1 To Nbar
    Yb_pr(i) = Foglio2.Cells(4 + i, 46) * fmL
    Zb_pr(i) = Foglio2.Cells(4 + i, 47) * fmL
    Db(i) = Foglio2.Cells(4 + i, 48) * fmDiamTond 'in cm
Next i
'2.ESECUZ
DatiSezioneCA '4.1 determina caratteristiche sezione
FsX = Puntixcm / DenomScala 'fattore di scala
FsY = 1.08 * FsX
'calcolo coordinate di disegno punto di origine sistema y'z'
If Ymax_pr > 0 Then
    Xod = Ymax_pr * FsX / fmL + Delt
Else
    Xod = Delt
End If
If Zmin_pr < 0 Then
    Yod = -Zmin_pr * FsY / fmL + Delt
Else
    Yod = Delt
End If
'disegno sezione
With Foglio6
    'cancella i disegni precedenti
    .Activate
    ActiveSheet.Shapes.SelectAll
        Selection.Delete
    'non visualizzare griglie e instaz di righe e colonne
    With ActiveWindow
        .DisplayGridlines = False
        .DisplayHeadings = False
    End With
    'disegna perimetro sezione
    If FormSez = "Circolare piena o cava" Then
        Xid = Xod - D / 2 * FsX / fmL
        Yid = Yod - D / 2 * FsY / fmL
        .Shapes.AddShape(msoShapeOval, Xid, Yid, D * FsX / fmL, D * FsY / fmL).Select
            Selection.ShapeRange.Line.Weight = 1.5
            Selection.ShapeRange.Fill.Visible = msoTrue
        If Di > 0 Then
            Xid = Xod - Di / 2 * FsX / fmL
            Yid = Yod - Di / 2 * FsY / fmL
            .Shapes.AddShape(msoShapeOval, Xid, Yid, Di * FsX / fmL, Di * FsY / fmL).Select
                Selection.ShapeRange.Line.Weight = 1.5
                Selection.ShapeRange.Fill.Visible = msoTrue
        End If
    Else
        For j = 1 To Npolig Step 1
            'carica coordinate poligonale j
            CaricaDaFg2CoordPolig j '1.2
            For i = 1 To Np Step 1
                If i = Np Then
                    i1 = 1
                Else
                    i1 = i + 1
                End If
                Xid = Xod - Ys_pr(i) * FsX / fmL
                Yid = Yod + Zs_pr(i) * FsY / fmL
                Xi1d = Xod - Ys_pr(i1) * FsX / fmL
                Yi1d = Yod + Zs_pr(i1) * FsY / fmL
                .Shapes.AddLine(Xid, Yid, Xi1d, Yi1d).Line.Weight = 2.5
                'indicazione n∞ vertici
                If IDvert Then
                    .Shapes.AddTextbox(msoOrientationHorizontal, Xid, Yid, 35, 20).Select
                    Selection.Characters.Text = i
                    Selection.ShapeRange.Line.Visible = msoFalse
                    Selection.ShapeRange.Fill.Visible = msoFalse
                    Selection.Font.ColorIndex = 3
                End If
            Next i
        Next j
    End If
    'disegna barre armatura
    For i = 1 To Nbar Step 1
        Xid = Xod - Yb_pr(i) * FsX / fmL - Db(i) / 2 * FsX / fmL
        Yid = Yod + Zb_pr(i) * FsY / fmL - Db(i) / 2 * FsY / fmL
        .Shapes.AddShape(msoShapeOval, Xid, Yid, Db(i) * FsX / fmL, Db(i) * FsY / fmL).Fill.ForeColor.SchemeColor = 8
        If IDtondini Then
            .Shapes.AddTextbox(msoOrientationHorizontal, Xid + 0.5 * Db(i) * FsX / fmL, Yid + 0.5 * Db(i) * FsX / fmL, 35, 20).Select
            Selection.Characters.Text = i
            Selection.ShapeRange.Line.Visible = msoFalse
            Selection.ShapeRange.Fill.Visible = msoFalse
        End If
    Next i
    'inserisci il sistema di riferimento utente y',z'
    .Shapes.AddLine(Xod, Yod, Xod - 50, Yod).Select
        Selection.ShapeRange.Line.Weight = 2.5
        Selection.ShapeRange.Line.EndArrowheadStyle = msoArrowheadTriangle
        Selection.ShapeRange.Line.DashStyle = msoLineSquareDot
        Selection.ShapeRange.Line.ForeColor.SchemeColor = 10
    .Shapes.AddLine(Xod, Yod, Xod, Yod + 50).Select
        Selection.ShapeRange.Line.Weight = 2.5
        Selection.ShapeRange.Line.EndArrowheadStyle = msoArrowheadTriangle
        Selection.ShapeRange.Line.DashStyle = msoLineSquareDot
        Selection.ShapeRange.Line.ForeColor.SchemeColor = 10
    .Shapes.AddTextbox(msoOrientationHorizontal, Xod - 50, Yod - 25, 30, 20).Select
        Selection.Characters.Text = "y'"
        Selection.Font.ColorIndex = 3
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    .Shapes.AddTextbox(msoOrientationHorizontal, Xod, Yod + 30, 30, 20).Select
        Selection.Characters.Text = "z'"
        Selection.Font.ColorIndex = 3
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    'inserisci gli assi baricentrici y,z paralleli a y',z'
    Xid = Xod - yG_pr * FsX / fmL
    Yid = Yod + zG_pr * FsY / fmL
    .Shapes.AddLine(Xid, Yid, Xid - 50, Yid).Select
        Selection.ShapeRange.Line.Weight = 2.5
        Selection.ShapeRange.Line.EndArrowheadStyle = msoArrowheadTriangle
        Selection.ShapeRange.Line.ForeColor.SchemeColor = 10
    .Shapes.AddLine(Xid, Yid, Xid, Yid + 50).Select
        Selection.ShapeRange.Line.Weight = 2.5
        Selection.ShapeRange.Line.EndArrowheadStyle = msoArrowheadTriangle
        Selection.ShapeRange.Line.ForeColor.SchemeColor = 10
    .Shapes.AddTextbox(msoOrientationHorizontal, Xid - 50, Yid - 25, 30, 20).Select
        Selection.Characters.Text = "y"
        Selection.Font.ColorIndex = 3
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    .Shapes.AddTextbox(msoOrientationHorizontal, Xid, Yid + 30, 30, 20).Select
        Selection.Characters.Text = "z"
        Selection.Font.ColorIndex = 3
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    'indicazione baricentro sezione omogeneizzata
    .Shapes.AddTextbox(msoOrientationHorizontal, Xod - yG_pr * FsX / fmL - 5, Yod + zG_pr * FsY / fmL - 5, 20, 20).Select
        Selection.Characters.Text = "G"
        Selection.Font.ColorIndex = 3
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    'disegna assi principali d'inerzia
    Xid = Xod - Ymin_pr * FsX / fmL
    Yid = Yod + z1_pr * FsY / fmL
    Xi1d = Xod - Ymax_pr * FsX / fmL
    Yi1d = Yod + z2_pr * FsY / fmL
    .Shapes.AddLine(Xid, Yid, Xi1d, Yi1d).Select
        Selection.ShapeRange.Line.DashStyle = msoLineSquareDot
        Selection.ShapeRange.Line.ForeColor.SchemeColor = 8
    .Shapes.AddTextbox(msoOrientationHorizontal, Xid, Yid - 5, 30, 20).Select
        Selection.Characters.Text = "yp"
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    .Shapes.AddTextbox(msoOrientationHorizontal, Xi1d - 20, Yi1d - 5, 30, 20).Select
        Selection.Characters.Text = "yp"
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    Xid = Xod - y3_pr * FsX / fmL
    Yid = Yod + Zmin_pr * FsY / fmL
    Xi1d = Xod - y4_pr * FsX / fmL
    Yi1d = Yod + Zmax_pr * FsY / fmL
    .Shapes.AddLine(Xid, Yid, Xi1d, Yi1d).Select
        Selection.ShapeRange.Line.DashStyle = msoLineSquareDot
        Selection.ShapeRange.Line.ForeColor.SchemeColor = 8
    .Shapes.AddTextbox(msoOrientationHorizontal, Xid - 5, Yid - 20, 30, 20).Select
        Selection.Characters.Text = "zp"
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    .Shapes.AddTextbox(msoOrientationHorizontal, Xi1d - 5, Yi1d, 30, 20).Select
        Selection.Characters.Text = "zp"
        Selection.ShapeRange.Line.Visible = msoFalse
        Selection.ShapeRange.Fill.Visible = msoFalse
    'indicazione del titolo disegno
    .Shapes.AddTextbox(msoOrientationHorizontal, Xod - Ymax_pr * FsX / fmL, Yod + Zmax_pr * FsY / fmL + 30, 300, 40).Select
        If FormSez = "Circolare piena o cava" Then
            If Di = 0 Then
                Selection.Characters.Text = "Sezione CIRCOLARE PIENA" & Chr(10) & " scala 1:" & DenomScala & " (D = " & D / fmL & umL & ")"
            Else
                Selection.Characters.Text = "Sezione CIRCOLARE CAVA" & Chr(10) & " scala 1:" & DenomScala & " (D = " & D / fmL & umL & ", Di = " & Di / fmL & umL & ")"
            End If
        ElseIf FormSez = "Rettangolare" Then
            Selection.Characters.Text = "Sezione RETTANGOLARE" & Chr(10) & " scala 1:" & DenomScala & " (B = " & B / fmL & umL & ", H = " & H / fmL & umL & ")"
        ElseIf FormSez = "a T" Then
            Selection.Characters.Text = "Sezione a T" & Chr(10) & " scala 1:" & DenomScala & " (B=" & B / fmL & umL & ", Bo=" & Bo / fmL & umL & ", H=" & H / fmL & umL & ", s=" & S / fmL & umL & ")"
        ElseIf FormSez = "a T rovescia" Then
            Selection.Characters.Text = "Sezione a T rovescia" & Chr(10) & " scala 1:" & DenomScala & " (B=" & B / fmL & umL & ", Bo=" & Bo / fmL & umL & ", H=" & H / fmL & umL & ", s=" & S / fmL & umL & ")"
        ElseIf FormSez = "a doppio T" Then
            Selection.Characters.Text = "Sezione a doppio T" & Chr(10) & " scala 1:" & DenomScala & " (B=" & B / fmL & umL & ", Bo=" & Bo / fmL & umL & ", H=" & H / fmL & umL & ", s=" & S / fmL & umL & ")"
        ElseIf FormSez = "Scatolare" Then
            Selection.Characters.Text = "Sezione SCATOLARE" & Chr(10) & " scala 1:" & DenomScala & " (B=" & B / fmL & umL & ", H=" & H / fmL & umL & ", s=" & S / fmL & umL & ")"
        Else
            Selection.Characters.Text = "Sezione GENERICA" & Chr(10) & " scala 1:" & DenomScala
        End If
        Selection.Characters(Start:=1, Length:=27).Font.FontStyle = "Grassetto"
        Selection.HorizontalAlignment = xlCenter
        Selection.ShapeRange.Line.Visible = msoFalse 'no contorno
        Selection.ShapeRange.Fill.Visible = msoFalse 'no sfondo bianco
    'disegna sezione parzializzata
    If NuovoCalcolo = False And MetodoTA Then
        For j = 1 To Foglio2.Cells(106, 26) Step 1
            'carica coordinate poligonale j
            Np_ns = Foglio2.Cells(107, 22 + 2 * j)
            If Np_ns > 0 Then
                ReDim Yns#(1 To Np_ns)
                ReDim Zns#(1 To Np_ns)
            End If
            For i = 1 To Np_ns Step 1
                Yns(i) = Foglio2.Cells(108 + i, 21 + 2 * j) * fmL
                Zns(i) = Foglio2.Cells(108 + i, 22 + 2 * j) * fmL
            Next i
            For i = 1 To Np_ns Step 1
                If i = Np_ns Then
                    i1 = 1
                Else
                    i1 = i + 1
                End If
                Xid = Xod - Yns(i) * FsX / fmL
                Yid = Yod + Zns(i) * FsY / fmL
                Xi1d = Xod - Yns(i1) * FsX / fmL
                Yi1d = Yod + Zns(i1) * FsY / fmL
                .Shapes.AddLine(Xid, Yid, Xi1d, Yi1d).Select
                    Selection.ShapeRange.Line.Weight = 2.5
                    Selection.ShapeRange.Line.DashStyle = msoLineSquareDot
                    Selection.ShapeRange.Line.ForeColor.SchemeColor = 10
            Next i
        Next j
        'inserisci gli assi yr,zr baricentrici della sezione reagente paralleli a y',z'
        yGr_pr = Foglio2.Cells(17, 11) * fmL
        zGr_pr = Foglio2.Cells(18, 11) * fmL
        Xid = Xod - yGr_pr * FsX / fmL
        Yid = Yod + zGr_pr * FsY / fmL
        .Shapes.AddLine(Xid, Yid, Xid - 20, Yid).Select
            Selection.ShapeRange.Line.Weight = 0.5
            Selection.ShapeRange.Line.EndArrowheadStyle = msoArrowheadTriangle
            Selection.ShapeRange.Line.ForeColor.SchemeColor = 10
        .Shapes.AddLine(Xid, Yid, Xid, Yid + 20).Select
            Selection.ShapeRange.Line.Weight = 0.5
            Selection.ShapeRange.Line.EndArrowheadStyle = msoArrowheadTriangle
            Selection.ShapeRange.Line.ForeColor.SchemeColor = 10
        .Shapes.AddTextbox(msoOrientationHorizontal, Xid - 20, Yid - 25, 30, 20).Select
            Selection.Characters.Text = "yr"
            Selection.Font.ColorIndex = 3
            Selection.ShapeRange.Line.Visible = msoFalse
            Selection.ShapeRange.Fill.Visible = msoFalse
        .Shapes.AddTextbox(msoOrientationHorizontal, Xid, Yid + 10, 30, 20).Select
            Selection.Characters.Text = "zr"
            Selection.Font.ColorIndex = 3
            Selection.ShapeRange.Line.Visible = msoFalse
            Selection.ShapeRange.Fill.Visible = msoFalse
        'indicazione baricentro
        .Shapes.AddTextbox(msoOrientationHorizontal, Xod - yGr_pr * FsX / fmL - 5, Yod + zGr_pr * FsY / fmL - 10, 30, 20).Select
            Selection.Characters.Text = "Gr"
            Selection.Font.ColorIndex = 3
            Selection.ShapeRange.Line.Visible = msoFalse
            Selection.ShapeRange.Fill.Visible = msoFalse
    End If
    .Cells(1, 1).Select
End With
End Sub
