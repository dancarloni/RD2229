param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$BasPath,
    [Parameter(Mandatory=$true)][string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Open((Resolve-Path $InputPath))

    # Abilita manualmente: Opzioni -> Centro protezione -> Impostazioni ->
    # "Considera attendibile l'accesso al modello a oggetti di progetto VBA"

    $vbProj = $wb.VBProject
    $vbProj.VBComponents.Import((Resolve-Path $BasPath)) | Out-Null

    $xlOpenXMLWorkbookMacroEnabled = 52
    $wb.SaveAs((Resolve-Path $OutputPath), $xlOpenXMLWorkbookMacroEnabled)
}
finally {
    if ($null -ne $wb) { $wb.Close($true) }
    if ($null -ne $excel) { $excel.Quit() }
}
