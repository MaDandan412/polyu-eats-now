param([switch]$Setup)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
function Assert-Success([string]$Step) {
  if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE)." }
}
if ($Setup) {
  python -m venv .venv
  Assert-Success 'Create Python environment'
  & '.\.venv\Scripts\python.exe' -m pip install -r backend/requirements.txt
  Assert-Success 'Install backend dependencies'
  & '.\.venv\Scripts\python.exe' -m playwright install chromium
  Assert-Success 'Install status-check browser'
  Push-Location frontend
  try {
    npm.cmd ci
    Assert-Success 'Install frontend dependencies'
    npm.cmd run build
    Assert-Success 'Build frontend'
  } finally { Pop-Location }
}
if (!(Test-Path -LiteralPath '.\.venv\Scripts\python.exe') -or !(Test-Path -LiteralPath '.\frontend\dist\index.html')) {
  throw 'First run: .\start.ps1 -Setup (requires Python 3.10+ and Node 20.19+).'
}
try {
  $foodNowHealth = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2
  if ($foodNowHealth.app -eq 'polyu-food-now') {
    Write-Host 'PolyU Eats Now is already running: http://127.0.0.1:8000'
    exit 0
  }
} catch { }
Write-Host 'PolyU Eats Now: http://127.0.0.1:8000'
Write-Host 'Live checks run in the background. Press Ctrl+C to stop.'
& '.\.venv\Scripts\python.exe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
