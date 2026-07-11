param(
    [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path $ProjectRoot).Path
$SourceRoot = Join-Path $PSScriptRoot "files"

if (-not (Test-Path (Join-Path $ProjectRoot "app\main.py"))) {
    throw "ProjectRoot must be the flyrank_pdf_report_generator folder containing app\main.py."
}

Write-Host "Applying AI feature to: $ProjectRoot"

Get-ChildItem -Path $SourceRoot -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Substring($SourceRoot.Length).TrimStart("\", "/")
    $destination = Join-Path $ProjectRoot $relativePath
    $destinationDirectory = Split-Path $destination -Parent

    if (-not (Test-Path $destinationDirectory)) {
        New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
    }

    Copy-Item $_.FullName $destination -Force
    Write-Host "  updated $relativePath"
}

Write-Host ""
Write-Host "Implementation applied successfully."
Write-Host "Your existing .env was not touched."
Write-Host "Add GROQ_API_KEY to .env, then rebuild and run the tests."
