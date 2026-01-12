# -*- coding: utf-8 -*-
"""UI Components - Các thành phần giao diện tái sử dụng với theme hiện đại"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from .theme import COLORS, FONTS, DIMENSIONS


class ModernFrame(tk.Frame):
    """Frame với style hiện đại"""
    
    def __init__(self, parent, **kwargs):
        bg = kwargs.pop('bg', COLORS["bg_primary"])
        super().__init__(parent, bg=bg, **kwargs)


class ModernLabelFrame(tk.LabelFrame):
    """LabelFrame với style hiện đại"""
    
    def __init__(self, parent, text="", **kwargs):
        super().__init__(
            parent,
            text=f"  {text}  ",
            bg=COLORS["bg_card"],
            fg=COLORS["text_accent"],
            font=FONTS["heading_small"],
            bd=1,
            relief="flat",
            highlightbackground=COLORS["border_primary"],
            highlightthickness=1,
            **kwargs
        )


class ModernLabel(tk.Label):
    """Label với style hiện đại"""
    
    def __init__(self, parent, text="", style="body", **kwargs):
        font = FONTS.get(style, FONTS["body"])
        fg = kwargs.pop('fg', COLORS["text_primary"])
        bg = kwargs.pop('bg', COLORS["bg_card"])
        super().__init__(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)


class ModernEntry(tk.Entry):
    """Entry với style hiện đại"""
    
    def __init__(self, parent, width=10, **kwargs):
        super().__init__(
            parent,
            width=width,
            font=FONTS["body"],
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_accent"],
            relief="flat",
            highlightbackground=COLORS["border_primary"],
            highlightthickness=1,
            highlightcolor=COLORS["accent_primary"],
            **kwargs
        )


class ModernButton(tk.Button):
    """Button với style hiện đại"""
    
    def __init__(self, parent, text="", style="secondary", command=None, **kwargs):
        # Chọn màu theo style
        if style == "primary":
            bg = COLORS["btn_primary_bg"]
            fg = COLORS["btn_primary_fg"]
            hover_bg = "#ff6b8a"
        elif style == "success":
            bg = COLORS["btn_success_bg"]
            fg = COLORS["btn_success_fg"]
            hover_bg = "#00f5b8"
        elif style == "danger":
            bg = COLORS["btn_danger_bg"]
            fg = COLORS["btn_danger_fg"]
            hover_bg = "#ff8a8a"
        else:  # secondary
            bg = COLORS["btn_secondary_bg"]
            fg = COLORS["btn_secondary_fg"]
            hover_bg = COLORS["bg_hover"]
        
        super().__init__(
            parent,
            text=text,
            font=FONTS["button"],
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            command=command,
            padx=DIMENSIONS["padding_md"],
            pady=DIMENSIONS["padding_xs"],
            **kwargs
        )
        
        self._bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.config(bg=self._hover_bg)
    
    def _on_leave(self, e):
        self.config(bg=self._bg)


class ModernCombobox(ttk.Combobox):
    """Combobox với style hiện đại"""
    
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(
            parent,
            values=values or [],
            font=FONTS["body"],
            state="readonly",
            **kwargs
        )


class ModernCheckbutton(tk.Checkbutton):
    """Checkbutton với style hiện đại"""
    
    def __init__(self, parent, text="", variable=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=FONTS["body"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_accent"],
            selectcolor=COLORS["bg_input"],
            variable=variable,
            cursor="hand2",
            **kwargs
        )


class ModernScale(tk.Scale):
    """Scale với style hiện đại"""
    
    def __init__(self, parent, from_=0, to=100, **kwargs):
        super().__init__(
            parent,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            font=FONTS["body_small"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
            troughcolor=COLORS["bg_input"],
            activebackground=COLORS["accent_primary"],
            highlightthickness=0,
            showvalue=False,
            **kwargs
        )


class ModernListbox(tk.Listbox):
    """Listbox với style hiện đại"""
    
    def __init__(self, parent, height=10, **kwargs):
        super().__init__(
            parent,
            height=height,
            font=FONTS["mono"],
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            selectbackground=COLORS["selection_bg"],
            selectforeground=COLORS["selection_fg"],
            activestyle='none',
            relief="flat",
            highlightbackground=COLORS["border_primary"],
            highlightthickness=1,
            highlightcolor=COLORS["accent_primary"],
            **kwargs
        )


class ModernScrollbar(tk.Scrollbar):
    """Scrollbar với style hiện đại"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=COLORS["bg_secondary"],
            troughcolor=COLORS["bg_input"],
            activebackground=COLORS["accent_primary"],
            highlightthickness=0,
            **kwargs
        )


