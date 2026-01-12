# -*- coding: utf-8 -*-
"""Main Window - Giao diện chính với thiết kế hiện đại"""

import tkinter as tk
from tkinter import ttk
import threading
import keyboard

from ..config import (
    WINDOW_TITLE, HOTKEYS, ACTION_TYPES, 
    CONDITION_TYPES, LOOP_ACTIONS, DEFAULT_DELAY, DEFAULT_CONFIDENCE, 
    DEFAULT_LOOP_COUNT, DEFAULT_LOOP_DELAY
)
from ..models import Action, Step, Script
from ..services import MouseService, ImageService, ScriptService, UpdateService
from ..core import AutomationEngine
from ..config import APP_VERSION
from .theme import COLORS, FONTS, DIMENSIONS
from .components import (
    ModernFrame, ModernLabelFrame, ModernLabel, ModernEntry,
    ModernButton, ModernCombobox, ModernCheckbutton, ModernScale,
    ModernListbox, ModernScrollbar, StatusBar, SectionHeader,
    IconButton, Separator
)
from .dialogs import DialogManager, RegionCaptureDialog, WindowSelectorDialog, UpdateDialog


class MainWindow:
    """Cửa sổ chính với giao diện hiện đại"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry("1280x1000")
        self.root.minsize(900, 650)
        self.root.configure(bg=COLORS["bg_primary"])
        
        # Services
        self.mouse_service = MouseService()
        self.image_service = ImageService()
        self.script_service = ScriptService()
        self.automation = AutomationEngine()
        self.update_service = UpdateService()
        
        # Update dialog reference
        self._update_dialog = None
        
        # Data
        self.steps: list[Step] = []
        self.current_step_index: int = -1
        self._editing_action_index = None
        
        # Setup
        self._setup_style()
        self._setup_ui()
        self._setup_hotkeys()
        self._setup_callbacks()
        self._update_mouse_position()
        self._check_for_updates()  # Kiểm tra cập nhật khi khởi động
    
    def _setup_style(self):
        """Thiết lập style cho ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Combobox style
        style.configure(
            "Modern.TCombobox",
            fieldbackground=COLORS["bg_input"],
            background=COLORS["bg_input"],
            foreground=COLORS["text_primary"],
            arrowcolor=COLORS["text_accent"],
            borderwidth=0,
            relief="flat"
        )
        style.map("Modern.TCombobox",
            fieldbackground=[("readonly", COLORS["bg_input"])],
            selectbackground=[("readonly", COLORS["selection_bg"])],
            selectforeground=[("readonly", COLORS["selection_fg"])]
        )
        
        # Configure option menu colors
        self.root.option_add('*TCombobox*Listbox.background', COLORS["bg_input"])
        self.root.option_add('*TCombobox*Listbox.foreground', COLORS["text_primary"])
        self.root.option_add('*TCombobox*Listbox.selectBackground', COLORS["selection_bg"])
        self.root.option_add('*TCombobox*Listbox.selectForeground', COLORS["selection_fg"])

    def _setup_callbacks(self):
        self.automation.set_callbacks(
            on_status=self._update_status,
            on_complete=self._on_automation_complete,
            on_loop_update=self._on_loop_update
        )
    
    def _on_loop_update(self, current_loop: int, total_loops: int, 
                        current_step: int, total_steps: int):
        """Cập nhật hiển thị tiến trình lặp trên UI"""
        def update():
            # Kiểm tra các widget đã được tạo chưa
            if not hasattr(self, 'loop_progress_frame'):
                return
            
            # Hiển thị frame tiến trình
            self.loop_progress_frame.pack(fill=tk.X, pady=(DIMENSIONS["padding_sm"], 0))
            
            # Cập nhật số lần lặp hiện tại
            self.loop_current_label.config(text=str(current_loop))
            
            # Cập nhật tổng số lần lặp
            if total_loops == 0:
                self.loop_total_label.config(text="∞")
            else:
                self.loop_total_label.config(text=str(total_loops))
            
            # Cập nhật bước hiện tại
            if current_step > 0:
                self.loop_step_label.config(text=f"Bước {current_step} / {total_steps}")
                # Cập nhật progress bar
                progress = current_step / total_steps if total_steps > 0 else 0
                self.progress_bar_fill.place(x=0, y=0, relheight=1, relwidth=progress)
            else:
                self.loop_step_label.config(text="Đang chờ...")
                self.progress_bar_fill.place(x=0, y=0, relheight=1, relwidth=0)
        
        # Chạy trên main thread
        self.root.after(0, update)
    
    def _setup_ui(self):
        """Thiết lập giao diện chính"""
        # Main container
        main = ModernFrame(self.root, bg=COLORS["bg_primary"])
        main.pack(fill=tk.BOTH, expand=True, padx=DIMENSIONS["padding_lg"], pady=DIMENSIONS["padding_lg"])
        
        # Header
        self._create_header(main)
        
        # Content - 2 cột
        content = ModernFrame(main, bg=COLORS["bg_primary"])
        content.pack(fill=tk.BOTH, expand=True, pady=(DIMENSIONS["padding_md"], 0))
        
        # Cột trái - Panel thêm hành động
        left_panel = ModernFrame(content, bg=COLORS["bg_primary"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, DIMENSIONS["padding_md"]))
        left_panel.config(width=450)
        left_panel.pack_propagate(False)
        self._create_action_panel(left_panel)
        
        # Cột phải - Danh sách + Điều khiển
        right_panel = ModernFrame(content, bg=COLORS["bg_primary"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._create_list_panel(right_panel)
        self._create_control_panel(right_panel)
    
    def _create_header(self, parent):
        """Tạo header với logo và title"""
        header = ModernFrame(parent, bg=COLORS["bg_secondary"])
        header.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_md"]))
        
        # Inner padding
        inner = ModernFrame(header, bg=COLORS["bg_secondary"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_lg"], pady=DIMENSIONS["padding_md"])
        
        # Logo và title
        title_frame = ModernFrame(inner, bg=COLORS["bg_secondary"])
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="AutoClick",
            font=FONTS["heading_large"],
            fg=COLORS["accent_primary"],
            bg=COLORS["bg_secondary"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Pro",
            font=FONTS["heading_large"],
            fg=COLORS["text_accent"],
            bg=COLORS["bg_secondary"]
        ).pack(side=tk.LEFT, padx=(4, 0))
        
        # Hotkey hints
        hints_frame = ModernFrame(inner, bg=COLORS["bg_secondary"])
        hints_frame.pack(side=tk.RIGHT)
        
        hints = [
            ("F2", "Chọn vị trí"),
            ("F4", "Chụp hình"),
            ("F6", "Bắt đầu"),
            ("F7", "Dừng"),
        ]
        for key, desc in hints:
            hint = ModernFrame(hints_frame, bg=COLORS["bg_secondary"])
            hint.pack(side=tk.LEFT, padx=DIMENSIONS["padding_sm"])
            tk.Label(hint, text=key, font=FONTS["button"], fg=COLORS["accent_primary"], bg=COLORS["bg_secondary"]).pack(side=tk.LEFT)
            tk.Label(hint, text=f" {desc}", font=FONTS["body_small"], fg=COLORS["text_muted"], bg=COLORS["bg_secondary"]).pack(side=tk.LEFT)

    def _create_action_panel(self, parent):
        """Panel thêm hành động"""
        frame = ModernLabelFrame(parent, text="THÊM HÀNH ĐỘNG")
        frame.pack(fill=tk.BOTH, expand=True)
        
        inner = ModernFrame(frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=DIMENSIONS["padding_md"], pady=DIMENSIONS["padding_md"])
        
        # Row 1: Loại hành động + Delay
        row1 = ModernFrame(inner, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_sm"]))
        
        ModernLabel(row1, text="Loại hành động:").pack(side=tk.LEFT)
        self.action_type = ModernCombobox(row1, values=ACTION_TYPES, width=20)
        self.action_type.configure(style="Modern.TCombobox")
        self.action_type.set(ACTION_TYPES[0])
        self.action_type.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.action_type.bind("<<ComboboxSelected>>", self._on_action_type_change)
        
        ModernLabel(row1, text="Độ trễ:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_md"], 0))
        self.delay = ModernEntry(row1, width=6)
        self.delay.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.delay.insert(0, str(DEFAULT_DELAY))
        ModernLabel(row1, text="giây").pack(side=tk.LEFT)
        
        # Container cho các tùy chọn
        self.options_frame = ModernFrame(inner, bg=COLORS["bg_card"])
        self.options_frame.pack(fill=tk.BOTH, expand=True, pady=DIMENSIONS["padding_sm"])
        
        # Tạo các frame tùy chọn
        self._create_click_frame()
        self._create_drag_frame()
        self._create_image_frame()
        self._create_keyboard_frame()
        self._create_if_frame()
        self._create_goto_frame()
        self._create_loop_frame()
        
        # Nút thêm
        btn_frame = ModernFrame(inner, bg=COLORS["bg_card"])
        btn_frame.pack(fill=tk.X, pady=(DIMENSIONS["padding_md"], 0))
        
        self.btn_add = IconButton(btn_frame, text="Thêm hành động", icon="+", style="primary", command=self._add_action)
        self.btn_add.pack(side=tk.LEFT, padx=(0, DIMENSIONS["padding_sm"]))
        IconButton(btn_frame, text="Làm mới", icon="↺", style="ghost", command=self._reset_form).pack(side=tk.LEFT)
        
        # Hiển thị frame mặc định
        self._on_action_type_change()

    def _create_click_frame(self):
        """Frame cho Click"""
        self.click_frame = ModernLabelFrame(self.options_frame, text="VỊ TRÍ CLICK")
        
        inner = ModernFrame(self.click_frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        ModernLabel(inner, text="X:").pack(side=tk.LEFT)
        self.pos_x = ModernEntry(inner, width=8)
        self.pos_x.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.pos_x.insert(0, "0")
        
        ModernLabel(inner, text="Y:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_md"], 0))
        self.pos_y = ModernEntry(inner, width=8)
        self.pos_y.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.pos_y.insert(0, "0")
        
        IconButton(inner, text="Chọn vị trí", icon="◎", style="secondary", command=self._pick_position).pack(side=tk.LEFT, padx=(DIMENSIONS["padding_md"], 0))
    
    def _create_drag_frame(self):
        """Frame cho Kéo thả"""
        self.drag_frame = ModernLabelFrame(self.options_frame, text="KÉO THẢ CHUỘT")
        
        inner = ModernFrame(self.drag_frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        # Row 1: Từ vị trí
        row1 = ModernFrame(inner, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_xs"]))
        
        ModernLabel(row1, text="Từ vị trí:").pack(side=tk.LEFT)
        ModernLabel(row1, text="X:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_sm"], 0))
        self.drag_x1 = ModernEntry(row1, width=7)
        self.drag_x1.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.drag_x1.insert(0, "0")
        ModernLabel(row1, text="Y:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_sm"], 0))
        self.drag_y1 = ModernEntry(row1, width=7)
        self.drag_y1.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.drag_y1.insert(0, "0")
        
        # Row 2: Đến vị trí
        row2 = ModernFrame(inner, bg=COLORS["bg_card"])
        row2.pack(fill=tk.X)
        
        ModernLabel(row2, text="Đến vị trí:").pack(side=tk.LEFT)
        ModernLabel(row2, text="X:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_sm"], 0))
        self.drag_x2 = ModernEntry(row2, width=7)
        self.drag_x2.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.drag_x2.insert(0, "0")
        ModernLabel(row2, text="Y:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_sm"], 0))
        self.drag_y2 = ModernEntry(row2, width=7)
        self.drag_y2.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.drag_y2.insert(0, "0")
    
    def _create_image_frame(self):
        """Frame cho Tìm hình ảnh"""
        self.image_frame = ModernLabelFrame(self.options_frame, text="TÌM HÌNH ẢNH")
        
        inner = ModernFrame(self.image_frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        # Row 1: Chọn hình
        row1 = ModernFrame(inner, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_xs"]))
        
        ModernLabel(row1, text="Hình ảnh:").pack(side=tk.LEFT)
        self.image_path = ModernEntry(row1, width=20)
        self.image_path.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        IconButton(row1, text="Chọn", icon="📁", style="secondary", command=self._select_image).pack(side=tk.LEFT, padx=2)
        IconButton(row1, text="Chụp", icon="📷", style="secondary", command=self._capture_region).pack(side=tk.LEFT, padx=2)
        
        # Row 2: Cấu hình
        row2 = ModernFrame(inner, bg=COLORS["bg_card"])
        row2.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_xs"]))
        
        ModernLabel(row2, text="Độ chính xác:").pack(side=tk.LEFT)
        self.confidence = ModernScale(row2, from_=50, to=100, length=100)
        self.confidence.set(DEFAULT_CONFIDENCE)
        self.confidence.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.conf_label = ModernLabel(row2, text=f"{DEFAULT_CONFIDENCE}%", fg=COLORS["text_accent"])
        self.conf_label.pack(side=tk.LEFT)
        self.confidence.bind("<Motion>", lambda e: self.conf_label.config(text=f"{int(self.confidence.get())}%"))
        
        ModernLabel(row2, text="Thời gian chờ:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_md"], 0))
        self.timeout = ModernEntry(row2, width=5)
        self.timeout.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.timeout.insert(0, "10")
        ModernLabel(row2, text="giây").pack(side=tk.LEFT)
        
        # Row 3: Tùy chọn click
        row3 = ModernFrame(inner, bg=COLORS["bg_card"])
        row3.pack(fill=tk.X)
        self.click_when_found = tk.BooleanVar(value=True)
        ModernCheckbutton(row3, text="Click vào hình khi tìm thấy", variable=self.click_when_found).pack(side=tk.LEFT)

    def _create_keyboard_frame(self):
        """Frame cho Bàn phím"""
        self.keyboard_frame = ModernLabelFrame(self.options_frame, text="BÀN PHÍM")
        
        inner = ModernFrame(self.keyboard_frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        # Row 1: Nhập văn bản
        row1 = ModernFrame(inner, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_xs"]))
        ModernLabel(row1, text="Văn bản nhập:").pack(side=tk.LEFT)
        self.input_text = ModernEntry(row1, width=30)
        self.input_text.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        
        # Row 2: Phím
        row2 = ModernFrame(inner, bg=COLORS["bg_card"])
        row2.pack(fill=tk.X)
        ModernLabel(row2, text="Phím/Tổ hợp:").pack(side=tk.LEFT)
        self.input_key = ModernCombobox(row2, width=18, values=[
            "enter", "tab", "space", "backspace", "delete", "escape",
            "up", "down", "left", "right", "home", "end",
            "ctrl+c", "ctrl+v", "ctrl+a", "ctrl+s", "ctrl+z", "alt+f4"
        ])
        self.input_key.configure(style="Modern.TCombobox")
        self.input_key.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.input_key.set("enter")

    def _create_if_frame(self):
        """Frame cho IF"""
        self.if_frame = ModernLabelFrame(self.options_frame, text="ĐIỀU KIỆN (NẾU...THÌ...)")
        
        inner = ModernFrame(self.if_frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        # Row 1: Loại điều kiện
        row1 = ModernFrame(inner, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_xs"]))
        ModernLabel(row1, text="Điều kiện:").pack(side=tk.LEFT)
        cond_values = [c[1] for c in CONDITION_TYPES]
        self.condition_type = ModernCombobox(row1, values=cond_values, width=30)
        self.condition_type.configure(style="Modern.TCombobox")
        self.condition_type.set(cond_values[0])
        self.condition_type.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.condition_type.bind("<<ComboboxSelected>>", self._on_condition_change)
        
        # Hình ảnh điều kiện
        self.cond_image_frame = ModernFrame(inner, bg=COLORS["bg_card"])
        ModernLabel(self.cond_image_frame, text="Hình:").pack(side=tk.LEFT)
        self.cond_image = ModernEntry(self.cond_image_frame, width=22)
        self.cond_image.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        IconButton(self.cond_image_frame, text="Chọn", icon="📁", style="secondary", command=self._select_cond_image).pack(side=tk.LEFT)
        
        # Màu điều kiện
        self.cond_color_frame = ModernFrame(inner, bg=COLORS["bg_card"])
        ModernLabel(self.cond_color_frame, text="Màu (r,g,b@x,y):").pack(side=tk.LEFT)
        self.cond_color = ModernEntry(self.cond_color_frame, width=18)
        self.cond_color.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        IconButton(self.cond_color_frame, text="Lấy màu", icon="🎨", style="secondary", command=self._pick_color).pack(side=tk.LEFT)
        
        # Hướng dẫn
        hint = ModernLabel(inner, text="Sau khi thêm điều kiện, hãy thêm THÌ/NGƯỢC LẠI/KẾT THÚC", fg=COLORS["text_muted"])
        hint.pack(anchor=tk.W, pady=(DIMENSIONS["padding_xs"], 0))
    
    def _create_goto_frame(self):
        """Frame cho GOTO"""
        self.goto_frame = ModernLabelFrame(self.options_frame, text="NHẢY ĐẾN BƯỚC")
        
        inner = ModernFrame(self.goto_frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        ModernLabel(inner, text="Nhảy đến bước số:").pack(side=tk.LEFT)
        self.goto_step = ModernEntry(inner, width=6)
        self.goto_step.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.goto_step.insert(0, "1")
        ModernLabel(inner, text="(nhập số thứ tự bước trong danh sách)", fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
    
    def _create_loop_frame(self):
        """Frame cho LOOP_CONTROL"""
        self.loop_frame = ModernLabelFrame(self.options_frame, text="ĐIỀU KHIỂN VÒNG LẶP")
        
        inner = ModernFrame(self.loop_frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        ModernLabel(inner, text="Hành động:").pack(side=tk.LEFT)
        loop_values = [l[1] for l in LOOP_ACTIONS]
        self.loop_action = ModernCombobox(inner, values=loop_values, width=25)
        self.loop_action.configure(style="Modern.TCombobox")
        self.loop_action.set(loop_values[0])
        self.loop_action.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])

    def _create_list_panel(self, parent):
        """Panel danh sách Step và Action"""
        frame = ModernLabelFrame(parent, text="DANH SÁCH STEP & HÀNH ĐỘNG")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, DIMENSIONS["padding_md"]))
        
        inner = ModernFrame(frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=DIMENSIONS["padding_md"], pady=DIMENSIONS["padding_md"])
        
        # === PHẦN STEP (trên) ===
        step_section = ModernFrame(inner, bg=COLORS["bg_card"])
        step_section.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_sm"]))
        
        SectionHeader(step_section, text="Các Step", icon="📋").pack(anchor=tk.W, pady=(0, DIMENSIONS["padding_xs"]))
        
        step_list_container = ModernFrame(step_section, bg=COLORS["bg_card"])
        step_list_container.pack(fill=tk.X)
        
        step_scrollbar = ModernScrollbar(step_list_container)
        step_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.step_list = ModernListbox(step_list_container, height=4)
        self.step_list.config(yscrollcommand=step_scrollbar.set, exportselection=False)
        self.step_list.pack(side=tk.LEFT, fill=tk.X, expand=True)
        step_scrollbar.config(command=self.step_list.yview)
        self.step_list.bind('<<ListboxSelect>>', self._on_step_select)
        
        # Buttons cho Step
        step_btn_frame = ModernFrame(step_section, bg=COLORS["bg_card"])
        step_btn_frame.pack(fill=tk.X, pady=(DIMENSIONS["padding_xs"], 0))
        
        IconButton(step_btn_frame, text="Thêm", icon="+", style="success", command=self._add_step).pack(side=tk.LEFT, padx=2)
        IconButton(step_btn_frame, text="Đổi tên", icon="✏", style="ghost", command=self._rename_step).pack(side=tk.LEFT, padx=2)
        IconButton(step_btn_frame, text="Lên", icon="↑", style="ghost", command=self._move_step_up).pack(side=tk.LEFT, padx=2)
        IconButton(step_btn_frame, text="Xuống", icon="↓", style="ghost", command=self._move_step_down).pack(side=tk.LEFT, padx=2)
        IconButton(step_btn_frame, text="Xóa", icon="×", style="danger", command=self._delete_step).pack(side=tk.LEFT, padx=2)
        
        # Separator
        Separator(inner).pack(fill=tk.X, pady=DIMENSIONS["padding_md"])
        
        # === PHẦN ACTION (dưới) ===
        action_section = ModernFrame(inner, bg=COLORS["bg_card"])
        action_section.pack(fill=tk.BOTH, expand=True)
        
        self.action_label = SectionHeader(action_section, text="Hành động: (chưa chọn Step)", icon="⚡")
        self.action_label.pack(anchor=tk.W, pady=(0, DIMENSIONS["padding_xs"]))
        
        action_list_container = ModernFrame(action_section, bg=COLORS["bg_card"])
        action_list_container.pack(fill=tk.BOTH, expand=True)
        
        action_scrollbar = ModernScrollbar(action_list_container)
        action_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.action_list = ModernListbox(action_list_container, height=10)
        self.action_list.config(yscrollcommand=action_scrollbar.set, exportselection=False)
        self.action_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        action_scrollbar.config(command=self.action_list.yview)
        
        # Buttons cho Action - Row 1
        btn_frame1 = ModernFrame(action_section, bg=COLORS["bg_card"])
        btn_frame1.pack(fill=tk.X, pady=(DIMENSIONS["padding_xs"], 2))
        
        IconButton(btn_frame1, text="Lên", icon="↑", style="ghost", command=self._move_up).pack(side=tk.LEFT, padx=2)
        IconButton(btn_frame1, text="Xuống", icon="↓", style="ghost", command=self._move_down).pack(side=tk.LEFT, padx=2)
        IconButton(btn_frame1, text="Sửa", icon="✏", style="secondary", command=self._edit_action).pack(side=tk.LEFT, padx=2)
        IconButton(btn_frame1, text="Xóa", icon="×", style="danger", command=self._delete_action).pack(side=tk.LEFT, padx=2)
        IconButton(btn_frame1, text="Xóa hết", icon="🗑", style="danger", command=self._clear_actions).pack(side=tk.LEFT, padx=2)
        
        # IF block buttons - Row 2
        btn_frame2 = ModernFrame(action_section, bg=COLORS["bg_card"])
        btn_frame2.pack(fill=tk.X, pady=(2, 0))
        ModernLabel(btn_frame2, text="IF Block:", fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=(0, DIMENSIONS["padding_xs"]))
        IconButton(btn_frame2, text="THÌ", style="secondary", command=lambda: self._add_block("THEN")).pack(side=tk.LEFT, padx=2)
        IconButton(btn_frame2, text="NGƯỢC LẠI", style="secondary", command=lambda: self._add_block("ELSE")).pack(side=tk.LEFT, padx=2)
        IconButton(btn_frame2, text="KẾT THÚC IF", style="secondary", command=lambda: self._add_block("END_IF")).pack(side=tk.LEFT, padx=2)

    def _create_control_panel(self, parent):
        """Panel điều khiển"""
        frame = ModernLabelFrame(parent, text="ĐIỀU KHIỂN")
        frame.pack(fill=tk.X)
        
        inner = ModernFrame(frame, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X, padx=DIMENSIONS["padding_md"], pady=DIMENSIONS["padding_md"])
        
        # Row 0: Chọn cửa sổ đích
        row0 = ModernFrame(inner, bg=COLORS["bg_card"])
        row0.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_sm"]))
        
        ModernLabel(row0, text="Cửa sổ đích:").pack(side=tk.LEFT)
        self.target_window_label = ModernLabel(row0, text="🌐 Toàn cục (chiếm chuột/bàn phím)", fg=COLORS["text_muted"])
        self.target_window_label.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        
        IconButton(row0, text="Chọn cửa sổ", icon="🪟", style="secondary", command=self._select_target_window).pack(side=tk.RIGHT, padx=2)
        IconButton(row0, text="Toàn cục", icon="🌐", style="ghost", command=self._clear_target_window).pack(side=tk.RIGHT, padx=2)
        
        # Row 1: Cấu hình lặp
        row1 = ModernFrame(inner, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_sm"]))
        
        ModernLabel(row1, text="Lặp:").pack(side=tk.LEFT)
        self.loop_count = ModernEntry(row1, width=5)
        self.loop_count.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.loop_count.insert(0, str(DEFAULT_LOOP_COUNT))
        ModernLabel(row1, text="lần").pack(side=tk.LEFT)
        
        self.infinite_loop = tk.BooleanVar(value=False)
        ModernCheckbutton(row1, text="Vô hạn", variable=self.infinite_loop).pack(side=tk.LEFT, padx=DIMENSIONS["padding_md"])
        
        ModernLabel(row1, text="Delay giữa các lần:").pack(side=tk.LEFT, padx=(DIMENSIONS["padding_md"], 0))
        self.loop_delay = ModernEntry(row1, width=5)
        self.loop_delay.pack(side=tk.LEFT, padx=DIMENSIONS["padding_xs"])
        self.loop_delay.insert(0, str(DEFAULT_LOOP_DELAY))
        ModernLabel(row1, text="giây").pack(side=tk.LEFT)
        
        # Row 2: Nút điều khiển
        row2 = ModernFrame(inner, bg=COLORS["bg_card"])
        row2.pack(fill=tk.X, pady=(0, DIMENSIONS["padding_sm"]))
        
        self.btn_start = IconButton(row2, text="BẮT ĐẦU (F6)", icon="▶", style="success", command=self._start)
        self.btn_start.pack(side=tk.LEFT, padx=(0, DIMENSIONS["padding_sm"]))
        
        self.btn_stop = IconButton(row2, text="DỪNG (F7)", icon="■", style="danger", command=self._stop)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, DIMENSIONS["padding_lg"]))
        self.btn_stop.config(state="disabled")
        
        IconButton(row2, text="Lưu", icon="💾", style="secondary", command=self._save_script).pack(side=tk.LEFT, padx=2)
        IconButton(row2, text="Tải", icon="📂", style="secondary", command=self._load_script).pack(side=tk.LEFT, padx=2)
        
        # Row 3: Hiển thị tiến trình lặp (thiết kế đẹp hơn)
        self.loop_progress_frame = ModernFrame(inner, bg=COLORS["bg_primary"])
        self.loop_progress_frame.pack(fill=tk.X, pady=(DIMENSIONS["padding_sm"], 0))
        self.loop_progress_frame.pack_forget()  # Ẩn ban đầu
        
        # Container chính với border và padding
        progress_container = tk.Frame(
            self.loop_progress_frame,
            bg=COLORS["accent_primary"],
            padx=2, pady=2
        )
        progress_container.pack(fill=tk.X)
        
        progress_inner = tk.Frame(progress_container, bg=COLORS["bg_secondary"])
        progress_inner.pack(fill=tk.X)
        
        # Left side: Loop counter
        left_frame = tk.Frame(progress_inner, bg=COLORS["bg_secondary"])
        left_frame.pack(side=tk.LEFT, padx=DIMENSIONS["padding_md"], pady=DIMENSIONS["padding_sm"])
        
        tk.Label(
            left_frame,
            text="VÒNG LẶP",
            font=("Segoe UI", 8, "bold"),
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor=tk.W)
        
        loop_num_frame = tk.Frame(left_frame, bg=COLORS["bg_secondary"])
        loop_num_frame.pack(anchor=tk.W)
        
        self.loop_current_label = tk.Label(
            loop_num_frame,
            text="0",
            font=("Segoe UI", 28, "bold"),
            fg=COLORS["accent_primary"],
            bg=COLORS["bg_secondary"]
        )
        self.loop_current_label.pack(side=tk.LEFT)
        
        self.loop_separator_label = tk.Label(
            loop_num_frame,
            text=" / ",
            font=("Segoe UI", 16),
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        )
        self.loop_separator_label.pack(side=tk.LEFT)
        
        self.loop_total_label = tk.Label(
            loop_num_frame,
            text="0",
            font=("Segoe UI", 16),
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        )
        self.loop_total_label.pack(side=tk.LEFT)
        
        # Separator line
        separator = tk.Frame(progress_inner, bg=COLORS["border_primary"], width=1)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=DIMENSIONS["padding_sm"], pady=DIMENSIONS["padding_sm"])
        
        # Right side: Step progress
        right_frame = tk.Frame(progress_inner, bg=COLORS["bg_secondary"])
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=DIMENSIONS["padding_md"], pady=DIMENSIONS["padding_sm"])
        
        tk.Label(
            right_frame,
            text="BƯỚC HIỆN TẠI",
            font=("Segoe UI", 8, "bold"),
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        ).pack(anchor=tk.W)
        
        self.loop_step_label = tk.Label(
            right_frame,
            text="Đang chờ...",
            font=("Segoe UI", 12),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_secondary"],
            anchor=tk.W
        )
        self.loop_step_label.pack(anchor=tk.W, fill=tk.X)
        
        # Progress bar frame
        self.progress_bar_frame = tk.Frame(right_frame, bg=COLORS["bg_input"], height=6)
        self.progress_bar_frame.pack(fill=tk.X, pady=(4, 0))
        self.progress_bar_frame.pack_propagate(False)
        
        self.progress_bar_fill = tk.Frame(self.progress_bar_frame, bg=COLORS["accent_primary"], height=6)
        self.progress_bar_fill.place(x=0, y=0, relheight=1, relwidth=0)
        
        # Status bar
        self.status_bar = StatusBar(inner)
        self.status_bar.pack(fill=tk.X, pady=(DIMENSIONS["padding_sm"], 0))

    def _setup_hotkeys(self):
        """Thiết lập phím tắt"""
        keyboard.add_hotkey(HOTKEYS["pick_position"], self._pick_position)
        keyboard.add_hotkey(HOTKEYS["capture_region"], self._capture_region)
        keyboard.add_hotkey(HOTKEYS["pick_color"], self._pick_color)
        keyboard.add_hotkey(HOTKEYS["start"], self._start)
        keyboard.add_hotkey(HOTKEYS["stop"], self._stop)
        keyboard.add_hotkey(HOTKEYS["emergency_stop"], self._stop)
    
    def _on_action_type_change(self, event=None):
        """Xử lý khi thay đổi loại hành động"""
        for widget in [self.click_frame, self.drag_frame, self.image_frame, 
                       self.keyboard_frame, self.if_frame, self.goto_frame, self.loop_frame]:
            widget.pack_forget()
        
        action = self.action_type.get()
        
        if action in ["Click chuột trái", "Click chuột phải", "Click đúp"]:
            self.click_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
        elif action == "Kéo thả chuột":
            self.drag_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
        elif action == "Tìm hình ảnh":
            self.image_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
        elif action in ["Nhập văn bản", "Nhấn phím", "Tổ hợp phím"]:
            self.keyboard_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
        elif action == "Điều kiện (IF)":
            self.if_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
            self._on_condition_change()
        elif action == "Nhảy đến bước (GOTO)":
            self.goto_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
        elif action == "Điều khiển lặp":
            self.loop_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
    
    def _on_condition_change(self, event=None):
        """Xử lý khi thay đổi loại điều kiện"""
        self.cond_image_frame.pack_forget()
        self.cond_color_frame.pack_forget()
        
        cond_text = self.condition_type.get()
        if "hình ảnh" in cond_text.lower():
            self.cond_image_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
        elif "màu" in cond_text.lower():
            self.cond_color_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
    
    def _update_status(self, message: str):
        # Kiểm tra status_bar đã được tạo chưa
        if not hasattr(self, 'status_bar'):
            return
        status_type = "info"
        if "thành công" in message.lower() or "đã" in message.lower():
            status_type = "success"
        elif "lỗi" in message.lower() or "không" in message.lower():
            status_type = "error"
        elif "đang chạy" in message.lower():
            status_type = "running"
        elif "cảnh báo" in message.lower():
            status_type = "warning"
        self.status_bar.set_status(message, status_type)
    
    def _update_mouse_position(self):
        # Kiểm tra status_bar đã được tạo chưa
        if not hasattr(self, 'status_bar'):
            self.root.after(100, self._update_mouse_position)
            return
        try:
            x, y = self.mouse_service.get_position()
            self.status_bar.set_mouse_position(x, y)
        except:
            pass
        self.root.after(100, self._update_mouse_position)
    
    def _pick_position(self):
        self._update_status("Di chuyển chuột đến vị trí cần chọn, nhấn SPACE để xác nhận...")
        def wait():
            keyboard.wait('space')
            x, y = self.mouse_service.get_position()
            self.pos_x.delete(0, tk.END)
            self.pos_x.insert(0, str(x))
            self.pos_y.delete(0, tk.END)
            self.pos_y.insert(0, str(y))
            self._update_status(f"Đã chọn vị trí: ({x}, {y})")
        threading.Thread(target=wait, daemon=True).start()
    
    def _select_image(self):
        filepath = DialogManager.select_image()
        if filepath:
            self.image_path.delete(0, tk.END)
            self.image_path.insert(0, filepath)
    
    def _capture_region(self):
        self._update_status("Kéo chuột để chọn vùng cần chụp...")
        def on_capture(region):
            if region:
                screenshot = self.image_service.capture_screenshot(region)
                filepath = DialogManager.save_image()
                if filepath:
                    screenshot.save(filepath)
                    self.image_path.delete(0, tk.END)
                    self.image_path.insert(0, filepath)
                    self._update_status(f"Đã lưu hình ảnh: {filepath}")
            else:
                self._update_status("Vùng chọn quá nhỏ")
        RegionCaptureDialog(self.root, on_capture).show()
    
    def _select_cond_image(self):
        filepath = DialogManager.select_image()
        if filepath:
            self.cond_image.delete(0, tk.END)
            self.cond_image.insert(0, filepath)
    
    def _pick_color(self):
        self._update_status("Di chuyển chuột đến vị trí cần lấy màu, nhấn SPACE...")
        def wait():
            keyboard.wait('space')
            x, y = self.mouse_service.get_position()
            pixel = self.image_service.get_pixel_color(x, y)
            color_str = f"{pixel[0]},{pixel[1]},{pixel[2]}@{x},{y}"
            self.cond_color.delete(0, tk.END)
            self.cond_color.insert(0, color_str)
            self._update_status(f"Đã lấy màu: RGB{pixel} tại ({x}, {y})")
        threading.Thread(target=wait, daemon=True).start()

    def _add_action(self):
        """Thêm hành động mới vào Step hiện tại"""
        if self.current_step_index < 0 or self.current_step_index >= len(self.steps):
            self._update_status("Vui lòng chọn hoặc tạo một Step trước!")
            return
        
        action_type = self.action_type.get()
        action = Action(type=action_type, delay=float(self.delay.get() or DEFAULT_DELAY))
        
        if action_type in ["Click chuột trái", "Click chuột phải", "Click đúp"]:
            action.x = int(self.pos_x.get() or 0)
            action.y = int(self.pos_y.get() or 0)
        
        elif action_type == "Kéo thả chuột":
            action.x = int(self.drag_x1.get() or 0)
            action.y = int(self.drag_y1.get() or 0)
            action.dest_x = int(self.drag_x2.get() or 0)
            action.dest_y = int(self.drag_y2.get() or 0)
        
        elif action_type == "Tìm hình ảnh":
            action.image = self.image_path.get()
            action.confidence = int(self.confidence.get()) / 100
            action.timeout = float(self.timeout.get() or 10)
            action.click_when_found = self.click_when_found.get()
        
        elif action_type == "Nhập văn bản":
            action.text = self.input_text.get()
        
        elif action_type in ["Nhấn phím", "Tổ hợp phím"]:
            action.key = self.input_key.get()
        
        elif action_type == "Điều kiện (IF)":
            cond_text = self.condition_type.get()
            for code, text in CONDITION_TYPES:
                if text == cond_text:
                    action.condition_type = code
                    break
            action.condition_image = self.cond_image.get()
            action.condition_color = self.cond_color.get()
        
        elif action_type == "Nhảy đến bước (GOTO)":
            action.goto_step = int(self.goto_step.get() or 1) - 1
        
        elif action_type == "Điều khiển lặp":
            loop_text = self.loop_action.get()
            for code, text in LOOP_ACTIONS:
                if text == loop_text:
                    action.loop_action = code
                    break
        
        current_step = self.steps[self.current_step_index]
        
        if self._editing_action_index is not None:
            current_step.actions[self._editing_action_index] = action
            self._update_status(f"Đã cập nhật hành động: {action_type}")
            self._editing_action_index = None
            self.btn_add.config(text="+ Thêm hành động")
        else:
            current_step.actions.append(action)
            self._update_status(f"Đã thêm hành động vào {current_step.name}: {action_type}")
        
        self._refresh_action_list()
        self._refresh_step_list()
    
    def _add_block(self, block_type: str):
        """Thêm block THEN/ELSE/END_IF vào Step hiện tại"""
        if self.current_step_index < 0 or self.current_step_index >= len(self.steps):
            self._update_status("Vui lòng chọn hoặc tạo một Step trước!")
            return
        
        action = Action(type=block_type)
        self.steps[self.current_step_index].actions.append(action)
        self._refresh_action_list()
        self._refresh_step_list()
        
        names = {"THEN": "THÌ (nếu đúng)", "ELSE": "NGƯỢC LẠI (nếu sai)", "END_IF": "KẾT THÚC điều kiện"}
        self._update_status(f"Đã thêm: {names.get(block_type, block_type)}")
    
    def _reset_form(self):
        """Reset form"""
        self._editing_action_index = None
        self.btn_add.config(text="+ Thêm hành động")
        self.action_type.set(ACTION_TYPES[0])
        self._on_action_type_change()
        self._update_status("Đã làm mới form")
    
    # === STEP MANAGEMENT ===
    def _add_step(self):
        """Thêm Step mới"""
        step_num = len(self.steps) + 1
        new_step = Step(name=f"Bước {step_num}")
        self.steps.append(new_step)
        self._refresh_step_list()
        self.current_step_index = len(self.steps) - 1
        self.step_list.selection_clear(0, tk.END)
        self.step_list.selection_set(self.current_step_index)
        self._on_step_select()
        self._update_status(f"Đã thêm: {new_step.name}")
    
    def _rename_step(self):
        """Đổi tên Step"""
        if self.current_step_index < 0:
            self._update_status("Vui lòng chọn một Step để đổi tên")
            return
        
        current_step = self.steps[self.current_step_index]
        new_name = DialogManager.ask_string("Đổi tên Step", "Nhập tên mới:", current_step.name)
        if new_name:
            current_step.name = new_name
            self._refresh_step_list()
            self._update_action_label()
            self._update_status(f"Đã đổi tên thành: {new_name}")
    
    def _move_step_up(self):
        """Di chuyển Step lên"""
        if self.current_step_index > 0:
            idx = self.current_step_index
            self.steps[idx], self.steps[idx-1] = self.steps[idx-1], self.steps[idx]
            self.current_step_index = idx - 1
            self._refresh_step_list()
            self.step_list.selection_set(self.current_step_index)
    
    def _move_step_down(self):
        """Di chuyển Step xuống"""
        if 0 <= self.current_step_index < len(self.steps) - 1:
            idx = self.current_step_index
            self.steps[idx], self.steps[idx+1] = self.steps[idx+1], self.steps[idx]
            self.current_step_index = idx + 1
            self._refresh_step_list()
            self.step_list.selection_set(self.current_step_index)
    
    def _delete_step(self):
        """Xóa Step"""
        if self.current_step_index < 0:
            self._update_status("Vui lòng chọn một Step để xóa")
            return
        
        step_name = self.steps[self.current_step_index].name
        if DialogManager.confirm("Xác nhận", f"Bạn có chắc muốn xóa '{step_name}' và tất cả hành động trong đó?"):
            del self.steps[self.current_step_index]
            self.current_step_index = -1
            self._refresh_step_list()
            self._refresh_action_list()
            self._update_action_label()
            self._update_status(f"Đã xóa: {step_name}")
    
    def _on_step_select(self, event=None):
        """Xử lý khi chọn Step"""
        sel = self.step_list.curselection()
        if sel:
            self.current_step_index = sel[0]
            self._refresh_action_list()
            self._update_action_label()
        # Không reset current_step_index khi không có selection
        # để giữ step đang chọn khi click vào action list
    
    def _update_action_label(self):
        """Cập nhật label hiển thị Step đang chọn"""
        # Destroy old label and create new one
        for widget in self.action_label.winfo_children():
            widget.destroy()
        
        if 0 <= self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            text = f"Hành động: {step.name}"
        else:
            text = "Hành động: (chưa chọn Step)"
        
        tk.Label(
            self.action_label,
            text="⚡",
            font=("Segoe UI", 12),
            fg=COLORS["accent_primary"],
            bg=COLORS["bg_card"]
        ).pack(side=tk.LEFT, padx=(0, DIMENSIONS["padding_xs"]))
        
        tk.Label(
            self.action_label,
            text=text,
            font=FONTS["heading_small"],
            fg=COLORS["text_accent"],
            bg=COLORS["bg_card"]
        ).pack(side=tk.LEFT)
    
    def _refresh_step_list(self):
        """Cập nhật danh sách Step"""
        self.step_list.delete(0, tk.END)
        for i, step in enumerate(self.steps):
            text = f"{i+1}. {step.get_display_text()}"
            self.step_list.insert(tk.END, text)
        
        if 0 <= self.current_step_index < len(self.steps):
            self.step_list.selection_set(self.current_step_index)
    
    def _refresh_action_list(self):
        """Cập nhật danh sách Action với hiển thị IF-ELSE đẹp hơn"""
        self.action_list.delete(0, tk.END)
        
        if self.current_step_index < 0 or self.current_step_index >= len(self.steps):
            return
        
        current_step = self.steps[self.current_step_index]
        
        # Stack lưu các IF đang mở
        if_stack = []
        
        for i, action in enumerate(current_step.actions):
            action_type = action.type
            
            # Tính indent level
            if action_type in ["IF", "Điều kiện (IF)"]:
                indent_level = len(if_stack)
                if_stack.append(indent_level)
                indent = "    " * indent_level
                text = f"{i+1:2}. {indent}[NẾU] {action._get_condition_text()}"
                
            elif action_type == "THEN":
                indent_level = len(if_stack)
                indent = "    " * indent_level
                text = f"{i+1:2}. {indent}[THÌ]:"
                
            elif action_type == "ELSE":
                indent_level = len(if_stack)
                indent = "    " * indent_level
                text = f"{i+1:2}. {indent}[NGƯỢC LẠI]:"
                
            elif action_type == "END_IF":
                if if_stack:
                    if_stack.pop()
                indent_level = len(if_stack)
                indent = "    " * indent_level
                text = f"{i+1:2}. {indent}[KẾT THÚC NẾU]"
                
            else:
                indent_level = len(if_stack) + 1 if if_stack else 0
                indent = "    " * indent_level
                display = action.get_display_text()
                text = f"{i+1:2}. {indent}{display}"
            
            self.action_list.insert(tk.END, text)
    
    def _get_selected_index(self):
        """Lấy index action được chọn trong Step hiện tại"""
        sel = self.action_list.curselection()
        return sel[0] if sel else None
    
    def _move_up(self):
        """Di chuyển action lên"""
        if self.current_step_index < 0:
            return
        idx = self._get_selected_index()
        current_step = self.steps[self.current_step_index]
        if idx is not None and idx > 0:
            current_step.actions[idx], current_step.actions[idx-1] = current_step.actions[idx-1], current_step.actions[idx]
            self._refresh_action_list()
            self.action_list.selection_set(idx-1)
    
    def _move_down(self):
        """Di chuyển action xuống"""
        if self.current_step_index < 0:
            return
        idx = self._get_selected_index()
        current_step = self.steps[self.current_step_index]
        if idx is not None and idx < len(current_step.actions) - 1:
            current_step.actions[idx], current_step.actions[idx+1] = current_step.actions[idx+1], current_step.actions[idx]
            self._refresh_action_list()
            self.action_list.selection_set(idx+1)

    def _edit_action(self):
        """Sửa hành động trong Step hiện tại"""
        if self.current_step_index < 0:
            self._update_status("Vui lòng chọn một Step trước")
            return
        
        idx = self._get_selected_index()
        if idx is None:
            self._update_status("Vui lòng chọn một hành động để sửa")
            return
        
        current_step = self.steps[self.current_step_index]
        action = current_step.actions[idx]
        self._editing_action_index = idx
        self.btn_add.config(text="💾 Lưu thay đổi")
        
        self.action_type.set(action.type)
        self._on_action_type_change()
        
        self.delay.delete(0, tk.END)
        self.delay.insert(0, str(action.delay))
        
        if action.type in ["Click chuột trái", "Click chuột phải", "Click đúp"]:
            self.pos_x.delete(0, tk.END)
            self.pos_x.insert(0, str(action.x))
            self.pos_y.delete(0, tk.END)
            self.pos_y.insert(0, str(action.y))
        
        elif action.type == "Kéo thả chuột":
            self.drag_x1.delete(0, tk.END)
            self.drag_x1.insert(0, str(action.x))
            self.drag_y1.delete(0, tk.END)
            self.drag_y1.insert(0, str(action.y))
            self.drag_x2.delete(0, tk.END)
            self.drag_x2.insert(0, str(action.dest_x))
            self.drag_y2.delete(0, tk.END)
            self.drag_y2.insert(0, str(action.dest_y))
        
        elif action.type == "Tìm hình ảnh":
            self.image_path.delete(0, tk.END)
            self.image_path.insert(0, action.image)
            self.confidence.set(action.confidence * 100)
            self.timeout.delete(0, tk.END)
            self.timeout.insert(0, str(action.timeout))
            self.click_when_found.set(action.click_when_found)
        
        elif action.type == "Nhập văn bản":
            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, action.text)
        
        elif action.type in ["Nhấn phím", "Tổ hợp phím"]:
            self.input_key.set(action.key)
        
        elif action.type in ["IF", "Điều kiện (IF)"]:
            for code, text in CONDITION_TYPES:
                if code == action.condition_type:
                    self.condition_type.set(text)
                    break
            self._on_condition_change()
            self.cond_image.delete(0, tk.END)
            self.cond_image.insert(0, action.condition_image)
            self.cond_color.delete(0, tk.END)
            self.cond_color.insert(0, action.condition_color)
        
        elif action.type in ["GOTO", "Nhảy đến bước (GOTO)"]:
            self.goto_step.delete(0, tk.END)
            self.goto_step.insert(0, str(action.goto_step + 1))
        
        elif action.type in ["LOOP_CONTROL", "Điều khiển lặp"]:
            for code, text in LOOP_ACTIONS:
                if code == action.loop_action:
                    self.loop_action.set(text)
                    break
        
        self._update_status(f"Đang sửa hành động {idx + 1}: {action.type}")
    
    def _delete_action(self):
        """Xóa action trong Step hiện tại"""
        if self.current_step_index < 0:
            self._update_status("Vui lòng chọn một Step trước")
            return
        
        idx = self._get_selected_index()
        if idx is not None:
            current_step = self.steps[self.current_step_index]
            del current_step.actions[idx]
            self._refresh_action_list()
            self._refresh_step_list()
            self._update_status("Đã xóa hành động")
        else:
            self._update_status("Vui lòng chọn một hành động để xóa")
    
    def _clear_actions(self):
        """Xóa tất cả action trong Step hiện tại"""
        if self.current_step_index < 0:
            self._update_status("Vui lòng chọn một Step trước")
            return
        
        current_step = self.steps[self.current_step_index]
        if DialogManager.confirm("Xác nhận", f"Bạn có chắc muốn xóa tất cả hành động trong '{current_step.name}'?"):
            current_step.actions.clear()
            self._refresh_action_list()
            self._refresh_step_list()
            self._update_status("Đã xóa tất cả hành động")
    
    def _get_script(self) -> Script:
        """Tạo Script từ danh sách Steps"""
        return Script(
            steps=self.steps,
            loop_count=int(self.loop_count.get() or DEFAULT_LOOP_COUNT),
            infinite_loop=self.infinite_loop.get(),
            loop_delay=float(self.loop_delay.get() or DEFAULT_LOOP_DELAY)
        )
    
    def _start(self):
        if not self.steps or all(len(s.actions) == 0 for s in self.steps):
            DialogManager.warning("Cảnh báo", "Chưa có hành động nào trong các Step!")
            return
        
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self._update_status("Đang chạy...")
        
        try:
            self.automation.start(self._get_script())
        except Exception as e:
            DialogManager.error("Lỗi", str(e))
            self._on_automation_complete()
    
    def _stop(self):
        self.automation.stop()
        self._on_automation_complete()
    
    def _on_automation_complete(self):
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        # Ẩn frame tiến trình sau 2 giây
        self.root.after(2000, lambda: self.loop_progress_frame.pack_forget())
    
    def _save_script(self):
        if not self.steps:
            DialogManager.warning("Cảnh báo", "Chưa có Step nào để lưu!")
            return
        
        filepath = DialogManager.save_script()
        if filepath:
            try:
                self.script_service.save(self._get_script(), filepath)
                self._update_status(f"Đã lưu kịch bản: {filepath}")
            except Exception as e:
                DialogManager.error("Lỗi", f"Không thể lưu: {e}")
    
    def _load_script(self):
        filepath = DialogManager.load_script()
        if filepath:
            try:
                script = self.script_service.load(filepath)
                self.steps = script.steps
                self.current_step_index = 0 if self.steps else -1
                
                self.loop_count.delete(0, tk.END)
                self.loop_count.insert(0, str(script.loop_count))
                self.infinite_loop.set(script.infinite_loop)
                self.loop_delay.delete(0, tk.END)
                self.loop_delay.insert(0, str(script.loop_delay))
                
                self._refresh_step_list()
                self._refresh_action_list()
                self._update_action_label()
                self._update_status(f"Đã tải kịch bản: {filepath} ({len(self.steps)} steps)")
            except Exception as e:
                DialogManager.error("Lỗi", f"Không thể tải: {e}")
    
    def _select_target_window(self):
        """Mở dialog chọn cửa sổ đích"""
        import ctypes
        window_service = self.automation.get_window_service()
        main_hwnd = ctypes.windll.user32.GetForegroundWindow()
        
        def on_window_selected(hwnd, win_info):
            if hwnd and win_info:
                if self.automation.set_target_window(hwnd):
                    title = win_info.title[:30] + "..." if len(win_info.title) > 30 else win_info.title
                    self.target_window_label.config(
                        text=f"🪟 {title} ({win_info.process_name})",
                        fg=COLORS["accent_primary"]
                    )
                    self._update_status(f"Đã chọn cửa sổ: {win_info.title}")
                else:
                    DialogManager.error("Lỗi", "Không thể chọn cửa sổ này!")
            else:
                # Quay về chế độ toàn cục
                self._clear_target_window()
            
            # Quay về ứng dụng chính
            self.root.after(100, lambda: self.root.focus_force())
        
        WindowSelectorDialog(self.root, window_service, on_window_selected).show()
    
    def _clear_target_window(self):
        """Xóa cửa sổ đích, quay về chế độ toàn cục"""
        self.automation.clear_target_window()
        self.target_window_label.config(
            text="🌐 Toàn cục (chiếm chuột/bàn phím)",
            fg=COLORS["text_muted"]
        )
        self._update_status("Đã chuyển về chế độ toàn cục")
    
    # ============== AUTO UPDATE ==============
    
    def _check_for_updates(self):
        """Kiểm tra cập nhật từ GitHub (chạy background, không block UI)"""
        def on_update_available(update_info):
            # Callback chạy trên background thread, cần schedule về main thread
            self.root.after(0, lambda: self._show_update_dialog(update_info))
        
        def on_error(error_msg):
            # Không hiện lỗi cho user, chỉ log
            print(f"[Update] Lỗi kiểm tra cập nhật: {error_msg}")
        
        self.update_service.check_for_updates(
            on_update_available=on_update_available,
            on_error=on_error
        )
    
    def _show_update_dialog(self, update_info):
        """Hiển thị dialog cập nhật"""
        def on_update():
            self._start_download(update_info)
        
        def on_skip():
            self._update_dialog = None
        
        self._update_dialog = UpdateDialog(
            self.root,
            update_info,
            on_update=on_update,
            on_skip=on_skip
        )
        self._update_dialog.show()
    
    def _start_download(self, update_info):
        """Bắt đầu tải bản cập nhật"""
        def on_progress(percent):
            # Schedule về main thread để update UI
            self.root.after(0, lambda p=percent: self._update_download_progress(p))
        
        def on_complete(file_path):
            # App sẽ tự đóng và restart
            pass
        
        def on_error(error_msg):
            self.root.after(0, lambda: self._on_download_error(error_msg))
        
        self.update_service.download_and_install(
            update_info,
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error
        )
    
    def _update_download_progress(self, percent: int):
        """Cập nhật progress bar (chạy trên main thread)"""
        if self._update_dialog:
            self._update_dialog.update_progress(percent)
    
    def _on_download_error(self, error_msg: str):
        """Xử lý lỗi khi tải"""
        if self._update_dialog:
            self._update_dialog.close()
            self._update_dialog = None
        DialogManager.error("Lỗi cập nhật", f"Không thể tải bản cập nhật:\n{error_msg}")
    
    def run(self):
        self.root.mainloop()
