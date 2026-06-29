"""
Script kiểm tra thủ công:
  1. Lưu tài khoản người dùng (AuthService.register_user)
  2. Gửi email xác nhận đặt lịch qua Gmail SMTP (EmailService)

Chạy: venv\\Scripts\\python scratch\\test_register_email.py
"""
import sys
import os

# Thêm root vào sys.path để import được config, src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from config import Config
from src.auth_service import AuthService
from src.csv_helper import CSVHelper
from src.email_service import EmailService

# ─────────────────────────────────────────────
# 1. Kiểm tra lưu tài khoản người dùng
# ─────────────────────────────────────────────
print("=" * 55)
print("  KIỂM TRA: Lưu tài khoản người dùng")
print("=" * 55)

TEST_EMAIL = "test_scratch@example.com"
TEST_PASS  = "Password@999"
TEST_PHONE = "0900000001"

# Xoá user test (nếu tồn tại từ lần chạy trước)
df = CSVHelper.get_users()
before_count = len(df)
df_clean = df[df['email'] != TEST_EMAIL]
if len(df_clean) < before_count:
    CSVHelper.save_users(df_clean)
    print(f"[INFO] Đã xoá user cũ '{TEST_EMAIL}' trước khi test.")

# Test 1: Đăng ký thành công
success, msg = AuthService.register_user("Test Scratch User", TEST_EMAIL, TEST_PASS, TEST_PHONE)
print(f"[TEST 1] Đăng ký hợp lệ  => success={success}, msg='{msg}'")
assert success, f"FAIL: {msg}"

# Xác nhận file CSV đã lưu
df_after = CSVHelper.get_users()
assert TEST_EMAIL in df_after['email'].values, "FAIL: Email không có trong CSV"
print(f"[TEST 1] User đã lưu vào CSV (tổng users: {len(df_after)})")

# Test 2: Email trùng lặp
s2, m2 = AuthService.register_user("Test Duplicate", TEST_EMAIL, TEST_PASS, TEST_PHONE)
print(f"[TEST 2] Email trùng       => success={s2}, msg='{m2}'")
assert not s2, "FAIL: Phải từ chối email trùng"

# Test 3: Mật khẩu yếu (không có ký tự đặc biệt)
s3, m3 = AuthService.register_user("Test Weak Pass", "weak@example.com", "Password1", "0900000002")
print(f"[TEST 3] Mật khẩu yếu     => success={s3}, msg='{m3}'")
assert not s3, "FAIL: Phải từ chối mật khẩu không có ký tự đặc biệt"

# Test 4: SĐT sai định dạng
s4, m4 = AuthService.register_user("Test Phone", "phone@example.com", TEST_PASS, "123")
print(f"[TEST 4] SĐT sai định dạng => success={s4}, msg='{m4}'")
assert not s4, "FAIL: Phải từ chối SĐT không đủ 10 số"

# Test 5: Login với tài khoản vừa tạo
user = AuthService.login_user(TEST_EMAIL, TEST_PASS)
print(f"[TEST 5] Login sau đăng ký => user={user['name'] if user else None}")
assert user is not None, "FAIL: Không thể đăng nhập sau khi đăng ký"
assert user['email'] == TEST_EMAIL

print("\n[OK] Tat ca kiem tra LUU TAI KHOAN deu PASS!")

# ─────────────────────────────────────────────
# 2. Kiểm tra gửi Gmail
# ─────────────────────────────────────────────
print()
print("=" * 55)
print("  KIỂM TRA: Gửi Email")
print("=" * 55)
print(f"[CONFIG] SMTP_SERVER   : {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
print(f"[CONFIG] SMTP_USER     : {Config.SMTP_USER}")
print(f"[CONFIG] SMTP_PASSWORD : {'*** (da cau hinh)' if Config.SMTP_PASSWORD else '(CHUA cau hinh)'}")
print(f"[CONFIG] EMAILJS       : {'Co ServiceID' if Config.EMAILJS_SERVICE_ID else 'Khong co'}")
print(f"[CONFIG] RESEND_API_KEY: {'Co' if Config.RESEND_API_KEY else 'Khong co'}")
print()

RECIPIENT_EMAIL = Config.SMTP_USER  # Gửi cho chính tài khoản cấu hình để kiểm tra

print(f"[EMAIL TEST] Gui email xac nhan dat lich den: {RECIPIENT_EMAIL}")
ok, result_msg = EmailService.send_booking_confirmation(
    user_email=RECIPIENT_EMAIL,
    user_name="Do Nam Khanh (Test)",
    doctor_name="BS. Nguyen Van A",
    date_str="2026-07-15",
    time_str="09:00 - 09:30",
    clinic_name="Phong kham Test",
    address="123 Duong ABC, Ha Noi",
    consultation_fee="200.000 VND",
    payment_note="Thanh toan tai quay"
)

print(f"[EMAIL TEST] Ket qua => ok={ok}, message='{result_msg}'")

if ok:
    print("\n[OK] Gui email THANH CONG (hoac da ghi log/queue)!")
else:
    print("\n[WARN] Gui email THAT BAI! Kiem tra cau hinh SMTP/EmailJS/Resend.")

# Kiểm tra log file
log_file = os.path.join(Config.DATA_DIR, 'email_notifications.log')
if os.path.exists(log_file):
    print(f"\n[LOG] File log email: {log_file}")
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"[LOG] Tong so dong log: {len(lines)}")
    print("[LOG] 10 dong cuoi:")
    print("".join(lines[-10:]))
else:
    print(f"\n[LOG] Chua co file log tai: {log_file}")

# ─────────────────────────────────────────────
# Dọn dẹp
# ─────────────────────────────────────────────
df_final = CSVHelper.get_users()
df_clean2 = df_final[df_final['email'] != TEST_EMAIL]
CSVHelper.save_users(df_clean2)
print(f"\n[CLEANUP] Da xoa user test '{TEST_EMAIL}' khoi CSV.")
print("\n=== HOAN TAT KIEM TRA ===")
