$ErrorActionPreference = "Stop"
$root = $PSScriptRoot   # folder this script lives in (src/)

function Start-Labeled($title, $color, $workDir, $command) {
    # Build a small wrapper command that sets the window title, colors
    # the host, and then runs the real command.
    $inner = @"
`$Host.UI.RawUI.WindowTitle = '$title'
`$Host.UI.RawUI.ForegroundColor = '$color'
Write-Host '=== $title ===' -ForegroundColor $color
Set-Location '$workDir'
$command
"@

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-Command", $inner
    )
}

Write-Host "Starting Kinetic (server, frontend, engine)..." -ForegroundColor Yellow

Start-Labeled -title "KINETIC - SERVER" -color "Cyan" `
    -workDir $root `
    -command "python server.py"

Start-Sleep -Seconds 1

Start-Labeled -title "KINETIC - FRONTEND" -color "Magenta" `
    -workDir (Join-Path $root "react_front") `
    -command "npm run dev"

Start-Sleep -Seconds 1

Start-Labeled -title "KINETIC - MAIN_CV" -color "Green" `
    -workDir (Join-Path $root "kinetic_cv") `
    -command "python main_cv.py"

Write-Host "All three windows launched. Close any window to stop that process." -ForegroundColor Yellow