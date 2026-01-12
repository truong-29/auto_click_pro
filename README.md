# 📦 Hướng dẫn cài đặt AutoClick Pro

## Yêu cầu hệ thống
- **OS**: Windows 7 trở lên
- **Python**: 3.8 hoặc cao hơn
- **RAM**: Tối thiểu 512MB
- **Quyền**: Administrator (để gửi input vào các cửa sổ khác)

## Cách cài đặt

### 1️⃣ Cài đặt Python (nếu chưa có)
Tải từ: https://www.python.org/downloads/

**Lưu ý quan trọng**: Khi cài đặt, hãy tích chọn **"Add Python to PATH"**

### 2️⃣ Cài đặt Dependencies

Mở Command Prompt (cmd) hoặc PowerShell tại thư mục dự án, rồi chạy:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3️⃣ Chạy ứng dụng

```bash
python main.py
```

Ứng dụng sẽ tự động yêu cầu quyền Administrator nếu cần.

---

## 📋 Danh sách Dependencies

| Package | Phiên bản | Mục đích |
|---------|----------|---------|
| **pyautogui** | ≥0.9.54 | Điều khiển chuột và bàn phím |
| **keyboard** | ≥0.13.5 | Xử lý phím tắt toàn cục |
| **Pillow** | ≥10.0.0 | Xử lý hình ảnh |
| **opencv-python** | ≥4.8.0 | Nhận dạng hình ảnh (template matching) |
| **numpy** | ≥1.24.0 | Xử lý mảng số (yêu cầu của OpenCV) |
| **pywin32** | ≥306 | Windows API (gửi input vào cửa sổ cụ thể) |
| **psutil** | ≥5.9.0 | Quản lý process hệ thống |
| **PyInstaller** | ≥6.0.0 | Build thành file .exe (tùy chọn) |

---

## 🔧 Xử lý sự cố

### ❌ Lỗi: "Python is not recognized"
**Giải pháp**: Python chưa được thêm vào PATH
- Cài đặt lại Python và tích chọn "Add Python to PATH"
- Hoặc thêm thủ công: `C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python313`

### ❌ Lỗi: "No module named 'tkinter'"
**Giải pháp**: Tkinter không được cài đặt với Python
- Cài đặt lại Python và chọn "tcl/tk and IDLE"

### ❌ Lỗi: "Permission denied" khi chạy
**Giải pháp**: Chạy Command Prompt với quyền Administrator
- Click phải vào cmd → "Run as administrator"

### ❌ Lỗi: "opencv-python" không cài được
**Giải pháp**: Cập nhật pip trước
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

---

## 🚀 Build thành file .exe (tùy chọn)

Nếu muốn tạo file .exe để chạy mà không cần Python:

### Build 1 file exe duy nhất (khuyên dùng)
```bash
python build.py
# hoặc
python build.py onefile
```
→ Output: `dist/AutoClickPro.exe` (1 file duy nhất, dễ phân phối)

### Build thành folder (khởi động nhanh hơn)
```bash
python build.py folder
```
→ Output: `dist/AutoClickPro/AutoClickPro.exe`

### So sánh 2 mode

| Tiêu chí | Onefile | Folder |
|----------|---------|--------|
| Output | 1 file .exe | Folder + nhiều file |
| Khởi động | Chậm hơn (~3-5s) | Nhanh |
| Phân phối | Dễ dàng | Cần zip folder |
| Kích thước | ~50-80MB | ~100-150MB |

### Lưu ý khi sử dụng file exe
- File exe đã bao gồm tất cả dependencies, không cần cài Python
- Lần đầu chạy sẽ tự động tạo folder `data/` cạnh file exe
- Scripts và images mới sẽ được lưu trong folder `data/`

---

## ✅ Kiểm tra cài đặt

Chạy lệnh này để kiểm tra tất cả dependencies:

```bash
python -c "import pyautogui, keyboard, PIL, cv2, numpy, win32gui, psutil; print('✅ Tất cả dependencies đã cài đặt!')"
```

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra lại Python version: `python --version`
2. Kiểm tra pip: `python -m pip --version`
3. Cập nhật pip: `python -m pip install --upgrade pip`
4. Cài lại dependencies: `python -m pip install -r requirements.txt --force-reinstall`
