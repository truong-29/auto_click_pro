# -*- coding: utf-8 -*-
"""Dialog hiển thị thông báo cập nhật"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from src.services.update_service import UpdateService


class UpdateDialog:
    """Dialog thông báo có bản cập nhật mới"""
    
    def __init__(self, parent, update_info: dict):
        self.parent = parent
        self.update_info = update_info
        self.update_service = UpdateService()
        self.update_service.latest_version = update_info.get("latest_version")
        self.update_service.download_url = None  # Sẽ lấy lại khi tải
        
        self.dialog = None
        self.progress_var = None
        self.status_label = None
        self.result = False
    
    def show(self) -> bool:
        """Hiển thị dialog, trả về True nếu user chọn cập nhật"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🔄 Cập nhật phần mềm")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 450) // 2
        y = (self.dialog.winfo_screenheight() - 350) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon và tiêu đề
        title_label = ttk.Label(
            main_frame,
            text="🎉 Có phiên bản mới!",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Thông tin phiên bản
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=5)
        
        current_ver = self.update_info.get("current_version", "?")
        latest_ver = self.update_info.get("latest_version", "?")
        
        ttk.Label(
            version_frame,
            text=f"Phiên bản hiện tại: {current_ver}",
            font=("Segoe UI", 10)
        ).pack()
        
        ttk.Label(
            version_frame,
            text=f"Phiên bản mới: {latest_ver}",
            font=("Segoe UI", 10, "bold"),
            foreground="green"
        ).pack()
        
        # Release notes
        notes_label = ttk.Label(main_frame, text="📝 Nội dung cập nhật:")
        notes_label.pack(anchor=tk.W, pady=(15, 5))
        
        notes_text = tk.Text(main_frame, height=6, width=50, wrap=tk.WORD)
        notes_text.insert("1.0", self.update_info.get("release_notes", "Không có ghi chú"))
        notes_text.config(state=tk.DISABLED)
        notes_text.pack(fill=tk.X)
        
        # Progress bar (ẩn ban đầu)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100
        )
        
        self.status_label = ttk.Label(main_frame, text="")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.update_btn = ttk.Button(
            btn_frame,
            text="⬇️ Cập nhật ngay",
            command=self._start_update
        )
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.skip_btn = ttk.Button(
            btn_frame,
            text="Bỏ qua",
            command=self._skip_update
        )
        self.skip_btn.pack(side=tk.RIGHT, padx=5)
    
    def _start_update(self):
        """Bắt đầu tải và cài đặt update"""
        self.update_btn.config(state=tk.DISABLED)
        self.skip_btn.config(state=tk.DISABLED)
        
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        self.status_label.pack()
        self.status_label.config(text="🔍 Đang kiểm tra...")
        
        # Chạy trong thread riêng
        thread = threading.Thread(target=self._download_and_install, daemon=True)
        thread.start()
    
    def _download_and_install(self):
        """Tải và cài đặt update (chạy trong thread)"""
        # Kiểm tra lại để lấy download_url
        self.dialog.after(0, lambda: self.status_label.config(text="🔍 Đang lấy thông tin..."))
        check_result = self.update_service.check_for_update()
        
        if check_result.get("error"):
            self.dialog.after(0, lambda: self._show_error(check_result["error"]))
            return
        
        # Tải file
        self.dialog.after(0, lambda: self.status_label.config(text="⬇️ Đang tải..."))
        
        def update_progress(percent):
            self.dialog.after(0, lambda p=percent: self.progress_var.set(p))
            self.dialog.after(0, lambda p=percent: self.status_label.config(text=f"⬇️ Đang tải... {p}%"))
        
        download_result = self.update_service.download_update(update_progress)
        
        if not download_result.get("success"):
            self.dialog.after(0, lambda: self._show_error(download_result.get("error", "Lỗi tải file")))
            return
        
        # Cài đặt
        self.dialog.after(0, lambda: self.status_label.config(text="📦 Đang cài đặt..."))
        install_result = self.update_service.install_update(download_result["file_path"])
        
        if install_result.get("success"):
            self.dialog.after(0, self._install_success)
        else:
            self.dialog.after(0, lambda: self._show_error(install_result.get("error", "Lỗi cài đặt")))
    
    def _show_error(self, error_msg):
        """Hiển thị lỗi"""
        self.status_label.config(text=f"❌ {error_msg}")
        self.update_btn.config(state=tk.NORMAL)
        self.skip_btn.config(state=tk.NORMAL)
        messagebox.showerror("Lỗi cập nhật", error_msg, parent=self.dialog)
    
    def _install_success(self):
        """Cài đặt thành công, đóng app"""
        self.status_label.config(text="✅ Cập nhật thành công! Đang khởi động lại...")
        self.result = True
        self.dialog.after(1000, self._close_app)
    
    def _close_app(self):
        """Đóng ứng dụng để batch script thay thế exe"""
        self.dialog.destroy()
        self.parent.destroy()
    
    def _skip_update(self):
        """Bỏ qua cập nhật"""
        self.result = False
        self.dialog.destroy()


def check_and_show_update(parent) -> bool:
    """
    Kiểm tra update và hiển thị dialog nếu có bản mới.
    Args:
        parent: Cửa sổ cha (tk.Tk hoặc tk.Toplevel)
    Returns:
        True nếu đang cập nhật (app sẽ đóng), False nếu không
    """
    service = UpdateService()
    result = service.check_for_update()
    
    if result.get("has_update") and not result.get("error"):
        # Cập nhật download_url vào result
        result["download_url"] = service.download_url
        dialog = UpdateDialog(parent, result)
        return dialog.show()
    
    return False
