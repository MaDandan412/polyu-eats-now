param([switch]$Disable)
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
$pythonWindowless = Join-Path $projectDirectory '.venv\Scripts\pythonw.exe'
$loginLauncher = Join-Path $projectDirectory 'tools\login_start.py'
$startupDirectory = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDirectory 'PolyU Eats Now.lnk'
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
    Write-Output 'Automatic startup disabled. Currently running app stays available.'
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
$shortcut.Description = 'Start PolyU Eats Now and live checks when signing in to Windows'
$shortcut.Save()

$runtimeDirectory = Join-Path $projectDirectory '.runtime'
New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
@{shortcut=$shortcutPath; target=$pythonWindowless; arguments=$launcherArguments; trigger='current-user-sign-in'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimeDirectory 'autostart.json') -Encoding UTF8
Write-Output ('Automatic startup enabled: ' + $shortcutPath)
