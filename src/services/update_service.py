# -*- coding: utf-8 -*-
"""
Update Service - Kiểm tra và cập nhật ứng dụng từ GitHub
Non-blocking: chạy trên background thread, không treo UI
"""

import os
import sys
import json
import tempfile
import subprocess
import threading
import urllib.request
import urllib.error
from typing import Optional, Callable

from ..config import APP_VERSION, GITHUB_REPO, APP_DIR


class UpdateInfo:
    """Thông tin về bản cập nhật"""
    def __init__(self, version: str, download_url: str, release_notes: str, published_at: str):
        self.version = version
        self.download_url = download_url
        self.release_notes = release_notes
        self.published_at = published_at


class UpdateService:
    """
    Service kiểm tra và tải cập nhật từ GitHub Releases.
    Tất cả operations chạy trên background thread → không block UI.
    """
    
    GITHUB_API = "https://api.github.com/repos/{}/releases/latest"
    
    def __init__(self):
        self._checking = False
        self._downloading = False
        self._cancel_download = False
    
    def check_for_updates(
        self,
        on_update_available: Optional[Callable[[UpdateInfo], None]] = None,
        on_no_update: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ):
        """
        Kiểm tra cập nhật (chạy background thread).
        
        Args:
            on_update_available: Callback khi có bản mới (nhận UpdateInfo)
            on_no_update: Callback khi đã là bản mới nhất
            on_error: Callback khi có lỗi (nhận error message)
        """
        if self._checking:
            return
        
        def _check():
            self._checking = True
            try:
                update_info = self._fetch_latest_release()
                
                if update_info and self._is_newer_version(update_info.version):
                    if on_update_available:
                        on_update_available(update_info)
                else:
                    if on_no_update:
                        on_no_update()
                        
            except Exception as e:
                if on_error:
                    on_error(str(e))
            finally:
                self._checking = False
        
        thread = threading.Thread(target=_check, daemon=True)
        thread.start()
    
    def download_and_install(
        self,
        update_info: UpdateInfo,
        on_progress: Optional[Callable[[int], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ):
        """
        Tải và cài đặt bản cập nhật (chạy background thread).
        
        Args:
            update_info: Thông tin bản cập nhật
            on_progress: Callback tiến trình (0-100%)
            on_complete: Callback khi hoàn tất (nhận đường dẫn file)
            on_error: Callback khi có lỗi
        """
        if self._downloading:
            return
        
        def _download():
            self._downloading = True
            self._cancel_download = False
            
            try:
                # Tải file về temp
                temp_path = self._download_file(
                    update_info.download_url,
                    on_progress
                )
                
                if self._cancel_download:
                    # Xóa file nếu bị hủy
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return
                
                # Tạo và chạy updater script
                self._create_and_run_updater(temp_path)
                
                if on_complete:
                    on_complete(temp_path)
                    
            except Exception as e:
                if on_error:
                    on_error(str(e))
            finally:
                self._downloading = False
        
        thread = threading.Thread(target=_download, daemon=True)
        thread.start()
    
    def cancel_download(self):
        """Hủy quá trình tải"""
        self._cancel_download = True
    
    def _fetch_latest_release(self) -> Optional[UpdateInfo]:
        """Lấy thông tin release mới nhất từ GitHub API"""
        url = self.GITHUB_API.format(GITHUB_REPO)
        
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'AutoClickPro-Updater',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise Exception("Không tìm thấy repository hoặc chưa có release nào.")
            raise Exception(f"Lỗi GitHub API: {e.code}")
        except urllib.error.URLError as e:
            raise Exception(f"Không thể kết nối đến GitHub: {e.reason}")
        
        # Tìm file .exe trong assets
        download_url = None
        for asset in data.get('assets', []):
            if asset['name'].endswith('.exe'):
                download_url = asset['browser_download_url']
                break
        
        if not download_url:
            raise Exception("Không tìm thấy file .exe trong release.")
        
        return UpdateInfo(
            version=data['tag_name'].lstrip('v'),
            download_url=download_url,
            release_notes=data.get('body', ''),
            published_at=data.get('published_at', '')
        )
    
    def _is_newer_version(self, remote_version: str) -> bool:
        """So sánh version: True nếu remote mới hơn local"""
        try:
            local_parts = [int(x) for x in APP_VERSION.split('.')]
            remote_parts = [int(x) for x in remote_version.split('.')]
            
            # Pad với 0 nếu độ dài khác nhau
            max_len = max(len(local_parts), len(remote_parts))
            local_parts.extend([0] * (max_len - len(local_parts)))
            remote_parts.extend([0] * (max_len - len(remote_parts)))
            
            return remote_parts > local_parts
        except ValueError:
            # Nếu không parse được, so sánh string
            return remote_version != APP_VERSION
    
    def _download_file(
        self,
        url: str,
        on_progress: Optional[Callable[[int], None]] = None
    ) -> str:
        """Tải file về thư mục temp, trả về đường dẫn"""
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "AutoClickPro_update.exe")
        
        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'AutoClickPro-Updater'}
        )
        
        with urllib.request.urlopen(request, timeout=60) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(temp_path, 'wb') as f:
                while True:
                    if self._cancel_download:
                        break
                    
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if on_progress and total_size > 0:
                        progress = int(downloaded * 100 / total_size)
                        on_progress(progress)
        
        return temp_path
    
    def _create_and_run_updater(self, new_exe_path: str):
        """Tạo batch script để thay thế exe và restart app"""
        if getattr(sys, 'frozen', False):
            current_exe = sys.executable
        else:
            # Khi chạy từ script, không thể tự update
            raise Exception("Auto-update chỉ hoạt động với bản build (.exe)")
        
        temp_dir = tempfile.gettempdir()
        batch_path = os.path.join(temp_dir, "autoclick_updater.bat")
        
        # Batch script: đợi app đóng → copy file mới → chạy lại app
        batch_content = f'''@echo off
chcp 65001 >nul
echo Đang cập nhật AutoClick Pro...
echo Vui lòng đợi...

:: Đợi app cũ đóng hoàn toàn
timeout /t 2 /nobreak >nul

:: Copy file mới đè lên file cũ
copy /y "{new_exe_path}" "{current_exe}"

:: Xóa file tạm
del /f "{new_exe_path}"

:: Chạy lại app
start "" "{current_exe}"

:: Tự xóa batch file
del /f "%~f0"
'''
        
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        # Chạy batch script (detached)
        subprocess.Popen(
            ['cmd', '/c', batch_path],
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            close_fds=True
        )
        
        # Thoát app hiện tại
        sys.exit(0)
