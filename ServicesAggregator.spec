# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Services Aggregator

block_cipher = None

a = Analysis(
    ['Services_Aggregator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'imaplib',
        'email',
        'email.message',
        'sqlite3',
        'csv',
        'cryptography',
        'json'
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
    name='ServicesAggregator',
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