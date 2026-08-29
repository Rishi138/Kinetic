        param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$desc
)

Write-Host "Staging changes..." -ForegroundColor Cyan
git add .

Write-Host "Committing: $desc" -ForegroundColor Cyan
git commit -m "$desc"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Nothing to commit (or commit failed) - skipping push." -ForegroundColor Yellow
    exit
}

Write-Host "Pushing to remote..." -ForegroundColor Cyan
git push

if ($LASTEXITCODE -eq 0) {
    Write-Host "Done - pushed successfully." -ForegroundColor Green
} else {
    Write-Host "Push failed - check the error above." -ForegroundColor Red
}
