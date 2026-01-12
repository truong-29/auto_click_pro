# -*- coding: utf-8 -*-
"""Service xử lý hình ảnh và nhận dạng - Hỗ trợ tìm trong cửa sổ cụ thể"""

import pyautogui
from PIL import Image
from typing import Optional, Tuple
import time
import os
import cv2
import numpy as np

from ..config import IMAGE_WAIT_TIMEOUT


class ImageService:
    """Service quản lý nhận dạng hình ảnh"""
    
    def __init__(self):
        self._window_service = None  # Sẽ được set từ executor
        self._window_offset = (0, 0)  # Offset của cửa sổ đích
    
    def set_window_service(self, window_service):
        """Đặt WindowService để tìm hình trong cửa sổ cụ thể"""
        self._window_service = window_service
    
    def find_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int, int, int]]:
        """Tìm hình ảnh trên màn hình"""
        if not image_path or not os.path.exists(image_path):
            return None
        try:
            return pyautogui.locateOnScreen(image_path, confidence=confidence)
        except TypeError:
            try:
                return pyautogui.locateOnScreen(image_path)
            except:
                return None
        except:
            return None
    
    def find_center_on_screen(self, image_path: str, confidence: float = 0.8, 
                               in_window: bool = False) -> Optional[Tuple[int, int]]:
        """
        Tìm tâm hình ảnh bằng OpenCV
        Args:
            image_path: Đường dẫn file hình ảnh
            confidence: Độ chính xác (0-1)
            in_window: True = tìm trong cửa sổ đích, False = tìm toàn màn hình
        Returns:
            Tọa độ (x, y) trên màn hình nếu tìm thấy, None nếu không
        """
        if not image_path or not os.path.exists(image_path):
            print(f"[ImageService] File không tồn tại: {image_path}")
            return None
        
        try:
            # Chụp ảnh nguồn
            if in_window and self._window_service and self._window_service.is_target_valid():
                # Chụp cửa sổ đích
                screenshot = self._window_service.capture_window()
                if screenshot is None:
                    print("[ImageService] Không thể chụp cửa sổ đích, dùng toàn màn hình")
                    screenshot = pyautogui.screenshot()
                    self._window_offset = (0, 0)
                else:
                    # Lưu offset để chuyển đổi tọa độ
                    rect = self._window_service.target_info.rect
                    self._window_offset = (rect[0], rect[1])
            else:
                # Chụp toàn màn hình
                screenshot = pyautogui.screenshot()
                self._window_offset = (0, 0)
            
            screen = np.array(screenshot)
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
            
            # Đọc template
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if template is None:
                print(f"[ImageService] Không đọc được file: {image_path}")
                return None
            
            # Tìm kiếm với template matching
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            print(f"[ImageService] Độ khớp: {max_val:.3f}, cần: {confidence}")
            
            # Kiểm tra độ khớp
            if max_val >= confidence:
                h, w = template.shape[:2]
                # Tọa độ trong ảnh chụp
                local_x = max_loc[0] + w // 2
                local_y = max_loc[1] + h // 2
                # Chuyển sang tọa độ màn hình
                screen_x = local_x + self._window_offset[0]
                screen_y = local_y + self._window_offset[1]
                print(f"[ImageService] Tìm thấy tại: ({screen_x}, {screen_y})")
                return (screen_x, screen_y)
            
            return None
        except Exception as e:
            print(f"[ImageService] Lỗi tìm hình: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def wait_for_image(self, image_path: str, confidence: float = 0.8, 
                       timeout: float = IMAGE_WAIT_TIMEOUT, check_running: callable = None) -> bool:
        """Chờ hình ảnh xuất hiện trên màn hình"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_running and not check_running():
                return False
            if self.find_center_on_screen(image_path, confidence):
                return True
            time.sleep(0.3)
        return False
    
    def capture_screenshot(self, region: Tuple[int, int, int, int] = None) -> Image.Image:
        """Chụp màn hình"""
        return pyautogui.screenshot(region=region)
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Lấy màu pixel tại vị trí"""
        screenshot = self.capture_screenshot()
        return screenshot.getpixel((x, y))
    
    def check_pixel_color(self, x: int, y: int, expected_rgb: Tuple[int, int, int], 
                          tolerance: int = 10) -> bool:
        """Kiểm tra màu pixel có khớp không"""
        current_color = self.get_pixel_color(x, y)
        return all(abs(current_color[i] - expected_rgb[i]) <= tolerance for i in range(3))
