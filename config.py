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
    
    # Email configuration
    EMAILJS_SERVICE_ID = os.environ.get('EMAILJS_SERVICE_ID', 'service_qdlw3em').strip()
    EMAILJS_PUBLIC_KEY = os.environ.get('EMAILJS_PUBLIC_KEY', '3AknfTh_9nfeelswy').strip()
    EMAILJS_PRIVATE_KEY = os.environ.get('EMAILJS_PRIVATE_KEY', '').strip()
    EMAILJS_TEMPLATE_ID = os.environ.get('EMAILJS_TEMPLATE_ID', 'template_1mv18ta').strip()
    EMAILJS_API_URL = 'https://api.emailjs.com/api/v1.0/email/send'
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY') or os.environ.get('RESEND_API_KEY_TEST')
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'onboarding@resend.dev')
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USER = os.environ.get('SMTP_USER', 'namkanhkanh@gmail.com')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # Use app password from Gmail
    EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', 'MedBooking - Đặt Lịch Khám Online')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'namkanhkanh@gmail.com')
    ENABLE_DEBUG_ROUTES = os.environ.get('ENABLE_DEBUG_ROUTES', 'false').lower() == 'true'
    SEND_EMAIL_ASYNC = os.environ.get('SEND_EMAIL_ASYNC', 'true').lower() == 'true'
    
    # Session options
    SESSION_COOKIE_NAME = 'medical_booking_session'

    # OpenStreetMap Nominatim (bắt buộc có User-Agent)
    NOMINATIM_USER_AGENT = os.environ.get(
        'NOMINATIM_USER_AGENT',
        'MedBooking/1.0 (dat-lich-kham-online; contact@medbooking.local)',
    )
