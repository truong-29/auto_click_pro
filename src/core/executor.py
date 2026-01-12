# -*- coding: utf-8 -*-
"""Core executor - Thực thi các hành động với hỗ trợ IF-ELSE lồng nhau và chế độ cửa sổ"""

import time
import os
from typing import Callable, Optional, Tuple, List

from ..models import Action
from ..services import MouseService, ImageService, KeyboardService, WindowService, get_vk_code
from ..config import COLOR_TOLERANCE


class ExecutionContext:
    """Context lưu trạng thái thực thi"""
    def __init__(self):
        self.last_search_result: Optional[bool] = None  # Kết quả tìm hình gần nhất
        self.last_found_location: Optional[Tuple[int, int]] = None  # Vị trí tìm thấy
        self.variables: dict = {}  # Biến tùy chỉnh


class ActionExecutor:
    """Thực thi các hành động tự động với hỗ trợ block lồng nhau"""
    
    def __init__(self):
        self.mouse = MouseService()
        self.image = ImageService()
        self.keyboard = KeyboardService()
        self.window = WindowService()
        self.is_running = False
        self.context = ExecutionContext()
        self.on_status_change: Optional[Callable[[str], None]] = None
        # Chế độ: "global" = toàn cục, "window" = chỉ trong cửa sổ đích
        self.mode = "global"
        # Kết nối ImageService với WindowService
        self.image.set_window_service(self.window)
    
    def set_target_window(self, hwnd: int) -> bool:
        """Đặt cửa sổ đích và chuyển sang chế độ window"""
        if self.window.set_target_window(hwnd):
            self.mode = "window"
            return True
        return False
    
    def clear_target_window(self):
        """Xóa cửa sổ đích và quay về chế độ global"""
        self.window.clear_target()
        self.mode = "global"
    
    def get_window_service(self) -> WindowService:
        """Lấy WindowService để UI có thể sử dụng"""
        return self.window
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Đặt callback để cập nhật trạng thái"""
        self.on_status_change = callback
    
    def _update_status(self, message: str):
        """Cập nhật trạng thái"""
        if self.on_status_change:
            self.on_status_change(message)
    
    def reset_context(self):
        """Reset context cho lần chạy mới"""
        self.context = ExecutionContext()
    
    def check_condition(self, action: Action) -> bool:
        """
        Kiểm tra điều kiện của IF block
        Returns: True nếu điều kiện thỏa mãn
        """
        cond_type = action.condition_type
        
        if cond_type == "last_search_found":
            return self.context.last_search_result == True
        
        elif cond_type == "last_search_not_found":
            return self.context.last_search_result == False
        
        elif cond_type == "image_found":
            if not action.condition_image or not os.path.exists(action.condition_image):
                self._update_status(f"⚠️ File điều kiện không tồn tại")
                return False
            try:
                location = self.image.find_center_on_screen(
                    action.condition_image, 
                    action.condition_confidence
                )
                return location is not None
            except:
                return False
        
        elif cond_type == "image_not_found":
            if not action.condition_image or not os.path.exists(action.condition_image):
                return True  # Không có file = không tìm thấy
            try:
                location = self.image.find_center_on_screen(
                    action.condition_image, 
                    action.condition_confidence
                )
                return location is None
            except:
                return True
        
        elif cond_type == "color_match":
            try:
                parts = action.condition_color.split("@")
                rgb = tuple(map(int, parts[0].split(",")))
                pos = tuple(map(int, parts[1].split(",")))
                return self.image.check_pixel_color(pos[0], pos[1], rgb, COLOR_TOLERANCE)
            except:
                return False
        
        elif cond_type == "color_not_match":
            try:
                parts = action.condition_color.split("@")
                rgb = tuple(map(int, parts[0].split(",")))
                pos = tuple(map(int, parts[1].split(",")))
                return not self.image.check_pixel_color(pos[0], pos[1], rgb, COLOR_TOLERANCE)
            except:
                return True
        
        return False
    
    def execute(self, action: Action) -> Tuple[bool, str, int]:
        """
        Thực thi một hành động
        Returns: (success: bool, special_action: str, goto_step: int)
        - special_action: "", "goto", "restart", "skip_loop", "stop"
        - goto_step: step cần nhảy đến (nếu special_action == "goto")
        """
        if not self.is_running:
            return (False, "stop", -1)
        
        action_type = action.type
        
        try:
            # === ACTIONS ĐƠN GIẢN ===
            if action_type == "Click chuột trái":
                self._update_status(f"🖱️ Click ({action.x}, {action.y})")
                self._do_click(action.x, action.y)
                time.sleep(action.delay)
                return (True, "", -1)
            
            elif action_type == "Click chuột phải":
                self._update_status(f"🖱️ Click phải ({action.x}, {action.y})")
                self._do_right_click(action.x, action.y)
                time.sleep(action.delay)
                return (True, "", -1)
            
            elif action_type == "Click đúp":
                self._update_status(f"🖱️ Click đúp ({action.x}, {action.y})")
                self._do_double_click(action.x, action.y)
                time.sleep(action.delay)
                return (True, "", -1)
            
            elif action_type == "Kéo thả chuột":
                self._update_status(f"🖱️ Kéo ({action.x},{action.y}) → ({action.dest_x},{action.dest_y})")
                self._do_drag(action.x, action.y, action.dest_x, action.dest_y)
                time.sleep(action.delay)
                return (True, "", -1)
            
            elif action_type == "Chờ (delay)":
                self._update_status(f"⏱️ Chờ {action.delay}s")
                time.sleep(action.delay)
                return (True, "", -1)
            
            elif action_type == "Nhập văn bản":
                self._update_status(f"⌨️ Nhập: {action.text[:20]}...")
                self._do_type_text(action.text)
                time.sleep(action.delay)
                return (True, "", -1)
            
            elif action_type in ["Nhấn phím", "Tổ hợp phím"]:
                self._update_status(f"⌨️ Phím: {action.key}")
                self._do_press_key(action.key)
                time.sleep(action.delay)
                return (True, "", -1)
            
            # === TÌM HÌNH ẢNH ===
            elif action_type == "Tìm hình ảnh":
                return self._execute_find_image(action)
            
            # === IF BLOCK ===
            elif action_type in ["IF", "Điều kiện (IF)"]:
                return self._execute_if_block(action)
            
            # === GOTO ===
            elif action_type in ["GOTO", "Nhảy đến bước (GOTO)"]:
                self._update_status(f"↪️ Nhảy đến bước {action.goto_step + 1}")
                return (True, "goto", action.goto_step)
            
            # === LOOP CONTROL ===
            elif action_type in ["LOOP_CONTROL", "Điều khiển lặp"]:
                if action.loop_action == "restart":
                    self._update_status("🔄 Chạy lại từ đầu")
                    return (True, "restart", -1)
                elif action.loop_action == "skip_to_next":
                    self._update_status("⏭️ Chuyển lần lặp tiếp")
                    return (True, "skip_loop", -1)
                elif action.loop_action == "stop":
                    self._update_status("⏹️ Dừng kịch bản")
                    return (True, "stop", -1)
                return (True, "", -1)
            
            # === PLACEHOLDER cho cấu trúc IF ===
            elif action_type in ["THEN", "ELSE", "END_IF"]:
                # Các action này chỉ để hiển thị, không thực thi
                return (True, "", -1)
            
            else:
                self._update_status(f"⚠️ Loại action không xác định: {action_type}")
                return (True, "", -1)
        
        except Exception as e:
            self._update_status(f"❌ Lỗi: {e}")
            return (False, "", -1)
    
    # === CÁC HÀM THỰC THI THEO CHẾ ĐỘ ===
    def _do_click(self, x: int, y: int):
        """Click chuột - tự động chọn chế độ"""
        if self.mode == "window" and self.window.is_target_valid():
            # Chuyển tọa độ màn hình sang tọa độ client
            client_x, client_y = self.window.screen_to_client(x, y)
            self.window.post_click(client_x, client_y)
        else:
            self.mouse.click(x, y)
    
    def _do_right_click(self, x: int, y: int):
        """Click chuột phải - tự động chọn chế độ"""
        if self.mode == "window" and self.window.is_target_valid():
            client_x, client_y = self.window.screen_to_client(x, y)
            self.window.post_right_click(client_x, client_y)
        else:
            self.mouse.right_click(x, y)
    
    def _do_double_click(self, x: int, y: int):
        """Double click - tự động chọn chế độ"""
        if self.mode == "window" and self.window.is_target_valid():
            client_x, client_y = self.window.screen_to_client(x, y)
            self.window.post_double_click(client_x, client_y)
        else:
            self.mouse.double_click(x, y)
    
    def _do_drag(self, x1: int, y1: int, x2: int, y2: int):
        """Kéo thả - tự động chọn chế độ"""
        if self.mode == "window" and self.window.is_target_valid():
            cx1, cy1 = self.window.screen_to_client(x1, y1)
            cx2, cy2 = self.window.screen_to_client(x2, y2)
            self.window.post_drag(cx1, cy1, cx2, cy2)
        else:
            self.mouse.drag(x1, y1, x2, y2)
    
    def _do_type_text(self, text: str):
        """Nhập văn bản - tự động chọn chế độ"""
        if self.mode == "window" and self.window.is_target_valid():
            self.window.post_text(text)
        else:
            self.keyboard.type_text(text)
    
    def _do_press_key(self, key: str):
        """Nhấn phím - tự động chọn chế độ"""
        if self.mode == "window" and self.window.is_target_valid():
            # Xử lý tổ hợp phím
            if '+' in key:
                keys = key.lower().split('+')
                for k in keys:
                    vk = get_vk_code(k.strip())
                    if vk:
                        self.window.post_key(vk)
            else:
                vk = get_vk_code(key.lower())
                if vk:
                    self.window.post_key(vk)
        else:
            self.keyboard.press_key(key)
    
    def _execute_find_image(self, action: Action) -> Tuple[bool, str, int]:
        """Thực thi tìm hình ảnh - hỗ trợ tìm trong cửa sổ đích"""
        if not action.image:
            self._update_status("❌ Chưa chọn hình ảnh!")
            self.context.last_search_result = False
            return (False, "", -1)
        
        if not os.path.exists(action.image):
            self._update_status(f"❌ File không tồn tại: {action.image}")
            self.context.last_search_result = False
            return (False, "", -1)
        
        start_time = time.time()
        location = None
        search_count = 0
        in_window = (self.mode == "window" and self.window.is_target_valid())
        
        mode_text = "trong cửa sổ" if in_window else "toàn màn hình"
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed >= action.timeout:
                self._update_status(f"⚠️ Không tìm thấy sau {action.timeout}s ({mode_text})")
                self.context.last_search_result = False
                self.context.last_found_location = None
                time.sleep(action.delay)
                return (True, "", -1)  # Vẫn success, chỉ là không tìm thấy
            
            if not self.is_running:
                return (False, "stop", -1)
            
            search_count += 1
            self._update_status(f"🔍 Tìm hình {mode_text}... ({elapsed:.1f}s/{action.timeout}s)")
            
            try:
                location = self.image.find_center_on_screen(
                    action.image, 
                    action.confidence,
                    in_window=in_window
                )
                if location:
                    break
            except Exception as e:
                print(f"[Executor] Lỗi tìm hình: {e}")
            
            time.sleep(0.3)
        
        # Tìm thấy
        self.context.last_search_result = True
        self.context.last_found_location = location
        
        if action.click_when_found:
            self._do_click(location[0], location[1])
            self._update_status(f"✅ Tìm thấy và click tại {location}")
        else:
            self._update_status(f"✅ Tìm thấy tại {location}")
        
        time.sleep(action.delay)
        return (True, "", -1)
    
    def _execute_if_block(self, action: Action) -> Tuple[bool, str, int]:
        """Thực thi IF block với các action con"""
        self._update_status(f"🔀 Kiểm tra: {action._get_condition_text()}")
        
        condition_result = self.check_condition(action)
        
        if condition_result:
            self._update_status("✅ Điều kiện ĐÚNG → thực thi THEN")
            actions_to_run = action.then_actions
        else:
            self._update_status("❌ Điều kiện SAI → thực thi ELSE")
            actions_to_run = action.else_actions
        
        # Thực thi các action con
        for sub_action in actions_to_run:
            if not self.is_running:
                return (False, "stop", -1)
            
            if isinstance(sub_action, Action):
                success, special, goto = self.execute(sub_action)
                
                # Propagate special actions
                if special in ["stop", "restart", "skip_loop", "goto"]:
                    return (success, special, goto)
                
                if not success:
                    return (False, "", -1)
        
        return (True, "", -1)
