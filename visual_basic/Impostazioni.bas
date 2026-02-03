Attribute VB_Name = "Impostazioni"
Option Explicit
Dim Nfile%
Dim Percorso_e_NomeFile As String
Dim Parola As String

Sub CreaBarraProgramma()
Dim bttAreaStampa As CommandBarButton, BttAnteprimaStampa As CommandBarButton
Dim BttCriteri As CommandBarButton, bttCalcola As CommandBarButton, bttCancellaAreaStampa As CommandBarButton
Dim BttDatiGenerali As CommandBarButton, BttDatiGenerali2 As CommandBarButton
Dim BttDominio As CommandBarButton, BttDominioMyMz As CommandBarButton
Dim BttDominioNxMy As CommandBarButton, BttDiagrMomCurvat As CommandBarButton
Dim BttEsecutivo As CommandBarButton
Dim bttGraficoTau As CommandBarButton, BttGenerali As CommandBarButton, BttGeomFRP As CommandBarButton
Dim BttGeomConfinFRP As CommandBarButton, BttGeomConfinCalastr As CommandBarButton, BttGeomCalastr As CommandBarButton
Dim BttInformazioniSu As CommandBarButton
Dim BttMateriali As CommandBarButton, BttMatFRC As CommandBarButton, BttMatFRP As CommandBarButton, BttMatAcc As CommandBarButton
Dim BttMateriali2 As CommandBarButton
Dim BttNuovoCalcolo As CommandBarButton
Dim BttRisultati As CommandBarButton, BttRelazEsplicativa As CommandBarButton
Dim bttSalva As CommandBarButton, BttSalvaConNome As CommandBarButton
Dim BttStampa As CommandBarButton, BttStabilit‡ As CommandBarButton
Dim bttSollecitazSLU As CommandBarButton, bttSollecitazSLE As CommandBarButton
Dim bttVerifSLE As CommandBarButton
Dim mnuDatiGenerali As CommandBarPopup, mnuFile As CommandBarPopup, mnuInput As CommandBarPopup, mnuMateriali As CommandBarPopup
Dim mnuVisualizza As CommandBarPopup, mnuSollecitaz As CommandBarPopup, mnuGeometria As CommandBarPopup
Dim NuovoCalcolo As Boolean
'INPUT
NuovoCalcolo = Foglio2.Cells(1, 8)
'CostruzNuova = Foglio2.Cells(20, 4)
CemFRC = Foglio2.Cells(26, 1)
'CostruzEsist = Foglio2.Cells(21, 4)
RinfFRP = Foglio2.Cells(81, 1)
RinfCamicieAcc = Foglio2.Cells(22, 4)
RinfCamicieCA = Foglio2.Cells(23, 4)
MetodoTA = Foglio2.Cells(57, 1)
MetodoSL08 = Foglio2.Cells(58, 1)
MetodoSL18 = Foglio2.Cells(59, 1)
CalcVerif = Foglio2.Cells(25, 1)
FormSez = Foglio2.Cells(54, 1)
SollecPiane = Foglio2.Cells(28, 1)
blnVerifCarPunta = Foglio2.Cells(46, 1)
blnVerifSLE = Foglio2.Cells(32, 6)
blnVerifDuttilit‡ = Foglio2.Cells(22, 1)
If MetodoSL18 And CalcVerif And (FormSez = "Rettangolare" Or FormSez = "Circolare piena o cava") Then
    blnConfinNessuno = Foglio2.Cells(66, 5)
    blnConfinStaffe = Foglio2.Cells(67, 5)
    blnConfinFRP = Foglio2.Cells(68, 5)
    blnConfinCamicieAcc = Foglio2.Cells(69, 5)
Else
    blnConfinNessuno = True
    blnConfinStaffe = False
    blnConfinFRP = False
    blnConfinCamicieAcc = False
End If
If Foglio2.Cells(51, 1) = "" Then Nr = 0 Else Nr = Foglio2.Cells(51, 1) * fmF
SwAttivato = Foglio2.Cells(5, 4)
If Foglio2.Cells(32, 1) = "" Then Tz = 0 Else Tz = Foglio2.Cells(32, 1) '* fmF
If SollecPiane Then
    Ty = 0
Else
    If Foglio2.Cells(27, 1) = "" Then Ty = 0 Else Ty = Foglio2.Cells(27, 1) '* fmF
End If
'ESECUZ
Set BarraProgramma = CommandBars.Add(Name:="PERS", Position:=msoBarTop, MenuBar:=False, Temporary:=True)
    BarraProgramma.Visible = True
Set mnuFile = BarraProgramma.Controls.Add(Type:=msoControlPopup, ID:=1)
    mnuFile.Caption = "FILE"
    Set BttNuovoCalcolo = mnuFile.Controls.Add(Type:=msoControlButton, ID:=1)
        BttNuovoCalcolo.Caption = "Nuovo calcolo"
        BttNuovoCalcolo.FaceId = 13
        BttNuovoCalcolo.Style = 3
        BttNuovoCalcolo.OnAction = "mnuBttNuovoCalcolo"
        BttNuovoCalcolo.TooltipText = "Azzera i dati"
    'inserisci comandi utili di excel
    Set bttSalva = mnuFile.Controls.Add(Type:=msoControlButton, ID:=3, Before:=2)
    Set BttSalvaConNome = mnuFile.Controls.Add(Type:=msoControlButton, ID:=748, Before:=3)
    Set BttAnteprimaStampa = mnuFile.Controls.Add(Type:=msoControlButton, ID:=109, Before:=4)
    Set BttStampa = mnuFile.Controls.Add(Type:=msoControlButton, ID:=4, Before:=5)
    Set bttAreaStampa = mnuFile.Controls.Add(Type:=msoControlButton, ID:=364, Before:=6)
    Set bttCancellaAreaStampa = mnuFile.Controls.Add(Type:=msoControlButton, ID:=1584, Before:=7)
