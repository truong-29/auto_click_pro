# -*- coding: utf-8 -*-
"""Model cho hành động - Hỗ trợ block lồng nhau"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Any
import json


@dataclass
class Action:
    """
    Đại diện cho một hành động trong kịch bản.
    
    Các loại action:
    - SIMPLE: Click, Nhập text, Nhấn phím, Delay (thực thi trực tiếp)
    - FIND_IMAGE: Tìm hình ảnh (trả về True/False, có thể click nếu tìm thấy)
    - IF_BLOCK: Khối điều kiện với các action con
    - GOTO: Nhảy đến step khác
    - LOOP_CONTROL: Điều khiển vòng lặp (restart, skip, stop)
    """
    
    # Loại hành động cơ bản
    type: str = "Click chuột trái"
    
    # Tham số cho click/drag
    x: int = 0
    y: int = 0
    dest_x: int = 0
    dest_y: int = 0
    
    # Tham số cho tìm hình ảnh
    image: str = ""
    confidence: float = 0.8
    timeout: float = 10.0
    click_when_found: bool = True  # Click vào hình khi tìm thấy
    
    # Tham số chung
    delay: float = 0.5  # Delay sau action
    
    # Tham số cho keyboard
    text: str = ""
    key: str = ""
    
    # === IF BLOCK ===
    # Điều kiện (dùng cho type="IF")
    condition_type: str = ""  # "image_found", "image_not_found", "color_match", "color_not_match"
    condition_image: str = ""  # Hình ảnh để kiểm tra
    condition_color: str = ""  # Màu để kiểm tra (format: "r,g,b@x,y")
    condition_confidence: float = 0.8
    
    # Actions con (cho IF block)
    then_actions: List[Any] = field(default_factory=list)  # Thực thi nếu điều kiện đúng
    else_actions: List[Any] = field(default_factory=list)  # Thực thi nếu điều kiện sai
    
    # === GOTO / LOOP CONTROL ===
    goto_step: int = -1  # -1 = không dùng, 0+ = nhảy đến step
    loop_action: str = ""  # "restart", "skip_to_next", "stop"
    
    # Mô tả (để hiển thị)
    description: str = ""
    
    def to_dict(self) -> dict:
        """Chuyển đổi thành dictionary"""
        data = {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "dest_x": self.dest_x,
            "dest_y": self.dest_y,
            "image": self.image,
            "confidence": self.confidence,
            "timeout": self.timeout,
            "click_when_found": self.click_when_found,
            "delay": self.delay,
            "text": self.text,
            "key": self.key,
            "condition_type": self.condition_type,
            "condition_image": self.condition_image,
            "condition_color": self.condition_color,
            "condition_confidence": self.condition_confidence,
            "goto_step": self.goto_step,
            "loop_action": self.loop_action,
            "description": self.description,
        }
        
        # Serialize nested actions
        if self.then_actions:
            data["then_actions"] = [
                a.to_dict() if isinstance(a, Action) else a 
                for a in self.then_actions
            ]
        else:
            data["then_actions"] = []
            
        if self.else_actions:
            data["else_actions"] = [
                a.to_dict() if isinstance(a, Action) else a 
                for a in self.else_actions
            ]
        else:
            data["else_actions"] = []
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Action":
        """Tạo Action từ dictionary với backward compatibility"""
        # Backward compatibility: chuyển đổi type cũ sang mới
        action_type = data.get("type", "Click chuột trái")
        if action_type == "Tìm hình ảnh và click":
            action_type = "Tìm hình ảnh"
            data["click_when_found"] = True
        elif action_type == "Chờ hình ảnh xuất hiện":
            action_type = "Tìm hình ảnh"
            data["click_when_found"] = False
        
        # Parse nested actions
        then_actions = []
        for a in data.get("then_actions", []):
            if isinstance(a, dict):
                then_actions.append(cls.from_dict(a))
            else:
                then_actions.append(a)
        
        else_actions = []
        for a in data.get("else_actions", []):
            if isinstance(a, dict):
                else_actions.append(cls.from_dict(a))
            else:
                else_actions.append(a)
        
        return cls(
            type=action_type,
            x=data.get("x", 0),
            y=data.get("y", 0),
            dest_x=data.get("dest_x", 0),
            dest_y=data.get("dest_y", 0),
            image=data.get("image", ""),
            confidence=data.get("confidence", 0.8),
            timeout=data.get("timeout", 10.0),
            click_when_found=data.get("click_when_found", True),
            delay=data.get("delay", 0.5),
            text=data.get("text", ""),
            key=data.get("key", ""),
            condition_type=data.get("condition_type", ""),
            condition_image=data.get("condition_image", ""),
            condition_color=data.get("condition_color", ""),
            condition_confidence=data.get("condition_confidence", 0.8),
            then_actions=then_actions,
            else_actions=else_actions,
            goto_step=data.get("goto_step", -1),
            loop_action=data.get("loop_action", ""),
            description=data.get("description", ""),
        )
    
    def get_display_text(self, indent: int = 0) -> str:
        """Lấy text hiển thị cho action"""
        import os
        
        if self.type in ["IF", "Điều kiện (IF)"]:
            return ""
        elif self.type == "THEN":
            return ""
        elif self.type == "ELSE":
            return ""
        elif self.type == "END_IF":
            return ""
        elif self.type == "Tìm hình ảnh":
            name = os.path.basename(self.image) if self.image else "?"
            click = " và Click" if self.click_when_found else ""
            return f"Tìm hình: {name} (chờ {self.timeout}s){click}"
        elif self.type in ["GOTO", "Nhảy đến bước (GOTO)"]:
            return f"Nhảy đến bước {self.goto_step + 1}"
        elif self.type in ["LOOP_CONTROL", "Điều khiển lặp"]:
            actions = {"restart": "Chạy lại từ đầu", "skip_to_next": "Chuyển lần lặp tiếp", "stop": "Dừng kịch bản"}
            return actions.get(self.loop_action, self.loop_action)
        elif self.type == "Click chuột trái":
            return f"Click tại ({self.x}, {self.y})"
        elif self.type == "Click chuột phải":
            return f"Click phải tại ({self.x}, {self.y})"
        elif self.type == "Click đúp":
            return f"Click đúp tại ({self.x}, {self.y})"
        elif self.type == "Kéo thả chuột":
            return f"Kéo từ ({self.x},{self.y}) đến ({self.dest_x},{self.dest_y})"
        elif self.type == "Chờ (delay)":
            return f"Chờ {self.delay} giây"
        elif self.type == "Nhập văn bản":
            txt = self.text[:20] + "..." if len(self.text) > 20 else self.text
            return f"Nhập: \"{txt}\""
        elif self.type in ["Nhấn phím", "Tổ hợp phím"]:
            return f"Nhấn phím: {self.key}"
        else:
            return f"{self.type}"
    
    def _get_condition_text(self) -> str:
        """Lấy text mô tả điều kiện"""
        import os
        if self.condition_type == "image_found":
            name = os.path.basename(self.condition_image) if self.condition_image else "?"
            return f"tìm thấy hình [{name}]"
        elif self.condition_type == "image_not_found":
            name = os.path.basename(self.condition_image) if self.condition_image else "?"
            return f"KHÔNG tìm thấy hình [{name}]"
        elif self.condition_type == "color_match":
            return f"màu pixel khớp [{self.condition_color}]"
        elif self.condition_type == "color_not_match":
            return f"màu pixel KHÔNG khớp [{self.condition_color}]"
        elif self.condition_type == "last_search_found":
            return "kết quả tìm kiếm trước = TÌM THẤY"
        elif self.condition_type == "last_search_not_found":
            return "kết quả tìm kiếm trước = KHÔNG TÌM THẤY"
        return self.condition_type


@dataclass
class Step:
    """Đại diện cho một bước (Step) chứa nhiều hành động"""
    
    name: str = "Bước mới"
    actions: List[Any] = field(default_factory=list)
    enabled: bool = True
    
    def to_dict(self) -> dict:
        """Chuyển đổi thành dictionary"""
        return {
            "name": self.name,
            "actions": [a.to_dict() if isinstance(a, Action) else a for a in self.actions],
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Step":
        """Tạo Step từ dictionary"""
        actions = [Action.from_dict(a) for a in data.get("actions", [])]
        return cls(
            name=data.get("name", "Bước mới"),
            actions=actions,
            enabled=data.get("enabled", True)
        )
    
    def get_display_text(self) -> str:
        """Lấy text hiển thị cho step"""
        status = "[ON]" if self.enabled else "[OFF]"
        return f"{status} {self.name} ({len(self.actions)} actions)"


@dataclass
class Script:
    """Đại diện cho một kịch bản (danh sách các Step)"""
    
    steps: List[Any] = field(default_factory=list)
    # Backward compatibility: giữ lại actions cho script cũ
    actions: list = field(default_factory=list)
    loop_count: int = 1
    infinite_loop: bool = False
    loop_delay: float = 1.0
    
    def to_dict(self) -> dict:
        """Chuyển đổi thành dictionary"""
        return {
            "steps": [s.to_dict() if isinstance(s, Step) else s for s in self.steps],
            "loop_count": self.loop_count,
            "infinite_loop": self.infinite_loop,
            "loop_delay": self.loop_delay
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Script":
        """Tạo Script từ dictionary với backward compatibility"""
        # Nếu có steps mới
        if "steps" in data and data["steps"]:
            steps = [Step.from_dict(s) for s in data.get("steps", [])]
            return cls(
                steps=steps,
                actions=[],
                loop_count=data.get("loop_count", 1),
                infinite_loop=data.get("infinite_loop", False),
                loop_delay=data.get("loop_delay", 1.0)
            )
        # Backward compatibility: chuyển actions cũ thành 1 step
        elif "actions" in data and data["actions"]:
            actions = [Action.from_dict(a) for a in data.get("actions", [])]
            step = Step(name="Bước 1 (imported)", actions=actions)
            return cls(
                steps=[step],
                actions=[],
                loop_count=data.get("loop_count", 1),
                infinite_loop=data.get("infinite_loop", False),
                loop_delay=data.get("loop_delay", 1.0)
            )
        return cls(
            steps=[],
            actions=[],
            loop_count=data.get("loop_count", 1),
            infinite_loop=data.get("infinite_loop", False),
            loop_delay=data.get("loop_delay", 1.0)
        )
    
    def get_all_actions(self) -> List[Action]:
        """Lấy tất cả actions từ tất cả steps (để thực thi)"""
        all_actions = []
        for step in self.steps:
            if step.enabled:
                all_actions.extend(step.actions)
        return all_actions
