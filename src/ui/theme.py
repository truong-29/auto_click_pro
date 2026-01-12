# -*- coding: utf-8 -*-
"""Theme - Định nghĩa màu sắc và style cho ứng dụng"""

# === COLOR PALETTE - Dark Elegant Theme ===
COLORS = {
    # Background colors
    "bg_primary": "#1a1a2e",      # Nền chính - xanh đen đậm
    "bg_secondary": "#16213e",     # Nền phụ - xanh navy
    "bg_tertiary": "#0f3460",      # Nền accent - xanh đậm
    "bg_card": "#1f2940",          # Nền card
    "bg_input": "#2a3f5f",         # Nền input
    "bg_hover": "#3a506b",         # Hover state
    
    # Text colors
    "text_primary": "#e8e8e8",     # Text chính - trắng nhạt
    "text_secondary": "#a0aec0",   # Text phụ - xám nhạt
    "text_muted": "#718096",       # Text mờ
    "text_accent": "#64ffda",      # Text accent - xanh mint
    
    # Accent colors
    "accent_primary": "#e94560",   # Đỏ hồng - nút chính
    "accent_secondary": "#0f4c75", # Xanh dương đậm
    "accent_success": "#00d9a5",   # Xanh lá - thành công
    "accent_warning": "#ffc107",   # Vàng - cảnh báo
    "accent_danger": "#ff6b6b",    # Đỏ - nguy hiểm
    "accent_info": "#4dabf7",      # Xanh dương nhạt - thông tin
    
    # Border colors
    "border_primary": "#3a506b",   # Border chính
    "border_light": "#4a5568",     # Border nhạt
    "border_accent": "#e94560",    # Border accent
    
    # Button colors
    "btn_primary_bg": "#e94560",
    "btn_primary_fg": "#ffffff",
    "btn_secondary_bg": "#0f4c75",
    "btn_secondary_fg": "#e8e8e8",
    "btn_success_bg": "#00d9a5",
    "btn_success_fg": "#1a1a2e",
    "btn_danger_bg": "#ff6b6b",
    "btn_danger_fg": "#ffffff",
    
    # Selection
    "selection_bg": "#e94560",
    "selection_fg": "#ffffff",
}

# === FONTS ===
FONTS = {
    "heading_large": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 12, "bold"),
    "heading_small": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 10),
    "body_small": ("Segoe UI", 9),
    "mono": ("Consolas", 10),
    "mono_small": ("Consolas", 9),
    "button": ("Segoe UI", 9, "bold"),
}

# === DIMENSIONS ===
DIMENSIONS = {
    "padding_xs": 4,
    "padding_sm": 8,
    "padding_md": 12,
    "padding_lg": 16,
    "padding_xl": 24,
    "border_radius": 8,
    "input_height": 32,
    "button_height": 36,
}
