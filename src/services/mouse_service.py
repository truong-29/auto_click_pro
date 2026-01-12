# -*- coding: utf-8 -*-
"""Service xử lý các thao tác chuột"""

import pyautogui
import time
from typing import Tuple
import ctypes

from ..config import FAILSAFE, PAUSE

# Windows API constants
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001


class MouseService:
    """Service quản lý các thao tác chuột"""
    
    def __init__(self):
        pyautogui.FAILSAFE = FAILSAFE
        pyautogui.PAUSE = PAUSE
        # Lấy kích thước màn hình
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    
    def _to_absolute(self, x: int, y: int) -> Tuple[int, int]:
        """Chuyển đổi tọa độ sang absolute (0-65535)"""
        abs_x = int(x * 65535 / self.screen_width)
        abs_y = int(y * 65535 / self.screen_height)
        return abs_x, abs_y
    
    def _mouse_event(self, flags: int, x: int = 0, y: int = 0):
        """Gọi Windows API mouse_event"""
        ctypes.windll.user32.mouse_event(flags, x, y, 0, 0)
    
    def _set_cursor_pos(self, x: int, y: int):
        """Di chuyển chuột bằng Windows API"""
        ctypes.windll.user32.SetCursorPos(x, y)
    
    def get_position(self) -> Tuple[int, int]:
        """Lấy vị trí chuột hiện tại"""
        return pyautogui.position()
    
    def click(self, x: int, y: int) -> None:
        """Click chuột trái bằng Windows API"""
        self._set_cursor_pos(x, y)
        time.sleep(0.05)
        self._mouse_event(MOUSEEVENTF_LEFTDOWN)
        time.sleep(0.02)
        self._mouse_event(MOUSEEVENTF_LEFTUP)
    
    def right_click(self, x: int, y: int) -> None:
        """Click chuột phải bằng Windows API"""
        self._set_cursor_pos(x, y)
        time.sleep(0.05)
        self._mouse_event(MOUSEEVENTF_RIGHTDOWN)
        time.sleep(0.02)
        self._mouse_event(MOUSEEVENTF_RIGHTUP)
    
    def double_click(self, x: int, y: int) -> None:
        """Click đúp"""
        self.click(x, y)
        time.sleep(0.1)
        self.click(x, y)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        """Kéo thả chuột"""
        self._set_cursor_pos(start_x, start_y)
        time.sleep(0.1)
        self._mouse_event(MOUSEEVENTF_LEFTDOWN)
        
        # Di chuyển từ từ
        steps = int(duration * 50)
        for i in range(steps):
            progress = (i + 1) / steps
            curr_x = int(start_x + (end_x - start_x) * progress)
            curr_y = int(start_y + (end_y - start_y) * progress)
            self._set_cursor_pos(curr_x, curr_y)
            time.sleep(duration / steps)
        
        self._mouse_event(MOUSEEVENTF_LEFTUP)
    
    def move_to(self, x: int, y: int) -> None:
        """Di chuyển chuột đến vị trí"""
        self._set_cursor_pos(x, y)
