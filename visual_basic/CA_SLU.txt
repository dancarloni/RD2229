Attribute VB_Name = "CA_SLU"
Option Explicit
Const N1 = 24 'n∞ punti del dominio di rottura My-Mz
Dim Approssimaz#
Dim AsseNeutroTrovato As Boolean, A_frp#
Dim dd#, Delta1#
Dim Deltz1#, Deltz# 'spessore degli straterelli di cls in cui si divide la parte compressa della sezione
Dim Eps_fi#, Eps_ci#, Eps_frp#, Eps_yd2# ', Eps0#
Dim fyd2#
Dim Hc 'copia di H
Dim Myu#, Mzu#, My_
Dim Nu#, Nu_max#, Nu_min#, Nx_
Dim Ns%
Dim Sig_fi#, Sig_ci#
Dim SnellLim#
Dim x#, x23#, x34#
Dim VerifCarPunta As Boolean
Dim Zs_min#, Zs_max#, Ybc#(), Zbc#(), Yfrp_c#, Zfrp_c#, Zbc_min#, Zbc_max#, Zb_max#
Dim zci#, yci#

Sub VerifResistCA_SLU_TensNorm() '4.7
'per una sez in c.a. di forma qualunque soggetta a Nx,My,Mz effettua la verifica allo SLU (tensioni normali) costruendo il dominio
'di rottura Nx-My (caso di sollecitaz piane) o My-Mz (caso sollecitaz spaziale)
Dim Af_ord#
Dim Ecc#, i%, i1%, j%
Dim Nx_i#, Nx_i1#
Dim PrimaRiga As Byte
Dim My_i#, Mz_i#, My_i1#, Mz_i1#
Dim m#, q#, Mzu#(), Mzu_s#, Mzu_i#
Dim MRy_s#, MRy_i#, MRz_s#, MRz_i#, MRz#, MRy#, Myu#()
Dim Myu_max#, Myu_min#
Dim x1#, x2#
'1. sollecitazioni di progetto (in alcuni casi possono diferire da quelle che derivano dalla risoluzione della struttura)
Ned = Nx
Medy = My
Medz = Mz
If Pilastro And My = 0 And Mz = 0 And Nx < 0 Then 'per i pilastri soggetti a compressione assiale inserisci un momento fittizio
    If MetodoSL08 Then
        Ecc = 0.05 * H
    ElseIf MetodoSL18 And blnVerifCarPunta Then
        Ecc = Application.Max(Beta_y * L, Beta_z * L) / 200
    End If
    If Ecc < 2 * fmL Then Ecc = 2 * fmL
    Medy = Nx * Ecc
End If
'2. input e impostazioni
'coordinate barre rispetto al sistema yz baricentrico della sezione omogeneizzata
If Nbar > 0 Then ReDim Zb#(1 To Nbar), Yb#(1 To Nbar)
For i = 1 To Nbar Step 1
    Zb(i) = Zb_pr(i) - zG_pr
    Yb(i) = Yb_pr(i) - yG_pr
Next i
'coordinate baricentro composito frp rispetto al sistema yz baricentrico della sezione omogeneizzata
If RinfFRP Then
    A_frp = B_frp * H_frp
    Zfrp_pr = H
    Yfrp_pr = B / 2
    Zfrp = Zfrp_pr - zG_pr
    Yfrp = Yfrp_pr - yG_pr
End If
'approssimazione
If blnParabRettang Then
    Approssimaz = 50 * fcUM 'kg
ElseIf blnTriangRettang Or blnStressBlock Then
    Approssimaz = 200 * fcUM
End If
Deltz1 = 0.2 * fmL 'spessore di 2 mm circa degli straterelli di cls in cui si divide la parte compressa della sezione
VerifCarPunta = False
'acciaio ordinario in trave in c.a.p.
fyd2 = fyk2 / Gammas
Eps_yd2 = fyd2 / Es
'3. DETERMINA VALORI ESTREMI SFORZO NORMALE
If CemArmOrd Then
    '3.1 calcolo massima resistenza a trazione Nu_max
    If CemFRC Then
        If Eps_Fu <= Eps_su Then
            Nu_max = fFtu * Asez + Aft * f_Sigf(Eps_Fu)
        Else
            Nu_max = f_Sigc(Eps_su) * Asez + Aft * fyd
        End If
    ElseIf RinfFRP Then
        If Eps_pu <= Eps_su Then
            Nu_max = (Eps_pu * E_frp) * A_frp + Aft * f_Sigf(Eps_pu)
        Else
            Nu_max = (Eps_su * E_frp) * A_frp + Aft * fyd
        End If
    Else
        Nu_max = Aft * fyd
    End If
    '3.2 calcolo massima resistenza a compressione Nu_min
    If blnConfinStaffe Then
        Nu_min = -fcd_c * (Asez - Psez * Cf) - fcd * (Psez * Cf) - Aft * f_Sigf(Eps_c2c) 'occorre togliere area del copriferro, esterna al confinamento
    ElseIf blnConfinFRP Or blnConfinCamicieAcc Then
        Nu_min = -fccd * Asez - Aft * f_Sigf(Eps_c2c)
    Else
        Nu_min = -fcd * Asez - Aft * f_Sigf(Eps_c2)
    End If
ElseIf CemCAP Then
    'ricava l'eventuale armatura ordinaria presente nella sez in c.a.p.
    Af_ord = 0
    For i = 1 To Nbar Step 1
        If TondArmonico(i) = False Then
            Af_ord = Af_ord + PiGreco * Db(i) ^ 2 / 4
        End If
    Next i
    '3.1 calcolo massima resistenza a trazione Nu_max
    If CemFRC Then
        If Eps_Fu <= Eps_su Then
            Nu_max = fFtu * Asez + (Aft - Af_ord) * f_Sigf(Eps_Fu) + Af_ord * f_Sigf2(Eps_Fu)
        Else
            Nu_max = f_Sigc(Eps_su) * Asez + (Aft - Af_ord) * fyd + Af_ord * fyd2
        End If
    ElseIf RinfFRP Then
        If Eps_pu <= Eps_su Then
            Nu_max = (Eps_pu * E_frp) * A_frp + (Aft - Af_ord) * f_Sigf(Eps_pu) + Af_ord * f_Sigf2(Eps_pu)
        Else
            Nu_max = (Eps_su * E_frp) * A_frp + (Aft - Af_ord) * fyd + Af_ord * fyd2
        End If
    Else
        Nu_max = (Aft - Af_ord) * fyd + Af_ord * fyd2
    End If
    '3.2 calcolo massima resistenza a compressione Nu_min
    If blnConfinStaffe Then
        Nu_min = -fcd_c * (Asez - Psez * Cf) - fcd * (Psez * Cf) - (Aft - Af_ord) * f_Sigf(Eps_c2c - Eps0) - Af_ord * f_Sigf2(Eps_c2c)
    ElseIf blnConfinFRP Or blnConfinCamicieAcc Then
        Nu_min = -fccd * Asez - (Aft - Af_ord) * f_Sigf(Eps_c2c - Eps0) - Af_ord * f_Sigf2(Eps_c2c)
    Else
        Nu_min = -fcd * Asez - (Aft - Af_ord) * f_Sigf(Eps_c2 - Eps0) - Af_ord * f_Sigf2(Eps_c2)
    End If
End If
'4. VERIFICA DI RESISTENZA
If Ned <= Nu_max And Ned >= Nu_min Then
    'il dominio Nx-My o My-Mz esiste
    Foglio4.Cells(302, 5) = True
    'pallino rosso in dominio
    Foglio4.Cells(2, 6) = Ned / fmF
    Foglio4.Cells(2, 7) = Medy / fmFL
    Foglio4.Cells(2, 8) = Medz / fmFL
    If SollecPiane = False Then
        'costruisci dominio
        DominioRotturaMyMz '4.7.1
        'verifica analitica
        Myu_max = Application.Max(Foglio4.Range("A302:A325")) * fmFL
        Myu_min = Application.Min(Foglio4.Range("A302:A325")) * fmFL
        If Medy < Myu_min Or Medy > Myu_max Then
            VerifResist = False
        Else
            ReDim Mzu#(1 To 10)
            j = 0
            For i = 1 To N1 Step 1
                If i = N1 Then
                    i1 = 1
                Else
                    i1 = i + 1
                End If
                My_i = Foglio4.Cells(301 + i, 1) * fmFL
                Mz_i = Foglio4.Cells(301 + i, 2) * fmFL
                My_i1 = Foglio4.Cells(301 + i1, 1) * fmFL
                Mz_i1 = Foglio4.Cells(301 + i1, 2) * fmFL
                If (Medy >= My_i1 And Medy <= My_i) Or (Medy >= My_i And Medy <= My_i1) Then
                    j = j + 1
                    'retta che passa per i e i1
                    m = (Mz_i1 - Mz_i) / (My_i1 - My_i)
                    q = Mz_i - m * My_i
                    Mzu(j) = m * Medy + q
                End If
            Next i
            If RinfCamicieCA Then
                Mzu_s = 0.9 * Application.Max(Mzu())
                Mzu_i = 0.9 * Application.Min(Mzu())
            Else
                Mzu_s = Application.Max(Mzu())
                Mzu_i = Application.Min(Mzu())
            End If
            If Medz >= Mzu_i And Medz <= Mzu_s Then
                VerifResist = True
            Else
                VerifResist = False
            End If
        End If
        'calcolo momenti resistenti per presso/tenso flessione retta
        If CalcVerif Then
            'intersezione con asse delle ascisse
            ReDim Mzu#(1 To 10)
            j = 0
            For i = 1 To N1 Step 1
                If i = N1 Then
                    i1 = 1
                Else
                    i1 = i + 1
                End If
                My_i = Foglio4.Cells(301 + i, 1) * fmFL
                Mz_i = Foglio4.Cells(301 + i, 2) * fmFL
                My_i1 = Foglio4.Cells(301 + i1, 1) * fmFL
                Mz_i1 = Foglio4.Cells(301 + i1, 2) * fmFL
                If Mz_i1 <> Mz_i Then
                    If (0 >= Mz_i1 And 0 <= Mz_i) Or (0 >= Mz_i And 0 <= Mz_i1) Then
                        j = j + 1
                        Mzu(j) = -Mz_i * (My_i1 - My_i) / (Mz_i1 - Mz_i) + My_i
                    End If
                End If
            Next i
            MRy_s = Application.Max(Mzu())
            MRy_i = Application.Min(Mzu())
            If Medy >= 0 Then
                MRy = MRy_s
            Else
                MRy = MRy_i
            End If
            'intersezione con asse delle ordinate
            ReDim Mzu#(1 To 10)
            j = 0
            For i = 1 To N1 Step 1
                If i = N1 Then
                    i1 = 1
                Else
                    i1 = i + 1
                End If
                My_i = Foglio4.Cells(301 + i, 1) * fmFL
                Mz_i = Foglio4.Cells(301 + i, 2) * fmFL
                My_i1 = Foglio4.Cells(301 + i1, 1) * fmFL
                Mz_i1 = Foglio4.Cells(301 + i1, 2) * fmFL
                If My_i1 <> My_i Then
                    If (0 >= My_i1 And 0 <= My_i) Or (0 >= My_i And 0 <= My_i1) Then
                        j = j + 1
                        'retta che passa per i e i1
                        m = (Mz_i1 - Mz_i) / (My_i1 - My_i)
                        q = Mz_i - m * My_i
                        Mzu(j) = m * 0 + q
                    End If
                End If
            Next i
            MRz_s = Application.Max(Mzu())
            MRz_i = Application.Min(Mzu())
            If Medz >= 0 Then
                MRz = MRz_s
            Else
                MRz = MRz_i
            End If
            If RinfCamicieCA Then
                MRy = 0.9 * MRy
                MRz = 0.9 * MRz
            End If
        End If
    ElseIf SollecPiane Then
        AsseNeutroTrovato = True
        'costruisci dominio di rottura My-Nx
        DominioRotturaMyNx '4.7.2
        'verifica analitica
        ReDim Myu#(1 To 10)
        j = 0
        For i = 1 To 208 Step 1
            If i = 208 Then i1 = 1 Else i1 = i + 1
            My_i = Foglio4.Cells(4 + i, 2) * fmFL
            Nx_i = Foglio4.Cells(4 + i, 1) * fmF
            My_i1 = Foglio4.Cells(4 + i1, 2) * fmFL
            Nx_i1 = Foglio4.Cells(4 + i1, 1) * fmF
            If (Ned >= Nx_i1 And Ned <= Nx_i) Or (Ned >= Nx_i And Ned <= Nx_i1) Then
                If Nx_i1 <> Nx_i Then
                    j = j + 1
                    'retta che passa per i e i1
                    m = (My_i1 - My_i) / (Nx_i1 - Nx_i)
                    q = My_i - m * Nx_i
                    Myu(j) = m * Ned + q
                End If
            End If
        Next i
        If RinfCamicieCA Then
            Myu_s = 0.9 * Application.Max(Myu())
            Myu_i = 0.9 * Application.Min(Myu())
        Else
            Myu_s = Application.Max(Myu())
            Myu_i = Application.Min(Myu())
        End If
        If Medy >= Myu_i And Medy <= Myu_s Then VerifResist = True Else VerifResist = False
        'calcolo posizione asse neutro x_u a rottura
        If Medy >= 0 Then PrimaRiga = 4 Else PrimaRiga = 108
        For i = 1 To 103 Step 1
            Nx_i = Foglio4.Cells(PrimaRiga + i, 1) * fmF
            Nx_i1 = Foglio4.Cells(PrimaRiga + i + 1, 1) * fmF
            If (Ned >= Nx_i1 And Ned <= Nx_i) Then
                If Nx_i1 <> Nx_i Then
                    x1 = Foglio4.Cells(PrimaRiga + i, 3) * fmL
                    x2 = Foglio4.Cells(PrimaRiga + i + 1, 3) * fmL
                    x_u = x1 + (x2 - x1) * (Ned - Nx_i) / (Nx_i1 - Nx_i)
                    If i <= 12 Then
                        RegioneRottura = 1
                    ElseIf i <= 33 Then
                        RegioneRottura = 2
                    ElseIf i <= 43 Then
                        RegioneRottura = 3
                    ElseIf i <= 58 Then
                        RegioneRottura = 4
                    ElseIf i <= 78 Then
                        RegioneRottura = 5
                    ElseIf i <= 104 Then
                        RegioneRottura = 6
                    End If
                    Exit For
                End If
            End If
        Next i
    End If
    'costruisci dominio di rottura Mz-Nx
    'DominioRotturaMzNx  '4.7.3
