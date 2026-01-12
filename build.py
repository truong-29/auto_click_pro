# -*- coding: utf-8 -*-
"""
Script build AutoClick Pro thành 1 file exe duy nhất
Chạy: python build.py
"""

import subprocess
import sys
import os
import shutil


def check_dependencies():
    """Kiểm tra và cài đặt các dependencies cần thiết cho build"""
    print("📦 Kiểm tra dependencies...")
    
    try:
        import PyInstaller
        print("   ✅ PyInstaller đã được cài đặt")
    except ImportError:
        print("   📥 Đang cài đặt PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    required = ['pyautogui', 'keyboard', 'PIL', 'cv2', 'numpy', 'win32api', 'psutil']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"   ⚠️ Thiếu một số packages: {missing}")
        print("   📥 Đang cài đặt từ requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("   ✅ Tất cả dependencies đã sẵn sàng")


def clean_build():
    """Xóa các folder và file build cũ"""
    folders = ['build', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            print(f"   🗑️ Xóa {folder}/")
            shutil.rmtree(folder)


def create_spec_file():
    """Tạo file build.spec nếu chưa có"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageGrab',
        'cv2',
        'numpy',
        'pyautogui',
        'keyboard',
        'win32api',
        'win32con',
        'win32gui',
        'win32ui',
        'win32process',
        'psutil',
        'pywintypes',
        'ctypes',
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
    name='AutoClickPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
)
'''
    with open('build.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("   ✅ Đã tạo file build.spec")


def build():
    """Build thành 1 file exe duy nhất"""
    print("\n" + "=" * 60)
    print("🔨 BUILD AUTOCLICK PRO - SINGLE EXE FILE")
    print("=" * 60)
    
    check_dependencies()
    
    print("\n📁 Dọn dẹp build cũ...")
    clean_build()
    
    # Tạo build.spec nếu chưa có
    if not os.path.exists('build.spec'):
        print("\n📝 Tạo file build.spec...")
        create_spec_file()
    
    print("\n🔧 Đang build exe (có thể mất vài phút)...")
    print("   Mode: Single file (onefile)")
    print("   Console: Hidden (GUI app)")
    print("   UAC: Admin required")
    print()
    
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "build.spec",
        "--clean",
        "--noconfirm"
    ])
    
    if result.returncode == 0:
        exe_path = os.path.join('dist', 'AutoClickPro.exe')
        if os.path.exists(exe_path):
            exe_size = os.path.getsize(exe_path) / (1024 * 1024)
            
            print("\n" + "=" * 60)
            print("✅ BUILD THÀNH CÔNG!")
            print("=" * 60)
            print(f"\n📂 File exe: dist/AutoClickPro.exe")
            print(f"📊 Kích thước: {exe_size:.1f} MB")
            print("\n💡 Hướng dẫn sử dụng:")
            print("   1. Copy file AutoClickPro.exe đến bất kỳ đâu")
            print("   2. Double-click để chạy (sẽ yêu cầu quyền Admin)")
            print("   3. Folder 'data' đã được đóng gói bên trong exe")
        else:
            print("\n⚠️ Build hoàn tất nhưng không tìm thấy file exe!")
            return 1
    else:
        print("\n" + "=" * 60)
        print("❌ BUILD THẤT BẠI!")
        print("=" * 60)
        print("\n� Kyiểm tra các lỗi phía trên để biết chi tiết.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(build())
