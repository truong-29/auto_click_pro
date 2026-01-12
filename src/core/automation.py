# -*- coding: utf-8 -*-
"""Core automation - Quản lý vòng lặp tự động hóa với hỗ trợ IF-ELSE"""

import threading
import time
from typing import Callable, List, Optional, Tuple

from ..models import Action, Step, Script
from .executor import ActionExecutor


class AutomationEngine:
    """Engine quản lý quá trình tự động hóa"""
    
    def __init__(self):
        self.executor = ActionExecutor()
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_status_change: Optional[Callable[[str], None]] = None
        self.on_complete: Optional[Callable[[], None]] = None
        self.on_loop_update: Optional[Callable[[int, int, int, int], None]] = None  # current_loop, total_loops, current_step, total_steps
    
    def set_callbacks(self, on_status: Callable[[str], None] = None,
                      on_complete: Callable[[], None] = None,
                      on_loop_update: Callable[[int, int, int, int], None] = None):
        """Đặt các callback"""
        self.on_status_change = on_status
        self.on_complete = on_complete
        self.on_loop_update = on_loop_update
        self.executor.set_status_callback(on_status)
    
    def set_target_window(self, hwnd: int) -> bool:
        """Đặt cửa sổ đích để gửi input"""
        return self.executor.set_target_window(hwnd)
    
    def clear_target_window(self):
        """Xóa cửa sổ đích, quay về chế độ toàn cục"""
        self.executor.clear_target_window()
    
    def get_window_service(self):
        """Lấy WindowService để UI sử dụng"""
        return self.executor.get_window_service()
    
    def get_execution_mode(self) -> str:
        """Lấy chế độ thực thi hiện tại: 'global' hoặc 'window'"""
        return self.executor.mode
    
    def _update_status(self, message: str):
        """Cập nhật trạng thái"""
        if self.on_status_change:
            self.on_status_change(message)
    
    def _update_loop_progress(self, current_loop: int, total_loops: int, 
                               current_step: int, total_steps: int):
        """Cập nhật tiến trình lặp lên UI"""
        if self.on_loop_update:
            self.on_loop_update(current_loop, total_loops, current_step, total_steps)
    
    def _get_all_actions_from_steps(self, steps: List[Step]) -> List[Action]:
        """Lấy tất cả actions từ các steps đã enabled"""
        all_actions = []
        for step in steps:
            if step.enabled:
                all_actions.extend(step.actions)
        return all_actions
    
    def _find_matching_block(self, actions: List[Action], start_idx: int, 
                              find_type: str) -> int:
        """
        Tìm vị trí của block tương ứng (THEN, ELSE, END_IF)
        Hỗ trợ IF lồng nhau
        """
        depth = 0
        for i in range(start_idx, len(actions)):
            action_type = actions[i].type
            
            if action_type in ["IF", "Điều kiện (IF)"]:
                depth += 1
            elif action_type == "END_IF":
                if depth == 0:
                    if find_type == "END_IF":
                        return i
                else:
                    depth -= 1
            elif action_type == "THEN":
                if depth == 0 and find_type == "THEN":
                    return i
            elif action_type == "ELSE":
                if depth == 0 and find_type == "ELSE":
                    return i
        
        return -1  # Không tìm thấy
    
    def _execute_actions(self, actions: List[Action], start_idx: int, 
                         end_idx: int) -> Tuple[int, str, int]:
        """
        Thực thi các actions từ start_idx đến end_idx (không bao gồm end_idx)
        Returns: (next_index, special_action, goto_step)
        """
        i = start_idx
        while i < end_idx and self.is_running:
            action = actions[i]
            action_type = action.type
            
            # Bỏ qua các block markers
            if action_type in ["THEN", "ELSE", "END_IF"]:
                i += 1
                continue
            
            # Xử lý IF block
            if action_type in ["IF", "Điều kiện (IF)"]:
                next_i, special, goto = self._handle_if_block(actions, i)
                if special:
                    return (next_i, special, goto)
                i = next_i
                continue
            
            # Thực thi action thường
            self._update_status(f"▶️ Bước {i+1}: {action.get_display_text()}")
            success, special_action, goto_step = self.executor.execute(action)
            
            if special_action:
                return (i + 1, special_action, goto_step)
            
            i += 1
        
        return (end_idx, "", -1)
    
    def _handle_if_block(self, actions: List[Action], if_idx: int) -> Tuple[int, str, int]:
        """
        Xử lý IF block hoàn chỉnh
        Returns: (next_index sau END_IF, special_action, goto_step)
        """
        if_action = actions[if_idx]
        
        # Tìm các vị trí THEN, ELSE, END_IF
        then_idx = self._find_matching_block(actions, if_idx + 1, "THEN")
        else_idx = self._find_matching_block(actions, if_idx + 1, "ELSE")
        end_if_idx = self._find_matching_block(actions, if_idx + 1, "END_IF")
        
        if end_if_idx == -1:
            self._update_status("⚠️ Thiếu KẾT THÚC IF")
            return (if_idx + 1, "", -1)
        
        # Kiểm tra điều kiện
        self._update_status(f"🔀 Kiểm tra điều kiện...")
        condition_result = self.executor.check_condition(if_action)
        
        if condition_result:
            self._update_status("✅ Điều kiện ĐÚNG → thực thi khối THÌ")
            # Thực thi từ sau THEN đến ELSE hoặc END_IF
            if then_idx != -1:
                start = then_idx + 1
                end = else_idx if else_idx != -1 else end_if_idx
                next_i, special, goto = self._execute_actions(actions, start, end)
                if special:
                    return (end_if_idx + 1, special, goto)
        else:
            self._update_status("❌ Điều kiện SAI → thực thi khối NGƯỢC LẠI")
            # Thực thi từ sau ELSE đến END_IF
            if else_idx != -1:
                start = else_idx + 1
                end = end_if_idx
                next_i, special, goto = self._execute_actions(actions, start, end)
                if special:
                    return (end_if_idx + 1, special, goto)
        
        # Trả về vị trí sau END_IF
        return (end_if_idx + 1, "", -1)

    def _run_loop(self, steps: List[Step], loop_count: int, 
                  infinite: bool, loop_delay: float):
        """Vòng lặp chính của automation"""
        current_loop = 0
        total_loops = 0 if infinite else loop_count
        
        # Lấy tất cả actions từ các steps
        actions = self._get_all_actions_from_steps(steps)
        total_steps = len(actions)
        
        if not actions:
            self._update_status("⚠️ Không có hành động nào để thực thi!")
            self.is_running = False
            if self.on_complete:
                self.on_complete()
            return
        
        self._update_status(f"🚀 Bắt đầu chạy {'vô hạn' if infinite else f'{loop_count} lần'}...")
        self._update_loop_progress(0, total_loops, 0, total_steps)
        
        while self.is_running:
            # Kiểm tra điều kiện dừng TRƯỚC khi tăng current_loop
            if not infinite and current_loop >= loop_count:
                self._update_status(f"✅ Hoàn thành {loop_count} lần lặp!")
                break
            
            current_loop += 1
            self._update_loop_progress(current_loop, total_loops, 0, total_steps)
            
            # Hiển thị thông tin lần lặp
            if infinite:
                self._update_status(f"🔄 Lần lặp #{current_loop}")
            else:
                self._update_status(f"🔄 Lần lặp {current_loop}/{loop_count}")
            
            # Reset context cho mỗi lần lặp
            self.executor.reset_context()
            
            i = 0
            
            while i < len(actions) and self.is_running:
                # Cập nhật tiến trình bước
                self._update_loop_progress(current_loop, total_loops, i + 1, total_steps)
                
                action = actions[i]
                action_type = action.type
                
                # Bỏ qua các block markers đơn lẻ
                if action_type in ["THEN", "ELSE", "END_IF"]:
                    i += 1
                    continue
                
                # Xử lý IF block
                if action_type in ["IF", "Điều kiện (IF)"]:
                    next_i, special, goto = self._handle_if_block(actions, i)
                    
                    if special == "stop":
                        self._update_status(f"⏹️ Dừng kịch bản (đã chạy {current_loop} lần)")
                        self.is_running = False
                        break
                    elif special == "restart":
                        self._update_status("🔄 Chạy lại từ đầu")
                        self.executor.reset_context()
                        i = 0
                        continue
                    elif special == "skip_loop":
                        self._update_status("⏭️ Chuyển lần lặp tiếp")
                        break
                    elif special == "goto":
                        if 0 <= goto < len(actions):
                            i = goto
                            continue
                    
                    i = next_i
                    continue
                
                # Thực thi action thường
                self._update_status(f"▶️ Bước {i+1}: {action.get_display_text()}")
                
                success, special_action, goto_step = self.executor.execute(action)
                
                # Xử lý special actions
                if special_action == "stop":
                    self._update_status(f"⏹️ Dừng kịch bản (đã chạy {current_loop} lần)")
                    self.is_running = False
                    break
                
                elif special_action == "restart":
                    self._update_status("🔄 Chạy lại từ đầu")
                    self.executor.reset_context()
                    i = 0
                    continue
                
                elif special_action == "skip_loop":
                    self._update_status("⏭️ Chuyển lần lặp tiếp")
                    break
                
                elif special_action == "goto":
                    if 0 <= goto_step < len(actions):
                        self._update_status(f"↪️ Nhảy đến bước {goto_step + 1}")
                        i = goto_step
                        continue
                    else:
                        self._update_status(f"⚠️ Bước {goto_step + 1} không hợp lệ")
                
                i += 1
            
            # Nếu không còn chạy, thoát vòng lặp chính
            if not self.is_running:
                break
            
            # Kiểm tra xem đã đủ số lần lặp chưa
            if not infinite and current_loop >= loop_count:
                self._update_status(f"✅ Hoàn thành {loop_count} lần lặp!")
                break
            
            # Delay giữa các lần lặp (chỉ khi còn lần lặp tiếp theo)
            if self.is_running:
                self._update_status(f"⏳ Chờ {loop_delay}s...")
                time.sleep(loop_delay)
        
        # Đảm bảo dừng hoàn toàn
        self.is_running = False
        self.executor.is_running = False
        self._update_loop_progress(current_loop, total_loops, 0, total_steps)
        
        if self.on_complete:
            self.on_complete()
    
    def start(self, script: Script):
        """Bắt đầu automation"""
        if not script.steps or all(len(s.actions) == 0 for s in script.steps):
            raise ValueError("Chưa có hành động nào!")
        
        self.is_running = True
        self.executor.is_running = True
        
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(script.steps, script.loop_count, script.infinite_loop, script.loop_delay),
            daemon=True
        )
        self._thread.start()
    
    def stop(self):
        """Dừng automation"""
        self.is_running = False
        self.executor.is_running = False
        self._update_status("⏹️ Đã dừng")