Else 'il dominio My-Mz non esiste
    Foglio4.Cells(302, 5) = False
    VerifResist = False
End If
'5. OUTPUT
If CalcVerif Then
    With Foglio1
        'iF1 = iF1 + 1
        .Range(Cells(iF1, 1), Cells(iF1 + 1, 1)).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "VERIFICA ALLO STATO LIMITE DI RESISTENZA (S.L.U.) PER SFORZO NORMALE E/O"
        .Cells(iF1 + 1, 1) = "MOMENTI FLETTENTI (tensioni normali)"
        .Cells(iF1 + 2, 1) = "sforzo normale di progetto,   Ned=Nx=" & Nx / fmF & umForze
        .Cells(iF1 + 3, 1) = "momento flettente di progetto,   Medy=" & Medy / fmFL & umMomenti
        iF1 = iF1 + 4
        If SollecPiane = False Then
            .Cells(iF1, 1) = "momento flettente di progetto,   Medz=" & Medz / fmFL & umMomenti
            iF1 = iF1 + 1
        End If
        .Cells(iF1, 1) = "sforzo normale massimo di trazione sopportabile dalla sezione,   Nu_max=" & FormatNumber(Nu_max / fmF, 1, , , vbTrue) & umForze
        .Cells(iF1 + 1, 1) = "sforzo normale massimo di compressione sopportabile dalla sezione,   Nu_min=" & FormatNumber(Nu_min / fmF, 1) & umForze
        iF1 = iF1 + 2
        If SollecPiane = False Then
            .Cells(iF1, 1) = "momento resist. a presso/tenso-flessione retta corrisp.nte a Ned attorno a y,   M_Ry=" & FormatNumber(MRy / fmFL, 1, , , vbTrue) & umMomenti
            .Cells(iF1 + 1, 1) = "momento resist. a presso/tenso-flessione retta corrisp.nte a Ned attorno a z,   M_Rz=" & FormatNumber(MRz / fmFL, 1, , , vbTrue) & umMomenti
            .Cells(iF1 + 2, 1) = "momenti ultimi o resistenti (corrispondenti a Ned e Medy)"
            .Cells(iF1 + 3, 1) = "    (sono i momenti che si leggono nel dominio di rottura in corrispondenza dell'intersezione"
            .Cells(iF1 + 4, 1) = "    con la verticale passante per il punto rosso rappresentativo delle sollecitazioni agenti)"
            .Cells(iF1 + 5, 1) = "    Mzu_s=" & FormatNumber(Mzu_s / fmFL, 1, , , vbTrue) & umMomenti
            .Cells(iF1 + 6, 1) = "    Mzu_i=" & FormatNumber(Mzu_i / fmFL, 1, , , vbTrue) & umMomenti
            iF1 = iF1 + 7
        Else
            .Cells(iF1, 1) = "momenti ultimi o resistenti della sezione soggetta a presso/tenso-flessione retta (corrispondenti a Ned)"
            .Cells(iF1 + 1, 1) = "   (sono i momenti che si leggono nel dominio di rottura in corrispondenza dell'intersezione"
            .Cells(iF1 + 2, 1) = "    con la verticale passante per il punto rosso rappresentativo delle sollecitazioni agenti)"
            .Cells(iF1 + 3, 1) = "    Myu_s=" & FormatNumber(Myu_s / fmFL, 1, , , vbTrue) & umMomenti
            .Cells(iF1 + 4, 1) = "    Myu_i=" & FormatNumber(Myu_i / fmFL, 1, , , vbTrue) & umMomenti
            .Cells(iF1 + 5, 1) = "distanza asse neutro da lembo maggiorm. compresso a rottura,   x_u=" & Round(x_u / fmL, 2) & umL
            .Cells(iF1 + 6, 1) = "regione di rottura = " & RegioneRottura
            iF1 = iF1 + 7
        End If
        If RinfCamicieCA Then
            .Cells(iF1, 1) = "N.B. I momenti resistenti della sezione rinforzata con camicia in C.A. sono ridotti del 10%"
            .Cells(iF1 + 1, 1) = "    come da normativa di riferimento (v. paragrafo C8.7.4.2 Circolare n. 7/2019)"
            iF1 = iF1 + 2
        End If
        'esito verifica
        If VerifResist Then
            If SollecPiane = False Then
                .Cells(iF1, 1) = "essendo il punto rappresentativo delle sollecitazioni di progetto non esterno al dominio di"
                .Cells(iF1 + 1, 1) = "    rottura My-Mz (Mzu_i<=Medz<=Mzu_s), costruito per Nxu=Ned, la verifica Ë soddisfatta"
            Else
                .Cells(iF1, 1) = "essendo il punto rappresentativo delle sollecitazioni di progetto non esterno al dominio di"
                .Cells(iF1 + 1, 1) = "    rottura Nx-My (Myu_i<=Medy<=Myu_s) la verifica Ë soddisfatta"
            End If
            iF1 = iF1 + 3
        Else
            .Cells(iF1, 1).Select
            FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
            .Cells(iF1, 1) = "attenzione: la sezione non verifica"
            iF1 = iF1 + 2
        End If
    End With
End If
End Sub

Sub DominioRotturaMyMz() '4.7.1
Const Nh = 10 'n∞ di altezze sezione che individua l'intervallo di investigazione dell'asse neutro (x varia tra -NhxH e NhxH)
Dim Alfa0#, Alfa_ii#
Dim Cont%
Dim j%, i%
Dim ii%
Dim N12#, N23#, N34#, N45#, N56#
Dim x1#, x2#
'angolo di rotazione della sezione ad ogni passo
Alfa0 = 2 * PiGreco / N1
'costruisci dominio per punti
For ii = 1 To N1 Step 1
    Alfa_ii = Alfa0 * (ii - 1)
    CosAlfa_ii = Cos(Alfa_ii)
    SinAlfa_ii = Sin(Alfa_ii)
    CoordinateSezRuotata_e_H_Hu_x23_x34_dd '4.7.1.1
    'CALCOLA Myu-Mzu, trovando prima la posizione dell'asse neutro imponendo che sia Nxu=Ned
    AsseNeutroTrovato = False
    'calcolo N12 (si ottiene per x=0)
    x = 0
    Nu_Myu_Mzu_Regione1 '4.7.1.2
    N12 = Nu
    If Nx >= N12 Then 'la rottura Ë in Regione 1 (x negativo da -infin fino a 0)
        'trova asse neutro e calcola momenti Myu Mzu corrispondenti
        x1 = -Nh * Hc
        x2 = 0
        Cont = 0
        Do
            x = (x1 + x2) / 2
            Nu_Myu_Mzu_Regione1 '4.7.1.2
            If Nu > Nx Then x1 = x Else x2 = x
            Cont = Cont + 1
            If Cont > 100 Then Exit Do
        Loop Until Abs(Nu - Nx) <= Approssimaz
        AsseNeutroTrovato = True 'Ë nota x per cui ora si calcolano le sollec a rottura Nu=Nx, Myu, Mzu (un punto del dominio My-Mz)
        Nu_Myu_Mzu_Regione1 '4.7.1.2
    Else
        'calcolo N23
        x = x23
        Nu_Myu_Mzu_Regione2 '4.7.1.3
        N23 = Nu
        If Nx >= N23 Then 'la rottura Ë in Regione 2 (x positivo da 0 a x23)
            'trova asse neutro e calcola momenti Myu Mzu corrispondenti
            x1 = 0
            x2 = x23
            Cont = 0
            Do
                x = (x1 + x2) / 2
                Nu_Myu_Mzu_Regione2 '4.7.1.3
                If Nu > Nx Then
                    x1 = x
                Else
                    x2 = x
                End If
                Cont = Cont + 1
                If Cont > 100 Then
                    Exit Do
                End If
            Loop Until Abs(Nu - Nx) <= Approssimaz
            AsseNeutroTrovato = True
            Nu_Myu_Mzu_Regione2 '4.7.1.3
        Else
            'calcolo N34
            x = x34
            Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
            N34 = Nu
            If Nx >= N34 Then 'la rottura Ë in Regione 3 (x positivo da x23 a x34)
                'trova asse neutro e calcola momenti Myu Mzu corrispondenti
                x1 = x23
                x2 = x34
                Cont = 0
                Do
                    x = (x1 + x2) / 2
                    Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
                    If Nu > Nx Then
                        x1 = x
                    Else
                        x2 = x
                    End If
                    Cont = Cont + 1
                    If Cont > 100 Then
                        Exit Do
                    End If
                Loop Until Abs(Nu - Nx) <= Approssimaz
                AsseNeutroTrovato = True
                Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
            Else
                'calcolo N45
                x = Hu
                Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
                N45 = Nu
                If Nx >= N45 Then 'la rottura Ë in Regione 4 (x positivo da x34 a Hu)
                    'trova asse neutro e calcola momenti Myu Mzu corrispondenti
                    x1 = x34
                    x2 = Hu
                    Cont = 0
                    Do
                        x = (x1 + x2) / 2
                        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
                        If Nu > Nx Then
                            x1 = x
                        Else
                            x2 = x
                        End If
                        Cont = Cont + 1
                        If Cont > 100 Then
                            Exit Do
                        End If
                    Loop Until Abs(Nu - Nx) <= Approssimaz
                    AsseNeutroTrovato = True
                    Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
                Else
                    'calcolo N56
                    x = Hc
                    Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
                    N56 = Nu
                    If Nx >= N56 Then 'la rottura Ë in Regione 5 (x positivo da Hu ad H)
                        'trova asse neutro e calcola momenti Myu Mzu corrispondenti
                        x1 = Hu
                        x2 = Hc
                        Cont = 0
                        Do
                            x = (x1 + x2) / 2
                            Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
                            If Nu > Nx Then
                                x1 = x
                            Else
                                x2 = x
                            End If
                            Cont = Cont + 1
                            If Cont > 100 Then
                                Exit Do
                            End If
                        Loop Until Abs(Nu - Nx) <= Approssimaz
                        AsseNeutroTrovato = True
                        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
                    Else
                        'la rottura Ë in Regione 6 (x positivo da H a +inf)
                        'trova asse neutro e calcola momenti Myu Mzu corrispondenti
                        x1 = Hc
                        x2 = Nh * Hc
                        Cont = 0
                        Do
                            x = (x1 + x2) / 2
                            Nu_Myu_Mzu_Regione6 '4.7.1.5
                            If Nu > Nx Then
                                x1 = x
                            Else
                                x2 = x
                            End If
                            Cont = Cont + 1
                            If Cont > 100 Then
                                Exit Do
                            End If
                        Loop Until Abs(Nu - Nx) <= Approssimaz
                        AsseNeutroTrovato = True
                        Nu_Myu_Mzu_Regione6 '4.7.1.5
                    End If
                End If
            End If
        End If
    End If
    '4)SCARICA Myu Mzu su Fg4
    With Foglio4
        .Cells(301 + ii, 1) = Myu / fmFL
        .Cells(301 + ii, 2) = Mzu / fmFL
    End With
