# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Services Tracker

block_cipher = None

a = Analysis(
    ['Services_Tracker.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'cv2',
        'keyring.backends.Windows',
        'cryptography',
        'sqlite3',
        'email',
        'smtplib',
        'json',
        'platform'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ServicesTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',  # Optional version file
    icon=None  # Add 'icon.ico' if you have an icon file
)