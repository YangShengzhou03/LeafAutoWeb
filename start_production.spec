# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 获取当前文件目录
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # 当__file__未定义时（如PyInstaller环境），使用当前工作目录
    current_dir = os.getcwd()

# 版本信息文件路径
version_file = os.path.join(current_dir, 'LeafAutoWeb_version_info.txt')

# 图标文件路径
icon_file = os.path.join(current_dir, 'resources', 'icon.ico')

# 收集所有依赖项
datas = []
binaries = []
hiddenimports = []

# 添加版本信息（如果文件存在）
version_info = None
if os.path.exists(version_file):
    version_info = version_file

# 主程序配置
a = Analysis(['start_production.py'],
             pathex=[current_dir],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 可执行文件配置
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='LeafAutoWeb',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,  # 保持控制台窗口以显示输出
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon=icon_file if os.path.exists(icon_file) else None,
          version=version_info)

# 单个文件夹输出
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='LeafAutoWeb')