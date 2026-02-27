Param()

$ErrorActionPreference = 'Stop'
Write-Output "Running elevated pre-commit maintenance script"

try {
    Write-Output "Taking ownership of user pre-commit cache..."
    & takeown /F "$env:USERPROFILE\.cache\pre-commit" /R /A | Write-Output
} catch {
    Write-Output "takeown may have failed or not needed: $_"
}

try {
    Write-Output "Granting full control to current user..."
    & icacls "$env:USERPROFILE\.cache\pre-commit" /grant "$env:USERNAME:F" /T | Write-Output
} catch {
    Write-Output "icacls may have failed or not needed: $_"
}

try {
    Write-Output "Removing user pre-commit cache..."
    Remove-Item -LiteralPath "$env:USERPROFILE\.cache\pre-commit" -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-Output "Remove-Item user cache error (non fatal): $_"
}

try {
    Write-Output "Removing repo local pre-commit cache if exists..."
    Remove-Item -LiteralPath "${PWD}\\.pre-commit-cache" -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-Output "Remove-Item repo cache error (non fatal): $_"
}

Write-Output "Creating fresh repo local cache and running pre-commit..."
New-Item -ItemType Directory -Path "${PWD}\\.pre-commit-cache" -ErrorAction SilentlyContinue | Out-Null
$env:PRE_COMMIT_HOME = (Resolve-Path ".pre-commit-cache").Path
Write-Output "PRE_COMMIT_HOME=$env:PRE_COMMIT_HOME"

try {
    py -3 -m pre_commit run --all-files
} catch {
    Write-Output "pre-commit run failed: $_"
    exit 1
}

Write-Output "Done"