Set mnuDatiGenerali = BarraProgramma.Controls.Add(Type:=msoControlPopup, ID:=1)
    mnuDatiGenerali.Caption = "   DATI GENERALI"
    Set BttDatiGenerali = mnuDatiGenerali.Controls.Add(Type:=msoControlButton, ID:=1)
        BttDatiGenerali.Caption = "Dati generali"
        BttDatiGenerali.Style = 2
        BttDatiGenerali.OnAction = "mnuBttDatiGene"
        BttDatiGenerali.TooltipText = "Dati generali"
    Set BttDatiGenerali2 = mnuDatiGenerali.Controls.Add(Type:=msoControlButton, ID:=1)
        BttDatiGenerali2.Caption = "Confinamento calcestruzzo"
        BttDatiGenerali2.Style = 2
        BttDatiGenerali2.OnAction = "mnuBttDatiGene2"
        BttDatiGenerali2.TooltipText = "Confinamento calcestruzzo"
        If MetodoSL18 = False Or CalcVerif = False Or FormSez = "a T" Or FormSez = "a T rovescia" Or FormSez = "a doppio T" Or FormSez = "Scatolare" Or FormSez = "Generica" Then
            BttDatiGenerali2.Enabled = False
        End If
Set mnuGeometria = BarraProgramma.Controls.Add(Type:=msoControlPopup, ID:=1)
    mnuGeometria.Caption = "   GEOMETRIA"
    Set BttGenerali = mnuGeometria.Controls.Add(Type:=msoControlButton, ID:=1)
        BttGenerali.Caption = "Sezione e armature"
        BttGenerali.Style = 2
        BttGenerali.OnAction = "mnuBttInputGenerali"
        BttGenerali.TooltipText = "Input sezione"
    Set BttGeomFRP = mnuGeometria.Controls.Add(Type:=msoControlButton, ID:=1)
        BttGeomFRP.Caption = "Rinforzi a flessione e/o taglio con FRP"
        BttGeomFRP.Style = 2
        BttGeomFRP.OnAction = "mnuBttGeomFRP"
        BttGeomFRP.TooltipText = "Geometria compositi FRP per rinforzi a flessione e/o taglio"
        If RinfFRP = False Then BttGeomFRP.Enabled = False
    Set BttGeomConfinFRP = mnuGeometria.Controls.Add(Type:=msoControlButton, ID:=1)
        BttGeomConfinFRP.Caption = "Confinamento con compositi FRP"
        BttGeomConfinFRP.Style = 2
        BttGeomConfinFRP.OnAction = "mnuBttGeomConfinFRP"
        BttGeomConfinFRP.TooltipText = "Geometria compositi FRP per confinamento"
        If blnConfinFRP = False Then BttGeomConfinFRP.Enabled = False
    'Set BttGeomCalastr = mnuGeometria.Controls.Add(Type:=msoControlButton, ID:=1)
        'BttGeomCalastr.Caption = "Rinforzo a taglio con camicie di acciaio"
        'BttGeomCalastr.Style = 2
        'BttGeomCalastr.OnAction = "mnuBttGeomCalastr"
        'BttGeomCalastr.TooltipText = "Geometria camicie di rinforzo in acciaio a taglio"
        'If RinfCamicieAcc = False Then BttGeomCalastr.Enabled = False
    Set BttGeomConfinCalastr = mnuGeometria.Controls.Add(Type:=msoControlButton, ID:=1)
        BttGeomConfinCalastr.Caption = "Confinamento e rinforzo a taglio con camicie in acciaio/CAM"
        BttGeomConfinCalastr.Style = 2
        BttGeomConfinCalastr.OnAction = "mnuBttGeomConfinCalastr"
        BttGeomConfinCalastr.TooltipText = "Geometria angolari e calastrelli o metodo CAM per il confinamento del cls"
        If RinfCamicieAcc = False And blnConfinCamicieAcc = False Then BttGeomConfinCalastr.Enabled = False
Set mnuMateriali = BarraProgramma.Controls.Add(Type:=msoControlPopup, ID:=1)
    mnuMateriali.Caption = "   MATERIALI"
    Set BttMateriali = mnuMateriali.Controls.Add(Type:=msoControlButton, ID:=1)
        BttMateriali.Caption = "Calcestruzzo e acciaio"
        BttMateriali.Style = 2
        BttMateriali.OnAction = "mnuBttMateriali"
        BttMateriali.TooltipText = "Dati materiali"
    Set BttMateriali2 = mnuMateriali.Controls.Add(Type:=msoControlButton, ID:=1)
        BttMateriali2.Caption = "Acciaio esistente"
        BttMateriali2.Style = 2
        BttMateriali2.OnAction = "mnuBttMaterialiEsist"
        BttMateriali2.TooltipText = "Dati acciaio esistente (incamicitaura in c.a.)"
        If RinfCamicieCA = False Then BttMateriali2.Enabled = False
    Set BttMatFRC = mnuMateriali.Controls.Add(Type:=msoControlButton, ID:=1)
        BttMatFRC.Caption = "Calcestruzzo fibrorinforzato FRC"
        BttMatFRC.Style = 2
        BttMatFRC.OnAction = "mnuBttMateriali2"
        BttMatFRC.TooltipText = "Dati calcestruzzo fibrorinforzato FRC"
        If CemFRC = False Then BttMatFRC.Enabled = False
    Set BttMatFRP = mnuMateriali.Controls.Add(Type:=msoControlButton, ID:=1)
        BttMatFRP.Caption = "Compositi fibrorinforzati FRP"
        BttMatFRP.Style = 2
        BttMatFRP.OnAction = "mnuBttMateriali3"
        BttMatFRP.TooltipText = "Dati compositi fibrorinforzati a matrice polimerica FRP"
        If RinfFRP = False And blnConfinFRP = False Then BttMatFRP.Enabled = False
    Set BttMatAcc = mnuMateriali.Controls.Add(Type:=msoControlButton, ID:=1)
        BttMatAcc.Caption = "Acciaio angolari e calastrelli"
        BttMatAcc.Style = 2
        BttMatAcc.OnAction = "mnuBttMateriali4"
        BttMatAcc.TooltipText = "Dati sull'acciaio delle camicie di rinforzo in acciaio"
        If RinfCamicieAcc = False And blnConfinCamicieAcc = False Then BttMatAcc.Enabled = False