Next ii
End Sub

Sub CoordinateSezRuotata_e_H_Hu_x23_x34_dd() '4.7.1.1
Dim j%
Dim Ys#(), Ysc#()
Dim Yminj#, Ymaxj#, Ys_min#, Ys_max#
Dim Zminj#, Zmaxj#, Zs#(), Zsc#()
Ys_min = 0
Ys_max = 0
Zs_min = 0
Zs_max = 0
'1)COORDINATE VERTICI E BARRE DI ARMATURA NELLA CONFIGURAZIONE RUOTATA
For j = 1 To Npolig Step 1
    'carica coordinate poligonale j
    CaricaDaFg2CoordPolig j '1.2
    If Np > 0 Then
        ReDim Ys#(1 To Np)
        ReDim Zs#(1 To Np)
        ReDim Ysc#(1 To Np)
        ReDim Zsc#(1 To Np)
    End If
    For i = 1 To Np Step 1
        Ys(i) = Ys_pr(i) - yG_pr
        Zs(i) = Zs_pr(i) - zG_pr
        Ysc(i) = Ys(i) * CosAlfa_ii + Zs(i) * SinAlfa_ii
        Zsc(i) = -Ys(i) * SinAlfa_ii + Zs(i) * CosAlfa_ii
    Next i
    Yminj = Application.Min(Ysc())
    Ymaxj = Application.Max(Ysc())
    Zminj = Application.Min(Zsc())
    Zmaxj = Application.Max(Zsc())
    If Yminj < Ys_min Then Ys_min = Yminj
    If Ymaxj > Ys_max Then Ys_max = Ymaxj
    If Zminj < Zs_min Then Zs_min = Zminj
    If Zmaxj > Zs_max Then Zs_max = Zmaxj
Next j
If Nbar > 0 Then
    ReDim Ybc#(1 To Nbar)
    ReDim Zbc#(1 To Nbar)
End If
For i = 1 To Nbar
    Ybc(i) = Yb(i) * CosAlfa_ii + Zb(i) * SinAlfa_ii
    Zbc(i) = -Yb(i) * SinAlfa_ii + Zb(i) * CosAlfa_ii
Next i
'composito FRP
If RinfFRP Then
    Yfrp_c = Yfrp * CosAlfa_ii + Zfrp * SinAlfa_ii
    Zfrp_c = -Yfrp * SinAlfa_ii + Zfrp * CosAlfa_ii
End If
'2)DETERMINA H,Hu e VALORI CARATTERISTICI DELL'ASSE NEUTRO
Hc = Zs_max - Zs_min
If Nbar > 0 Then
    Zbc_max = Application.Max(Zbc())
    Zbc_min = Application.Min(Zbc())
    Hu = Zbc_max - Zs_min
    Delta1 = Zbc_min - Zs_min 'Db(1) / 2 + Cf
ElseIf Nbar = 0 Then
    Hu = Hc
    Delta1 = 0 'Cf
End If
'calcolo x23
If CemFRC And (Nbar = 0 Or Eps_Fu < Eps_su) Then
    If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then
        x23 = Eps_cuc * Hc / (Eps_Fu + Eps_cuc)
    Else
        x23 = Eps_cu * Hc / (Eps_Fu + Eps_cu)
    End If
ElseIf RinfFRP And Zfrp_c > Zbc_max And Eps_pu < Eps_su Then
    If blnConfinStaffe Or blnConfinFRP Then
        x23 = Eps_cuc * Hc / (Eps_pu + Eps0f + Eps_cuc)
    Else
        x23 = Eps_cu * Hc / (Eps_pu + Eps0f + Eps_cu)
    End If
Else
    If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then
        x23 = Eps_cuc * Hu / (Eps_su + Eps_cuc)
    Else
        x23 = Eps_cu * Hu / (Eps_su + Eps_cu)
    End If
End If
'calcolo x34 e dd
If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then
    x34 = Eps_cuc * Hu / (Eps_yd + Eps_cuc)
    dd = (Eps_cuc - Eps_c2c) / Eps_cuc * Hc
Else
    x34 = Eps_cu * Hu / (Eps_yd + Eps_cu)
    dd = (Eps_cu - Eps_c2) / Eps_cu * Hc
End If
End Sub

Sub Nu_Myu_Mzu_Regione1() '4.7.1.2
'Calcola Nu,Myu,Mzu per fissato valore x dell'asse neutro tra -inf e zero (la sezione Ë tutta tesa)
Dim i%, Afi#, yob#, zob#, yoci#, zoci#, Sig_cic#, Sig_frp#
Nu = 0
Myu = 0
Mzu = 0
'1. contributo del cls se FRC che resiste a trazione
If CemFRC Then
    Ns = Int(Hc / Deltz1) + 1
    Deltz = Hc / Ns
    For i = 1 To Ns Step 1
        zci = Zs_min + Deltz / 2 + Deltz * (i - 1)
        Calcola_Lsi_yci zci
        If Eps_Fu < Eps_su Or Nbar = 0 Then
            Eps_ci = (Zs_min - zci + x) * Eps_Fu / (Hc - x) '<0
        Else
            Eps_ci = (Zs_min - zci + x) * Eps_su / (Hu - x) '<0
        End If
        Sig_ci = f_Sigc(Eps_ci)
        Nu = Nu + Sig_ci * Lsi * Deltz
        If AsseNeutroTrovato Then
            yoci = yci * CosAlfa_ii - zci * SinAlfa_ii
            zoci = yci * SinAlfa_ii + zci * CosAlfa_ii
            Myu = Myu + Sig_ci * Lsi * Deltz * zoci
            Mzu = Mzu + Sig_ci * Lsi * Deltz * yoci
        End If
    Next i
End If
'2. contributo delle armature tese
For i = 1 To Nbar Step 1
    'calcola area barra
    Afi = PiGreco * Db(i) ^ 2 / 4
    'calcola deformazine della barra i-esima
    If CemFRC And Eps_Fu < Eps_su Then
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_Fu / (Hc - x) '>0
    ElseIf RinfFRP And (Eps_pu + Eps0f) < Eps_su And Zfrp_c > Zbc_max Then
        Eps_fi = -(Zs_min - Zbc(i) + x) * (Eps_pu + Eps0f) / (Hc - x) '>0
    Else
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_su / (Hu - x)
    End If
    'nota la deformazione, calcola tensione nella barra i-esima
    If CemArmOrd Then
        If TondNuovo(i) Then Sig_fi = f_Sigf(Eps_fi) Else Sig_fi = f_Sigf_es(Eps_fi)
    ElseIf CemCAP Then 'c.a.p.
        If TondArmonico(i) Then 'barra da precompresso
            Sig_fi = f_Sigf(Eps_fi + Eps0)
        Else
            Sig_fi = f_Sigf2(Eps_fi)
        End If
    End If
    'calcola contributo allo sforzo normale
    Nu = Nu + Afi * Sig_fi
    'calcola contributo ai momenti flettenti
    If AsseNeutroTrovato Then
        yob = Ybc(i) * CosAlfa_ii - Zbc(i) * SinAlfa_ii 'distanza tondino rispetto al sistema yozo solidale alla sezione ruotata
        zob = Ybc(i) * SinAlfa_ii + Zbc(i) * CosAlfa_ii
        Myu = Myu + Afi * Sig_fi * zob
        Mzu = Mzu + Afi * Sig_fi * yob
    End If
Next i
'3. contributo del composito FRP
If RinfFRP Then
    If (Eps_pu + Eps0f) < Eps_su And Zfrp_c > Zbc_max Then
        Eps_frp = -(Zs_min - Zfrp_c + x) * (Eps_pu + Eps0f) / (Hc - x) '>0
        Sig_frp = (Eps_frp - Eps0f) * E_frp
    Else
        Eps_frp = -(Zs_min - Zfrp_c + x) * Eps_su / (Hu - x)
        If Eps_frp < 0 Or Eps_frp > Eps_pu + Eps0f Then
            Sig_frp = 0 'si rompe il FRP
        Else
            Sig_frp = (Eps_frp - Eps0f) * E_frp
        End If
    End If
    'Sig_frp = (Eps_frp - Eps0f) * E_frp
    Nu = Nu + A_frp * Sig_frp
    'calcola contributo ai momenti flettenti
    If AsseNeutroTrovato Then
        yob = Yfrp_c * CosAlfa_ii - Zfrp_c * SinAlfa_ii
        zob = Yfrp_c * SinAlfa_ii + Zfrp_c * CosAlfa_ii
        Myu = Myu + A_frp * Sig_frp * zob
        Mzu = Mzu + A_frp * Sig_frp * yob
    End If
End If
'4. cambio di segno
Mzu = -Mzu
End Sub

Sub Nu_Myu_Mzu_Regione2() '4.7.1.3
'Calcola Nu,Myu,Mzu per fissato valore x dell'asse neutro tra zero e x23
Dim i%, Afi#, y_i#, yob#, zob#, yoci#, zoci#, Sig_cic#, Sig_frp#
Nu = 0
Myu = 0
Mzu = 0
'1. contributo del cls compresso e, nel caso FRC, teso
If CemFRC Then
    Ns = Int(Hc / Deltz1) + 1
    Deltz = Hc / Ns
Else
    Ns = Int(x / Deltz1) + 1
    Deltz = x / Ns
End If
For i = 1 To Ns Step 1
    zci = Zs_min + Deltz / 2 + Deltz * (i - 1)
    Calcola_Lsi_yci zci
    y_i = Zs_min + x - zci
    If CemFRC And (Eps_Fu < Eps_su Or Nbar = 0) Then
        Eps_ci = y_i * Eps_Fu / (Hc - x)
    ElseIf RinfFRP And (Eps_pu + Eps0f < Eps_su Or Nbar = 0) And Zfrp_c > Zbc_max Then
        Eps_ci = y_i * (Eps_pu + Eps0f) / (Hc - x)
    Else
        Eps_ci = y_i * Eps_su / (Hu - x)
    End If
    Sig_ci = f_Sigc(Eps_ci) 'cls copriferro o tutto nel caso confinato con FRP o Calastr
    If blnConfinStaffe And Eps_ci > 0 Then 'compressione. Cls del nucleo confibato
        If zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
            Sig_cic = f_Sigc2(Eps_ci)
            Nu = Nu + Sig_ci * (2 * Cf) * Deltz + Sig_cic * (Lsi - 2 * Cf) * Deltz
        Else
            Nu = Nu + Sig_ci * Lsi * Deltz
        End If
    Else
        Nu = Nu + Sig_ci * Lsi * Deltz
    End If
    If AsseNeutroTrovato Then
        yoci = yci * CosAlfa_ii - zci * SinAlfa_ii
        zoci = yci * SinAlfa_ii + zci * CosAlfa_ii
        If blnConfinStaffe And Eps_ci > 0 Then
            If zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
                Myu = Myu + Sig_ci * (2 * Cf) * Deltz * zoci + Sig_cic * (Lsi - 2 * Cf) * Deltz * zoci
                Mzu = Mzu + Sig_ci * (2 * Cf) * Deltz * yoci + Sig_cic * (Lsi - 2 * Cf) * Deltz * yoci
            Else
                Myu = Myu + Sig_ci * Lsi * Deltz * zoci
                Mzu = Mzu + Sig_ci * Lsi * Deltz * yoci
            End If
        Else
            Myu = Myu + Sig_ci * Lsi * Deltz * zoci
            Mzu = Mzu + Sig_ci * Lsi * Deltz * yoci
        End If
    End If
