# -*- coding: utf-8 -*-
"""Cấu hình ứng dụng"""

import os
import sys

# ============== THÔNG TIN ỨNG DỤNG ==============
APP_VERSION = "1.0.0"  # Cập nhật khi release mới
GITHUB_REPO = "your-username/autoclick-pro"  # Thay bằng repo của bạn

# Thư mục gốc - lấy từ vị trí main.py
if getattr(sys, 'frozen', False):
    # Nếu chạy từ exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    # Nếu chạy từ script
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Thư mục dữ liệu
DATA_DIR = os.path.join(APP_DIR, "data")
SCRIPTS_DIR = os.path.join(DATA_DIR, "scripts")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# Tạo thư mục nếu chưa tồn tại
for folder in [DATA_DIR, SCRIPTS_DIR, IMAGES_DIR]:
    os.makedirs(folder, exist_ok=True)

# Cấu hình cửa sổ
WINDOW_TITLE = "🖱️ AutoClick Pro - Công cụ tự động click"
WINDOW_SIZE = "750x850"

# Cấu hình PyAutoGUI
FAILSAFE = True
PAUSE = 0.1

# Phím tắt
HOTKEYS = {
    "pick_position": "f2",
    "pick_destination": "f3",
    "capture_region": "f4",
    "pick_color": "f5",
    "start": "f6",
    "stop": "f7",
    "emergency_stop": "esc"
}

# Cấu hình mặc định
DEFAULT_DELAY = 0.5
DEFAULT_CONFIDENCE = 80
DEFAULT_LOOP_COUNT = 1
DEFAULT_LOOP_DELAY = 1
IMAGE_WAIT_TIMEOUT = 30
COLOR_TOLERANCE = 10

# Loại hành động
ACTION_TYPES = [
    "Click chuột trái",
    "Click chuột phải",
    "Click đúp",
    "Kéo thả chuột",
    "Tìm hình ảnh",
    "Chờ (delay)",
    "Nhập văn bản",
    "Nhấn phím",
    "Tổ hợp phím",
    "Điều kiện (IF)",
    "Nhảy đến bước (GOTO)",
    "Điều khiển lặp",
]

# Loại điều kiện cho IF
CONDITION_TYPES = [
    ("last_search_found", "Kết quả tìm trước = TÌM THẤY"),
    ("last_search_not_found", "Kết quả tìm trước = KHÔNG THẤY"),
    ("image_found", "Tìm thấy hình ảnh"),
    ("image_not_found", "KHÔNG tìm thấy hình ảnh"),
    ("color_match", "Màu pixel khớp"),
    ("color_not_match", "Màu pixel KHÔNG khớp"),
]

# Hành động điều khiển vòng lặp
LOOP_ACTIONS = [
    ("restart", "🔄 Chạy lại từ đầu"),
    ("skip_to_next", "⏭️ Chuyển lần lặp tiếp"),
    ("stop", "⏹️ Dừng kịch bản"),
]

# File filters
IMAGE_FILETYPES = [("Hình ảnh", "*.png *.jpg *.jpeg *.bmp"), ("Tất cả", "*.*")]
SCRIPT_FILETYPES = [("JSON", "*.json")]