Set mnuSollecitaz = BarraProgramma.Controls.Add(Type:=msoControlPopup, ID:=1)
    mnuSollecitaz.Caption = "   SOLLECITAZIONI"
    Set bttSollecitazSLU = mnuSollecitaz.Controls.Add(Type:=msoControlButton, ID:=1)
        bttSollecitazSLU.Caption = "Verifiche di resistenza SLU"
        bttSollecitazSLU.Style = 2
        bttSollecitazSLU.OnAction = "bttInputSollecitazSLU"
        bttSollecitazSLU.TooltipText = "Input caratteristiche di sollecitazione agenti sulla sezione ai fini delle verifiche di resistenza"
    Set bttSollecitazSLE = mnuSollecitaz.Controls.Add(Type:=msoControlButton, ID:=1)
        bttSollecitazSLE.Caption = "Verifiche agli SLE"
        bttSollecitazSLE.Style = 2
        bttSollecitazSLE.OnAction = "bttInputSollecitazSLE"
        bttSollecitazSLE.TooltipText = "Input caratteristiche di sollecitazione agenti sulla sezione ai fini delle verifiche agli SLE"
        If MetodoTA Or blnVerifSLE = False Then bttSollecitazSLE.Enabled = False
Set BttStabilit‡ = BarraProgramma.Controls.Add(Type:=msoControlButton, ID:=1)
    BttStabilit‡.Caption = "  STABILITA' ASTA  "
    BttStabilit‡.Style = 2
    BttStabilit‡.OnAction = "mnuBttStabilit‡Asta"
    BttStabilit‡.TooltipText = "Input per le verifiche di stabilit‡ relative all'intera asta"
    If blnVerifCarPunta = False Then BttStabilit‡.Enabled = False
Set BttCriteri = BarraProgramma.Controls.Add(Type:=msoControlButton, ID:=1)
    BttCriteri.Caption = "  ALTRI DATI  "
    'BttGenerali.FaceId = 5
    BttCriteri.Style = 2
    BttCriteri.OnAction = "mnuBttCriteri"
    BttCriteri.TooltipText = "Criteri per la scelta dei tondini"
    'If CalcVerif Then BttCriteri.Enabled = False
Set bttVerifSLE = BarraProgramma.Controls.Add(Type:=msoControlButton, ID:=1)
    bttVerifSLE.Caption = "  VERIF. S.L.E.  "
    bttVerifSLE.Style = 2
    bttVerifSLE.OnAction = "mnuBttVerifSLE"
    bttVerifSLE.TooltipText = "Dati per le verifiche agli Stati Limite di Esercizio"
    If MetodoTA Or blnVerifSLE = False Then bttVerifSLE.Enabled = False
Set bttCalcola = BarraProgramma.Controls.Add(Type:=msoControlButton, ID:=1)
    bttCalcola.Caption = "  CALCOLA  "
    bttCalcola.Style = 2
    bttCalcola.OnAction = "mnuBttCalcola"
    bttCalcola.TooltipText = "Calcola e visualizza risultati"
