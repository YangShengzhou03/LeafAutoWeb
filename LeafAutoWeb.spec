# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['start_production.py'],
    pathex=[],
    binaries=[],
    datas=[('frontend\\dist', 'frontend/dist'), ('data', 'data'), ('resources', 'resources'), ('frontend', 'frontend'), ('app.py', '.')],
    hiddenimports=['comtypes.stream'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['unused_module'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LeafAutoWeb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='LeafAutoWeb_version_info.txt',
    icon=['resources\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LeafAutoWeb',
)