Next i
'2. contributo delle armature
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    If CemFRC And Eps_Fu < Eps_su Then
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_Fu / (Hc - x)
    ElseIf RinfFRP And (Eps_pu + Eps0f) < Eps_su And Zfrp_c > Zbc_max Then
        Eps_fi = -(Zs_min - Zbc(i) + x) * (Eps_pu + Eps0f) / (Hc - x)
    Else
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_su / (Hu - x)
    End If
    If CemArmOrd Then
        Sig_fi = f_Sigf(Eps_fi)
    ElseIf CemCAP Then 'c.a.p.
        If TondArmonico(i) Then 'barra da precompresso
            Sig_fi = f_Sigf(Eps_fi + Eps0)
        Else
            Sig_fi = f_Sigf2(Eps_fi)
        End If
    End If
    Nu = Nu + Afi * Sig_fi
    If AsseNeutroTrovato Then
        yob = Ybc(i) * CosAlfa_ii - Zbc(i) * SinAlfa_ii
        zob = Ybc(i) * SinAlfa_ii + Zbc(i) * CosAlfa_ii
        Myu = Myu + Afi * Sig_fi * zob
        Mzu = Mzu + Afi * Sig_fi * yob
    End If
Next i
'3. contributo del composito FRP
If RinfFRP Then
    If (Eps_pu + Eps0f) < Eps_su And Zfrp_c > Zbc_max Then
        Eps_frp = -(Zs_min - Zfrp_c + x) * (Eps_pu + Eps0f) / (Hc - x) '>0
    Else
        Eps_frp = -(Zs_min - Zfrp_c + x) * Eps_su / (Hu - x)
        If Eps_frp < 0 Or Eps_frp > Eps_pu + Eps0f Then Eps_frp = Eps0f 'si rompe il FRP
    End If
    Sig_frp = (Eps_frp - Eps0f) * E_frp
    Nu = Nu + A_frp * Sig_frp
    'calcola contributo ai momenti flettenti
    If AsseNeutroTrovato Then
        yob = Yfrp_c * CosAlfa_ii - Zfrp_c * SinAlfa_ii
        zob = Yfrp_c * SinAlfa_ii + Zfrp_c * CosAlfa_ii
        Myu = Myu + A_frp * Sig_frp * zob
        Mzu = Mzu + A_frp * Sig_frp * yob
    End If
End If
'4. cambio di segno
Mzu = -Mzu
End Sub

Sub Nu_Myu_Mzu_Regione3_4_5() '4.7.1.4
'Calcola Nu,Myu,Mzu per fissato valore x dell'asse neutro tra x23 e x34, tra x34 e Hu e tra Hu ed H
Dim i%, Afi#, y_i#, yob#, zob#, yoci#, zoci#, Sig_cic#, Sig_frp#
Nu = 0
Myu = 0
Mzu = 0
'1. contributo del cls
If CemFRC Then
    Ns = Int(Hc / Deltz1) + 1
    Deltz = Hc / Ns
Else
    Ns = Int(x / Deltz1) + 1
    Deltz = x / Ns
End If
For i = 1 To Ns Step 1
    zci = Zs_min + Deltz / 2 + Deltz * (i - 1)
    Calcola_Lsi_yci zci
    y_i = Zs_min + x - zci
    If blnConfinStaffe Then
        Eps_ci = y_i * Eps_cuc / x
        Sig_ci = f_Sigc(Eps_ci)
        If Eps_ci > 0 Then 'cls compresso
            Sig_cic = f_Sigc2(Eps_ci)
            If zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
                Nu = Nu + Sig_ci * (2 * Cf) * Deltz + Sig_cic * (Lsi - 2 * Cf) * Deltz
            Else
                Nu = Nu + Sig_ci * Lsi * Deltz
            End If
        Else
            Nu = Nu + Sig_ci * Lsi * Deltz
        End If
    Else
        If blnConfinFRP Or blnConfinCamicieAcc Then
            Eps_ci = y_i * Eps_cuc / x
        Else
            Eps_ci = y_i * Eps_cu / x
        End If
        Sig_ci = f_Sigc(Eps_ci)
        Nu = Nu + Sig_ci * Lsi * Deltz
    End If
    If AsseNeutroTrovato Then
        yoci = yci * CosAlfa_ii - zci * SinAlfa_ii
        zoci = yci * SinAlfa_ii + zci * CosAlfa_ii
        If blnConfinStaffe And Eps_ci > 0 Then
            If zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
                Myu = Myu + Sig_ci * (2 * Cf) * Deltz * zoci + Sig_cic * (Lsi - 2 * Cf) * Deltz * zoci
                Mzu = Mzu + Sig_ci * (2 * Cf) * Deltz * yoci + Sig_cic * (Lsi - 2 * Cf) * Deltz * yoci
            Else
                Myu = Myu + Sig_ci * Lsi * Deltz * zoci
                Mzu = Mzu + Sig_ci * Lsi * Deltz * yoci
            End If
        Else
            Myu = Myu + Sig_ci * Lsi * Deltz * zoci
            Mzu = Mzu + Sig_ci * Lsi * Deltz * yoci
        End If
    End If
Next i
'2. contributo delle armature
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_cuc / x
    Else
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_cu / x
    End If
    If CemArmOrd Then
        Sig_fi = f_Sigf(Eps_fi)
    ElseIf CemCAP Then 'c.a.p.
        If TondArmonico(i) Then 'barra da precompresso
            Sig_fi = f_Sigf(Eps_fi + Eps0)
        Else
            Sig_fi = f_Sigf2(Eps_fi)
        End If
    End If
    Nu = Nu + Afi * Sig_fi
    If AsseNeutroTrovato Then
        yob = Ybc(i) * CosAlfa_ii - Zbc(i) * SinAlfa_ii
        zob = Ybc(i) * SinAlfa_ii + Zbc(i) * CosAlfa_ii
        Myu = Myu + Afi * Sig_fi * zob
        Mzu = Mzu + Afi * Sig_fi * yob
    End If
Next i
'3. contributo del composito FRP
If RinfFRP Then
    If blnConfinStaffe Or blnConfinFRP Then
        Eps_frp = -(Zs_min - Zfrp_c + x) * Eps_cuc / x
    Else
        Eps_frp = -(Zs_min - Zfrp_c + x) * Eps_cu / x
    End If
    If Eps_frp < 0 Or Eps_frp > Eps_pu + Eps0f Then 'compressione o si rompe il FRP
        Eps_frp = Eps0f
    End If
    Sig_frp = (Eps_frp - Eps0f) * E_frp
    Nu = Nu + A_frp * Sig_frp
    'calcola contributo ai momenti flettenti
    If AsseNeutroTrovato Then
        yob = Yfrp_c * CosAlfa_ii - Zfrp_c * SinAlfa_ii
        zob = Yfrp_c * SinAlfa_ii + Zfrp_c * CosAlfa_ii
        Myu = Myu + A_frp * Sig_frp * zob
        Mzu = Mzu + A_frp * Sig_frp * yob
    End If
End If
'4. cambio di segno
Mzu = -Mzu
End Sub

Sub Nu_Myu_Mzu_Regione6() '4.7.1.5
'Calcola Nu,Myu,Mzu per fissato valore x dell'asse neutro tra H e +inf (sezione tutta compressa)
Dim i%, Afi#, y_i#, yob#, zob#, yoci#, zoci#, Sig_cic#
Nu = 0
Myu = 0
Mzu = 0
'1. contributo del cls
Ns = Int(Hc / Deltz1) + 1
Deltz = Hc / Ns
For i = 1 To Ns Step 1
    y_i = x - Hc + Deltz / 2 + Deltz * (i - 1)
    zci = x + Zs_min - y_i
    Calcola_Lsi_yci zci
    If blnConfinStaffe Then
        Eps_ci = y_i * Eps_c2c / (x - dd) 'Ë>0 compressione
        Sig_ci = f_Sigc(Eps_ci)
        Sig_cic = f_Sigc2(Eps_ci)
        If zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
            Nu = Nu + Sig_ci * (2 * Cf) * Deltz + Sig_cic * (Lsi - 2 * Cf) * Deltz
        Else
            Nu = Nu + Sig_ci * Lsi * Deltz
        End If
    Else
        If blnConfinFRP Or blnConfinCamicieAcc Then
            Eps_ci = y_i * Eps_c2c / (x - dd)
        Else
            Eps_ci = y_i * Eps_c2 / (x - dd)
        End If
        Sig_ci = f_Sigc(Eps_ci)
        Nu = Nu + Sig_ci * Lsi * Deltz
    End If
    If AsseNeutroTrovato Then
        yoci = yci * CosAlfa_ii - zci * SinAlfa_ii
        zoci = yci * SinAlfa_ii + zci * CosAlfa_ii
        If blnConfinStaffe Then
            If zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
                Myu = Myu + Sig_ci * (2 * Cf) * Deltz * zoci + Sig_cic * (Lsi - 2 * Cf) * Deltz * zoci
                Mzu = Mzu + Sig_ci * (2 * Cf) * Deltz * yoci + Sig_cic * (Lsi - 2 * Cf) * Deltz * yoci
            Else
                Myu = Myu + Sig_ci * Lsi * Deltz * zoci
                Mzu = Mzu + Sig_ci * Lsi * Deltz * yoci
            End If
        Else
            Myu = Myu + Sig_ci * Lsi * Deltz * zoci
            Mzu = Mzu + Sig_ci * Lsi * Deltz * yoci
        End If
    End If
Next i
'2. contributo delle armature
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_c2c / (x - dd)
    Else
        Eps_fi = -(Zs_min - Zbc(i) + x) * Eps_c2 / (x - dd)
    End If
    If CemArmOrd Then
        Sig_fi = f_Sigf(Eps_fi)
    ElseIf CemCAP Then
        If TondArmonico(i) Then 'barra da precompresso
            Sig_fi = f_Sigf(Eps_fi + Eps0)
        Else
            Sig_fi = f_Sigf2(Eps_fi)
        End If
    End If
    Nu = Nu + Afi * Sig_fi
    If AsseNeutroTrovato Then
        yob = Ybc(i) * CosAlfa_ii - Zbc(i) * SinAlfa_ii
        zob = Ybc(i) * SinAlfa_ii + Zbc(i) * CosAlfa_ii
        Myu = Myu + Afi * Sig_fi * zob
        Mzu = Mzu + Afi * Sig_fi * yob
    End If
Next i
'3. Il contributo dell'eventuale FRP non c'Ë essendo la sezione tutta compressa
'4. cambio di segno
Mzu = -Mzu
End Sub

