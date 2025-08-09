@echo off
echo ============================================
echo Building QR Code Maker Executable
echo ============================================
echo.

REM Clean previous build
if exist "dist\QRCodeMaker.exe" del "dist\QRCodeMaker.exe"

REM Build using spec file
echo Building QRCodeMaker.exe...
pyinstaller QRCodeMaker.spec --noconfirm

if exist "dist\QRCodeMaker.exe" (
    echo.
    echo ============================================
    echo Build Successful!
    echo ============================================
    echo Executable location: dist\QRCodeMaker.exe
    echo File size: 
    for %%A in ("dist\QRCodeMaker.exe") do echo %%~zA bytes
) else (
    echo.
    echo ============================================
    echo Build Failed!
    echo ============================================
    echo Please check the error messages above.
)

echo.
pause