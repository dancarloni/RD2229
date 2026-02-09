# Script eseguito con privilegi elevati per pulire cache pre-commit e rilanciare i hook
$ErrorActionPreference = 'Stop'

# Use a pre-commit cache located inside the project's .venv to avoid
# cross-user permission problems on Windows.
$ErrorActionPreference = 'Stop'
Write-Output "Running elevated pre-commit maintenance script (venv-local cache)"

$repo = (Resolve-Path ".").Path
$venv_cache = Join-Path $repo '.venv\.cache\pre-commit'
Write-Output "Ensuring venv cache exists: $venv_cache"
New-Item -ItemType Directory -Path $venv_cache -Force | Out-Null

try {
    Write-Output "Taking ownership and granting full control to current user on venv cache..."
    & takeown /F $venv_cache /R /A | Write-Output
    & icacls $venv_cache /grant "$env:USERNAME:F" /T | Write-Output
} catch {
    Write-Output "Ownership/ACL operations may have failed or not needed: $_"
}

try {
    Write-Output "Clearing read-only attribute from repository files..."
    cmd /c attrib -R "${repo}\*.*" /S
} catch {
    Write-Output "attrib failed (non fatal): $_"
}

Write-Output "Setting PRE_COMMIT_HOME to venv cache and running pre-commit"
$env:PRE_COMMIT_HOME = $venv_cache
Write-Output "PRE_COMMIT_HOME=$env:PRE_COMMIT_HOME"

try {
    & "${repo}\.venv\Scripts\python.exe" -m pre_commit run --all-files
} catch {
    Write-Output "pre-commit run failed: $_"
    exit 1
}

Write-Output "Done"
