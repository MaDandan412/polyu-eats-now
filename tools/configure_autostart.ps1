param([switch]$Disable)
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
$pythonWindowless = Join-Path $projectDirectory '.venv\Scripts\pythonw.exe'
$loginLauncher = Join-Path $projectDirectory 'tools\login_start.py'
$startupDirectory = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDirectory 'PolyU Eats Now.lnk'
$runtimeDirectory = Join-Path $projectDirectory '.runtime'
$watchdogDisabledPath = Join-Path $runtimeDirectory 'watchdog.disabled'
$launcherArguments = '"' + $loginLauncher + '"'
$shellObject = New-Object -ComObject WScript.Shell

# Touch only the shortcut owned by this exact project, even after moving folders.
if (Test-Path -LiteralPath $shortcutPath) {
    $existingShortcut = $shellObject.CreateShortcut($shortcutPath)
    if ($existingShortcut.TargetPath -ne $pythonWindowless -or $existingShortcut.Arguments -ne $launcherArguments) {
        throw 'A different shortcut already uses this name. Nothing was changed.'
    }
}

if ($Disable) {
    if (Test-Path -LiteralPath $shortcutPath) {
        Remove-Item -LiteralPath $shortcutPath
    }
    New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
    Set-Content -LiteralPath $watchdogDisabledPath -Value 'disabled' -Encoding UTF8
    Write-Output 'Automatic startup disabled. Background watchdog stops after its current check; the running app stays available.'
    exit 0
}

if (-not (Test-Path -LiteralPath $pythonWindowless) -or -not (Test-Path -LiteralPath $loginLauncher)) {
    throw 'Install project dependencies with start.ps1 -Setup first.'
}
$shortcut = $shellObject.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonWindowless
$shortcut.Arguments = $launcherArguments
$shortcut.WorkingDirectory = $projectDirectory
$shortcut.WindowStyle = 7
$shortcut.Description = 'Start PolyU Eats Now at sign-in and recover a stopped backend'
$shortcut.Save()

New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
if (Test-Path -LiteralPath $watchdogDisabledPath) {
    Remove-Item -LiteralPath $watchdogDisabledPath
}
@{shortcut=$shortcutPath; target=$pythonWindowless; arguments=$launcherArguments; trigger='current-user-sign-in'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimeDirectory 'autostart.json') -Encoding UTF8
Write-Output ('Automatic startup enabled: ' + $shortcutPath)