Set mnuVisualizza = BarraProgramma.Controls.Add(Type:=msoControlPopup, ID:=1)
    mnuVisualizza.Caption = "   VISUALIZZA"
    Set BttRisultati = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        BttRisultati.Caption = "Tabulato di calcolo"
        BttRisultati.Style = 3
        BttRisultati.OnAction = "BttRisultati"
        BttRisultati.TooltipText = "Tabulato di calcolo"
    Set BttEsecutivo = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        BttEsecutivo.Caption = "Disegno sezione"
        BttEsecutivo.Style = 3
        BttEsecutivo.OnAction = "BttEsecutivo"
        BttEsecutivo.TooltipText = "Esecutivo in C.A."
        'If NuovoCalcolo Then BttEsecutivo.Enabled = False
    Set BttDominioMyMz = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        BttDominioMyMz.Caption = "Dominio di rottura My-Mz"
        BttDominioMyMz.Style = 3
        BttDominioMyMz.OnAction = "BttDominioMyMz"
        BttDominioMyMz.TooltipText = "Dominio di rottura My-Mz"
        If MetodoTA Or NuovoCalcolo Or Foglio4.Cells(302, 5) = False Or SollecPiane Then BttDominioMyMz.Enabled = False
    Set BttDominioNxMy = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        BttDominioNxMy.Caption = "Dominio di rottura Nx-My"
        BttDominioNxMy.Style = 3
        BttDominioNxMy.OnAction = "BttDominioNxMy"
        BttDominioNxMy.TooltipText = "Dominio di rottura Nx-My"
        If MetodoTA Or NuovoCalcolo Or Foglio4.Cells(302, 5) = False Or SollecPiane = False Then BttDominioNxMy.Enabled = False
    Set BttDominio = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        BttDominio.Caption = "Dominio di rottura Nx-My (carico di punta)"
        BttDominio.Style = 3
        BttDominio.OnAction = "BttDominioMyNx_cp"
        BttDominio.TooltipText = "Dominio di rottura Nx-My per la verifica a carico di punta"
        If MetodoTA Or NuovoCalcolo Or blnVerifCarPunta = False Or Nr >= 0 Then BttDominio.Enabled = False
    Set BttDiagrMomCurvat = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        BttDiagrMomCurvat.Caption = "Diagramma Momenti-Curvatura"
        BttDiagrMomCurvat.Style = 3
        BttDiagrMomCurvat.OnAction = "BttDiagrammaMomCurv"
        BttDiagrMomCurvat.TooltipText = "diagramma momenti-curvatura della sezione in c.a."
        If MetodoTA Or MetodoSL08 Or blnVerifDuttilit‡ = False Or NuovoCalcolo Then BttDiagrMomCurvat.Enabled = False
    Set bttGraficoTau = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        bttGraficoTau.Caption = "Diagramma tensioni tangenziali tau_xz"
        bttGraficoTau.Style = 3
        bttGraficoTau.OnAction = "BttDiagrammaTau"
        bttGraficoTau.TooltipText = "Diagramma tensioni tangenziali tau_xz"
        If MetodoTA And FormSez <> "Generica" And Ty = 0 And Tz <> 0 And NuovoCalcolo = False Then
            bttGraficoTau.Enabled = True
        Else
            bttGraficoTau.Enabled = False
        End If
    Set BttRelazEsplicativa = mnuVisualizza.Controls.Add(Type:=msoControlButton, ID:=1)
        BttRelazEsplicativa.Caption = "Relazione di calcolo"
        BttRelazEsplicativa.Style = 3
        BttRelazEsplicativa.OnAction = "BttRelazEsplicativa"
        BttRelazEsplicativa.TooltipText = "Relazione di calcolo"
        If SwAttivato = False Then BttRelazEsplicativa.Enabled = False
Set BttInformazioniSu = BarraProgramma.Controls.Add(Type:=msoControlButton, ID:=1)
    BttInformazioniSu.Caption = "  INFORMAZIONI SU  "
    BttInformazioniSu.Style = 2
    BttInformazioniSu.OnAction = "BttInformazioniSu"
    BttInformazioniSu.TooltipText = "Informazioni su"
End Sub

Sub mnuBttDatiGene() '1.1
frmDatiGene.Show
End Sub

Sub mnuBttDatiGene2() '1.2
frmdatiGene2.Show
End Sub

Sub mnuBttInputGenerali() '2.1
FormSez = Foglio2.Cells(54, 1)
If FormSez = "Rettangolare" Then
    frmGeomSezRettCA.Show
ElseIf FormSez = "Circolare piena o cava" Then
    frmGeomSezCircCA.Show
ElseIf FormSez = "a doppio T" Then
    frmGeomSezDoppioT.Show
ElseIf FormSez = "a T" Then
    frmGeomSezT.Show
ElseIf FormSez = "a T rovescia" Then
    frmGeomSezTrovescia.Show
ElseIf FormSez = "Scatolare" Then
    frmGeomSezScat.Show
ElseIf FormSez = "Generica" Then
    frmGeomSezGenerica.Show
End If
End Sub

Sub mnuBttGeomFRP() '2.2
frmGeomFRP.Show
End Sub

Sub mnuBttGeomConfinFRP() '2.3
frmGeomFRPconfin.Show
End Sub

'Sub mnuBttGeomCalastr() '2.4
'frmGeomCalastr.Show
'End Sub

Sub mnuBttGeomConfinCalastr() '2.5
frmGeomCalastrConfin.Show
End Sub

Sub mnuBttMateriali() '3.1
frmMaterCA.Show
End Sub

Sub mnuBttMaterialiEsist() '3.2
frmMaterCAesist.Show
End Sub

Sub mnuBttMateriali2() '3.3
frmMaterFRC.Show
End Sub

Sub mnuBttMateriali3() '3.4
frmMaterFRP.Show
End Sub

Sub mnuBttMateriali4() '3.5
frmMaterAcc.Show
End Sub

Sub bttInputSollecitazSLU() '4.1
frmSollecitazSLU.Show
End Sub

Sub bttInputSollecitazSLE() '4.2
frmSollecitazSLE.Show
End Sub

Sub mnuBttStabilit‡Asta() '5.
frmStabilit‡.Show
End Sub

Sub mnuBttCriteri() '6.
frmAltriDati.Show
End Sub

Sub mnuBttVerifSLE() '7.
frmVerifSLE.Show
End Sub

Sub mnuBttCalcola() '8.
Dim PrimoAvvio As Boolean, Nfile
SettaFg1xoutput
Ncalcolaz = Foglio2.Cells(3, 1)
PrimoAvvio = Foglio2.Cells(1, 5)
'PrimoAvvio = False
SwAttivato = fSwAttivato
If SwAttivato Then
    'avvio programma
    Programma_principale
    Foglio2.Cells(4, 1) = iF1
    Foglio2.Cells(1, 8) = False 'nuovo calcolo
    ActiveWorkbook.Save
