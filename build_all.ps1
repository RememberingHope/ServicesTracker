# PowerShell script to build all executables
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Building SPED Services Tracker Executables" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$python = "C:\python\WPy64-31230\python-3.12.3.amd64\python.exe"

# Check if Python exists
if (Test-Path $python) {
    Write-Host "[FOUND] Python at: $python" -ForegroundColor Green
    & $python --version
} else {
    Write-Host "[ERROR] Python not found at: $python" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Building executables..." -ForegroundColor Yellow
Write-Host ""

# Build ServicesTracker
Write-Host "Building ServicesTracker.exe..." -ForegroundColor Cyan
& $python -m PyInstaller ServicesTracker.spec --noconfirm --clean

# Build QRCodeMaker
Write-Host ""
Write-Host "Building QRCodeMaker.exe..." -ForegroundColor Cyan
& $python -m PyInstaller QRCodeMaker.spec --noconfirm --clean

# Build ServicesAggregator
Write-Host ""
Write-Host "Building ServicesAggregator.exe..." -ForegroundColor Cyan
& $python -m PyInstaller ServicesAggregator.spec --noconfirm --clean

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Build Results" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check results
$success = $true

if (Test-Path "dist\ServicesTracker.exe") {
    $size = (Get-Item "dist\ServicesTracker.exe").Length
    Write-Host "[SUCCESS] ServicesTracker.exe ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "[FAILED] ServicesTracker.exe" -ForegroundColor Red
    $success = $false
}

if (Test-Path "dist\QRCodeMaker.exe") {
    $size = (Get-Item "dist\QRCodeMaker.exe").Length
    Write-Host "[SUCCESS] QRCodeMaker.exe ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "[FAILED] QRCodeMaker.exe" -ForegroundColor Red
    $success = $false
}

if (Test-Path "dist\ServicesAggregator.exe") {
    $size = (Get-Item "dist\ServicesAggregator.exe").Length
    Write-Host "[SUCCESS] ServicesAggregator.exe ($size bytes)" -ForegroundColor Green
} else {
    Write-Host "[FAILED] ServicesAggregator.exe" -ForegroundColor Red
    $success = $false
}

Write-Host ""
if ($success) {
    Write-Host "All executables built successfully!" -ForegroundColor Green
    Write-Host "Find them in the 'dist' folder." -ForegroundColor Cyan
} else {
    Write-Host "Some builds failed. Check the error messages above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")