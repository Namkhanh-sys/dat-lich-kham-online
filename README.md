# Đặt Lịch Khám Trực Tuyến (Online Medical Appointment Booking)

Ứng dụng web Flask giúp đặt lịch khám trực tuyến dựa trên triệu chứng và khoảng cách địa lý đến phòng khám. Hệ thống lưu trữ dữ liệu dạng CSV để dễ quản lý và kiểm thử.

## Cấu Trúc Dự Án

```text
dat-lich-kham-online/
├── data/                    # Dữ liệu CSV lưu trữ thông tin
│   ├── clinics.csv
│   ├── doctors.csv
│   ├── appointments.csv
│   └── users.csv
├── src/                     # Logic nghiệp vụ Python
│   ├── __init__.py
│   ├── auth_service.py      # Đăng ký, đăng nhập, bảo mật session
│   ├── csv_helper.py        # Đọc/ghi cơ sở dữ liệu CSV bằng pandas
│   ├── distance_calculator.py # Tính khoảng cách địa lý (Haversine)
│   ├── symptom_matcher.py   # Bản đồ triệu chứng -> chuyên khoa -> bác sĩ
│   ├── booking_manager.py   # Xử lý đặt lịch, kiểm tra trùng, gợi ý thay thế
│   └── email_service.py     # Giả lập gửi email thông báo đặt lịch
├── templates/               # Giao diện Jinja2 HTML
│   ├── layout.html          # Khung trang chính
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html       # Quản lý lịch hẹn của bệnh nhân
│   ├── profile.html         # Cập nhật thông tin cá nhân
│   ├── index.html           # Tìm kiếm theo triệu chứng
│   ├── select_doctor.html   # Đề xuất bác sĩ theo triệu chứng & khoảng cách
│   ├── booking.html         # Chọn giờ đặt lịch
│   └── confirmation.html    # Xác nhận thành công
├── static/                  # File tĩnh (CSS, JS, hình ảnh)
│   └── css/
│       └── style.css        # Vanilla CSS giao diện Glassmorphism cao cấp
├── tests/                   # Thư mục chứa Unit Tests
│   ├── test_auth.py
│   ├── test_booking.py
│   ├── test_distance.py
│   └── test_symptom.py
├── app.py                   # Điểm khởi chạy Flask Web Server
├── config.py                # File cấu hình hệ thống
└── requirements.txt         # Khai báo thư viện phụ thuộc
```

## Cách Cài Đặt và Chạy

1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

2. Khởi chạy ứng dụng:
   ```bash
   python app.py
   ```

3. Mở trình duyệt và truy cập: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Chạy Unit Test

Đảm bảo rằng toàn bộ các chức năng hoạt động đúng bằng cách chạy lệnh test:
```bash
pytest tests/
```
