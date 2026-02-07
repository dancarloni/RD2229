Attribute VB_Name = "CA_SLE"
Option Explicit
Dim Beta1#, Beta2#
Dim Delt_s#, Delt_smax
Dim Eps_sm#
Dim Fi#
Dim k2#, k1#, kt#, k3#, k4#
Dim Mf#
Dim Ro_eff#
Dim Sig_s#, S#, Sig_sr#
Dim wa#, wd#

Sub VerificheSLE() '9.
'verifiche che per definizione sono solo con le NTC2008 e NTC2018
Dim Af_eff#
Dim Curv1#, Curv#, Curv2#, Coeff1#, Coeff2#
Dim I11#, I22#
Dim l_lim#
Dim Nx_c#, Nx_f#, Nx_qp#, Ntt%
Dim My_c#, My_f#, My_qp#, Mz_c#, Mz_f#, Mz_qp#
Dim Ro#, Ropr#
Dim Sig1#, Sig2#, Sigc_c#, Sigf_c#, Sigc_qp#, Sig#
Dim StadioI As Boolean
'1)INPUT
If Foglio2.Cells(34, 7) = "" Then Nx_c = 0 Else Nx_c = Foglio2.Cells(34, 7) * fmF 'caratteristica
If Foglio2.Cells(35, 7) = "" Then My_c = 0 Else My_c = Foglio2.Cells(35, 7) * fmFL
If Foglio2.Cells(36, 7) = "" Then Mz_c = 0 Else Mz_c = Foglio2.Cells(36, 7) * fmFL
If Foglio2.Cells(34, 8) = "" Then Nx_f = 0 Else Nx_f = Foglio2.Cells(34, 8) * fmF 'frequente
If Foglio2.Cells(35, 8) = "" Then My_f = 0 Else My_f = Foglio2.Cells(35, 8) * fmFL
If Foglio2.Cells(36, 8) = "" Then Mz_f = 0 Else Mz_f = Foglio2.Cells(36, 8) * fmFL
If Foglio2.Cells(34, 9) = "" Then Nx_qp = 0 Else Nx_qp = Foglio2.Cells(34, 9) * fmF 'quasi perman
If Foglio2.Cells(35, 9) = "" Then My_qp = 0 Else My_qp = Foglio2.Cells(35, 9) * fmFL
If Foglio2.Cells(36, 9) = "" Then Mz_qp = 0 Else Mz_qp = Foglio2.Cells(36, 9) * fmFL
'2)DATI CHE SERVONO A PIU' VERIFICHE O PREMILINARI
Beta1 = 1 'siamo con le NTC con barre sempre ad aderenza migliorata
k2 = 0.4
k1 = 0.8
'carichi breve/lunga durata
If blnCarichiBrevi Then
    Beta2 = 1
    kt = 0.6
Else
    Beta2 = 0.5 'effetti della viscosità
    kt = 0.4
End If
'calcolo momento di fessurazione
DatiSezioneCA '4.1
Mf = fctm * Iy / (H - zG_pr)
'3)VERIFICA ALLO SLE FESSURAZIONE
'3.1 Primi output
With Foglio1
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "VERIFICA ALLO S.L.E. DI FESSURAZIONE"
    If MetodoFess1996 Then
        .Cells(iF1 + 1, 1) = "coeff. barre ad aderenza migliorata,   k2=" & k2
    ElseIf MetodoFess2008 Then
        .Cells(iF1 + 1, 1) = "coeff. barre ad aderenza migliorata,   k1=" & k1
    End If
    .Cells(iF1 + 2, 1) = "coeff. barre ad aderenza migliorata,   beta1=" & Beta1
    If blnCarichiBrevi Then
        .Cells(iF1 + 3, 1) = "coeff. per carichi di breve durata,   beta2=" & Beta2
    Else
        .Cells(iF1 + 3, 1) = "coeff. per carichi di lunga durata o ciclici (viscosità),   beta2=" & Beta2
    End If
    .Cells(iF1 + 4, 1) = "momento di fessurazione della sezione,   Mf=" & FormatNumber(Mf / fmFL, 2, , , vbTrue) & umMomenti
    iF1 = iF1 + 5
