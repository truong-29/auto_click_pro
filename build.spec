# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file cho AutoClick Pro
Chạy: pyinstaller build.spec
"""

import sys
import os

block_cipher = None

# Đường dẫn gốc
BASE_PATH = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[BASE_PATH],
    binaries=[],
    datas=[
        # Thêm folder data vào bundle (sẽ copy ra ngoài khi chạy)
        ('data', 'data'),
    ],
    hiddenimports=[
        'pyautogui',
        'keyboard',
        'PIL',
        'PIL.Image',
        'cv2',
        'numpy',
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'ctypes',
        'psutil',
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
    [],
    exclude_binaries=True,
    name='AutoClickPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Không hiện console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,  # Yêu cầu quyền Admin
    icon=None,  # Thêm icon nếu có: icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoClickPro',
)
