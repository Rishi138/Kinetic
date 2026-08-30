$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$script:procs = @{}

function Start-Labeled($title, $color, $workDir, $command) {
    $inner = @"
`$Host.UI.RawUI.WindowTitle = '$title'
`$Host.UI.RawUI.ForegroundColor = '$color'
Write-Host '=== $title ===' -ForegroundColor $color
Set-Location '$workDir'
$command
"@

    $proc = Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-Command", $inner
    ) -PassThru

    return $proc
}

function Start-All {
    Write-Host "Starting Kinetic (server, frontend, cv)..." -ForegroundColor Yellow

    $script:procs["server"] = Start-Labeled -title "KINETIC - SERVER" -color "Cyan" `
        -workDir $root `
        -command "python server.py"

    Start-Sleep -Seconds 1

    $script:procs["frontend"] = Start-Labeled -title "KINETIC - FRONTEND" -color "Magenta" `
        -workDir (Join-Path $root "react_front") `
        -command "npm run dev"

    Start-Sleep -Seconds 1

    $script:procs["main_cv"] = Start-Labeled -title "KINETIC - MAIN_CV" -color "Green" `
        -workDir (Join-Path $root "kinetic_cv") `
        -command "python main_cv.py"

    Write-Host "All three windows launched." -ForegroundColor Yellow
}

function Stop-All {
    Write-Host "Stopping all processes..." -ForegroundColor Yellow
    foreach ($key in $script:procs.Keys) {
        $proc = $script:procs[$key]
        if ($proc -and -not $proc.HasExited) {
            try {
                # kill the whole process tree (powershell -> npm/python child)
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                Get-CimInstance Win32_Process -Filter "ParentProcessId=$($proc.Id)" |
                    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
            } catch {}
        }
    }
    $script:procs.Clear()
    Write-Host "Stopped." -ForegroundColor Yellow
}


Start-All

Write-Host ""
Write-Host "Controls: [R] restart all  [Q] quit all" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    $key = [System.Console]::ReadKey($true)
    switch ($key.Key) {
        "R" {
            Stop-All
            Start-Sleep -Seconds 1
            Start-All
        }
        "Q" {
            Stop-All
            Write-Host "Exiting control panel." -ForegroundColor Yellow
            exit
        }
        default {
            # ignore other keys
        }
    }
}