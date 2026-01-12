# -*- coding: utf-8 -*-
"""Service xử lý bàn phím"""

import keyboard
import time


class KeyboardService:
    """Service quản lý bàn phím"""
    
    def type_text(self, text: str, interval: float = 0.02):
        """Nhập văn bản (hỗ trợ tiếng Việt)"""
        keyboard.write(text, delay=interval)
    
    def press_key(self, key: str):
        """Nhấn một phím đặc biệt"""
        keyboard.press_and_release(key)
    
    def hotkey(self, *keys):
        """Nhấn tổ hợp phím (vd: ctrl, c)"""
        combo = '+'.join(keys)
        keyboard.press_and_release(combo)
