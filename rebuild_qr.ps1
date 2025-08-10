# PowerShell script to rebuild QRCodeMaker.exe
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Rebuilding QR Code Maker Executable" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$python = "C:\python\WPy64-31230\python-3.12.3.amd64\python.exe"

# Kill any running instance
Write-Host "Closing any running QRCodeMaker.exe..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object {$_.Name -eq "QRCodeMaker"}
if ($processes) {
    $processes | Stop-Process -Force
    Write-Host "Closed running instance." -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "No running instance found." -ForegroundColor Gray
}

# Delete old executable
Write-Host "Removing old executable..." -ForegroundColor Yellow
if (Test-Path "dist\QRCodeMaker.exe") {
    Remove-Item "dist\QRCodeMaker.exe" -Force
    Write-Host "Old executable removed." -ForegroundColor Green
}

# Build new executable
Write-Host ""
Write-Host "Building QRCodeMaker.exe..." -ForegroundColor Cyan
& $python -m PyInstaller QRCodeMaker.spec --noconfirm --clean

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Check result
if (Test-Path "dist\QRCodeMaker.exe") {
    $size = (Get-Item "dist\QRCodeMaker.exe").Length
    Write-Host "[SUCCESS] QRCodeMaker.exe rebuilt successfully!" -ForegroundColor Green
    Write-Host "Size: $size bytes" -ForegroundColor Cyan
    Write-Host "Location: dist\QRCodeMaker.exe" -ForegroundColor Cyan
} else {
    Write-Host "[FAILED] Build failed. Check error messages above." -ForegroundColor Red
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")