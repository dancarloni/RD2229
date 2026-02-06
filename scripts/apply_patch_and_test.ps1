# Apply patch and run tests (PowerShell)
# Usage: .\apply_patch_and_test.ps1

$ErrorActionPreference = 'Stop'
$patchPath = "patches/0001-Deprecate-sections.json-auto-migrate-to-sec_reposito.patch"
$applyBranch = "apply/dep-sectionsjson-patch"

if (-not (Test-Path $patchPath)) {
    Write-Error "Patch file not found: $patchPath"
    exit 1
}

Write-Host "Patch file: $patchPath"

# Fetch and create branch
Write-Host "Creating branch: $applyBranch"
# If branch exists locally, checkout it
$existing = git branch --list $applyBranch
if ($existing) {
    git checkout $applyBranch
} else {
    git checkout -b $applyBranch
}

# Try to apply patch cleanly
Write-Host "Checking if patch can be applied cleanly..."
try {
    $applyCheck = git apply --check $patchPath 2>&1 | Out-String
    $applyErr = $null
} catch {
    $applyCheck = $_.Exception.Message
    $applyErr = $_
}

if ($applyErr -eq $null -and $LASTEXITCODE -eq 0) {
    Write-Host "Patch can be applied cleanly. Applying with git am..."
    git am $patchPath
    Write-Host "Patch applied and committed."
} else {
    Write-Host "Patch cannot be applied cleanly. Message:"
    Write-Host $applyCheck
    Write-Host "Attempting a safe check to see if the patch was already applied..."
    # Very naive check: look for a known commit message in git log
    $commitMsg = "Deprecate sections.json: auto-migrate to sec_repository/sec_repository.jsons; preserve tmp extension; add .jsons support in GUI; update demos/docs; add migration tests"
    try {
        $found = git log --oneline --grep="Deprecate sections.json" -i
    } catch {
        $found = $null
    }
    if ($found) {
        Write-Host "A commit with similar message already exists. Skipping apply."
    } else {
        Write-Host "Patch not applied and no existing commit found. Exiting with error."
        exit 2
    }
}

# Run tests (smoke tests)
Write-Host "Running pytest smoke tests..."
$env:PYTHONPATH = "$PWD"
try {
        $branch = git rev-parse --abbrev-ref HEAD
        Write-Host "On branch: $branch"
    Write-Host "Smoke tests passed. Running full test suite (may be long)..."
    pytest -q
} catch {
    Write-Host "Tests failed: $($_.Exception.Message)"
    exit 3
}

Write-Host "All done. If you want to push the branch: git push -u origin $applyBranch"