Else
    If PrimoAvvio Then
        If Dir(NomeFileControllo) = "" Then
            'crea cartella in pc se inesistente (quando la cartella esiste ed Ë vuota, perche l'utente l'ha svuotata, MkDir da errore)
            If Dir(NomeCartella & "\*.txt") = "" Then
                MkDir NomeCartella
            End If
            'crea file controllo
            Nfile = FreeFile
            Open NomeFileControllo For Output As #Nfile
                Print #Nfile, "c"
            Close #Nfile
            'aggiorna variabile PrimoAvvio
            Foglio2.Cells(1, 5) = False
            ActiveWorkbook.Save
            'avvio programma
            If CLng(Date) <= CLng(CDate(DataFineSw1)) And CLng(Date) >= (CLng(CDate(DataFineSw1)) - DurataggProvaSw) And Ncalcolaz <= NmaxCalc Then
                Programma_principale
                Foglio2.Cells(4, 1) = iF1
                Foglio2.Cells(3, 1) = Ncalcolaz + 1
                Foglio2.Cells(1, 8) = False 'nuovo calcolo
                ActiveWorkbook.Save
            Else
                MsgBox MessFineCalc_o_Tempo, vbCritical, VersioneSw
                frmInformaz.Show
            End If
        Else 'file controlo esistente
            MsgBox MessFineCalc_o_Tempo, vbCritical, VersioneSw
            frmInformaz.Show
        End If
    Else
        If CLng(Date) <= CLng(CDate(DataFineSw1)) And CLng(Date) >= (CLng(CDate(DataFineSw1)) - DurataggProvaSw) And Ncalcolaz <= NmaxCalc Then
            'avvio programma
            Programma_principale
            Foglio2.Cells(4, 1) = iF1
            Foglio2.Cells(3, 1) = Ncalcolaz + 1
            Foglio2.Cells(1, 8) = False 'nuovo calcolo
            ActiveWorkbook.Save
        Else
            MsgBox MessFineCalc_o_Tempo, vbCritical, VersioneSw
            frmInformaz.Show
        End If
    End If
End If
'Ricrea la barra strumenti in modo da disattivare men˘
Application.CommandBars("PERS").Delete
CreaBarraProgramma
End Sub

Function fSwAttivato() As Boolean
'controlla se il sw Ë stato attivato
Dim NSsw, NSu1, NSu2, NSu3, CH1, CH2, CH3, CH1_, CH2_, CH3_, UltimiNumeri1
Dim UltimiNumeri2, UltimiNumeri3
Dim Ncaratt%
NSsw = Val(Foglio2.Cells(4, 4))
CH1 = Foglio2.Cells(3, 4)
CH2 = Foglio2.Cells(2, 4)
CH3 = Foglio2.Cells(1, 4)
Ncaratt = Len(CH1)
If Ncaratt > N∞carattIDsw Then
    CH1_ = Left(CH1, Ncaratt - N∞carattIDsw)
    UltimiNumeri1 = Val(Right(CH1, N∞carattIDsw))
End If
NSu1 = Val(CH1_) - 1257412574
Ncaratt = Len(CH2)
If Ncaratt > N∞carattIDsw Then
    CH2_ = Left(CH2, Ncaratt - N∞carattIDsw)
    UltimiNumeri2 = Val(Right(CH2, N∞carattIDsw))
End If
NSu2 = Val(CH2_) - 1257412574
Ncaratt = Len(CH3)
If Ncaratt > N∞carattIDsw Then
    CH3_ = Left(CH3, Ncaratt - N∞carattIDsw)
    UltimiNumeri3 = Val(Right(CH3, N∞carattIDsw))
End If
NSu3 = Val(CH3_) - 1257412574
If (NSu1 = NSsw And UltimiNumeri1 = IDsw) Or (NSu2 = NSsw And UltimiNumeri2 = IDsw) Or (NSu3 = NSsw And UltimiNumeri3 = IDsw) Then
    fSwAttivato = True
    Foglio2.Cells(5, 4) = True
    'Foglio2.Cells(3, 1) = NmaxCalc
Else
    fSwAttivato = False
    Foglio2.Cells(5, 4) = False
End If
End Function

Function SerialeHD(letteraHD As String) As String
Dim Fs, dc
Set Fs = CreateObject("Scripting.FileSystemObject")
Set dc = Fs.GetDrive(Fs.GetDriveName(Fs.GetAbsolutePathName(letteraHD)))
SerialeHD = Str(dc.SerialNumber)
Set dc = Nothing
Set Fs = Nothing
End Function

Sub BttRisultati() '9.1
'If LimitazStampa Then Foglio1.Protect PasswordMe
Foglio1.Activate
End Sub

Sub BttEsecutivo() '9.2
frmVisuSez.Show
End Sub

Sub BttDominioMyMz() '9.3
'input
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
'esecuz
With Grafico3
    .Unprotect PasswordMe
    .Activate
    .Axes(xlCategory).AxisTitle.Select
        Selection.Characters.Text = "My (" & umMomenti & ")"
    .Axes(xlValue).AxisTitle.Select
        Selection.Characters.Text = "Mz (" & umMomenti & ")"
    .PageSetup.LeftFooter = "&""Arial,Grassetto""&8" & PiËPagina & Foglio2.Cells(6, 1) & " (n∞ di serie: " & Foglio2.Cells(4, 4) & ")"
    .Protect PasswordMe
End With
End Sub

