import os

class Config:
    # Secure by default: generate a random key if none is provided via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # Path to the directories
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # CSV file paths
    CLINICS_CSV = os.path.join(DATA_DIR, 'clinics.csv')
    DOCTORS_CSV = os.path.join(DATA_DIR, 'doctors.csv')
    APPOINTMENTS_CSV = os.path.join(DATA_DIR, 'appointments.csv')
    USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
    
    # Email configuration (Mock or SMTP)
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_EMAIL = os.environ.get('SMTP_EMAIL') or 'namkanhkanh@gmail.com'
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or 'cskh vjug lnbm ohjz'
    
    # Session options
    SESSION_COOKIE_NAME = 'medical_booking_session'

    # OpenStreetMap Nominatim (bắt buộc có User-Agent)
    NOMINATIM_USER_AGENT = os.environ.get(
        'NOMINATIM_USER_AGENT',
        'MedBooking/1.0 (dat-lich-kham-online; contact@medbooking.local)',
    )
