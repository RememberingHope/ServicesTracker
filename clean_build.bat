@echo off
echo ============================================
echo Cleaning Build Artifacts
echo ============================================
echo.
echo This will remove all PyInstaller build files
echo and temporary directories.
echo.
pause

echo.
echo Removing build directories...

REM Remove PyInstaller directories
if exist "build" (
    rmdir /s /q "build"
    echo Removed: build\
)

if exist "dist" (
    rmdir /s /q "dist"
    echo Removed: dist\
)

REM Remove PyInstaller cache
if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo Removed: __pycache__\
)

REM Remove spec file backups if any
if exist "*.spec.bak" (
    del /q "*.spec.bak"
    echo Removed: *.spec.bak files
)

REM Clean up any .pyc files
del /s /q "*.pyc" 2>nul

echo.
echo ============================================
echo Cleanup Complete!
echo ============================================
echo.
echo Build directories have been removed.
echo Run build_all.bat to create fresh executables.
echo.
pause