Sub BttDominioNxMy() '9.4
'input
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
'esecuz
With Grafico5
    .Unprotect PasswordMe
    .Activate
    .Axes(xlCategory).AxisTitle.Select
        Selection.Characters.Text = "Nx (" & umForze & ")"
    .Axes(xlValue).AxisTitle.Select
        Selection.Characters.Text = "My (" & umMomenti & ")"
    .Protect PasswordMe
End With
End Sub

Sub BttDominioMyNx_cp() '9.5
'input
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
'esecuz
With Grafico1
    .Unprotect PasswordMe
    .Activate
    .Axes(xlCategory).AxisTitle.Select
        Selection.Characters.Text = "Nx (" & umForze & ")"
    .Axes(xlValue).AxisTitle.Select
        Selection.Characters.Text = "My (" & umMomenti & ")"
    .PageSetup.LeftFooter = "&""Arial,Grassetto""&8" & PiËPagina & Foglio2.Cells(6, 1) & " (n∞ di serie: " & Foglio2.Cells(4, 4) & ")"
    .Protect PasswordMe
End With
End Sub

Sub BttDiagrammaMomCurv() '9.6
Dim Testo As String, Nrighe%
'input
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
FormSez = Foglio2.Cells(54, 1)
If Foglio2.Cells(9, 1) = "" Then B = 0 Else B = Foglio2.Cells(9, 1) * fmL
If Foglio2.Cells(10, 1) = "" Then H = 0 Else H = Foglio2.Cells(10, 1) * fmL
If Foglio2.Cells(31, 1) = "" Then Nx = 0 Else Nx = Foglio2.Cells(31, 1) * fmF
If Foglio2.Cells(19, 1) = "" Then Rck = 0 Else Rck = Foglio2.Cells(19, 1) * fmFL_2
TipoAcciaioCA = Foglio2.Cells(18, 1)
blnParabRettang = Foglio2.Cells(65, 1)
blnTriangRettang = Foglio2.Cells(67, 1)
blnStressBlock = Foglio2.Cells(66, 1)
blnElastPerfettPlastico = Foglio2.Cells(24, 8)
blnBilineare = Foglio2.Cells(25, 8)
Nrighe = Foglio4.Cells(6, 36)
'Definisci grafico
With Grafico6
    .Activate
    .Unprotect PasswordMe
    .Axes(xlCategory).AxisTitle.Select
    .Axes(xlValue, xlPrimary).AxisTitle.Text = "Curvatura  (1/" & umL & ")"
    Selection.Format.TextFrame2.TextRange.Characters.Text = "Curvatura  (1/" & umL & ")"
    .Axes(xlValue).AxisTitle.Select
    .Axes(xlValue, xlPrimary).AxisTitle.Text = "My (" & umMomenti & ")"
    .ChartTitle.Select
    .ChartTitle.Text = "DIAGRAMMA MOMENTO CURVATURA SEZIONE C.A. (sezione " & FormSez & " soggetta a Nx=" & Nx / fmF & umForze & ")"
    Testo = "Rck=" & Rck / fmFL_2 & umTens & "  acciaio:" & TipoAcciaioCA & "  B=" & B / fmL & umL & "  H=" & H / fmL & umL
    If FormSez = "Rettangolare" Or FormSez = "a T" Or FormSez = "a T rovescia" Or FormSez = "a doppio T" Or FormSez = "Scatolare" Then
        If Foglio2.Cells(13, 1) <> "" Then Testo = Testo & "   Asup=" & Foglio2.Cells(13, 1) & "f" & Foglio2.Cells(12, 1) & "   Ainf=" & Foglio2.Cells(15, 1) & "f" & Foglio2.Cells(14, 1)
    ElseIf FormSez = "Circolare piena o cava" Then
        Testo = Testo & "   Af=" & Foglio2.Cells(11, 11) & "f" & Foglio2.Cells(10, 11)
    End If
    If blnParabRettang Then
        Testo = Testo & "   diagr. cls: parabola-rettangolo"
    ElseIf blnTriangRettang Then
        Testo = Testo & "   diagr. cls: triangolo-rettangolo"
    ElseIf blnStressBlock Then
        Testo = Testo & "   diagr. cls: ""Stress-Block"""
    End If
    If blnElastPerfettPlastico Then
        Testo = Testo & "   diagr. acciaio: elastico perfettamente plastico"
    ElseIf blnBilineare Then
        Testo = Testo & "   diagr. acciaio: bilineare con incrudimento"
    End If
    .Shapes(1).TextFrame2.TextRange.Characters.Text = Testo
    .Shapes(2).TextFrame2.TextRange.Characters.Text = "duttilit‡ sezione = " & Foglio4.Cells(8, 36)
    If Nrighe > 0 Then
        .SeriesCollection(1).XValues = "=Foglio4!$AD$6:$AD$" & (5 + Nrighe)
        .SeriesCollection(1).Values = "=Foglio4!$AE$6:$AE$" & (5 + Nrighe)
    End If
    '.Protect PasswordMe
End With
End Sub

Sub BttDiagrammaTau() '9.7
'input
SistemaTecnico = Foglio2.Cells(68, 1)
DefinisciUnit‡Misura
'esecuz
With Grafico2
    .Unprotect PasswordMe
    .Activate
    .Axes(xlCategory).AxisTitle.Select
        Selection.Characters.Text = "Tau (" & umTens & ")"
    .Protect PasswordMe
End With
End Sub

Sub BttRelazEsplicativa() '9.8
frmRelazCalc.Show
End Sub

Sub BttInformazioniSu() '10
frmInformaz.Show
End Sub

