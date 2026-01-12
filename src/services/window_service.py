# -*- coding: utf-8 -*-
"""Service quản lý cửa sổ ứng dụng - Gửi input trực tiếp vào cửa sổ đích"""

import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32api
import win32process
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
from PIL import Image
import time

# Windows API constants
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_LBUTTONDBLCLK = 0x0203
WM_MOUSEMOVE = 0x0200
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_SETTEXT = 0x000C

MK_LBUTTON = 0x0001


@dataclass
class WindowInfo:
    """Thông tin cửa sổ"""
    hwnd: int
    title: str
    class_name: str
    process_id: int
    process_name: str
    rect: Tuple[int, int, int, int]  # left, top, right, bottom
    
    @property
    def width(self) -> int:
        return self.rect[2] - self.rect[0]
    
    @property
    def height(self) -> int:
        return self.rect[3] - self.rect[1]
    
    def __str__(self):
        return f"{self.title} ({self.process_name})"


class WindowService:
    """Service quản lý và tương tác với cửa sổ ứng dụng"""
    
    def __init__(self):
        self.target_hwnd: Optional[int] = None
        self.target_info: Optional[WindowInfo] = None
        # Load user32.dll
        self.user32 = ctypes.windll.user32
    
    def get_all_windows(self) -> List[WindowInfo]:
        """Lấy danh sách tất cả cửa sổ đang mở"""
        windows = []
        
        def enum_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # Chỉ lấy cửa sổ có title
                    try:
                        info = self._get_window_info(hwnd)
                        if info:
                            windows.append(info)
                    except:
                        pass
            return True
        
        win32gui.EnumWindows(enum_callback, None)
        return sorted(windows, key=lambda w: w.title.lower())
    
    def _get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """Lấy thông tin chi tiết của cửa sổ"""
        try:
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            
            # Lấy process info
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            process_name = self._get_process_name(process_id)
            
            return WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                process_id=process_id,
                process_name=process_name,
                rect=rect
            )
        except:
            return None
    
    def _get_process_name(self, pid: int) -> str:
        """Lấy tên process từ PID"""
        try:
            import psutil
            process = psutil.Process(pid)
            return process.name()
        except:
            return "Unknown"
    
    def set_target_window(self, hwnd: int) -> bool:
        """Đặt cửa sổ đích để gửi input"""
        if win32gui.IsWindow(hwnd):
            self.target_hwnd = hwnd
            self.target_info = self._get_window_info(hwnd)
            return True
        return False
    
    def set_target_by_title(self, title: str) -> bool:
        """Đặt cửa sổ đích theo title"""
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            return self.set_target_window(hwnd)
        return False
    
    def clear_target(self):
        """Xóa cửa sổ đích (quay về chế độ toàn cục)"""
        self.target_hwnd = None
        self.target_info = None
    
    def get_target_info(self) -> Optional[WindowInfo]:
        """Lấy thông tin cửa sổ đích hiện tại"""
        if self.target_hwnd and win32gui.IsWindow(self.target_hwnd):
            self.target_info = self._get_window_info(self.target_hwnd)
            return self.target_info
        return None
    
    def is_target_valid(self) -> bool:
        """Kiểm tra cửa sổ đích còn tồn tại không"""
        return self.target_hwnd is not None and win32gui.IsWindow(self.target_hwnd)
    
    def get_client_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """Lấy vùng client của cửa sổ đích (không bao gồm title bar)"""
        if not self.is_target_valid():
            return None
        try:
            rect = win32gui.GetClientRect(self.target_hwnd)
            point = win32gui.ClientToScreen(self.target_hwnd, (0, 0))
            return (point[0], point[1], point[0] + rect[2], point[1] + rect[3])
        except:
            return None
    
    def screen_to_client(self, x: int, y: int) -> Tuple[int, int]:
        """Chuyển tọa độ màn hình sang tọa độ client của cửa sổ"""
        if not self.is_target_valid():
            return (x, y)
        try:
            return win32gui.ScreenToClient(self.target_hwnd, (x, y))
        except:
            return (x, y)
    
    def client_to_screen(self, x: int, y: int) -> Tuple[int, int]:
        """Chuyển tọa độ client sang tọa độ màn hình"""
        if not self.is_target_valid():
            return (x, y)
        try:
            return win32gui.ClientToScreen(self.target_hwnd, (x, y))
        except:
            return (x, y)
    
    def _make_lparam(self, x: int, y: int) -> int:
        """Tạo LPARAM từ tọa độ x, y"""
        return (y << 16) | (x & 0xFFFF)
    
    def post_click(self, x: int, y: int) -> bool:
        """Gửi click chuột trái vào cửa sổ đích (không chiếm chuột)"""
        if not self.is_target_valid():
            return False
        try:
            lparam = self._make_lparam(x, y)
            win32gui.PostMessage(self.target_hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
            time.sleep(0.02)
            win32gui.PostMessage(self.target_hwnd, WM_LBUTTONUP, 0, lparam)
            return True
        except Exception as e:
            print(f"[WindowService] Lỗi post_click: {e}")
            return False
    
    def post_right_click(self, x: int, y: int) -> bool:
        """Gửi click chuột phải vào cửa sổ đích"""
        if not self.is_target_valid():
            return False
        try:
            lparam = self._make_lparam(x, y)
            win32gui.PostMessage(self.target_hwnd, WM_RBUTTONDOWN, 0, lparam)
            time.sleep(0.02)
            win32gui.PostMessage(self.target_hwnd, WM_RBUTTONUP, 0, lparam)
            return True
        except Exception as e:
            print(f"[WindowService] Lỗi post_right_click: {e}")
            return False
    
    def post_double_click(self, x: int, y: int) -> bool:
        """Gửi double click vào cửa sổ đích"""
        if not self.is_target_valid():
            return False
        try:
            lparam = self._make_lparam(x, y)
            win32gui.PostMessage(self.target_hwnd, WM_LBUTTONDBLCLK, MK_LBUTTON, lparam)
            time.sleep(0.02)
            win32gui.PostMessage(self.target_hwnd, WM_LBUTTONUP, 0, lparam)
            return True
        except Exception as e:
            print(f"[WindowService] Lỗi post_double_click: {e}")
            return False

    def post_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                  duration: float = 0.5) -> bool:
        """Gửi kéo thả chuột vào cửa sổ đích"""
        if not self.is_target_valid():
            return False
        try:
            # Mouse down tại điểm bắt đầu
            lparam_start = self._make_lparam(start_x, start_y)
            win32gui.PostMessage(self.target_hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam_start)
            
            # Di chuyển từ từ
            steps = max(int(duration * 50), 10)
            for i in range(steps):
                progress = (i + 1) / steps
                curr_x = int(start_x + (end_x - start_x) * progress)
                curr_y = int(start_y + (end_y - start_y) * progress)
                lparam = self._make_lparam(curr_x, curr_y)
                win32gui.PostMessage(self.target_hwnd, WM_MOUSEMOVE, MK_LBUTTON, lparam)
                time.sleep(duration / steps)
            
            # Mouse up tại điểm kết thúc
            lparam_end = self._make_lparam(end_x, end_y)
            win32gui.PostMessage(self.target_hwnd, WM_LBUTTONUP, 0, lparam_end)
            return True
        except Exception as e:
            print(f"[WindowService] Lỗi post_drag: {e}")
            return False
    
    def post_key(self, vk_code: int) -> bool:
        """Gửi phím vào cửa sổ đích"""
        if not self.is_target_valid():
            return False
        try:
            win32gui.PostMessage(self.target_hwnd, WM_KEYDOWN, vk_code, 0)
            time.sleep(0.02)
            win32gui.PostMessage(self.target_hwnd, WM_KEYUP, vk_code, 0)
            return True
        except Exception as e:
            print(f"[WindowService] Lỗi post_key: {e}")
            return False
    
    def post_text(self, text: str) -> bool:
        """Gửi văn bản vào cửa sổ đích (từng ký tự)"""
        if not self.is_target_valid():
            return False
        try:
            for char in text:
                win32gui.PostMessage(self.target_hwnd, WM_CHAR, ord(char), 0)
                time.sleep(0.01)
            return True
        except Exception as e:
            print(f"[WindowService] Lỗi post_text: {e}")
            return False
    
    def capture_window(self) -> Optional[Image.Image]:
        """Chụp ảnh cửa sổ đích"""
        if not self.is_target_valid():
            return None
        try:
            import win32ui
            from ctypes import windll
            
            # Lấy kích thước cửa sổ
            left, top, right, bottom = win32gui.GetWindowRect(self.target_hwnd)
            width = right - left
            height = bottom - top
            
            # Tạo device context
            hwnd_dc = win32gui.GetWindowDC(self.target_hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # Tạo bitmap
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)
            
            # Sử dụng PrintWindow để chụp cả khi cửa sổ bị che
            result = windll.user32.PrintWindow(self.target_hwnd, save_dc.GetSafeHdc(), 2)
            
            if result:
                # Chuyển sang PIL Image
                bmpinfo = bitmap.GetInfo()
                bmpstr = bitmap.GetBitmapBits(True)
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
            else:
                img = None
            
            # Cleanup
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self.target_hwnd, hwnd_dc)
            
            return img
        except Exception as e:
            print(f"[WindowService] Lỗi capture_window: {e}")
            return None
    
    def bring_to_front(self) -> bool:
        """Đưa cửa sổ đích lên trước"""
        if not self.is_target_valid():
            return False
        try:
            win32gui.SetForegroundWindow(self.target_hwnd)
            return True
        except:
            return False
    
    def find_window_at_cursor(self) -> Optional[WindowInfo]:
        """Tìm cửa sổ tại vị trí con trỏ chuột"""
        try:
            point = win32api.GetCursorPos()
            hwnd = win32gui.WindowFromPoint(point)
            # Lấy cửa sổ cha (top-level window)
            root_hwnd = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
            if root_hwnd:
                return self._get_window_info(root_hwnd)
        except:
            pass
        return None


# Virtual Key Codes mapping
VK_CODES = {
    'enter': 0x0D, 'return': 0x0D,
    'tab': 0x09,
    'space': 0x20,
    'backspace': 0x08, 'back': 0x08,
    'delete': 0x2E, 'del': 0x2E,
    'escape': 0x1B, 'esc': 0x1B,
    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
    'home': 0x24, 'end': 0x23,
    'pageup': 0x21, 'pagedown': 0x22,
    'insert': 0x2D,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
    'ctrl': 0x11, 'control': 0x11,
    'alt': 0x12, 'menu': 0x12,
    'shift': 0x10,
    'win': 0x5B, 'windows': 0x5B,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
}


def get_vk_code(key: str) -> int:
    """Lấy Virtual Key Code từ tên phím"""
    return VK_CODES.get(key.lower(), 0)
