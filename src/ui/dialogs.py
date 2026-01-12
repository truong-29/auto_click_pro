# -*- coding: utf-8 -*-
"""UI Dialogs - Các hộp thoại với style hiện đại"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional
import time

from ..config import IMAGE_FILETYPES, SCRIPT_FILETYPES, SCRIPTS_DIR, IMAGES_DIR
from .theme import COLORS, FONTS, DIMENSIONS


class DialogManager:
    """Quản lý các hộp thoại"""
    
    @staticmethod
    def select_image() -> Optional[str]:
        """Chọn file hình ảnh"""
        return filedialog.askopenfilename(
            title="Chọn hình ảnh",
            initialdir=IMAGES_DIR,
            filetypes=IMAGE_FILETYPES
        )
    
    @staticmethod
    def save_image() -> Optional[str]:
        """Lưu file hình ảnh"""
        return filedialog.asksaveasfilename(
            title="Lưu hình ảnh",
            initialdir=IMAGES_DIR,
            defaultextension=".png",
            filetypes=[("PNG", "*.png")]
        )
    
    @staticmethod
    def save_script() -> Optional[str]:
        """Lưu file kịch bản"""
        return filedialog.asksaveasfilename(
            title="Lưu kịch bản",
            initialdir=SCRIPTS_DIR,
            defaultextension=".json",
            filetypes=SCRIPT_FILETYPES
        )
    
    @staticmethod
    def load_script() -> Optional[str]:
        """Tải file kịch bản"""
        return filedialog.askopenfilename(
            title="Tải kịch bản",
            initialdir=SCRIPTS_DIR,
            filetypes=SCRIPT_FILETYPES
        )
    
    @staticmethod
    def confirm(title: str, message: str) -> bool:
        """Hộp thoại xác nhận"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def warning(title: str, message: str):
        """Hộp thoại cảnh báo"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def error(title: str, message: str):
        """Hộp thoại lỗi"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def ask_string(title: str, prompt: str, initial_value: str = "") -> Optional[str]:
        """Hộp thoại nhập chuỗi"""
        return simpledialog.askstring(title, prompt, initialvalue=initial_value)


class RegionCaptureDialog:
    """Dialog chụp vùng màn hình với style hiện đại"""
    
    def __init__(self, parent, on_capture: callable):
        self.parent = parent
        self.on_capture = on_capture
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        self.info_label = None
    
    def show(self):
        """Hiển thị dialog chụp vùng"""
        self.parent.iconify()
        time.sleep(0.3)
        
        self.overlay = tk.Toplevel()
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.4)
        self.overlay.configure(bg=COLORS["bg_primary"])
        
        self.canvas = tk.Canvas(
            self.overlay, 
            cursor="cross", 
            bg=COLORS["bg_primary"], 
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Hướng dẫn
        self.canvas.create_text(
            self.overlay.winfo_screenwidth() // 2,
            50,
            text="Kéo chuột để chọn vùng cần chụp - Nhấn ESC để hủy",
            font=FONTS["heading"],
            fill=COLORS["text_accent"]
        )
        
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.overlay.bind("<Escape>", self._on_cancel)
    
    def _on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline=COLORS["accent_primary"], 
            width=2,
            dash=(5, 3)
        )
        # Info label
        self.info_label = self.canvas.create_text(
            self.start_x, self.start_y - 20,
            text="0 x 0",
            font=FONTS["mono_small"],
            fill=COLORS["text_accent"],
            anchor="sw"
        )
    
    def _on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.canvas.coords(self.info_label, min(self.start_x, event.x), min(self.start_y, event.y) - 5)
        self.canvas.itemconfig(self.info_label, text=f"{width} x {height}")
    
    def _on_release(self, event):
        self.overlay.destroy()
        self.parent.deiconify()
        
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        
        if x2 - x1 > 10 and y2 - y1 > 10:
            self.on_capture((x1, y1, x2 - x1, y2 - y1))
        else:
            self.on_capture(None)
    
    def _on_cancel(self, event):
        self.overlay.destroy()
        self.parent.deiconify()
        self.on_capture(None)


