$ErrorActionPreference = 'Stop'

$inputPath = "F:\StudioCallari\Condomini - Documenti\Tagliamento 20\VERIFICA CONFORMITA SISMICA\RD2229_BEAM_patch.xlsx"
$basPath = "F:\StudioCallari\Condomini - Documenti\Tagliamento 20\VERIFICA CONFORMITA SISMICA\RD2229_TA_TandC_Module_PATCH1 (1).bas"

Write-Host "Avvio Excel..." -ForegroundColor Cyan
$excel = $null
$wb = $null

try {
    # Crea istanza Excel
    $excel = New-Object -ComObject "Excel.Application"
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AutomationSecurity = 1  # msoAutomationSecurityLow
    
    Write-Host "Apertura workbook tramite reflection..." -ForegroundColor Cyan
    # Usa reflection per bypassare problemi di localizzazione
    $bindingFlags = [System.Reflection.BindingFlags]::InvokeMethod
    $wb = $excel.Workbooks.GetType().InvokeMember(
        "Open",
        $bindingFlags,
        $null,
        $excel.Workbooks,
        @($inputPath, 0, $false, 5, "", "", $false, 2, "", $true, $false, 0, $false, $false, 0)
    )
    
    Write-Host "Workbook aperto: $($wb.Name)" -ForegroundColor Green
    
    Write-Host "Importazione modulo VBA..." -ForegroundColor Cyan
    $vbComp = $wb.VBProject.VBComponents.GetType().InvokeMember(
        "Import",
        $bindingFlags,
        $null,
        $wb.VBProject.VBComponents,
        @($basPath)
    )
    
    Write-Host "Salvataggio..." -ForegroundColor Cyan
    $wb.Save()
    
    Write-Host "`nModulo VBA importato con successo nel file:" -ForegroundColor Green
    Write-Host $inputPath -ForegroundColor Green
}
catch {
    Write-Host "`nErrore durante l'importazione:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host $_.Exception.InnerException.Message -ForegroundColor Yellow
    
    if ($_.Exception.Message -match "programmazione|programmatic") {
        Write-Host "`nATTENZIONE: Devi abilitare l'accesso al modello a oggetti di progetto VBA:" -ForegroundColor Yellow
        Write-Host "1. Apri Excel" -ForegroundColor Yellow
        Write-Host "2. File -> Opzioni -> Centro protezione -> Impostazioni Centro protezione" -ForegroundColor Yellow
        Write-Host "3. Impostazioni macro -> Attiva 'Consenti l'accesso al modello a oggetti del progetto VBA'" -ForegroundColor Yellow
    }
}
finally {
    Write-Host "Chiusura Excel..." -ForegroundColor Cyan
    if ($wb) { 
        $wb.Close($true)
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($wb) | Out-Null
    }
    if ($excel) { 
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    Write-Host "Completato." -ForegroundColor Cyan
}