End With
'3.2 Condizioni ambientali ordinarie
If CondizAmb = "Ordinarie" Then
    '3.2.1 combinazione frequente >> Stato limite di apertura delle fessure
    'valore ammissibile fessure
    If SensibArmat = "Armature sensibili" Then
        wa = 0.03 * fmL 'cm
    ElseIf SensibArmat = "Armature poco sensibili" Then
        wa = 0.04 * fmL
    End If
    'valore di calcolo apertura fessure
    Calcolo_wd Nx_f, My_f, Mz_f '9.1
    'output
    With Foglio1
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "1) Combinazione di carico frequente"
        .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di apertura delle fessure"
        iF1 = iF1 + 2
        Out_wd
    End With
    '3.2.2 combinazione quasi permanente >> Stato limite di apertura delle fessure
    'valore ammissibile fessure
    If SensibArmat = "Armature sensibili" Then
        wa = 0.02 * fmL 'cm
    ElseIf SensibArmat = "Armature poco sensibili" Then
        wa = 0.03 * fmL
    End If
    'valore di calcolo apertura fessure
    Calcolo_wd Nx_qp, My_qp, Mz_qp
    'output
    With Foglio1
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "2) Combinazione di carico quasi permanente"
        .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di apertura delle fessure"
        iF1 = iF1 + 2
        Out_wd
        iF1 = iF1 + 1
    End With
'3.3 Condizioni ambientali aggressive
ElseIf CondizAmb = "Aggressive" Then
    '3.3.1 combinazione frequente >> Stato limite di apertura delle fessure
    'valore ammissibile fessure
    If SensibArmat = "Armature sensibili" Then
        wa = 0.02 * fmL 'cm
    ElseIf SensibArmat = "Armature poco sensibili" Then
        wa = 0.03 * fmL
    End If
    'valore di calcolo apertura fessure
    Calcolo_wd Nx_f, My_f, Mz_f
    'output
    With Foglio1
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
        .Cells(iF1, 1) = "1) Combinazione di carico frequente"
        .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di apertura delle fessure"
        iF1 = iF1 + 2
        Out_wd
    End With
    '3.3.2 combinazione quasi permanente
    If SensibArmat = "Armature sensibili" Then '>>Stato Limite di decompressione
        ClsResistTraz = True
        CalcoloTensNormali Nx_qp, My_qp, Mz_qp, True '4.3
        Sig1 = Sigc_max
        Sig2 = Sigc_min
        With Foglio1
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
            .Cells(iF1, 1) = "2) Combinazione di carico quasi permanente"
            .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di decompressione"
            .Cells(iF1 + 2, 1) = "tensione massima nel cls (con segno) = " & FormatNumber(Sig1 / fmFL_2, 1, , , vbTrue) & umTens
            .Cells(iF1 + 3, 1) = "tensione minima nel cls (con segno) = " & FormatNumber(Sig2 / fmFL_2, 1) & umTens
            If Sig1 <= 0 Then
                .Cells(iF1 + 4, 1) = "Verifica di fessurazione soddisfatta"
            Else
                .Cells(iF1 + 4, 1).Select
                FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                .Cells(iF1 + 4, 1) = "Verifica di fessurazione non soddisfatta"
            End If
            iF1 = iF1 + 5
        End With
    ElseIf SensibArmat = "Armature poco sensibili" Then '>>Stato Limite apertura delle fessure
        wa = 0.02 * fmL
        Calcolo_wd Nx_qp, My_qp, Mz_qp
        'output
        With Foglio1
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
            .Cells(iF1, 1) = "2) Combinazione di carico quasi permanente"
            .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di apertura delle fessure"
            iF1 = iF1 + 2
            Out_wd
        End With
    End If
    iF1 = iF1 + 1