class WindowSelectorDialog:
    """Dialog chọn cửa sổ ứng dụng đích"""
    
    def __init__(self, parent, window_service, on_select: callable):
        self.parent = parent
        self.window_service = window_service
        self.on_select = on_select
        self.selected_hwnd = None
        self.windows = []
    
    def show(self):
        """Hiển thị dialog chọn cửa sổ"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Chọn cửa sổ ứng dụng")
        self.dialog.geometry("600x450")
        self.dialog.configure(bg=COLORS["bg_primary"])
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 600) // 2
        y = (self.dialog.winfo_screenheight() - 450) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(self.dialog, bg=COLORS["bg_secondary"])
        header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header,
            text="🪟 Chọn cửa sổ ứng dụng",
            font=FONTS["heading"],
            fg=COLORS["text_accent"],
            bg=COLORS["bg_secondary"]
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Nút làm mới
        refresh_btn = tk.Button(
            header,
            text="🔄 Làm mới",
            font=FONTS["button"],
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            relief="flat",
            cursor="hand2",
            command=self._refresh_list
        )
        refresh_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Hướng dẫn
        hint_frame = tk.Frame(self.dialog, bg=COLORS["bg_primary"])
        hint_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(
            hint_frame,
            text="💡 Chọn cửa sổ để gửi input trực tiếp vào đó (không chiếm chuột/bàn phím)",
            font=FONTS["body_small"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_primary"]
        ).pack(anchor=tk.W)
        
        # Listbox với scrollbar
        list_frame = tk.Frame(self.dialog, bg=COLORS["bg_primary"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame,
            font=FONTS["mono_small"],
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            selectbackground=COLORS["selection_bg"],
            selectforeground=COLORS["selection_fg"],
            relief="flat",
            highlightthickness=1,
            highlightcolor=COLORS["accent_primary"],
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind('<Double-1>', lambda e: self._on_select())
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg=COLORS["bg_primary"])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút chọn bằng chuột
        pick_btn = tk.Button(
            btn_frame,
            text="🎯 Chọn bằng chuột (F8)",
            font=FONTS["button"],
            bg=COLORS["accent_secondary"],
            fg=COLORS["text_primary"],
            relief="flat",
            cursor="hand2",
            command=self._pick_by_mouse
        )
        pick_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút xóa chọn (quay về global)
        clear_btn = tk.Button(
            btn_frame,
            text="🌐 Chế độ toàn cục",
            font=FONTS["button"],
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            relief="flat",
            cursor="hand2",
            command=self._clear_selection
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút chọn
        select_btn = tk.Button(
            btn_frame,
            text="✓ Chọn",
            font=FONTS["button"],
            bg=COLORS["accent_primary"],
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            command=self._on_select
        )
        select_btn.pack(side=tk.RIGHT, padx=5)
        
        # Nút hủy
        cancel_btn = tk.Button(
            btn_frame,
            text="✕ Hủy",
            font=FONTS["button"],
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            relief="flat",
            cursor="hand2",
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Load danh sách cửa sổ
        self._refresh_list()
        
        # Bind phím tắt
        self.dialog.bind('<F8>', lambda e: self._pick_by_mouse())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        self.dialog.bind('<Return>', lambda e: self._on_select())
    
    def _refresh_list(self):
        """Làm mới danh sách cửa sổ"""
        self.listbox.delete(0, tk.END)
        self.windows = self.window_service.get_all_windows()
        
        for i, win in enumerate(self.windows):
            # Hiển thị: [Process] Title (WxH)
            text = f"[{win.process_name}] {win.title[:50]} ({win.width}x{win.height})"
            self.listbox.insert(tk.END, text)
    
    def _pick_by_mouse(self):
        """Chọn cửa sổ bằng cách di chuột đến và nhấn phím"""
        import keyboard as kb
        import ctypes
        
        self.dialog.withdraw()
        self._pick_cancelled = False
        self._overlay = None
        self._main_hwnd = None
        
        # Lưu hwnd của ứng dụng chính
        user32 = ctypes.windll.user32
        self._main_hwnd = user32.GetForegroundWindow()
        
        # Tạo overlay hướng dẫn
        overlay = tk.Toplevel()
        overlay.overrideredirect(True)
        overlay.attributes('-topmost', True)
        overlay.configure(bg=COLORS["bg_secondary"])
        self._overlay = overlay
        
        screen_w = overlay.winfo_screenwidth()
        overlay.geometry(f"450x80+{(screen_w-450)//2}+50")
        
        label = tk.Label(
            overlay,
            text="🎯 Di chuột đến cửa sổ, nhấn SPACE để chọn\nNhấn ESC để hủy",
            font=FONTS["heading"],
            fg=COLORS["text_accent"],
            bg=COLORS["bg_secondary"],
            padx=20, pady=15
        )
        label.pack(expand=True, fill=tk.BOTH)
        
        def cleanup():
            try:
                kb.remove_hotkey('escape')
                kb.remove_hotkey('space')
            except:
                pass
        
        def cancel_pick():
            self._pick_cancelled = True
            if self._overlay:
                self._overlay.destroy()
                self._overlay = None
            cleanup()
            self.dialog.deiconify()
            # Quay về ứng dụng chính
            if self._main_hwnd:
                user32.SetForegroundWindow(self._main_hwnd)
        
        def do_pick():
            if self._pick_cancelled:
                return
            if self._overlay:
                self._overlay.destroy()
                self._overlay = None
            cleanup()
            
            win_info = self.window_service.find_window_at_cursor()
            if win_info and win_info.title:
                self.selected_hwnd = win_info.hwnd
                self.dialog.destroy()
                self.on_select(win_info.hwnd, win_info)
                # Quay về ứng dụng chính
                if self._main_hwnd:
                    time.sleep(0.1)
                    user32.SetForegroundWindow(self._main_hwnd)
            else:
                self.dialog.deiconify()
                if self._main_hwnd:
                    user32.SetForegroundWindow(self._main_hwnd)
        
        # Bind phím tắt
        kb.add_hotkey('escape', cancel_pick, suppress=True)
        kb.add_hotkey('space', do_pick, suppress=True)
    
    def _on_select(self):
        """Xử lý khi chọn cửa sổ từ danh sách"""
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            win = self.windows[idx]
            self.selected_hwnd = win.hwnd
            self.dialog.destroy()
            self.on_select(win.hwnd, win)
    
    def _clear_selection(self):
        """Xóa chọn, quay về chế độ toàn cục"""
        self.dialog.destroy()
        self.on_select(None, None)
    
    def _on_cancel(self):
        """Hủy dialog"""
        self.dialog.destroy()