class StatusBar(ModernFrame):
    """Thanh trạng thái với style hiện đại"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_secondary"])
        
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.mouse_var = tk.StringVar(value="Chuột: (0, 0)")
        
        # Status container
        status_frame = ModernFrame(self, bg=COLORS["bg_secondary"])
        status_frame.pack(fill=tk.X, pady=DIMENSIONS["padding_xs"])
        
        # Status icon và text
        self.status_icon = tk.Label(
            status_frame,
            text="●",
            font=("Segoe UI", 12),
            fg=COLORS["accent_success"],
            bg=COLORS["bg_secondary"]
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, DIMENSIONS["padding_xs"]))
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=FONTS["body"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_secondary"]
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Mouse position
        self.mouse_label = tk.Label(
            status_frame,
            textvariable=self.mouse_var,
            font=FONTS["mono_small"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        )
        self.mouse_label.pack(side=tk.RIGHT)
    
    def set_status(self, message: str, status_type: str = "info"):
        """Cập nhật trạng thái với màu sắc tương ứng"""
        self.status_var.set(message)
        
        # Đổi màu icon theo loại status
        colors = {
            "success": COLORS["accent_success"],
            "warning": COLORS["accent_warning"],
            "error": COLORS["accent_danger"],
            "info": COLORS["accent_info"],
            "running": COLORS["accent_primary"],
        }
        self.status_icon.config(fg=colors.get(status_type, COLORS["accent_info"]))
    
    def set_mouse_position(self, x: int, y: int):
        self.mouse_var.set(f"X: {x}  Y: {y}")


class SectionHeader(ModernFrame):
    """Header cho các section với icon"""
    
    def __init__(self, parent, text="", icon=""):
        super().__init__(parent, bg=COLORS["bg_card"])
        
        if icon:
            tk.Label(
                self,
                text=icon,
                font=("Segoe UI", 12),
                fg=COLORS["accent_primary"],
                bg=COLORS["bg_card"]
            ).pack(side=tk.LEFT, padx=(0, DIMENSIONS["padding_xs"]))
        
        tk.Label(
            self,
            text=text,
            font=FONTS["heading_small"],
            fg=COLORS["text_accent"],
            bg=COLORS["bg_card"]
        ).pack(side=tk.LEFT)


class IconButton(tk.Button):
    """Button với icon"""
    
    def __init__(self, parent, text="", icon="", style="secondary", command=None, **kwargs):
        display_text = f"{icon} {text}" if icon else text
        
        if style == "primary":
            bg = COLORS["btn_primary_bg"]
            fg = COLORS["btn_primary_fg"]
            hover_bg = "#ff6b8a"
        elif style == "success":
            bg = COLORS["btn_success_bg"]
            fg = COLORS["btn_success_fg"]
            hover_bg = "#00f5b8"
        elif style == "danger":
            bg = COLORS["btn_danger_bg"]
            fg = COLORS["btn_danger_fg"]
            hover_bg = "#ff8a8a"
        elif style == "ghost":
            bg = COLORS["bg_card"]
            fg = COLORS["text_secondary"]
            hover_bg = COLORS["bg_hover"]
        else:
            bg = COLORS["btn_secondary_bg"]
            fg = COLORS["btn_secondary_fg"]
            hover_bg = COLORS["bg_hover"]
        
        super().__init__(
            parent,
            text=display_text,
            font=FONTS["button"],
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            command=command,
            padx=DIMENSIONS["padding_sm"],
            pady=DIMENSIONS["padding_xs"],
            **kwargs
        )
        
        self._bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.config(bg=self._hover_bg)
    
    def _on_leave(self, e):
        self.config(bg=self._bg)


class Separator(ModernFrame):
    """Đường phân cách"""
    
    def __init__(self, parent, orient="horizontal"):
        super().__init__(parent, bg=COLORS["border_primary"])
        if orient == "horizontal":
            self.config(height=1)
        else:
            self.config(width=1)
