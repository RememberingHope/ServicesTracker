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
echo.
echo ============================================================
echo   HOW THIS SCRIPT SEARCHES FOR PYTHON:
echo ============================================================
echo   1. 'python' command in system PATH
echo   2. 'py' launcher (Windows Python Launcher)  
echo   3. WinPython folders:
echo      - C:\WinPython*, C:\WPy* (like C:\WPy64-31110)
echo      - C:\python\WPy*, C:\python\WinPython*
echo   4. C:\Python* folders (standard installs)
echo   5. Common locations:
echo      - C:\Anaconda3, C:\Miniconda3
echo      - User profile Python folders
echo.
echo   If Python is not found automatically:
echo   - You'll be prompted to enter the path manually
echo   - Example: C:\WPy64-31110\python-3.11.1.amd64\python.exe
echo ============================================================
echo.

REM Initialize Python command variable
set PYTHON_CMD=

REM Method 1: Check standard 'python' command in PATH
echo Checking: 'python' command in PATH...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [FOUND] Python in PATH!
    python --version
    set PYTHON_CMD=python
    goto :install_deps
)
echo [NOT FOUND] 'python' not in PATH

REM Method 2: Check 'py' launcher (common on Windows)
echo Checking: 'py' launcher...
py --version >nul 2>&1
if %errorlevel% == 0 (
    echo [FOUND] Python via py launcher!
    py --version
    set PYTHON_CMD=py
    goto :install_deps
)
echo [NOT FOUND] 'py' launcher not available

REM Method 3: Search for WinPython in various locations
echo Checking: WinPython/WPy folders in C:\ and C:\python\...
set found_winpython=0

REM Check C:\ root for WinPython patterns
for %%P in (WinPython WPy) do (
    for /d %%D in (C:\%%P*) do (
        set found_winpython=1
        echo   Checking: %%D
        
        REM Check for python.exe in python-* subdirectory
        for /d %%S in ("%%D\python-*") do (
            if exist "%%S\python.exe" (
                echo [FOUND] WinPython at: %%S
                "%%S\python.exe" --version
                set "PYTHON_CMD=%%S\python.exe"
                goto :install_deps
            )
        )
        
        REM Check for python.exe directly in the main folder
        if exist "%%D\python.exe" (
            echo [FOUND] Python at: %%D
            "%%D\python.exe" --version
            set "PYTHON_CMD=%%D\python.exe"
            goto :install_deps
        )
    )
)

REM Also check C:\python\ directory for WinPython installations
if exist "C:\python\" (
    echo   Checking: C:\python\ subdirectories...
    for /d %%D in (C:\python\WPy* C:\python\WinPython*) do (
        set found_winpython=1
        echo   Checking: %%D
        
        REM Check for python.exe in python-* subdirectory
        for /d %%S in ("%%D\python-*") do (
            if exist "%%S\python.exe" (
                echo [FOUND] WinPython at: %%S
                "%%S\python.exe" --version
                set "PYTHON_CMD=%%S\python.exe"
                goto :install_deps
            )
        )
        
        REM Check for python.exe directly
        if exist "%%D\python.exe" (
            echo [FOUND] Python at: %%D
            "%%D\python.exe" --version
            set "PYTHON_CMD=%%D\python.exe"
            goto :install_deps
        )
    )
)

if %found_winpython%==0 echo [NOT FOUND] No WinPython/WPy folders in checked locations

REM Method 4: Search for standard Python in C:\ root
echo Checking: C:\Python* folders...
set found_python=0
for /d %%D in (C:\Python*) do (
    set found_python=1
    if exist "%%D\python.exe" (
        echo [FOUND] Python at: %%D
        "%%D\python.exe" --version
        set "PYTHON_CMD=%%D\python.exe"
        goto :install_deps
    )
)
if %found_python%==0 echo [NOT FOUND] No C:\Python* folders

REM Method 5: Check for Anaconda/Miniconda in common locations
echo Checking: Common Anaconda/Miniconda locations...
for %%L in (
    "C:\Anaconda3"
    "C:\Miniconda3"
    "C:\ProgramData\Anaconda3"
    "C:\ProgramData\Miniconda3"
    "%USERPROFILE%\Anaconda3"
    "%USERPROFILE%\Miniconda3"
    "%LOCALAPPDATA%\Programs\Python\Python*"
) do (
    for /d %%D in (%%L) do (
        if exist "%%D\python.exe" (
            echo [FOUND] Python at: %%D
            "%%D\python.exe" --version
            set "PYTHON_CMD=%%D\python.exe"
            goto :install_deps
        )
    )
)
echo [NOT FOUND] No Python in common locations