Sub mnuBttNuovoCalcolo()
Dim Risp As Integer
Risp = MsgBox("Sei sicuro di volere azzerare i dati e procedere ad un nuovo calcolo?", vbYesNo, VersioneSw)
If Risp = vbYes Then
    SettaFg1xoutput
    With Foglio2 'cancella dati di input precedenti
        .Activate
        '1. DATI GENERALI
        '1.1 Dati Generali
        .Range("d13:d15").ClearContents
        .Range("d17:d18").ClearContents
        .Cells(20, 1) = True 'CemArmOrd
        .Cells(21, 1) = False 'CemArmPrecompr
        .Cells(26, 1) = False 'CemFRC
        '.Cells(20, 4) = True 'Costruz nuova
        '.Cells(21, 4) = False 'Costruz esist
        .Cells(81, 1) = False 'rinf FRP
        .Cells(22, 4) = False 'rinf camicie acciaio
        .Cells(23, 4) = False 'rinf camicia CA
        .Cells(25, 1) = True 'calcolo verifica
        .Cells(24, 1) = False 'calcolo progetto
        .Cells(54, 1) = "Rettangolare" 'forma sezione
        .Cells(3, 26) = 1 'n∞ poligonali che formano sezione
        .Cells(36, 1) = False 'pilastro
        .Cells(37, 1) = True 'trave
        .Cells(38, 1) = False 'trave fondaz
        .Cells(28, 1) = True 'sollecitaz piane
        .Cells(29, 1) = False 'sollecitaz spaziali
        .Cells(32, 6) = False 'blnVerifSLE
        .Cells(46, 1) = False 'verif a carico di punta
        .Cells(22, 1) = False 'verif di duttilit‡
        '1.2 Confinamento calcestruzzo
        .Cells(66, 5) = True 'nessuno
        .Cells(67, 5) = False 'staffe
        .Cells(68, 5) = False 'FRP
        .Cells(69, 5) = False 'camicie acc
        '2. GEOMETRIA
        '2.1 Sezioni e armature longitud
        .Range("a9:a10").ClearContents 'B,H
        .Range("k14:k15").ClearContents 'Bo,S
        .Range("a12:a16").ClearContents 'dsup, dinf, Nbi, Nbs, Cf
        .Range("k9:k12").ClearContents 'D,Di,Nf,Df
        .Cells(23, 1) = True 'armatura solo nei due lembi
        .Cells(4, 24) = 0 'n vertici
        .Cells(4, 26) = 0 'n vertici
        .Cells(4, 28) = 0 'n vertici
        .Cells(4, 30) = 0 'n vertici
        .Cells(4, 32) = 0 'n vertici
        .Range("W6:AF100").ClearContents
        .Cells(3, 42) = 0 'Npacch
        .Range("AL5:AR54").ClearContents
        .Range("AJ5:AJ54").ClearContents
        .Cells(3, 47) = 0 'Nbarre
        .Range("AT5:AW200").ClearContents
        .Cells(106, 26) = 0 'n∞ polig sezione parzializzata
        .Cells(107, 24) = 0 'n vertici
        .Cells(107, 26) = 0 'n vertici
        .Cells(107, 28) = 0 'n vertici
        .Cells(107, 30) = 0 'n vertici
        .Cells(107, 32) = 0 'n vertici
        .Range("W109:AF200").ClearContents
        '2.2 Composito FRP rinforzo a flessione e taglio
        .Range("A87:A88").ClearContents
        .Range("A91:A94").ClearContents
        .Range("A96:A97").ClearContents
        '2.3 Composito FRP confinamento
        .Range("A101:A103").ClearContents
        .Cells(104, 1) = 0
        .Cells(106, 1) = ""
        '2.4 Confinamento e rinforzo a taglio con calastrelli
        .Range("E101:E103").ClearContents
        .Cells(106, 5) = ""
        '3. MATERIALI
        '3.1 Cls e acciaio
        .Cells(19, 1) = "" 'Rck
        .Cells(19, 3) = "" 'classe cls
        .Cells(18, 1) = "" 'tipo acciaio
        .Cells(62, 1) = "" 'Es
        .Cells(23, 8) = "" 'n
        .Range("h9:h22").ClearContents 'Ec,Sigca,TauC0,TauC1,fcm ...,fyk,fyd
        .Cells(24, 8) = True 'diagramma acciaio
        .Cells(25, 8) = False
        .Cells(26, 8) = 6.75 'Eps_su
        .Cells(27, 8) = 1.2 'k
        .Cells(29, 8) = "" 'fyko
        .Cells(60, 1) = 1.5 'Gammac
        .Cells(61, 1) = 1.15 'Gammas
        .Cells(65, 1) = True 'diagramma cls parab-rettang
        .Cells(66, 1) = False
        .Cells(67, 1) = False
        .Cells(63, 1) = "" 'Eps_cu
        .Cells(64, 1) = "" 'Eps_c2
        .Cells(63, 3) = "" 'Eps_c3
        .Cells(64, 3) = "" 'Eps_c4
        '3.2 Acciaio esistente
        .Range("J72:J75").ClearContents
        '3.3 cls fifrorinforzato
        .Range("A72:A75").ClearContents
        .Cells(76, 1) = True
        .Cells(77, 1) = False
        .Cells(78, 1) = False
        '3.4 Composito FRP
        .Range("A83:A85").ClearContents
        .Range("E84:E93").ClearContents
        '3.5 Acciaio per angolari e calastrelli
        .Range("E72:E77").ClearContents
        '4. SOLLECITAZIONI
        .Cells(11, 1) = ""
        .Cells(17, 1) = ""
        .Cells(27, 1) = ""
        .Range("A30:A32").ClearContents
        .Range("G34:I36").ClearContents
        '5. STABILITA' ASTA
        .Range("A39:A39").ClearContents
        .Range("A47:A48").ClearContents
        .Range("A51:A52").ClearContents
        .Range("C51:C52").ClearContents
        '6. ALTRI DATI
        .Cells(9, 14) = True 'zona sism
        .Cells(10, 14) = False 'zona non sism
        .Cells(11, 14) = True 'CDA
        .Cells(11, 16) = False 'CDB
        .Cells(35, 1) = "" 'dfp
        .Cells(34, 1) = 30 'Pmax
        .Cells(40, 1) = 3 'sLmin
        .Cells(41, 1) = 0.5 'Mu_
        .Cells(14, 14) = 8 'diam armatura a taglio
        .Cells(13, 14) = 45 'Teta_ta
        .Cells(15, 14) = "" 'Pst_ta
        .Cells(16, 14) = 90 'Alfa_ta
        .Cells(17, 14) = 2 'n. braccia
        .Cells(18, 14) = 2
        .Cells(20, 14) = "" 'Alo torsione
        .Cells(21, 14) = 8 'diam armatura a torsione
        .Cells(22, 14) = ""
        .Cells(23, 14) = 90
        .Range("L27:L31").ClearContents 'dati per diagramma curvatura
        .Cells(42, 1) = "" 'sez in c.a.p. deformazione inziale armatura Eps0
        '7. VERIFICHE SLE
        .Cells(37, 6) = "Ordinarie"
        .Cells(38, 6) = "Armature poco sensibili"
        .Cells(39, 6) = 60
        .Cells(40, 6) = 45
        .Cells(41, 6) = 80
        .Cells(44, 6) = False
        .Cells(45, 6) = True
        .Cells(46, 6) = 1
        '9.relazione di calcolo
        .Range("H3:H5").ClearContents
    End With
    'cancella disegno sezione precedente
    Foglio6.Activate
    ActiveSheet.Shapes.SelectAll
    Selection.Delete
    'Ricrea la barra strumenti in modo da disattivare men˘
    Foglio2.Cells(1, 8) = True
    Application.CommandBars("PERS").Delete
    CreaBarraProgramma
    Foglio1.Activate