Sub DominioRotturaMyNx() '4.7.2
Dim Alfa0#, Alfa_ii#
Dim Coeff#
Dim ii%, i%
Dim xstell#, Passo#, x_#(1 To 12)
'angolo di rotazione ad ogni passo (due soli passi)
Alfa0 = PiGreco
'costruisci dominio per punti
j = 1
For ii = 1 To 2 Step 1
    Alfa_ii = Alfa0 * (ii - 1) 'prima 0∞ e poi 180∞ (sezione capovolta)
    CosAlfa_ii = Cos(Alfa_ii)
    SinAlfa_ii = Sin(Alfa_ii)
    CoordinateSezRuotata_e_H_Hu_x23_x34_dd
    'CALCOLA Nu e Myu al variare di x, ottenendo punti del dominio di rottura
    'REGIONE 1 (x negativo fino a 0)
    x_(1) = -10 * Hc
    x_(2) = -8 * Hc
    x_(3) = -3 * Hc
    x_(4) = -1 * Hc
    x_(5) = -0.2 * Hc
    x_(6) = -0.16 * Hc
    x_(7) = -0.12 * Hc
    x_(8) = -0.08 * Hc
    x_(9) = -0.06 * Hc
    x_(10) = -0.04 * Hc
    x_(11) = -0.02 * Hc
    x_(12) = 0
    For i = 1 To 12
        x = x_(i)
        Nu_Myu_Mzu_Regione1 '4.7.1.2
        OutNuMyuSuFg4
    Next i
    'REGIONE 2 (x da 0 a x23)
    x = 0
    Passo = x23 / 21 '21 punti
    For i = 1 To 21
        x = x + Passo
        Nu_Myu_Mzu_Regione2 '4.7.1.3
        OutNuMyuSuFg4
    Next i
    'REGIONE 3 (x da x23 a x34)
    x = x23
    Passo = (x34 - x23) / 10 '10 punti
    For i = 1 To 10
        x = x + Passo
        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
        OutNuMyuSuFg4
    Next i
    'REGIONE 4 (x da x34 a Hu)
    x = x34
    Passo = (Hu - x34) / 15 '15 punti
    For i = 1 To 15
        x = x + Passo
        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
        OutNuMyuSuFg4
    Next
    'REGIONE 5 (x da Hu a H)
    x = Hu
    Passo = (Hc - Hu) / 20 '20 punti
    For i = 1 To 20
        x = x + Passo
        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
        OutNuMyuSuFg4
    Next
    'REGIONE 6
    x = Hc
    For i = 1 To 26 '26 punti
        If i <= 10 Then
            Coeff = 1 + 0.05 * i
        ElseIf i <= 20 Then
            Coeff = 1.5 + 0.5 * (i - 10)
        Else
            Coeff = 6.5 + 2 * (i - 20)
        End If
        x = Hc * Coeff
        Nu_Myu_Mzu_Regione6 '4.7.1.5
        OutNuMyuSuFg4
    Next i
Next ii
End Sub

Sub DominioRotturaMzNx() '4.7.3
Dim Alfa0#, Alfa_ii#
Dim Coeff#
Dim ii%, i%
Dim xstell#, Passo#
'angolo di rotazione ad ogni passo (due soli passi)
Alfa0 = PiGreco
'costruisci dominio per punti
j = 1
For ii = 1 To 2 Step 1
    Alfa_ii = PiGreco / 2 + Alfa0 * (ii - 1) 'prima 90∞ e poi 270∞
    CosAlfa_ii = Cos(Alfa_ii)
    SinAlfa_ii = Sin(Alfa_ii)
    CoordinateSezRuotata_e_H_Hu_x23_x34_dd
    'Calcola Nu e Mzu al variare di x, ottenendo punti del dominio di rottura
    'REGIONE 1 (x negativo fino a 0)
    xstell = -(Eps_yd * Hu - Eps_su * Delta1) / (Eps_su - Eps_yd)
    Passo = Abs(xstell) / 11 '12 punti
    x = xstell - Passo
    For i = 1 To 12
        x = x + Passo
        Nu_Myu_Mzu_Regione1 '4.7.1.2
        OutNuMzuSuFg4
    Next i
    'REGIONE 2 (x da 0 a x23)
    x = 0
    Passo = x23 / 21 '21 punti
    For i = 1 To 21
        x = x + Passo
        Nu_Myu_Mzu_Regione2 '4.7.1.3
        OutNuMzuSuFg4
    Next i
    'REGIONE 3 (x da x23 a x34)
    x = x23
    Passo = (x34 - x23) / 10 '10 punti
    For i = 1 To 10
        x = x + Passo
        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
        OutNuMzuSuFg4
    Next i
    'REGIONE 4 (x da x34 a Hu)
    x = x34
    Passo = (Hu - x34) / 15 '15 punti
    For i = 1 To 15
        x = x + Passo
        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
        OutNuMzuSuFg4
    Next
    'REGIONE 5 (x da Hu a H)
    x = Hu
    Passo = (Hc - Hu) / 20 '20 punti
    For i = 1 To 20
        x = x + Passo
        Nu_Myu_Mzu_Regione3_4_5 '4.7.1.4
        OutNuMzuSuFg4
    Next
    'REGIONE 6
    x = Hc
    'Passo = (10 * Hc - Hc) / 26
    For i = 1 To 26 '26 punti
        If i <= 10 Then
            Coeff = 1 + 0.05 * i
        ElseIf i <= 20 Then
            Coeff = 1.5 + 0.5 * (i - 10)
        Else
            Coeff = 6.5 + 2 * (i - 20)
        End If
        x = Hc * Coeff
        'x = x + Passo
        Nu_Myu_Mzu_Regione6 '4.7.1.5
        OutNuMzuSuFg4
    Next i
Next ii
End Sub

Sub CostruzioneDiagrMomentiCurvatura() '4.8
'costruisce il diagramma Momenti-Curvatura con le leggi sig-eps dei materiali non lineari (parabola rettangolo ecc.)
Dim Cont%, Cont2%
Dim Curv#, CurvSnerv_f#, CurvSnerv_c#, CurvSnervMin#, Curv_u#, CurvPrimaPlast#
Dim Epsfmax#, Epscd#, Epsct_max#
Dim Epsf#, Epsf1#, Epsf2#, ErrEps#, Epsc#, Epsc1#, Epsc2#
Dim Duttilit‡Sez#
Dim i%, k%
Dim Msnerv_f#, Msnerv_c#, Myd_pr#
Dim Nx1#, Nx2#
Dim Npx% 'numero posizioni asse neutro da esaminare (punti del diagramma)
Dim Passox#
Dim ScartoEpsf#, ScartoEpsc#
Dim x1#, x2#
'1.input
If Foglio2.Cells(27, 12) = "" Then Npx = 0 Else Npx = Foglio2.Cells(27, 12)
'If Foglio2.Cells(28, 12) = "" Then DeltaEps = 0 Else DeltaEps = Foglio2.Cells(28, 12)
'If Foglio2.Cells(29, 12) = "" Then Deltz1 = 0 Else Deltz1 = Foglio2.Cells(29, 12) * fmL
If Foglio2.Cells(30, 12) = "" Then x1 = 0 Else x1 = Foglio2.Cells(30, 12) * fmL
If Foglio2.Cells(31, 12) = "" Then x2 = 0 Else x2 = Foglio2.Cells(31, 12) * fmL
With Foglio4 'cancella dati Fg4
    .Range("AD6:AI400").ClearContents
    .Cells(6, 36) = ""
    .Cells(8, 36) = ""
    .Range("Ak6:Ak400").ClearContents
