@echo off
echo ============================================================
echo SPED Services Tracker Suite - Build All Executables
echo ============================================================
echo.
echo This script will build all three applications:
echo   1. Services Tracker (Kiosk App)
echo   2. QR Code Maker (Admin App)
echo   3. Services Aggregator (Dashboard App)
echo.
pause

REM Create dist folder if it doesn't exist
if not exist "dist" mkdir dist

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "dist\ServicesTracker.exe" del "dist\ServicesTracker.exe"
if exist "dist\QRCodeMaker.exe" del "dist\QRCodeMaker.exe"
if exist "dist\ServicesAggregator.exe" del "dist\ServicesAggregator.exe"

REM Build Services Tracker
echo.
echo ============================================================
echo [1/3] Building Services Tracker...
echo ============================================================
pyinstaller ServicesTracker.spec --noconfirm --clean

REM Build QR Code Maker
echo.
echo ============================================================
echo [2/3] Building QR Code Maker...
echo ============================================================
pyinstaller QRCodeMaker.spec --noconfirm --clean

REM Build Services Aggregator
echo.
echo ============================================================
echo [3/3] Building Services Aggregator...
echo ============================================================
pyinstaller ServicesAggregator.spec --noconfirm --clean

REM Check results
echo.
echo ============================================================
echo Build Summary
echo ============================================================
echo.

set /a success=0
set /a failed=0

if exist "dist\ServicesTracker.exe" (
    echo [SUCCESS] ServicesTracker.exe
    for %%A in ("dist\ServicesTracker.exe") do echo          Size: %%~zA bytes
    set /a success+=1
) else (
    echo [FAILED]  ServicesTracker.exe
    set /a failed+=1
)

if exist "dist\QRCodeMaker.exe" (
    echo [SUCCESS] QRCodeMaker.exe
    for %%A in ("dist\QRCodeMaker.exe") do echo          Size: %%~zA bytes
    set /a success+=1
) else (
    echo [FAILED]  QRCodeMaker.exe
    set /a failed+=1
)

if exist "dist\ServicesAggregator.exe" (
    echo [SUCCESS] ServicesAggregator.exe
    for %%A in ("dist\ServicesAggregator.exe") do echo          Size: %%~zA bytes
    set /a success+=1
) else (
    echo [FAILED]  ServicesAggregator.exe
    set /a failed+=1
)

echo.
echo ============================================================
echo Build Complete: %success% successful, %failed% failed
echo ============================================================

if %success%==3 (
    echo.
    echo All executables built successfully!
    echo They are located in the 'dist' folder.
    echo.
    echo Next steps:
    echo   1. Test each executable on a clean machine
    echo   2. Create deployment package with all three .exe files
    echo   3. Include IMPLEMENTATION_BRIEF.md as documentation
) else (
    echo.
    echo Some builds failed. Please check the error messages above.
    echo Run individual build scripts to troubleshoot:
    echo   - build_tracker.bat
    echo   - build_qr_maker.bat
    echo   - build_aggregator.bat
)

echo.
pause