echo.
echo ============================================================
echo   Python not found automatically
echo ============================================================
echo.

:manual_path
echo If you have Python installed in a custom location, you can:
echo   1. Enter the full path to python.exe
echo   2. Type 'download' to get Python
echo   3. Type 'exit' to quit
echo.
echo Example paths:
echo   C:\WPy64-31110\python-3.11.1.amd64\python.exe
echo   C:\python\WPy64-31230\python-3.12.3.amd64\python.exe
echo   C:\WinPython\python-3.11.5.amd64\python.exe
echo   D:\Python311\python.exe
echo.
set /p user_path="Enter path to python.exe (or 'download'/'exit'): "

if /i "%user_path%"=="exit" exit /b
if /i "%user_path%"=="download" goto :download_python

REM Check if user-provided path exists
if exist "%user_path%" (
    echo.
    echo Checking provided path...
    "%user_path%" --version >nul 2>&1
    if %errorlevel% == 0 (
        echo [SUCCESS] Valid Python found!
        "%user_path%" --version
        set "PYTHON_CMD=%user_path%"
        goto :install_deps
    ) else (
        echo [ERROR] File exists but doesn't appear to be valid Python
        echo.
        goto :manual_path
    )
) else (
    echo [ERROR] File not found: %user_path%
    echo Please check the path and try again.
    echo.
    goto :manual_path
)

:download_python
echo.
echo ============================================================
echo   Download Python Options
echo ============================================================
echo.
echo   1. WinPython (Recommended - Portable, No Admin)
echo      - Extract to C:\ for auto-detection
echo      - Example: C:\WinPython
echo.
echo   2. Standard Python (Requires Admin)
echo      - Must check "Add to PATH" during install
echo.
echo Which would you like to download?
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Opening WinPython download page...
    echo.
    echo IMPORTANT: Extract to C:\ root for auto-detection
    echo Example: C:\WinPython or C:\WinPython64-3.11.5.0
    echo.
    echo After extracting, run setup.bat again.
    echo.
    start https://sourceforge.net/projects/winpython/files/
    pause
    exit /b
)

if "%choice%"=="2" (
    echo.
    echo Opening Python.org download page...
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    echo After installing, run setup.bat again.
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b
)

echo Invalid choice. Returning to manual path entry...
echo.
goto :manual_path

:install_deps
echo.
echo [2/4] Installing required Python packages...
echo Using Python: %PYTHON_CMD%
echo.

REM Upgrade pip first
echo Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip

REM Install PyInstaller
echo.
echo Installing PyInstaller...
%PYTHON_CMD% -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Install other requirements
echo.
echo Installing application dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
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

REM Determine PyInstaller command based on how Python was found
set PYINSTALLER_CMD=pyinstaller

REM If we're using a full path to Python, PyInstaller might be in Scripts folder
if not "%PYTHON_CMD%"=="python" if not "%PYTHON_CMD%"=="py" (
    REM Extract the directory from Python path
    for %%F in ("%PYTHON_CMD%") do set PYTHON_DIR=%%~dpF
    if exist "%PYTHON_DIR%Scripts\pyinstaller.exe" (
        set "PYINSTALLER_CMD=%PYTHON_DIR%Scripts\pyinstaller.exe"
        echo Using PyInstaller at: %PYINSTALLER_CMD%
    ) else (
        REM Try running pyinstaller through Python
        set "PYINSTALLER_CMD=%PYTHON_CMD% -m PyInstaller"
        echo Using PyInstaller via: %PYINSTALLER_CMD%
    )
)

REM Build Services Tracker
echo Building Services Tracker...
%PYINSTALLER_CMD% ServicesTracker.spec --noconfirm --clean
if not exist "dist\ServicesTracker.exe" (
    echo WARNING: ServicesTracker.exe build failed
    set build_failed=1
)

REM Build QR Code Maker
echo.
echo Building QR Code Maker...
%PYINSTALLER_CMD% QRCodeMaker.spec --noconfirm --clean
if not exist "dist\QRCodeMaker.exe" (
    echo WARNING: QRCodeMaker.exe build failed
    set build_failed=1
)

REM Build Services Aggregator
echo.
echo Building Services Aggregator...
%PYINSTALLER_CMD% ServicesAggregator.spec --noconfirm --clean
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