@echo off
echo ============================================
echo Building Services Aggregator Executable
echo ============================================
echo.

REM Clean previous build
if exist "dist\ServicesAggregator.exe" del "dist\ServicesAggregator.exe"

REM Build using spec file
echo Building ServicesAggregator.exe...
pyinstaller ServicesAggregator.spec --noconfirm

if exist "dist\ServicesAggregator.exe" (
    echo.
    echo ============================================
    echo Build Successful!
    echo ============================================
    echo Executable location: dist\ServicesAggregator.exe
    echo File size: 
    for %%A in ("dist\ServicesAggregator.exe") do echo %%~zA bytes
) else (
    echo.
    echo ============================================
    echo Build Failed!
    echo ============================================
    echo Please check the error messages above.
)

echo.
pause