End If
End Sub

Sub SettaFg1xoutput()
iF1pr = Foglio2.Cells(4, 1)
Foglio1.Activate
Foglio1.Range("a3:i" & iF1pr).Select
    Selection.ClearContents
    Selection.Font.Bold = False
    Selection.Font.Size = Hcaratt
    Selection.Font.Italic = False
    Selection.Font.Underline = xlUnderlineStyleNone
    Selection.Font.ColorIndex = 0
    Selection.Font.Name = TipoCaratt
    Selection.HorizontalAlignment = xlLeft
    'Selection.VerticalAlignment = xlBottom
    'Selection.WrapText = False
    'Selection.Orientation = 0
    'Selection.AddIndent = False
    'Selection.ShrinkToFit = False
    'Selection.MergeCells = False
End Sub

Sub FormattaCella(Grass As Boolean, TipoCaratt As String, AltezCaratt As Integer, Corsivo As Boolean, Sottolineato As Boolean, N∞colore As Integer, TestoaCapo As Boolean, UnisciCelle As Boolean)
If Sottolineato = True Then Selection.Font.Underline = xlUnderlineStyleSingle
Selection.Font.Bold = Grass
Selection.Font.Italic = Corsivo
Selection.Font.ColorIndex = N∞colore
Selection.MergeCells = UnisciCelle
Selection.WrapText = TestoaCapo
With Selection.Font
    .Name = TipoCaratt
    .Size = AltezCaratt
End With
End Sub

Sub DefinisciUnit‡Misura()
umL = " cm"
umL2 = " cmq"
umL3 = " cm^3"
umL4 = " cm^4"
umDiamTond = " mm"
If SistemaTecnico Then
    'unit‡ di esecuzione: kg e cm
    umForze = " kg"
    umMomenti = " kg*m"
    umTens = " kg/cmq"
    fmF = 1
    fmFL = 100
    fmFL_2 = 1
    fmL = 1
    fmL2 = 1
    fmL3 = 1
    fmL4 = 1
    fmDiamTond = 0.1 'da mm a cm
    'fattore di conversione unit‡ esecuzione ST a unit‡ esecuzione sistema assunto (es kg a kg)
    fcUM = 1
    fc1 = 0.0981  'da unit‡ esec tens a N/mmq
    fc3 = 10 'da unit‡ di esecuzione Lstr a mm
Else
    'unit‡ di esecuzione: N e mm
    umForze = " kN"
    umMomenti = " kN*m"
    umTens = " N/mmq"
    fmF = 1000 'da kN (input) a N (esecuzione)
    fmFL = 1000000 'da kN*m (input) a N*mm (esecuzione)
    fmFL_2 = 1
    fmL = 10 'da cm (input) a mm (esecuzione)
    fmL2 = 100 'da cm2 (input) a mm2 (esecuzione)
    fmL3 = 1000
    fmL4 = 10000
    fmDiamTond = 1
    'fattore di conversione unit‡ esecuzione ST a unit‡ esecuzione sistema assunto (es kg a N)
    fcUM = 10
    fc1 = 1  'da unit‡ esec tens a N/mmq
    fc3 = 1 'da unit‡ di esecuzione Lstr a mm
End If
End Sub
