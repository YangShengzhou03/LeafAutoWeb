# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件列表
datas = [
    ('data/*.json', 'data'),
    ('resources/*.ico', 'resources'),
    ('logging_config.py', '.'),
    ('data_manager.py', '.'),
    ('task_scheduler.py', '.'),
    ('wechat_instance.py', '.'),
    ('ai_worker.py', '.'),
    ('server_manager.py', '.')
]

hiddenimports=['comtypes.stream']

a = Analysis(
    ['start_backend.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='LeafAutoBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 显示控制台窗口以便查看日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='LeafAutoWeb_version_info.txt',
    icon=['resources\\icon.ico'],
)

# 收集所有文件到dist文件夹
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LeafAutoBackend',
)