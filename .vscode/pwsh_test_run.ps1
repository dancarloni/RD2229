. $PROFILE
Write-Output '---PROFILE-LOADED---'
Write-Output 'test-history-line-1'
Write-Output 'test-history-line-2'
Start-Sleep -Milliseconds 300
$f = Join-Path $env:APPDATA 'Code\User\globalStorage\ms-vscode.powershell\history.txt'
Write-Output "HISTORY_FILE: $f"
if (Test-Path $f) {
    Write-Output 'HISTORY_EXISTS'
    Get-Content $f -Tail 40
}
else {
    Write-Output 'NO_HISTORY_FILE'
}

# Try invoking AddToHistoryHandler directly (simulates typed input)
$h = (Get-PSReadLineOption -ErrorAction SilentlyContinue).AddToHistoryHandler
if ($h) {
    Write-Output 'INVOKING_HANDLER'
    try {
        # If delegate, invoke via Invoke method
        if ($h -is [System.Delegate]) {
            $h.Invoke('simulated-typed-line-1') | Out-Null
        }
        else {
            # Fallback: try call as scriptblock
            & $h 'simulated-typed-line-1'
        }
    }
    catch {
        Write-Output "HANDLER_INVOKE_FAILED: $_"
    }
    Start-Sleep -Milliseconds 200
    if (Test-Path $f) {
        Write-Output 'HISTORY_EXISTS_AFTER_INVOKE'
        Get-Content $f -Tail 40
    }
    else {
        Write-Output 'NO_HISTORY_FILE_AFTER_INVOKE'
    }
}
else {
    Write-Output 'NO_HANDLER'
}