End With
'2.esecuzione
If Ned <= Nu_max And Ned >= Nu_min Then
    '2.1 calcolo momento di fessurazione e risultati per 1∞ stadio (primi 4 punti diagramma)
    DatiSezioneCA '4.1
    Zs_min = Zmin_pr - zG_pr
    Zs_max = Zmax_pr - zG_pr
    Mfess = fctm * Iy / Zs_max  'Iy Ë quello della sezione omogeneizzata (Ë tutta reagente infatti)
    For k = 1 To 4
        My = (k - 1) / 3 * Mfess
        Curv = My / (Ec * Iy)
        With Foglio4
            .Cells(5 + k, 30) = Round(Curv / (1 / fmL) * 100, 8)
            .Cells(5 + k, 31) = Round(My / fmFL, 2)
        End With
    Next k
    '2.2 calcolo coppie Curv-My nel secondo stadio, per il grafico
    Passox = (x2 - x1) / (Npx - 1)
    Cont = 0
    ScartoEpsf = 1
    ScartoEpsc = 1
    For i = 1 To Npx
        x = x1 + Passox * (i - 1)
        'trova stato deformativo sezione per fissata posizione dell'asse neutro con l'equaz equlibr alla traslaz lungo l'asse della trave
        'uso metodo Bisezione
        If x <= 0 Then 'A) sezione tutta tesa (contributo delle sole armature tese e del cls se FRC)
            'punto a intervallo dove c'Ë la soluzione
            Epsf1 = 0.00001
            Calcola_Nx_My_1 Epsf1 '4.8.1  trova Nx_ e My_
            Nx1 = Nx_ 'f(a)  valore della funzione
            'punto b intervallo dove c'Ë la soluzione
            If CemFRC And Eps_Fu <= Eps_su Then 'si rimpe prima il cls teso
                Epsf2 = Eps_Fu
            Else
                Epsf2 = Eps_su
            End If
            Calcola_Nx_My_1 Epsf2 '4.8.1  trova Nx_ e My_
            Nx2 = Nx_ 'f(b)  valore della funzione
            'Nx2 = Nu_max 'f(b)
            If (Nx1 - Ned) * (Nx2 - Ned) <= 0 Then
                'la soluzione c'Ë per l'x fissato
                Cont2 = 1
                ErrEps = (Epsf2 - Epsf1) / 10000 'fisso errore tollerato pari a un millesimo dell'intervallo
                While Cont2 <= 100 And (Epsf2 - Epsf1) >= ErrEps
                    Epsf = (Epsf1 + Epsf2) / 2
                    Calcola_Nx_My_1 Epsf '4.8.1
                    'verifico dove cade lo zero soluzione
                    If (Nx1 - Ned) * (Nx_ - Ned) <= 0 Then
                        'lo zero Ë nel sottoinsieme di sinistra
                        Epsf2 = Epsf
                        Nx2 = Nx_
                    Else
                        'lo zero Ë nel sottoinsieme di destra
                        Epsf1 = Epsf
                        Nx1 = Nx_
                    End If
                    Cont2 = Cont2 + 1
                Wend
                'uscendo fuori dal ciclo ho trovato Epsf e Nx_ e My_ corrispondente
                Curv = Epsf / (Hu - x)
                'aggiorna momento e curvatura in corrispondenza snervamento dell'armatura tesa
                If Abs((Epsf - Eps_yd) / Eps_yd) <= ScartoEpsf Then
                    ScartoEpsf = Abs((Epsf - Eps_yd) / Eps_yd)
                    Msnerv_f = My_
                    CurvSnerv_f = Curv
                End If
                'output su Fg4
                If My_ > Mfess Then
                    With Foglio4
                        Cont = Cont + 1
                        .Cells(9 + Cont, 30) = Round(Curv / (1 / fmL) * 100, 8) 'curvatura
                        .Cells(9 + Cont, 31) = Round(My_ / fmFL, 2)
                        .Cells(9 + Cont, 32) = Round(Nx_ / fmF, 2)
                        .Cells(9 + Cont, 33) = Round(x / fmL, 5)
                        .Cells(9 + Cont, 35) = Round(Epsf, 6) * 100 & "%"
                        .Cells(9 + Cont, 37) = Cont2 'numero iterazioni metodo bisezione
                    End With
                End If
            End If
        ElseIf x <= H Then 'B) sezione in parte compressa e in parte tesa
            'estremo sinistra a=Epsc1 dell'intervallo dove c'Ë la soluzione e valore f(a)
            Epsc1 = 0.00001
            Calcola_Nx_My_2 Epsc1 '4.8.2   trova Nx_ e My_
            Nx1 = Nx_
            'punto b intervallo dove c'Ë la soluzione e f(b). Epsc2=valore massimo deformaz cls deve essere tale che il corrispondente
            'Epsf massimo nell'armatura sia <= Eps_su
            If CemFRC And Eps_Fu <= Eps_su Then
                If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then
                    Epsct_max = Eps_cuc * (H - x) / x
                    If Epsct_max > Eps_Fu Then Epsc2 = Eps_Fu * x / (H - x) Else Epsc2 = Eps_cuc
                Else
                    Epsct_max = Eps_cu * (H - x) / x
                    If Epsct_max > Eps_Fu Then Epsc2 = Eps_Fu * x / (H - x) Else Epsc2 = Eps_cu
                End If
            Else
                If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then
                    Epsfmax = Eps_cuc * (Hu - x) / x
                    If Epsfmax > Eps_su Then Epsc2 = Eps_su * x / (Hu - x) Else Epsc2 = Eps_cuc
                Else
                    Epsfmax = Eps_cu * (Hu - x) / x
                    If Epsfmax > Eps_su Then Epsc2 = Eps_su * x / (Hu - x) Else Epsc2 = Eps_cu
                End If
            End If
            Calcola_Nx_My_2 Epsc2 '4.8.2   trova Nx_ e My_
            Nx2 = Nx_
            If (Nx1 - Ned) * (Nx2 - Ned) <= 0 Then
                'la soluzione c'Ë per l'x fissato
                Cont2 = 1
                ErrEps = (Epsc2 - Epsc1) / 10000 'fisso errore tollerato pari a un millesimo dell'intervallo
                While Cont2 <= 100 And (Epsc2 - Epsc1) >= ErrEps
                    Epsc = (Epsc1 + Epsc2) / 2
                    Calcola_Nx_My_2 Epsc '4.8.2   trova Nx_ e My_
                    'verifico dove cade lo zero soluzione
                    If (Nx1 - Ned) * (Nx_ - Ned) <= 0 Then
                        'lo zero Ë nel sottoinsieme di sinistra
                        Epsc2 = Epsc
                        Nx2 = Nx_
                    Else
                        'lo zero Ë nel sottoinsieme di destra
                        Epsc1 = Epsc
                        Nx1 = Nx_
                    End If
                    Cont2 = Cont2 + 1
                Wend
                'uscendo fuori dal ciclo ho trovato Epsc e Nx e My corrispondente
                Curv = Epsc / x
                Epsf = Epsc / x * (Hu - x)
                'aggiorna momento e curvatura in corrispondenza snervamento dell'armatura tesa e in corrisp deformaz di picco cls
                If Abs((Epsf - Eps_yd) / Eps_yd) <= ScartoEpsf Then
                    ScartoEpsf = Abs((Epsf - Eps_yd) / Eps_yd)
                    Msnerv_f = My_
                    CurvSnerv_f = Curv
                End If
                If blnParabRettang Then
                    If Abs((Epsc - Eps_c2) / Eps_c2) <= ScartoEpsc Then
                        ScartoEpsc = Abs((Epsc - Eps_c2) / Eps_c2)
                        Msnerv_c = My_
                        CurvSnerv_c = Curv
                    End If
                ElseIf blnTriangRettang Then
                    If Abs((Epsc - Eps_c3) / Eps_c3) <= ScartoEpsc Then
                        ScartoEpsc = Abs((Epsc - Eps_c3) / Eps_c3)
                        Msnerv_c = My_
                        CurvSnerv_c = Curv
                    End If
                End If
                'output su Fg4
                If My_ > Mfess Then
                    With Foglio4
                        Cont = Cont + 1
                        .Cells(9 + Cont, 30) = Round(Curv / (1 / fmL) * 100, 8)
                        .Cells(9 + Cont, 31) = Round(My_ / fmFL, 2)
                        .Cells(9 + Cont, 32) = Round(Nx_ / fmF, 2)
                        .Cells(9 + Cont, 33) = Round(x / fmL, 5)
                        .Cells(9 + Cont, 34) = Round(Epsc, 6) * 100 & "%"
                        .Cells(9 + Cont, 35) = Round(Epsf, 6) * 100 & "%"
                        .Cells(9 + Cont, 37) = Cont2 'numero iterazioni metodo bisezione
                    End With
                End If
            End If
        ElseIf x > H Then 'C) sezione tutta compressa
            If blnConfinStaffe Then
                dd = H * (Eps_cuc - Eps_c2c) / Eps_cuc
                Epscd = Eps_c2c * x / (x - dd)
            Else
                dd = H * (Eps_cu - Eps_c2) / Eps_cu
                Epscd = Eps_c2 * x / (x - dd)
            End If
            'punto a intervallo dove c'Ë la soluzione e f(a)
            Epsc1 = 0.00001
            Calcola_Nx_My_3 Epsc1 'trova Nx_ e My_
            Nx1 = Nx_
            'Nx1 = 0
            'punto b intervallo dove c'Ë la soluzione e f(b)
            Epsc2 = Epscd
            Calcola_Nx_My_3 Epsc2 'trova Nx_ e My_
            Nx2 = Nx_
            If (Nx1 - Ned) * (Nx2 - Ned) <= 0 Then
                'la soluzione c'Ë per l'x fissato
                Cont2 = 1
                ErrEps = (Epsc2 - Epsc1) / 10000 'fisso errore tollerato pari a un millesimo dell'intervallo
                While Cont2 <= 100 And (Epsc2 - Epsc1) >= ErrEps
                    Epsc = (Epsc1 + Epsc2) / 2
                    Calcola_Nx_My_3 Epsc 'trova Nx_ e My_
                    'verifico dove cade lo zero soluzione
                    If (Nx1 - Ned) * (Nx_ - Ned) <= 0 Then
                        'lo zero Ë nel sottoinsieme di sinistra
                        Epsc2 = Epsc
                        Nx2 = Nx_
                    Else
                        'lo zero Ë nel sottoinsieme di destra
                        Epsc1 = Epsc
                        Nx1 = Nx_
                    End If
                    Cont2 = Cont2 + 1
                Wend
                'uscendo fuori dal ciclo ho trovato Epsc e Nx e My corrispondente
                Curv = Epsc / x
                'aggiorna momento e curvatura in corrispondenza snervamento dell'armatura tesa e in corrisp deformaz di picco cls
                If Abs((Epsf - Eps_yd) / Eps_yd) <= ScartoEpsf Then
                    ScartoEpsf = Abs((Epsf - Eps_yd) / Eps_yd)
                    Msnerv_f = My_
                    CurvSnerv_f = Curv
                End If
                If blnParabRettang Then
                    If Abs((Epsc - Eps_c2) / Eps_c2) <= ScartoEpsc Then
                        ScartoEpsc = Abs((Epsc - Eps_c2) / Eps_c2)
                        Msnerv_c = My_
                        CurvSnerv_c = Curv
                    End If
                ElseIf blnTriangRettang Then
                    If Abs((Epsc - Eps_c3) / Eps_c3) <= ScartoEpsc Then
                        ScartoEpsc = Abs((Epsc - Eps_c3) / Eps_c3)
                        Msnerv_c = My_
                        CurvSnerv_c = Curv
                    End If
                End If
                'output su Fg4
                If My_ > Mfess Then
                    With Foglio4
                        Cont = Cont + 1
                        .Cells(9 + Cont, 30) = Round(Curv / (1 / fmL) * 100, 8)
                        .Cells(9 + Cont, 31) = Round(My_ / fmFL, 2)
                        .Cells(9 + Cont, 32) = Round(Nx_ / fmF, 2)
                        .Cells(9 + Cont, 33) = Round(x / fmL, 5)
                        .Cells(9 + Cont, 34) = Round(Epsc, 6) * 100 & "%"
                        .Cells(9 + Cont, 37) = Cont2 'numero iterazioni metodo bisezione
                    End With
                End If
            End If
        End If
    Next i
    '2.3 ultimo punto del diagramma Curv_u, Myu_s
    If RegioneRottura = 1 Or RegioneRottura = 2 Then
        Curv_u = Eps_su / (Hu - x_u)
    Else
        If blnConfinStaffe Or blnConfinFRP Or blnConfinCamicieAcc Then Curv_u = Eps_cuc / x_u Else Curv_u = Eps_cu / x_u
    End If
    '2.4 calcolo duttilit‡ sezione
    If CurvSnerv_c > 0 Then
        If CurvSnerv_c < CurvSnerv_f Then
            CurvSnervMin = CurvSnerv_c
            Myd_pr = Msnerv_c
        Else
            CurvSnervMin = CurvSnerv_f
            Myd_pr = Msnerv_f
        End If
    Else
        CurvSnervMin = CurvSnerv_f
        Myd_pr = Msnerv_f
    End If
    If Myd_pr > 0 Then
        CurvPrimaPlast = Myu_s * CurvSnervMin / Myd_pr
        Duttilit‡Sez = Curv_u / CurvPrimaPlast
    End If
    '3. output ultimi
    With Foglio4
        .Activate
        .Cells(9 + Cont + 1, 30) = Round(Curv_u / (1 / fmL) * 100, 8)
        .Cells(9 + Cont + 1, 31) = Round(Myu_s / fmFL, 2)
        .Cells(6, 36) = 4 + Cont + 1
        .Cells(8, 36) = Round(Duttilit‡Sez, 2)
        'ordina dati su Fg4 per curvatura crescente
        .Range("AD5:AI" & (5 + .Cells(6, 36))).Select
        ActiveWorkbook.Worksheets("Foglio4").Sort.SortFields.Clear
        ActiveWorkbook.Worksheets("Foglio4").Sort.SortFields.Add Key:=Range( _
            "AD6:AD" & (5 + .Cells(6, 36))), SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:= _
            xlSortNormal
        With ActiveWorkbook.Worksheets("Foglio4").Sort
            .SetRange Range("AD5:AI" & (5 + Foglio4.Cells(6, 36)))
            .Header = xlYes
            .MatchCase = False
            .Orientation = xlTopToBottom
            .SortMethod = xlPinYin
            .Apply
        End With
        'intervallo di variazione asse neutro
        x1 = Application.Min(Foglio4.Range("AG10:AG" & (5 + .Cells(6, 36))))
        x2 = Application.Max(Foglio4.Range("AG10:AG" & (5 + .Cells(6, 36))))
    End With
    'output su Fg1
    With Foglio1
        .Activate
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "VERIFICA ALLO STATO LIMITE (SLU) DI DUTTILITA' DELLA SEZIONE"
        .Cells(iF1 + 1, 1) = "sforzo normale di progetto,   Ned=Nx=" & Ned / fmF & umForze
        .Cells(iF1 + 2, 1) = "forza assiale adimensionalizzata di progetto,   vd=Ned/Ac*fcd=" & Round(Abs(Ned) / (Asez * fcd), 3)
        .Cells(iF1 + 3, 1) = "momento di fessurazione,   Mf=" & FormatNumber(Mfess / fmFL, 2, , , vbTrue) & umMomenti
        .Cells(iF1 + 4, 1) = "momento di snervamento dell'armatura tesa,   Msn_f=" & FormatNumber(Msnerv_f / fmFL, 2, , , vbTrue) & umMomenti
        .Cells(iF1 + 5, 1) = "curvatura allo snervamento dell'armatura tesa,   Ksn_f=" & Round(CurvSnerv_f * fmL * 100, 6) & "   1/m" '& umL
        iF1 = iF1 + 6
        If blnParabRettang Or blnTriangRettang Then
            .Cells(iF1, 1) = "momento di snervamento del cls compresso,   Msn_c=" & FormatNumber(Msnerv_c / fmFL, 2, , , vbTrue) & umMomenti
            .Cells(iF1 + 1, 1) = "curvatura allo snervamento del cls compresso,   Ksn_c=" & Round(CurvSnerv_c * fmL * 100, 6) & "   1/m" '& umL
            iF1 = iF1 + 2
        End If
        .Cells(iF1, 1) = "momento di resistenza della sezione,   Myu=" & FormatNumber(Myu_s / fmFL, 2, , , vbTrue) & umMomenti
        .Cells(iF1 + 1, 1) = "curvatura allo stato ultimo di rottura della sezione,   Ku=" & Round(Curv_u * fmL * 100, 6) & "   1/m" '& umL
        .Cells(iF1 + 2, 1) = "curvatura convenzionale di prima plasticizzazione della sezione,   Kyd=" & Round(CurvPrimaPlast * fmL * 100, 6) & "   1/m" '& umL
        .Cells(iF1 + 3, 1) = "intervallo di variazione dell'asse neutro (x1=" & Round(x1, 2) & umL & "   x2=" & Round(x2, 2) & umL & ")"
        .Cells(iF1 + 4, 1) = "duttilit‡ della sezione = " & Round(Duttilit‡Sez, 2)
        iF1 = iF1 + 6
    End With
