@echo off
echo ============================================
echo SPED Services Tracker - Dependency Installer
echo ============================================
echo.
echo This script will install all required Python packages
echo for building the SPED Services Tracker executables.
echo.
pause

echo.
echo Installing PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo Installing application dependencies...
python -m pip install --upgrade -r requirements.txt

echo.
echo Installing additional build dependencies...
python -m pip install --upgrade pyinstaller-hooks-contrib

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo You can now run build_all.bat to create the executables.
echo.
pause