'3.4 Condiz ambientali molto aggressive
ElseIf CondizAmb = "Molto aggressive" Then
    '3.4.1 combinazione frequente
    If SensibArmat = "Armature sensibili" Then '>>Stato Limite di formazione delle fessure
        ClsResistTraz = True
        CalcoloTensNormali Nx_f, My_f, Mz_f, True '4.3
        Sig1 = Sigc_max
        Sig2 = Sigc_min
        With Foglio1
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
            .Cells(iF1, 1) = "1) Combinazione di carico frequente"
            .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di formazione delle fessure"
            .Cells(iF1 + 2, 1) = "tensione di trazione ammissib. = fctm/1,2 = " & FormatNumber(fctm / 1.2 / fmFL_2, 1, , , vbTrue) & umTens
            .Cells(iF1 + 3, 1) = "tensione massima nel cls (con segno) = " & FormatNumber(Sig1 / fmFL_2, 1, , , vbTrue) & umTens
            .Cells(iF1 + 4, 1) = "tensione minima nel cls (con segno) = " & FormatNumber(Sig2 / fmFL_2, 1, , , vbTrue) & umTens
            If Sig1 < fctm / 1.2 Then
                .Cells(iF1 + 5, 1) = "Verifica di fessurazione soddisfatta"
            Else
                .Cells(iF1 + 5, 1).Select
                FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                .Cells(iF1 + 5, 1) = "Verifica di fessurazione non soddisfatta"
            End If
            iF1 = iF1 + 6
        End With
    ElseIf SensibArmat = "Armature poco sensibili" Then '>>Stato Limite di apertura delle fessure
        wa = 0.02 * fmL
        Calcolo_wd Nx_f, My_f, Mz_f
        'output
        With Foglio1
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
            .Cells(iF1, 1) = "1) Combinazione di carico frequente"
            .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di apertura delle fessure"
            iF1 = iF1 + 2
            Out_wd
        End With
    End If
    '3.4.2 combinazione quasi permanente
    If SensibArmat = "Armature sensibili" Then '>>Stato Limite di decompressione
        ClsResistTraz = True
        CalcoloTensNormali Nx_qp, My_qp, Mz_qp, True '4.3
        Sig1 = Sigc_max
        Sig2 = Sigc_min
        With Foglio1
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
            .Cells(iF1, 1) = "2) Combinazione di carico quasi permanente"
            .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di decompressione"
            .Cells(iF1 + 2, 1) = "tensione massima nel cls (con segno) = " & FormatNumber(Sig1 / fmFL_2, 1, , , vbTrue) & umTens
            .Cells(iF1 + 3, 1) = "tensione minima nel cls (con segno) = " & FormatNumber(Sig2 / fmFL_2, 1, , , vbTrue) & umTens
            If Sig1 <= 0 Then
                .Cells(iF1 + 4, 1) = "Verifica di fessurazione soddisfatta"
            Else
                .Cells(iF1 + 4, 1).Select
                FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
                .Cells(iF1 + 4, 1) = "Verifica di fessurazione non soddisfatta"
            End If
            iF1 = iF1 + 5
        End With
    ElseIf SensibArmat = "Armature poco sensibili" Then '>>Stato Limite di apertura delle fessure
        wa = 0.02 * fmL
        Calcolo_wd Nx_qp, My_qp, Mz_qp
        'output
        With Foglio1
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
            .Cells(iF1, 1) = "2) Combinazione di carico quasi permanente"
            .Cells(iF1 + 1, 1) = "Stato Limite da considerare: Stato Limite di apertura delle fessure"
            iF1 = iF1 + 2
            Out_wd
        End With
    End If
    iF1 = iF1 + 1