Else 'sforzo normale non sopportabile
    With Foglio1
        .Activate
        .Cells(iF1, 1).Select
        FormattaCella True, TipoCaratt, Hcaratt + 2, False, True, 0, False, False
        .Cells(iF1, 1) = "VERIFICA ALLO STATO LIMITE (SLU) DI DUTTILITA' DELLA SEZIONE"
        .Range(.Cells(iF1 + 1, 1), .Cells(iF1 + 2, 1)).Select
        FormattaCella True, TipoCaratt, Hcaratt, False, False, 3, False, False
        .Cells(iF1 + 1, 1) = "Verifica di duttilit‡ non soddisfatta (il diagramma momenti-curvature non puÚ essere costruito"
        .Cells(iF1 + 2, 1) = "in quanto lo sforzo normale agente nella sezione supera quello massimo sopportabile)"
        iF1 = iF1 + 4
    End With
End If
End Sub

Sub Calcola_Nx_My_1(Epsf#) '4.8.1
'Diagramma momenti-curvatura: calcola Nx e My per fissata posizione asse neutro x<=0 (sezione tutta tesa) e deformazione massima
'nell'acciaio Epsf nota
Dim Afi#
Dim Deltz1#, Deltz#
Dim Eps_fi#
Dim i%
Dim Ns%
Dim Sig_ci#, Sig_cic# 'tensione cls confinato striscia i-esima
Dim Sig_fi#, Sig_frp#
'1. input e impostazioni
If Foglio2.Cells(29, 12) = "" Then Deltz1 = 0 Else Deltz1 = Foglio2.Cells(29, 12) * fmL
Nx_ = 0
My_ = 0
'2. contributo cls teso se FRC
If CemFRC Then
    Ns = Int(H / Deltz1) + 1
    Deltz = H / Ns
    For i = 1 To Ns Step 1
        zci = Zs_min + Deltz / 2 + Deltz * (i - 1)
        Calcola_Lsi_yci zci
        If CemFRC And (Eps_Fu < Eps_su Or Nbar = 0) Then
            Eps_ci = (Zs_min - zci + x) * Eps_Fu / (H - x) '<0
        Else
            Eps_ci = (Zs_min - zci + x) * Eps_su / (Hu - x) '<0
        End If
        Sig_ci = f_Sigc(Eps_ci)
        Nx_ = Nx_ + Sig_ci * Lsi * Deltz
        My_ = My_ + Sig_ci * Lsi * Deltz * zci
    Next i
End If
'3. contributo dell'acciaio
Zb_max = Application.Max(Zb())
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    'calcola deformazine della barra i-esima
    If CemFRC And Eps_Fu < Epsf Then
        Eps_fi = -(Zs_min - Zb(i) + x) * Eps_Fu / (H - x) '>0
    ElseIf RinfFRP And (Eps_pu + Eps0f) < Epsf And Zfrp > Zb_max Then
        Eps_fi = -(Zs_min - Zb(i) + x) * (Eps_pu + Eps0f) / (H - x) '>0
    Else
        Eps_fi = -(Zs_min - Zb(i) + x) * Epsf / (Hu - x)
    End If
    If CemArmOrd Then
        Sig_fi = f_Sigf(Eps_fi)
    ElseIf CemCAP Then
        If TondArmonico(i) Then
            Sig_fi = f_Sigf(Eps_fi + Eps0)
        Else
            Sig_fi = f_Sigf2(Eps_fi)
        End If
    End If
    Nx_ = Nx_ + Afi * Sig_fi
    My_ = My_ + Afi * Sig_fi * Zb(i)
Next i
'4. contributo del FRP
If RinfFRP Then
    If (Eps_pu + Eps0f) < Epsf And Zfrp > Zb_max Then
        Eps_frp = -(Zs_min - Zfrp + x) * (Eps_pu + Eps0f) / (H - x) '>0
        Sig_frp = (Eps_frp - Eps0f) * E_frp
    Else
        Eps_frp = -(Zs_min - Zfrp + x) * Epsf / (Hu - x)
        If Eps_frp < 0 Or Eps_frp > Eps_pu + Eps0f Then
            Sig_frp = 0 'si rompe il FRP
        Else
            Sig_frp = (Eps_frp - Eps0f) * E_frp
        End If
    End If
    Nx_ = Nx_ + A_frp * Sig_frp
    My_ = My_ + A_frp * Sig_frp * Zfrp
End If
End Sub

Sub Calcola_Nx_My_2(Epsc#) '4.8.2
'Diagramma momenti-curvatura: calcola Nx e My per fissata posizione asse neutro 0<x<=H e deformazione massima Epsc nel cls
Dim Afi#
Dim Deltz1#, Deltz#
Dim Eps_ci#, Eps_fi# ', Epsf#
Dim i%
Dim y_i#, yfi#
Dim Ns%
Dim Sig_ci#, Sig_cic# 'tensione cls confinato striscia i-esima
Dim Sig_fi#, Sig_frp#
Dim zci#
'1. input e impostazioni
If Foglio2.Cells(29, 12) = "" Then Deltz1 = 0 Else Deltz1 = Foglio2.Cells(29, 12) * fmL
If CemFRC Then
    Ns = Int(H / Deltz1) + 1
    Deltz = H / Ns
Else
    Ns = Int(x / Deltz1) + 1
    Deltz = x / Ns
End If
Nx_ = 0
My_ = 0
'2. contributo cls compresso
For i = 1 To Ns Step 1
    zci = Zs_min + Deltz / 2 + Deltz * (i - 1)
    Calcola_Lsi_yci zci
    y_i = Zs_min + x - zci
    Eps_ci = y_i * Epsc / x
    Sig_ci = f_Sigc(Eps_ci)
    If blnConfinStaffe And Eps_ci > 0 And zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
        Sig_cic = f_Sigc2(Eps_ci)
        Nx_ = Nx_ + Sig_ci * (2 * Cf) * Deltz + Sig_cic * (Lsi - 2 * Cf) * Deltz
        My_ = My_ + Sig_ci * (2 * Cf) * Deltz * zci + Sig_cic * (Lsi - 2 * Cf) * Deltz * zci
    Else
        Nx_ = Nx_ + Sig_ci * Lsi * Deltz
        My_ = My_ + Sig_ci * Lsi * Deltz * zci
    End If
Next i
'3. contributo delle armature tese e compresse
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    'yfi = Abs(Zs_min) + Zb(i) - x
    yfi = -(Zs_min - Zb(i) + x)
    Eps_fi = yfi * Epsc / x
    If CemArmOrd Then
        Sig_fi = f_Sigf(Eps_fi)
    ElseIf CemCAP Then
        If TondArmonico(i) Then 'barra da precompresso
            Sig_fi = f_Sigf(Eps_fi + Eps0)
        Else
            Sig_fi = f_Sigf2(Eps_fi)
        End If
    End If
    Nx_ = Nx_ + Afi * Sig_fi
    My_ = My_ + Afi * Sig_fi * Zb(i)
Next i
'4. contributo del composito FRP
If RinfFRP Then
    Eps_frp = -(Zs_min - Zfrp + x) * Epsc / x
    If Eps_frp < 0 Or Eps_frp > Eps_pu + Eps0f Then 'compressione o si rompe il FRP
        Eps_frp = Eps0f
    End If
    Sig_frp = (Eps_frp - Eps0f) * E_frp
    Nx_ = Nx_ + A_frp * Sig_frp
    My_ = My_ + A_frp * Sig_frp * Zfrp
End If
End Sub

Sub Calcola_Nx_My_3(Epsc#) '4.8.3
'Diagramma momenti-curvatura: calcola Nx e My per fissata posizione asse neutro x>H e deformazione massima Epsc nel cls
'sezione tutta compressa
Dim Afi#
Dim Deltz1#, Deltz#
Dim Eps_ci#, Eps_fi# ', Epsf#
Dim i%
Dim y_i#, yfi#
Dim Ns%
Dim Sig_ci#, Sig_cic# 'tensione cls confinato striscia i-esima
Dim Sig_fi#
Dim zci#
'1. input e impostazioni
If Foglio2.Cells(29, 12) = "" Then Deltz1 = 0 Else Deltz1 = Foglio2.Cells(29, 12) * fmL
Ns = Int(H / Deltz1) + 1
Deltz = H / Ns
Nx_ = 0
My_ = 0
'2. contributo cls compresso
For i = 1 To Ns Step 1
    y_i = x - H + Deltz / 2 + Deltz * (i - 1)
    zci = Zs_min + x - y_i
    Calcola_Lsi_yci zci
    Eps_ci = y_i * Epsc / x
    Sig_ci = f_Sigc(Eps_ci)
    If blnConfinStaffe And zci <= (Zs_max - Cf) And zci >= (Zs_min + Cf) And (Lsi - 2 * Cf) > 0 Then
        Sig_cic = f_Sigc2(Eps_ci)
        Nx_ = Nx_ + Sig_ci * (2 * Cf) * Deltz + Sig_cic * (Lsi - 2 * Cf) * Deltz
        My_ = My_ + Sig_ci * (2 * Cf) * Deltz * zci + Sig_cic * (Lsi - 2 * Cf) * Deltz * zci
    Else
        Nx_ = Nx_ + Sig_ci * Lsi * Deltz
        My_ = My_ + Sig_ci * Lsi * Deltz * zci
    End If
Next i
'3. contributo delle armature
For i = 1 To Nbar Step 1
    Afi = PiGreco * Db(i) ^ 2 / 4
    yfi = -(Zs_min - Zb(i) + x)
    Eps_fi = yfi * Epsc / x
    If CemArmOrd Then
        Sig_fi = f_Sigf(Eps_fi)
    ElseIf CemCAP Then 'c.a.p.
        If TondArmonico(i) Then  'barra da precompresso
            Sig_fi = f_Sigf(Eps_fi + Eps0)
        Else
            Sig_fi = f_Sigf2(Eps_fi)
        End If
    End If
    Nx_ = Nx_ + Afi * Sig_fi
    My_ = My_ + Afi * Sig_fi * Zb(i)
Next i
'4. Il contributo dell'eventuale FRP non c'Ë, essendo la sezione tutta compressa
End Sub

Sub VerifResistCA_SLU_TensNorm_xCarPunta() '8.2
'per una sez in c.a. di forma qualunque soggetta a Nx e My, propri della verifica a carico di punta, effettua la verifica allo SLU
'(tensioni normali) costruendo il dominio di rottura Nx-My
Dim Ecc#, i%, i1%, j%
Dim My_i#, Nx_i#, My_i1#, Nx_i1#
Dim m#, q#, Myu#()
Dim MRy_s#, MRy_i#, MRz_s#, MRz_i#, MRz#, MRy#
Dim Myu_max#, Myu_min# ', Myu_s#, Myu_i#
'1)INPUT
'sollecitazioni di progetto
Ned = Nx
Medy = My
Medz = Mz
'coordinate barre rispetto al sistema yz baricentrico della sezione omogeneizzata
If Nbar > 0 Then
    ReDim Zb#(1 To Nbar)
    ReDim Yb#(1 To Nbar)
End If
For i = 1 To Nbar Step 1
    Zb(i) = Zb_pr(i) - zG_pr
    Yb(i) = Yb_pr(i) - yG_pr
Next i
Deltz1 = 0.2 * fmL 'spessore di 2 mm circa degli straterelli di cls in cui si divide la parte compressa della sezione
VerifCarPunta = True
'2)DETERMINA VALORI ESTREMI SFORZO NORMALE
Nu_max = Aft * fyd
Nu_min = -fcd * Asez - Aft * f_Sigf(Eps_c2)
'3)VERIFICA DI RESISTENZA
If Nx <= Nu_max And Nx >= Nu_min Then
    'pallino rosso in dominio
    Foglio4.Cells(2, 10) = Ned / fmF
    Foglio4.Cells(2, 11) = Medy / fmFL
    'costruisci dominio di rottura My-N
    AsseNeutroTrovato = True
    DominioRotturaMyNx '4.7.2
    'verifica analitica
    ReDim Myu#(1 To 10)
    j = 0
    For i = 1 To 208 Step 1
        If i = 208 Then
            i1 = 1
        Else
            i1 = i + 1
        End If
        My_i = Foglio4.Cells(4 + i, 11) * fmFL
        Nx_i = Foglio4.Cells(4 + i, 10) * fmF
        My_i1 = Foglio4.Cells(4 + i1, 11) * fmFL
        Nx_i1 = Foglio4.Cells(4 + i1, 10) * fmF
        If (Ned >= Nx_i1 And Ned <= Nx_i) Or (Ned >= Nx_i And Ned <= Nx_i1) Then
            j = j + 1
            'retta che passa per i e i1
            m = (My_i1 - My_i) / (Nx_i1 - Nx_i)
            q = My_i - m * Nx_i
            Myu(j) = m * Ned + q
        End If
    Next i
    Myu_s = Application.Max(Myu())
    Myu_i = Application.Min(Myu())
    If Medy >= Myu_i And Medy <= Myu_s Then
        VerifResist = True
    Else
        VerifResist = False
    End If
Else 'il dominio non esiste
    VerifResist = False
End If
End Sub

Sub Calcola_Lsi_yci(Z#)
'calcola la lunghezza dello straterello di cls e la distanza del suo baricentro rispetto all'asse z
Dim k%, j%, i%, i1%, yf#, Yff#(1 To 40), Appogg#, L#, Sz#, Ys#(), Zs#()
Dim R#, Ri#, Fi#, b_e#, b_i#, Fi_i#
If FormSez <> "Circolare piena o cava" Then
    k = 0
    For j = 1 To Npolig Step 1
        'carica coordinate poligonale j e riferiscili al sistema yz
        CaricaDaFg2CoordPolig j '1.2
        If Np > 0 Then
            ReDim Ys#(1 To Np)
            ReDim Zs#(1 To Np)
            ReDim Ysc#(1 To Np)
            ReDim Zsc#(1 To Np)
        End If
        For i = 1 To Np Step 1
            Ys(i) = Ys_pr(i) - yG_pr
            Zs(i) = Zs_pr(i) - zG_pr
            Ysc(i) = Ys(i) * CosAlfa_ii + Zs(i) * SinAlfa_ii
            Zsc(i) = -Ys(i) * SinAlfa_ii + Zs(i) * CosAlfa_ii
        Next i
        'punti di intersezione con poligonale j
        For i = 1 To Np Step 1
            If i = Np Then
                i1 = 1
            Else
                i1 = i + 1
            End If
            If Round(Zsc(i), 5) <> Round(Zsc(i1), 5) Then
                If (Z >= Zsc(i) And Z <= Zsc(i1)) Or (Z >= Zsc(i1) And Z <= Zsc(i)) Then
                    k = k + 1
                    yf = ((Z - Zsc(i)) * (Ysc(i1) - Ysc(i)) + (Zsc(i1) - Zsc(i)) * Ysc(i)) / (Zsc(i1) - Zsc(i))
                    Yff(k) = yf
                End If
            End If
        Next i
    Next j
    'ordina elementi del vettore Yff_pr
    For i = 1 To k Step 1
        For j = i + 1 To k Step 1
            If Yff(j) < Yff(i) Then
                Appogg = Yff(j)
                Yff(j) = Yff(i)
                Yff(i) = Appogg
            End If
        Next j
    Next i
    'calcola lunghezza striscia
    Lsi = 0
    Sz = 0
    For i = 1 To k / 2 Step 1
        L = Yff(2 * i) - Yff(2 * i - 1)
        Lsi = Lsi + L
        Sz = Sz + L * (Yff(2 * i) + Yff(2 * i - 1)) / 2
    Next i
    'e distanza del baricentro della striscia dall'asse z
    yci = Sz / Lsi
ElseIf FormSez = "Circolare piena o cava" Then
    R = D / 2
    Ri = Di / 2
    If (Z >= Ri And Z <= R) Or (Z >= -R And Z <= -Ri) Then
        Fi = Application.Acos(Z / R)
        Lsi = 2 * R * Sin(Fi)
    Else
        Fi = Application.Acos(Z / R)
        b_e = 2 * R * Sin(Fi)
        Fi_i = Application.Acos(Z / Ri)
        b_i = 2 * Ri * Sin(Fi_i)
        Lsi = b_e - b_i
    End If
    yci = 0
End If
End Sub

Function f_Sigf#(Eps#)
'calcola la tensione nella barra di acciaio (>0 trazione, <0 compressione) nota la sua deformazione Eps (>0 trazione, <0 compress)
If Abs(Eps) < Eps_yd Then
    f_Sigf = Es * Eps
ElseIf Round(Abs(Eps), 5) <= Eps_su Then
    If blnElastPerfettPlastico Then
        If Eps > 0 Then
            f_Sigf = fyd
        Else
            f_Sigf = -fyd
        End If
    ElseIf blnBilineare Then
        If Eps > 0 Then
            f_Sigf = fyd + (Kincr * fyd - fyd) * (Eps - Eps_yd) / (Eps_su - Eps_yd)
        Else
            f_Sigf = -(fyd + (Kincr * fyd - fyd) * (Eps - Eps_yd) / (Eps_su - Eps_yd))
        End If
    End If
Else
    f_Sigf = 0
End If
End Function

Function f_Sigf2#(Eps#)
'calcola tensione acciaio (>0 trazione, <0 compressione) nota la sua deformazione Eps (>0 trazione, <0 compress) nelle barre di
'acciaio ordinario eventualmente presente nella sezione in C.A.P.
If Abs(Eps) < Eps_yd2 Then
    f_Sigf2 = Es * Eps
ElseIf Round(Abs(Eps), 5) <= Eps_su Then
    If blnElastPerfettPlastico Then
        If Eps > 0 Then
            f_Sigf2 = fyd2
        Else
            f_Sigf2 = -fyd2
        End If
    ElseIf blnBilineare Then
        If Eps > 0 Then
            f_Sigf2 = fyd2 + (Kincr * fyd2 - fyd2) * (Eps - Eps_yd2) / (Eps_su - Eps_yd2)
        Else
            f_Sigf2 = -(fyd2 + (Kincr * fyd2 - fyd2) * (Eps - Eps_yd2) / (Eps_su - Eps_yd2))
        End If
    End If
Else
    f_Sigf2 = 0
End If
End Function

Function f_Sigf_es#(Eps#)
'calcola la tensione nella barra di acciaio esistente (>0 trazione, <0 compressione) nota la sua deformazione Eps (>0 trazione, <0 compress)
'rinforzo con incamiciatura in c.a.
If Abs(Eps) < Eps_yd_e Then
    f_Sigf_es = Es * Eps
ElseIf Round(Abs(Eps), 5) <= Eps_su Then
    If blnElastPerfettPlastico Then
        If Eps > 0 Then
            f_Sigf_es = fyd_e
        Else
            f_Sigf_es = -fyd_e
        End If
    ElseIf blnBilineare Then
        If Eps > 0 Then
            f_Sigf_es = fyd_e + (Kincr * fyd_e - fyd_e) * (Eps - Eps_yd_e) / (Eps_su - Eps_yd_e)
        Else
            f_Sigf_es = -(fyd_e + (Kincr * fyd_e - fyd_e) * (Eps - Eps_yd_e) / (Eps_su - Eps_yd_e))
        End If
    End If
Else
    f_Sigf_es = 0
End If
End Function

Function f_Sigc#(Eps#)
'calcola la tensione nel cls (>0 trazione, <0 compressione), nota la deformazione Eps (>0 compress, <0 trazione)
If Eps >= 0 Then 'tensione di compressione <0
    If blnConfinFRP Or blnConfinCamicieAcc Then 'cls confinato con FRP o calastrelli: fccd e Eps_cuc (Eps_c2 Ë quello del cls non confinato)
        'diagramma parabola rettangolo
        If Eps < Eps_c2 Then
            f_Sigc = -(-fccd * Eps ^ 2 / (Eps_c2 ^ 2) + 2 * fccd * Eps / Eps_c2)
        ElseIf Round(Eps, 5) <= Eps_cuc Then
            f_Sigc = -fccd
        Else
            f_Sigc = 0
        End If
    Else 'cls non confinato
        If blnParabRettang Then
            If Eps < Eps_c2 Then
                f_Sigc = -(-fcd * Eps ^ 2 / (Eps_c2 ^ 2) + 2 * fcd * Eps / Eps_c2)
            ElseIf Round(Eps, 5) <= Eps_cu Then
                f_Sigc = -fcd
            Else
                f_Sigc = 0
            End If
        ElseIf blnTriangRettang Then
            If Eps < Eps_c3 Then
                f_Sigc = -fcd * Eps / Eps_c3
            ElseIf Round(Eps, 5) <= Eps_cu Then
                f_Sigc = -fcd
            Else
                f_Sigc = 0
            End If
        ElseIf blnStressBlock Then
            If Eps < Eps_c4 Then
                f_Sigc = 0
            ElseIf Round(Eps, 5) <= Eps_cu Then
                f_Sigc = -fcd
            Else
                f_Sigc = 0
            End If
        End If
    End If
ElseIf Eps < 0 Then 'tensione di trazione >0
    If Eps >= -Eps_Fs Then
        f_Sigc = -fFts * Eps / Eps_Fs
    ElseIf Round(Eps, 5) >= -Eps_Fu Then
        f_Sigc = fFts + (fFtu - fFts) * (-Eps - Eps_Fs) / (Eps_Fu - Eps_Fs)
    Else
        f_Sigc = 0
    End If
End If
End Function

Function f_Sigc2#(Eps#)
'calcola la tensione nel cls confinato (Eps Ë di compressione quindi >0, sig<0) con staffe e legature, nota la deformazione Eps
'diagr solo parabola-rettangolo per la parte a compressione
'If Eps >= 0 Then 'tensione di compressione <0
    If Eps < Eps_c2c Then
        f_Sigc2 = -(-fcd_c * Eps ^ 2 / (Eps_c2c ^ 2) + 2 * fcd_c * Eps / Eps_c2c)
    ElseIf Round(Eps, 5) <= Eps_cuc Then
        f_Sigc2 = -fcd_c
    Else
        f_Sigc2 = 0
    End If
'ElseIf Eps < 0 Then 'tensione di trazione >0
    'If Eps >= -Eps_Fs Then
        'f_Sigc2 = -fFts * Eps / Eps_Fs
    'ElseIf Round(Eps, 5) >= -Eps_Fu Then
        'f_Sigc2 = fFts + (fFtu - fFts) * (-Eps - Eps_Fs) / (Eps_Fu - Eps_Fs)
    'Else
        'f_Sigc2 = 0
    'End If
'End If
End Function

Sub OutNuMyuSuFg4()
With Foglio4
    If VerifCarPunta = False Then
        .Cells(4 + j, 1) = Nu / fmF
        .Cells(4 + j, 2) = Myu / fmFL
        .Cells(4 + j, 3) = x / fmL
    Else
        .Cells(4 + j, 10) = Nu / fmF
        .Cells(4 + j, 11) = Myu / fmFL
        .Cells(4 + j, 12) = x / fmL
    End If
    j = j + 1
End With
End Sub

Sub OutNuMzuSuFg4()
With Foglio4
    .Cells(4 + j, 5) = Nu / fmF
    .Cells(4 + j, 6) = Mzu / fmFL
    .Cells(4 + j, 7) = x / fmL
    j = j + 1
End With
End Sub
