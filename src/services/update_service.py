# -*- coding: utf-8 -*-
"""Service xử lý auto-update từ GitHub"""

import os
import sys
import json
import tempfile
import subprocess
import threading
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from src.config import VERSION, GITHUB_REPO, APP_DIR


class UpdateService:
    """Service kiểm tra và cập nhật phiên bản mới từ GitHub"""
    
    GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    def __init__(self):
        self.latest_version = None
        self.download_url = None
        self.release_notes = None
        self.download_progress = 0
        self.is_downloading = False
    
    def check_for_update(self) -> dict:
        """
        Kiểm tra phiên bản mới trên GitHub.
        Returns: dict với keys: has_update, latest_version, release_notes, error
        """
        try:
            req = Request(self.GITHUB_API, headers={"User-Agent": "AutoClickPro"})
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            self.latest_version = data.get("tag_name", "").lstrip("v")
            self.release_notes = data.get("body", "Không có ghi chú")
            
            # Tìm file exe trong assets
            for asset in data.get("assets", []):
                if asset["name"].endswith(".exe"):
                    self.download_url = asset["browser_download_url"]
                    break
            
            has_update = self._compare_versions(VERSION, self.latest_version)
            
            return {
                "has_update": has_update,
                "latest_version": self.latest_version,
                "current_version": VERSION,
                "release_notes": self.release_notes,
                "error": None
            }
        except (URLError, HTTPError) as e:
            return {"has_update": False, "error": f"Lỗi kết nối: {e}"}
        except Exception as e:
            return {"has_update": False, "error": f"Lỗi: {e}"}
    
    def _compare_versions(self, current: str, latest: str) -> bool:
        """So sánh 2 phiên bản, trả về True nếu latest > current"""
        try:
            current_parts = [int(x) for x in current.split(".")]
            latest_parts = [int(x) for x in latest.split(".")]
            return latest_parts > current_parts
        except:
            return False
    
    def download_update(self, progress_callback=None) -> dict:
        """
        Tải file exe mới về thư mục temp.
        Args:
            progress_callback: Hàm callback(percent) để cập nhật progress
        Returns: dict với keys: success, file_path, error
        """
        if not self.download_url:
            return {"success": False, "error": "Không tìm thấy link tải"}
        
        self.is_downloading = True
        temp_path = os.path.join(tempfile.gettempdir(), "AutoClickPro_update.exe")
        
        try:
            req = Request(self.download_url, headers={"User-Agent": "AutoClickPro"})
            with urlopen(req, timeout=60) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0 and progress_callback:
                            percent = int(downloaded * 100 / total_size)
                            self.download_progress = percent
                            progress_callback(percent)
            
            self.is_downloading = False
            return {"success": True, "file_path": temp_path, "error": None}
        
        except Exception as e:
            self.is_downloading = False
            return {"success": False, "error": f"Lỗi tải: {e}"}
    
    def install_update(self, new_exe_path: str) -> dict:
        """
        Cài đặt bản cập nhật bằng cách tạo batch script.
        Args:
            new_exe_path: Đường dẫn file exe mới đã tải
        Returns: dict với keys: success, error
        """
        try:
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                # Đang chạy từ script, không thể tự update
                return {"success": False, "error": "Chỉ hỗ trợ update khi chạy từ file exe"}
            
            # Tạo batch script để thay thế exe
            batch_path = os.path.join(tempfile.gettempdir(), "update_autoclick.bat")
            batch_content = f'''@echo off
chcp 65001 >nul
echo Đang cập nhật AutoClick Pro...
echo Vui lòng đợi...

:: Chờ app đóng hoàn toàn
timeout /t 2 /nobreak >nul

:: Thử xóa file cũ (retry nếu còn đang chạy)
:retry
del /f /q "{current_exe}" 2>nul
if exist "{current_exe}" (
    timeout /t 1 /nobreak >nul
    goto retry
)

:: Copy file mới
copy /y "{new_exe_path}" "{current_exe}"

:: Khởi động lại app
start "" "{current_exe}"

:: Xóa file tạm
del /f /q "{new_exe_path}" 2>nul
del /f /q "%~f0" 2>nul
'''
            
            with open(batch_path, "w", encoding="utf-8") as f:
                f.write(batch_content)
            
            # Chạy batch script và thoát app
            subprocess.Popen(
                ["cmd", "/c", batch_path],
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=tempfile.gettempdir()
            )
            
            return {"success": True, "error": None}
        
        except Exception as e:
            return {"success": False, "error": f"Lỗi cài đặt: {e}"}
    
    def check_update_async(self, callback):
        """Kiểm tra update trong background thread"""
        def _check():
            result = self.check_for_update()
            callback(result)
        
        thread = threading.Thread(target=_check, daemon=True)
        thread.start()
