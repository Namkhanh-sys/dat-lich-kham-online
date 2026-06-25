# Đặt Lịch Khám Trực Tuyến (MedBooking - Online Medical Appointment Booking)

Ứng dụng web Flask giúp đặt lịch khám trực tuyến dựa trên triệu chứng và khoảng cách địa lý đến phòng khám, tích hợp Trợ lý y tế AI (DocBot) thông minh để tối ưu hóa quy trình thăm khám của bệnh nhân.

## 🚀 Các Tính Năng Nổi Bật

1. **Nhận định Triệu chứng bằng AI (DocBot):** Tích hợp Google Gemini AI chatbot trả lời các câu hỏi y tế, chẩn đoán sơ bộ triệu chứng và gợi ý chuyên khoa cũng như bác sĩ phù hợp trực tiếp trong khung chat.
2. **Tìm kiếm Bác sĩ theo Vị trí (GPS/IP):** Tính toán khoảng cách địa lý thực tế bằng công thức **Haversine** từ tọa độ của người dùng (GPS, IP hoặc bản đồ thủ công) đến phòng khám để gợi ý bác sĩ gần nhất.
3. **Đặt lịch Chống tranh chấp (Atomic Lock):** Sử dụng cơ chế khóa nguyên tử `_booking_lock` để ngăn chặn Race Condition (trùng lịch khi nhiều người đặt cùng lúc). Đồng thời chặn trùng lịch kép (không cho người dùng đặt nhiều lịch khám ở cùng một khung giờ).
4. **Hồi phục Biểu mẫu nháp (LocalStorage):** Tự động lưu form điền lịch khám vào `localStorage`. Khi session hết hạn và đăng nhập lại, thông tin sẽ được khôi phục kèm banner thông báo để bệnh nhân không phải điền lại.
5. **Thông báo qua Email tự động:** Xác nhận đặt lịch thành công hoặc hủy lịch khám tức thì qua EmailJS hoặc SMTP.
6. **Nhắc lịch chạy nền (Background Scheduler):** Tự động quét cơ sở dữ liệu và gửi email nhắc nhở bệnh nhân trước giờ hẹn khám.

## 📁 Cấu Trúc Dự Án

```text
dat-lich-kham-online/
├── data/                    # Cơ sở dữ liệu dạng file phẳng CSV
│   ├── clinics.csv
│   ├── doctors.csv
│   ├── appointments.csv
│   └── users.csv
├── src/                     # Logic nghiệp vụ Python
│   ├── __init__.py
│   ├── auth_service.py      # Đăng ký, đăng nhập, mã hóa bảo mật
│   ├── csv_helper.py        # Đọc/ghi dữ liệu CSV bằng pandas + Caching RAM
│   ├── distance_calculator.py # Tính toán khoảng cách địa lý Haversine
│   ├── symptom_matcher.py   # Bản đồ triệu chứng -> chuyên khoa -> bác sĩ
│   ├── booking_manager.py   # Xử lý đặt lịch, khóa nguyên tử và kiểm tra trùng
│   ├── gemini_chatbot.py    # Tích hợp Google Gemini AI cho DocBot
│   └── email_service.py     # Dịch vụ gửi email thông báo qua SMTP/EmailJS
├── templates/               # Giao diện Jinja2 HTML (Glassmorphism design)
│   ├── layout.html          # Khung trang chính & Fab Widget Chatbot AI
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html       # Quản lý lịch hẹn của bệnh nhân (Hủy/Đổi lịch)
│   ├── profile.html         # Cập nhật thông tin hồ sơ
│   ├── index.html           # Tìm kiếm triệu chứng thông minh
│   ├── select_doctor.html   # Gợi ý bác sĩ theo khoảng cách & triệu chứng
│   ├── booking.html         # Form đặt lịch (Tự lưu nháp localStorage)
│   └── confirmation.html    # Xác nhận thành công
├── static/                  # File tĩnh (CSS, JS, hình ảnh)
│   └── css/
│       └── style.css        # Thiết kế Glassmorphism & Micro-animations
├── tests/                   # Thư mục chứa Unit Tests (Pytest)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_booking.py      # Test kiểm tra trùng giờ, đổi lịch, hủy lịch
│   ├── test_distance.py
│   ├── test_security.py     # Test kiểm tra rate limiting & CSRF
│   └── test_symptom.py
├── app.py                   # Khởi chạy Flask Web Server & API Endpoints
├── config.py                # Cấu hình hệ thống (API keys, đường dẫn dữ liệu)
└── requirements.txt         # Thư viện phụ thuộc
```

## 🛠️ Cách Cài Đặt và Chạy

1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

2. Khởi chạy ứng dụng:
   ```bash
   python app.py
   ```

3. Mở trình duyệt và truy cập: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🧪 Chạy Unit Test

Đảm bảo rằng toàn bộ các chức năng hoạt động đúng bằng cách chạy lệnh test:
```bash
pytest tests/
```

