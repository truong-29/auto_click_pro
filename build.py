# -*- coding: utf-8 -*-
"""
Script build AutoClick Pro thành file exe
Chạy: python build.py
"""

import subprocess
import sys
import os
import shutil


def check_pyinstaller():
    """Kiểm tra và cài đặt PyInstaller nếu cần"""
    try:
        import PyInstaller
        print("✅ PyInstaller đã được cài đặt")
        return True
    except ImportError:
        print("📦 Đang cài đặt PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True


def clean_build():
    """Xóa các folder build cũ"""
    folders = ['build', 'dist', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            print(f"🗑️ Xóa {folder}/")
            shutil.rmtree(folder)
    
    # Xóa file .spec cũ nếu có (không phải build.spec)
    for f in os.listdir('.'):
        if f.endswith('.spec') and f != 'build.spec':
            os.remove(f)


def build():
    """Build exe"""
    print("\n" + "="*50)
    print("🔨 BẮT ĐẦU BUILD AUTOCLICK PRO")
    print("="*50 + "\n")
    
    # Kiểm tra PyInstaller
    check_pyinstaller()
    
    # Clean
    print("\n📁 Dọn dẹp build cũ...")
    clean_build()
    
    # Build
    print("\n🔧 Đang build...")
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "build.spec",
        "--clean",
        "--noconfirm"
    ])
    
    if result.returncode == 0:
        print("\n" + "="*50)
        print("✅ BUILD THÀNH CÔNG!")
        print("="*50)
        print("\n📂 File exe nằm tại: dist/AutoClickPro/")
        print("📌 Chạy file: dist/AutoClickPro/AutoClickPro.exe")
        print("\n💡 Lưu ý:")
        print("   - Folder 'data' đã được copy vào dist/AutoClickPro/data/")
        print("   - Bạn có thể copy toàn bộ folder AutoClickPro đi bất kỳ đâu")
        print("   - Scripts và images sẽ được lưu trong folder data/ cạnh file exe")
    else:
        print("\n❌ BUILD THẤT BẠI!")
        print("Kiểm tra lỗi ở trên để biết chi tiết.")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
