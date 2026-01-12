# -*- coding: utf-8 -*-
"""Cấu hình ứng dụng"""

import os
import sys

# Thông tin phiên bản và GitHub
VERSION = "1.0.1"
GITHUB_REPO = "truong-29/auto_click_pro"
CHECK_UPDATE_ON_START = True


def get_app_dir():
    """Lấy thư mục chứa exe hoặc script"""
    if getattr(sys, 'frozen', False):
        # Chạy từ exe - lấy thư mục chứa file exe
        return os.path.dirname(sys.executable)
    else:
        # Chạy từ script - lấy thư mục gốc project
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bundle_dir():
    """Lấy thư mục chứa resources được đóng gói (cho onefile mode)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller onefile mode: extract vào _MEIPASS
        # PyInstaller onedir mode: cùng thư mục với exe
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Thư mục gốc của ứng dụng (chứa exe)
APP_DIR = get_app_dir()

# Thư mục chứa bundled resources (có thể là temp folder với onefile)
BUNDLE_DIR = get_bundle_dir()

# Thư mục dữ liệu người dùng (cạnh exe, để lưu scripts/images mới)
USER_DATA_DIR = os.path.join(APP_DIR, "data")
USER_SCRIPTS_DIR = os.path.join(USER_DATA_DIR, "scripts")
USER_IMAGES_DIR = os.path.join(USER_DATA_DIR, "images")

# Thư mục dữ liệu đóng gói (read-only, trong bundle)
BUNDLE_DATA_DIR = os.path.join(BUNDLE_DIR, "data")
BUNDLE_SCRIPTS_DIR = os.path.join(BUNDLE_DATA_DIR, "scripts")
BUNDLE_IMAGES_DIR = os.path.join(BUNDLE_DATA_DIR, "images")

# Alias cho tương thích ngược
DATA_DIR = USER_DATA_DIR
SCRIPTS_DIR = USER_SCRIPTS_DIR
IMAGES_DIR = USER_IMAGES_DIR

# Tạo thư mục user data nếu chưa tồn tại
for folder in [USER_DATA_DIR, USER_SCRIPTS_DIR, USER_IMAGES_DIR]:
    os.makedirs(folder, exist_ok=True)


def get_resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối đến resource.
    Ưu tiên user data, fallback về bundled data.
    """
    # Thử tìm trong user data trước
    user_path = os.path.join(USER_DATA_DIR, relative_path)
    if os.path.exists(user_path):
        return user_path
    
    # Fallback về bundled data
    bundle_path = os.path.join(BUNDLE_DATA_DIR, relative_path)
    if os.path.exists(bundle_path):
        return bundle_path
    
    # Trả về user path để tạo mới
    return user_path


def copy_bundled_data_if_needed():
    """
    Copy dữ liệu mẫu từ bundle sang user data nếu chưa có.
    Chỉ chạy lần đầu khi user data trống.
    """
    import shutil
    
    # Copy scripts mẫu
    if os.path.exists(BUNDLE_SCRIPTS_DIR):
        for filename in os.listdir(BUNDLE_SCRIPTS_DIR):
            src = os.path.join(BUNDLE_SCRIPTS_DIR, filename)
            dst = os.path.join(USER_SCRIPTS_DIR, filename)
            if not os.path.exists(dst) and os.path.isfile(src):
                shutil.copy2(src, dst)
    
    # Copy images mẫu
    if os.path.exists(BUNDLE_IMAGES_DIR):
        for filename in os.listdir(BUNDLE_IMAGES_DIR):
            src = os.path.join(BUNDLE_IMAGES_DIR, filename)
            dst = os.path.join(USER_IMAGES_DIR, filename)
            if not os.path.exists(dst) and os.path.isfile(src):
                shutil.copy2(src, dst)


# Copy dữ liệu mẫu khi khởi động
copy_bundled_data_if_needed()

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
