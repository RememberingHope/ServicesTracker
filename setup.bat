@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   SPED Services Tracker - Automated Setup
echo ============================================================
echo.
echo This script will:
echo   1. Check for Python installation
echo   2. Install Python if needed (portable version)
echo   3. Install required packages
echo   4. Build executables
echo.
echo Press any key to start or Ctrl+C to cancel...
pause >nul

REM Check for Python
echo.
echo [1/4] Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python is installed!
    python --version
    goto :install_deps
)

echo Python is not installed or not in PATH.
echo.
echo ============================================================
echo   Python Installation Options
echo ============================================================
echo.
echo   1. Download portable WinPython (recommended - no admin needed)
echo   2. Download standard Python installer (requires admin)
echo   3. Skip Python installation (I'll install it myself)
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto :winpython
if "%choice%"=="2" goto :standard_python
if "%choice%"=="3" goto :manual_install

:winpython
echo.
echo ------------------------------------------------------------
echo Please download WinPython from:
echo https://sourceforge.net/projects/winpython/files/
echo.
echo Recommended: WinPython64-3.11.x.x (latest 3.11 version)
echo.
echo Steps:
echo   1. Download the exe file
echo   2. Run it to extract (no admin needed)
echo   3. Extract to C:\WinPython or any folder
echo   4. Run "WinPython Command Prompt.exe" from that folder
echo   5. Navigate back to this folder and run setup.bat again
echo.
echo Opening download page in browser...
start https://sourceforge.net/projects/winpython/files/
echo.
pause
exit /b

:standard_python
echo.
echo ------------------------------------------------------------
echo Please download Python from:
echo https://www.python.org/downloads/
echo.
echo IMPORTANT: During installation, check "Add Python to PATH"
echo.
echo After installation:
echo   1. Close this window
echo   2. Open a new Command Prompt
echo   3. Run setup.bat again
echo.
echo Opening download page in browser...
start https://www.python.org/downloads/
echo.
pause
exit /b

:manual_install
echo.
echo Please install Python 3.8 or later, then run this script again.
echo Make sure Python is added to your system PATH.
pause
exit /b

:install_deps
echo.
echo [2/4] Installing required Python packages...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install PyInstaller
echo Installing PyInstaller...
python -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Install other requirements
echo.
echo Installing application dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check requirements.txt exists
    pause
    exit /b 1
)

echo.
echo [3/4] Building executables...
echo.

REM Check if dist folder exists, create if not
if not exist "dist" mkdir dist

REM Build Services Tracker
echo Building Services Tracker...
pyinstaller ServicesTracker.spec --noconfirm --clean
if not exist "dist\ServicesTracker.exe" (
    echo WARNING: ServicesTracker.exe build failed
    set build_failed=1
)

REM Build QR Code Maker
echo.
echo Building QR Code Maker...
pyinstaller QRCodeMaker.spec --noconfirm --clean
if not exist "dist\QRCodeMaker.exe" (
    echo WARNING: QRCodeMaker.exe build failed
    set build_failed=1
)

REM Build Services Aggregator
echo.
echo Building Services Aggregator...
pyinstaller ServicesAggregator.spec --noconfirm --clean
if not exist "dist\ServicesAggregator.exe" (
    echo WARNING: ServicesAggregator.exe build failed
    set build_failed=1
)

echo.
echo [4/4] Setup complete!
echo.
echo ============================================================
echo   Setup Results
echo ============================================================
echo.

if exist "dist\ServicesTracker.exe" (
    echo [SUCCESS] ServicesTracker.exe
    for %%A in ("dist\ServicesTracker.exe") do echo           Size: %%~zA bytes
) else (
    echo [FAILED]  ServicesTracker.exe
)

if exist "dist\QRCodeMaker.exe" (
    echo [SUCCESS] QRCodeMaker.exe  
    for %%A in ("dist\QRCodeMaker.exe") do echo           Size: %%~zA bytes
) else (
    echo [FAILED]  QRCodeMaker.exe
)

if exist "dist\ServicesAggregator.exe" (
    echo [SUCCESS] ServicesAggregator.exe
    for %%A in ("dist\ServicesAggregator.exe") do echo           Size: %%~zA bytes
) else (
    echo [FAILED]  ServicesAggregator.exe
)

echo.
echo ============================================================
if defined build_failed (
    echo Some builds failed. Please check error messages above.
    echo You can try running individual build scripts:
    echo   - build_tracker.bat
    echo   - build_qr_maker.bat
    echo   - build_aggregator.bat
) else (
    echo All executables built successfully!
    echo.
    echo Executables are located in the 'dist' folder:
    echo   - ServicesTracker.exe (for classroom kiosks)
    echo   - QRCodeMaker.exe (for administrators)
    echo   - ServicesAggregator.exe (for data collection)
    echo.
    echo For the Analytics Dashboard, run:
    echo   run_dashboard.bat
)
echo ============================================================
echo.
pause