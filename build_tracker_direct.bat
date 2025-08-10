@echo off
echo ============================================
echo Building Services Tracker Executable
echo ============================================
echo.

REM Clean previous build
if exist "dist\ServicesTracker.exe" del "dist\ServicesTracker.exe"

REM Build using spec file with full Python path
echo Building ServicesTracker.exe...
C:\python\WPy64-31230\python-3.12.3.amd64\python.exe -m PyInstaller ServicesTracker.spec --noconfirm --clean

if exist "dist\ServicesTracker.exe" (
    echo.
    echo ============================================
    echo Build Successful!
    echo ============================================
    echo Executable location: dist\ServicesTracker.exe
    echo File size: 
    for %%A in ("dist\ServicesTracker.exe") do echo %%~zA bytes
) else (
    echo.
    echo ============================================
    echo Build Failed!
    echo ============================================
    echo Please check the error messages above.
)

echo.
pause