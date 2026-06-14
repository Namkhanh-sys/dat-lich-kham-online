import pytest
import pandas as pd
from src.auth_service import AuthService
from src.csv_helper import CSVHelper

def test_password_hashing():
    p1 = "secret_password"
    hash1 = AuthService.hash_password(p1)
    hash2 = AuthService.hash_password(p1)
    assert hash1 == hash2
    assert hash1 != p1
    assert len(hash1) == 64 # SHA-256 length in hex

def test_login_user():
    # Correct login
    user = AuthService.login_user("test@example.com", "password123")
    assert user is not None
    assert user['name'] == "Nguyễn Văn Khách"
    
    # Wrong password
    user_wrong = AuthService.login_user("test@example.com", "wrongpass")
    assert user_wrong is None

    # Nonexistent user
    user_none = AuthService.login_user("nonexistent@example.com", "pass")
    assert user_none is None

def test_register_user():
    # Successful registration
    success, msg = AuthService.register_user("User New", "new@example.com", "secure123!", "0123456789")
    assert success is True
    assert "thành công" in msg.lower()

    # Check if user exists in database
    df = CSVHelper.get_users()
    assert "new@example.com" in df['email'].values

    # Duplicate registration
    success2, msg2 = AuthService.register_user("User Duplicate", "new@example.com", "secure123!", "0123456789")
    assert success2 is False
    assert "đã được đăng ký" in msg2

    # Phone validation failure (not 10 digits)
    success3, msg3 = AuthService.register_user("User Phone Fail", "phonefail@example.com", "secure123!", "01234")
    assert success3 is False
    assert "10 chữ số" in msg3

    # Password validation failure (less than 8 chars)
    success4, msg4 = AuthService.register_user("User Pass Fail", "passfail@example.com", "sec!", "0123456789")
    assert success4 is False
    assert "tối thiểu 8 ký tự" in msg4

    # Password validation failure (no special character)
    success5, msg5 = AuthService.register_user("User Spec Fail", "specfail@example.com", "secure123", "0123456789")
    assert success5 is False
    assert "ký tự đặc biệt" in msg5

def test_update_profile():
    # Find test user ID
    df = CSVHelper.get_users()
    user_id = df[df['email'] == "test@example.com"]['id'].values[0]

    # Update profile
    success, msg = AuthService.update_profile(user_id, "Nguyễn Văn Đã Cập Nhật", "0999999999")
    assert success is True
    
    # Verify updates
    df_after = CSVHelper.get_users()
    updated_user = df_after[df_after['id'] == user_id].iloc[0]
    assert updated_user['name'] == "Nguyễn Văn Đã Cập Nhật"
    assert updated_user['phone'] == "0999999999"

def test_change_password():
    df = CSVHelper.get_users()
    user_id = df[df['email'] == "test@example.com"]['id'].values[0]

    # Change password unsuccessfully (wrong old password)
    success1, msg1 = AuthService.change_password(user_id, "wrongold", "newpass123")
    assert success1 is False
    assert "cũ không chính xác" in msg1

    # Change password successfully
    success2, msg2 = AuthService.change_password(user_id, "password123", "newpass123")
    assert success2 is True

    # Try logging in with new password
    user = AuthService.login_user("test@example.com", "newpass123")
    assert user is not None
