param(
    [string]$SettingsModule = $env:DJANGO_SETTINGS_MODULE
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ManagePy = Join-Path $ProjectRoot "src\manage.py"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if ([string]::IsNullOrWhiteSpace($SettingsModule)) {
    $SettingsModule = "config.settings.local"
}

if (Test-Path $VenvPython) {
    $Python = $VenvPython
} else {
    $Python = "python"
}

$env:DJANGO_SETTINGS_MODULE = $SettingsModule

Write-Host "Using settings: $SettingsModule"
Write-Host "Checking migrations..."
& $Python $ManagePy makemigrations --check --dry-run

Write-Host "Applying database migrations..."
& $Python $ManagePy migrate

Write-Host "Database tables are up to date."
