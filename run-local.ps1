#!/usr/bin/env pwsh
param([string]$TargetDir = "RD2229-local")

Write-Host "Clonazione repository in: $TargetDir"
git clone https://github.com/dancarloni/RD2229.git $TargetDir

Set-Location $TargetDir

Write-Host "Creazione virtualenv .venv"
python -m venv .venv

Write-Host "Installazione dipendenze (se presente requirements.txt)"
if (Test-Path .\.venv\Scripts\python.exe) {
    . .\.venv\Scripts\Activate.ps1 2>$null
    . .\.venv\Scripts\python.exe -m pip install --upgrade pip
    if (Test-Path requirements.txt) {
        . .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    }
} else {
    Write-Warning "Python virtualenv non trovato. Assicurati che Python sia installato e raggiungibile." 
}

Write-Host "Creazione branch locale senza upstream: 'local-work'"
git checkout -b local-work
try {
    git branch --unset-upstream local-work 2>$null
} catch {
    # ignore if not supported
}

Write-Host "Setup completato. Per lavorare offline mantieni la remote ma evita comandi git remoti (fetch/pull/push)."
Write-Host "Per aprire il progetto in VS Code: code ."