End If
'4)VERIFICA ALLE TENSIONI DI ESERCIZIO
ClsResistTraz = False
'4.1)combinazione caratteristica o rara
CalcoloTensNormali Nx_c, My_c, Mz_c, True '4.3
Sigc_c = Sigc
Sigf_c = Sigf
'4.2)combinazione quasi permanente
CalcoloTensNormali Nx_qp, My_qp, Mz_qp, True '4.3
Sigc_qp = Sigc
'4.3 output
With Foglio1
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "VERIFICA ALLO S.L.E. DELLE TENSIONI DI ESERCIZIO"
    .Cells(iF1 + 1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1 + 1, 1) = "1) Combinazione di carico caratteristica o rara"
    .Cells(iF1 + 2, 1) = "tens. ammiss. nel cls = " & Perc_cls_c & "% di fck = " & FormatNumber(Perc_cls_c / 100 * fck / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 3, 1) = "tens. ammiss. nell'acciaio = " & Perc_acc_c & "% di fyk = " & FormatNumber(Perc_acc_c / 100 * fyk / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 4, 1) = "tens. massima di compress. nel cls = " & FormatNumber(Abs(Sigc_c) / fmFL_2, 2, , , vbTrue) & umTens
    iF1 = iF1 + 5
    If CemFRC Then
        .Cells(iF1, 1) = "tens. massima di trazione nel cls = " & FormatNumber(Sigc_pos / fmFL_2, 2, , , vbTrue) & umTens
        iF1 = iF1 + 1
    End If
    .Cells(iF1, 1) = "tens. massima nell'acciaio = " & FormatNumber(Sigf_c / fmFL_2, 2, , , vbTrue) & umTens
    If Abs(Sigc_c) < Perc_cls_c / 100 * fck And Sigf_c < Perc_acc_c / 100 * fyk Then
        .Cells(iF1 + 1, 1) = "Verifica alle tensioni di esercizio soddisfatta"
    Else
        .Cells(iF1 + 1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
        .Cells(iF1 + 1, 1) = "Verifica alle tensioni di esercizio non soddisfatta"
    End If
    .Cells(iF1 + 2, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1 + 2, 1) = "2) Combinazione di carico quasi permanente"
    .Cells(iF1 + 3, 1) = "tens. ammiss. nel cls = " & Perc_cls_qp & "% di fck = " & FormatNumber(Perc_cls_qp / 100 * fck / fmFL_2, 2, , , vbTrue) & umTens
    .Cells(iF1 + 4, 1) = "tens. massima di compress. nel cls = " & FormatNumber(Abs(Sigc_qp) / fmFL_2, 2, , , vbTrue) & umTens
    If Abs(Sigc_qp) < Perc_cls_qp / 100 * fck Then
        .Cells(iF1 + 5, 1) = "Verifica alle tensioni di esercizio soddisfatta"
    Else
        .Cells(iF1 + 5, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
        .Cells(iF1 + 5, 1) = "Verifica alle tensioni di esercizio non soddisfatta"
    End If
    iF1 = iF1 + 7
End With
'5)VERIFICA STATO LIMITE DI DEFORMAZIONE
'5.1 curvatura della sezione
ClsResistTraz = True
CalcoloTensNormali 0, My_qp, 0, True '4.3    si ottiene I11 e Sigc_max
I11 = Iy
Curv1 = My_qp / (Ec * I11)
If Sigc_max <= fctm Then 'Stato I non fessurato
    StadioI = True
    Curv = Curv1
Else 'Stato II fessurato
    StadioI = False
    ClsResistTraz = False
    CalcoloTensNormali 0, My_qp, 0, True '4.3    si ottiene I22
    I22 = Iy
    Curv2 = My_qp / (Ec * I22)
    If My_qp <> 0 Then
        Coeff1 = Beta1 * Beta2 * (Mf / My_qp) ^ 2
        Coeff2 = 1 - Beta1 * Beta2 * (Mf / My_qp) ^ 2
        Curv = Curv1 * Coeff1 + Curv2 * Coeff2
    Else
        Curv = 0
    End If
End If
'calcolo armatura tesa
Sig = Sig_fi(1)
Ntt = 0
Af_eff = 0
If Sig_fi(1) > 0 Then
    Ntt = Ntt + 1
    Af_eff = Af_eff + PiGreco * Db(1) ^ 2 / 4
End If
For i = 2 To Nbar Step 1
    If Sig_fi(i) > 0 Then
        Ntt = Ntt + 1
        Af_eff = Af_eff + PiGreco * Db(i) ^ 2 / 4
    End If
Next i
'5.2 snellezza limite superata la quale occorre fare verifica alle deformaz.
Ro = Af_eff / Asez
Ropr = (Aft - Af_eff) / Asez
l_lim = KK * (11 + 0.0015 * (fck * fc1) / (Ro + Ropr)) * (500 * Af_eff / ((fyk * fc1) * Aft))
'5.3 output
With Foglio1
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
    .Cells(iF1, 1) = "VERIFICA ALLO S.L.E. DI DEFORMAZIONE"
    .Cells(iF1 + 1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1 + 1, 1) = "Curvatura della sezione (combinazione di carico quasi permanente)"
    .Cells(iF1 + 2, 1) = "momento d'inerzia rispetto all'asse y dell'intera sezione reagente,   I1=" & FormatNumber(I11 / fmL4, 1, , , vbTrue) & umL4
    iF1 = iF1 + 3
    If StadioI Then
        .Cells(iF1, 1) = "curvatura della sezione (Stadio 1 non fessurato) = " & Round(Curv / (1 / fmL), 10) & "    1/" & umL
        iF1 = iF1 + 1
    Else
        .Cells(iF1, 1) = "momento d'inerzia rispetto all'asse y della sezione reagente fessurata,   I2=" & FormatNumber(I22 / fmL4, 1, , , vbTrue) & umL4
        .Cells(iF1 + 1, 1) = "curvatura della sezione (Stadio 1 non fessurato),   Curv1=" & Round(Curv1 / (1 / fmL), 10) & "    1/" & umL
        .Cells(iF1 + 2, 1) = "curvatura della sezione (Stadio 2 fessurato),   Curv2=" & Round(Curv2 / (1 / fmL), 10) & "    1/" & umL
        .Cells(iF1 + 3, 1) = "coefficiente 1 per calcolo curvatura complessiva = " & Round(Coeff1, 4)
        .Cells(iF1 + 4, 1) = "coefficiente 2 per calcolo curvatura complessiva = " & Round(Coeff2, 4)
        .Cells(iF1 + 5, 1) = "curvatura della sezione,   Curv=Curv1*c1+Curv2*c2=" & Round(Curv / (1 / fmL), 10) & "    1/" & umL
        iF1 = iF1 + 6
    End If
    .Cells(iF1, 1).Select
    FormattaCella True, TipoCaratt, Hcaratt, False, False, 0, False, False
    .Cells(iF1, 1) = "Snellezza limite al di sotto della quale non occorre verifica di deformazione"
    '.Cells(iF1 + 2, 1) = "coeff. K sistema strutturale (Tab. C4.1.I Circolare 2009) = " & KK
    .Cells(iF1 + 1, 1) = "snellezza limite = " & Round(l_lim, 1)
    iF1 = iF1 + 3
End With
End Sub

Sub Calcolo_wd(Nx#, My#, Mz#) '9.1
Dim Af_eff#, Ac_eff#, Alfa_e#
Dim b_eff#
Dim Delt_smax2#
Dim h_eff#
Dim Ntt%
Dim Pos%
Dim Sig#
Dim s1#, s2#
'1. calcolo Sig_s e coeff. k3 e k4
ClsResistTraz = False
CalcoloTensNormali Nx, My, Mz, True '4.3
If Sigf_max > 0 Then Sig_s = Sigf_max Else Sig_s = 0
If Sigc_min <= 0 Then
    k3 = 0.125
    k4 = 0.5
Else
    k3 = 0.25 * (Sigc_max + Sigc_min) / (2 * Sigc_max)
    k4 = (Sigc_max + Sigc_min) / (2 * Sigc_max)
End If
'2. diametro delle barre tese e loro interasse. Calcolo del n° barre tese e corrisp area
Sig = Sig_fi(1)
Fi = Db(1)
Pos = 1
Ntt = 0
Af_eff = 0
If Sig_fi(1) > 0 Then
    Ntt = Ntt + 1
    Af_eff = Af_eff + PiGreco * Db(1) ^ 2 / 4
End If
For i = 2 To Nbar Step 1
    If Sig_fi(i) > 0 Then
        Ntt = Ntt + 1
        Af_eff = Af_eff + PiGreco * Db(i) ^ 2 / 4
    End If
    If Sig_fi(i) > Sig Then
        Sig = Sig_fi(i)
        Fi = Db(i)
        Pos = i 'posizione della barra maggiormente tesa
    End If
Next i
If Pos > 1 And Pos < Nbar Then
    s1 = ((Zb_pr(Pos) - Zb_pr(Pos - 1)) ^ 2 + (Yb_pr(Pos) - Yb_pr(Pos - 1)) ^ 2) ^ 0.5
    s2 = ((Zb_pr(Pos) - Zb_pr(Pos + 1)) ^ 2 + (Yb_pr(Pos) - Yb_pr(Pos + 1)) ^ 2) ^ 0.5
    S = Application.Min(s1, s2)
ElseIf Pos = 1 Then
    S = ((Zb_pr(Pos) - Zb_pr(Pos + 1)) ^ 2 + (Yb_pr(Pos) - Yb_pr(Pos + 1)) ^ 2) ^ 0.5
ElseIf Pos = Nbar Then
    S = ((Zb_pr(Pos) - Zb_pr(Pos - 1)) ^ 2 + (Yb_pr(Pos) - Yb_pr(Pos - 1)) ^ 2) ^ 0.5
End If
'3. calcolo Ro_eff
If FormSez = "Generica" Then
    Cf = Application.Max(Zs_pr()) - Zb_pr(Pos)
End If
h_eff = Application.Min(2.5 * (Cf + Fi / 2), H / 2, (H - xx) / 3)
If Ntt > 0 Then
    b_eff = (Ntt - 1) * S + 2 * (Cf + Fi / 2)
    Ac_eff = h_eff * b_eff
    Ro_eff = Af_eff / Ac_eff
Else
    b_eff = 0
    Ro_eff = 0
End If
'4. calcolo wd
If MetodoFess1996 Then
    'calcolo Sig_sr
    ClsResistTraz = False
    CalcoloTensNormali 0, Mf, 0, True '4.3
    If Sigf_max > 0 Then Sig_sr = Sigf_max Else Sig_sr = 0
    'Eps_sm
    If Sig_s <> 0 Then
        Eps_sm = Sig_s / Es * (1 - Beta1 * Beta2 * (Sig_sr / Sig_s) ^ 2)
    Else
        Eps_sm = 0
    End If
    If Eps_sm < 0.4 * Sig_s / Es Then Eps_sm = 0.4 * Sig_s / Es
    'calcolo della distanza media tra le fessure
    If Ro_eff <> 0 Then
        Delt_s = 2 * (Cf + S / 10) + k2 * k3 * Fi / Ro_eff
    Else
        Delt_s = 0
    End If
    'calcolo wd
    wd = 1.7 * Eps_sm * Delt_s
ElseIf MetodoFess2008 Then
    'Eps_sm
    Alfa_e = Es / Ec
    If Ro_eff <> 0 Then
        Eps_sm = (Sig_s - kt * fctm / Ro_eff * (1 + Alfa_e * Ro_eff)) / Es
    Else
        Eps_sm = 0
    End If
    If Eps_sm < 0.6 * Sig_s / Es Then Eps_sm = 0.6 * Sig_s / Es
    'calcolo della distanza max tra le fessure
    If Ro_eff <> 0 Then
        Delt_smax = 3.4 * Cf + 0.425 * k1 * k4 * Fi / Ro_eff
    Else
        Delt_smax = 0
    End If
    If S > 5 * (Cf + Fi / 2) Then
        Delt_smax2 = 1.3 * (H - xx)
        Delt_smax = Application.Max(Delt_smax, Delt_smax2)
    End If
    wd = Eps_sm * Delt_smax
End If
End Sub

Sub Out_wd() '9.2
With Foglio1
    .Cells(iF1, 1) = "ampiezza ammissibile di apertura delle fessure,   wa=" & wa * 10 & " mm"
    .Cells(iF1 + 1, 1) = "copriferro,   Cf=" & Cf / fmL & umL
    .Cells(iF1 + 2, 1) = "interasse tra le armature tese,   s=" & Round(S / fmL, 2) & umL
    .Cells(iF1 + 3, 1) = "diametro le armature tese,   Fi=" & Fi / fmDiamTond & " mm"
    .Cells(iF1 + 4, 1) = "tensione di trazione nelle armature tese,   Sigs=" & Round(Sig_s / fmFL_2, 1) & umTens
    .Cells(iF1 + 5, 1) = "rapporto armatura efficace,   Ro_eff=" & Round(Ro_eff, 3)
    If MetodoFess1996 Then
        .Cells(iF1 + 6, 1) = "coeff. funzione della sollecitazione in sezione,   k3=" & Round(k3, 4)
        .Cells(iF1 + 7, 1) = "tensione di trazione armature soggette a momento di fessuraz.,   Sig_sr=" & FormatNumber(Sig_sr / fmFL_2, 1, , , vbTrue) & umTens
        .Cells(iF1 + 8, 1) = "distanza media tra le fessure,   Delt_s=" & Round(Delt_s / fmL, 2) & umL
        iF1 = iF1 + 9
    ElseIf MetodoFess2008 Then
        .Cells(iF1 + 6, 1) = "coeff. funzione della sollecitazione in sezione,   k4=" & Round(k4, 4)
        .Cells(iF1 + 7, 1) = "distanza massima tra le fessure,   Delt_max=" & Round(Delt_smax / fmL, 2) & umL
        iF1 = iF1 + 8
    End If
    .Cells(iF1, 1) = "deformaz. unitaria media delle barre di armatura,   Eps_sm=" & Round(Eps_sm, 7)
    .Cells(iF1 + 1, 1) = "valore di calcolo di apertura delle fessure,   wd=" & Round(wd / fmL * 10, 3) & " mm"
    If wd <= wa Then
        .Cells(iF1 + 2, 1) = "Verifica di fessurazione soddisfatta"
    Else
        .Cells(iF1 + 2, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
        .Cells(iF1 + 2, 1) = "Verifica di fessurazione non soddisfatta"
    End If
    iF1 = iF1 + 3
End With
End Sub
