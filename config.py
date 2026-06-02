import os

class Config:
    # Secure by default: generate a random key if none is provided via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # Path to the directories
    # Use __file__ to get the config.py location, then go to parent directory to get project root
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # DEBUG: Print paths for troubleshooting (remove in production if needed)
    # print(f"[CONFIG] BASE_DIR: {BASE_DIR}")
    # print(f"[CONFIG] DATA_DIR: {DATA_DIR}")
    # print(f"[CONFIG] DATA_DIR exists: {os.path.exists(DATA_DIR)}")
    
    # CSV file paths
    CLINICS_CSV = os.path.join(DATA_DIR, 'clinics.csv')
    DOCTORS_CSV = os.path.join(DATA_DIR, 'doctors.csv')
    APPOINTMENTS_CSV = os.path.join(DATA_DIR, 'appointments.csv')
    USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
    
    # Email configuration - Resend
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
    EMAIL_FROM = 'onboarding@resend.dev'  # Resend default domain
    EMAIL_FROM_NAME = 'MedBooking - Đặt Lịch Khám Online'
    SUPPORT_EMAIL = 'support@medbooking.local'
    
    # Session options
    SESSION_COOKIE_NAME = 'medical_booking_session'

    # OpenStreetMap Nominatim (bắt buộc có User-Agent)
    NOMINATIM_USER_AGENT = os.environ.get(
        'NOMINATIM_USER_AGENT',
        'MedBooking/1.0 (dat-lich-kham-online; contact@medbooking.local)',
    )
