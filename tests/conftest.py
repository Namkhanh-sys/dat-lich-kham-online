import pytest
import os
import shutil
import pandas as pd
from datetime import datetime, timedelta
from config import Config

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(tmp_path_factory):
    """Set up a clean temporary database directory for all tests."""
    # Create temp directory for data
    temp_dir = tmp_path_factory.mktemp("test_data")
    
    # Save original config paths
    orig_users = Config.USERS_CSV
    orig_doctors = Config.DOCTORS_CSV
    orig_clinics = Config.CLINICS_CSV
    orig_appointments = Config.APPOINTMENTS_CSV
    
    # Override paths in Config
    Config.USERS_CSV = os.path.join(temp_dir, "users.csv")
    Config.DOCTORS_CSV = os.path.join(temp_dir, "doctors.csv")
    Config.CLINICS_CSV = os.path.join(temp_dir, "clinics.csv")
    Config.APPOINTMENTS_CSV = os.path.join(temp_dir, "appointments.csv")
    
    # Write mock data to temp CSV files for testing
    pd.DataFrame({
        'id': ['u1'],
        'name': ['Nguyễn Văn Khách'],
        'email': ['test@example.com'],
        'password_hash': ['ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'], # password123
        'phone': ['0987654321']
    }).to_csv(Config.USERS_CSV, index=False)
    
    pd.DataFrame({
        'id': ['c1', 'c2'],
        'name': ['Phòng khám A', 'Phòng khám B'],
        'address': ['12 Hàng Bài Hoàn Kiếm Hà Nội', '36 Điện Biên Phủ Ba Đình Hà Nội'],
        'lat': [21.0278, 21.0362],
        'lon': [105.8523, 105.8340],
        'city': ['Hà Nội', 'Hà Nội'],
    }).to_csv(Config.CLINICS_CSV, index=False)

    pd.DataFrame({
        'id': ['d1', 'd2'],
        'name': ['Bác sĩ X', 'Bác sĩ Y'],
        'specialty': ['Tai Mũi Họng', 'Nội khoa'],
        'symptoms': ['đau họng;ho;sổ mũi', 'sốt;mệt mỏi;đau đầu'],
        'clinic_id': ['c1', 'c2']
    }).to_csv(Config.DOCTORS_CSV, index=False)

    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    pd.DataFrame({
        'id': ['a1'],
        'user_id': ['u1'],
        'doctor_id': ['d1'],
        'date': [tomorrow],
        'time': ['09:00'],
        'status': ['Đã xác nhận']
    }).to_csv(Config.APPOINTMENTS_CSV, index=False)

    yield
    
    # Restore original configuration
    Config.USERS_CSV = orig_users
    Config.DOCTORS_CSV = orig_doctors
    Config.CLINICS_CSV = orig_clinics
    Config.APPOINTMENTS_CSV = orig_appointments
