# -*- coding: utf-8 -*-
"""
AutoClick Pro - Ứng dụng tự động click chuột
Entry point của ứng dụng
"""

import sys
import os
import ctypes


def is_admin():
    """Kiểm tra xem có đang chạy với quyền Admin không"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Chạy lại ứng dụng với quyền Admin"""
    if sys.platform == 'win32':
        if getattr(sys, 'frozen', False):
            # Chạy từ exe
            exe_path = sys.executable
            script_dir = os.path.dirname(exe_path)
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas",
                exe_path,
                params,
                script_dir,
                1
            )
        else:
            # Chạy từ script Python
            script = os.path.abspath(sys.argv[0])
            script_dir = os.path.dirname(script)
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas",
                sys.executable,
                f'"{script}" {params}',
                script_dir,
                1
            )
        return ret > 32


def main():
    """Khởi chạy ứng dụng"""
    # Đảm bảo working directory đúng
    # Nếu chạy từ exe, lấy thư mục chứa exe
    # Nếu chạy từ script, lấy thư mục chứa main.py
    if getattr(sys, 'frozen', False):
        # Chạy từ exe (PyInstaller)
        script_dir = os.path.dirname(sys.executable)
    else:
        # Chạy từ script Python
        script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Kiểm tra quyền Admin trên Windows
    if sys.platform == 'win32' and not is_admin():
        print("⚠️ Ứng dụng cần quyền Administrator để click vào các cửa sổ khác.")
        print("🔄 Đang yêu cầu quyền Admin...")
        
        if run_as_admin():
            # Đã khởi chạy process mới với quyền Admin, thoát process hiện tại
            sys.exit(0)
        else:
            print("❌ Không thể lấy quyền Admin. Một số tính năng có thể không hoạt động.")
            print("💡 Hãy thử chạy lại bằng cách click phải → 'Run as administrator'")
            input("Nhấn Enter để tiếp tục không có quyền Admin...")
    
    try:
        from src.ui import MainWindow
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")
        import traceback
        traceback.print_exc()
        input("Nhấn Enter để thoát...")


if __name__ == "__main__":
    main()
