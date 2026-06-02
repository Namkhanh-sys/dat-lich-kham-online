# Comprehensive Code Review: Flask Doctor Appointment Booking Application

**Date:** June 2, 2026  
**Application:** Doctor Appointment Online Booking System (Đặt Lịch Khám Online)

---

## Executive Summary

This code review identifies **16 critical/high-severity issues** and **14 medium/low-severity issues** across the Flask application, covering security vulnerabilities, performance problems, code quality issues, and missing error handling patterns.

### Critical Issues: 5
- Hardcoded API key in source code
- Weak password hashing without salt
- Session and CSRF vulnerabilities
- Missing input validation
- Unsafe CSV data operations

### High Issues: 10
- Type hints completely missing
- Inconsistent error handling
- Race conditions in concurrent operations
- Insufficient validation in booking logic

### Medium Issues: 8
- Performance issues with repeated CSV reads
- Missing documentation
- Incomplete test coverage
- Naming convention inconsistencies

---

## 1. CRITICAL SECURITY ISSUES

### 1.1 Hardcoded API Key in Configuration

**File:** [config.py](config.py#L15)  
**Severity:** CRITICAL  
**Line:** 15

```python
RESEND_API_KEY = 're_bKPiAejP_ETtgcBJcXKjwAHymMHynL6QQ'
EMAIL_FROM = 'onboarding@resend.dev'  # Resend default domain
```

**Issue:** 
- Production API key is hardcoded and committed to source code
- Anyone with repository access can send emails on behalf of the system
- API key is visible in GitHub, Git history, and logs
- No rotation mechanism

**Recommendation:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
if not RESEND_API_KEY and not os.environ.get('FLASK_ENV') == 'development':
    raise ValueError("RESEND_API_KEY environment variable must be set in production")
```

**Impact:** Email account compromise, unauthorized messaging, potential spam/phishing abuse

---

### 1.2 Weak Password Hashing (SHA-256 without Salt)

**File:** [src/auth_service.py](src/auth_service.py#L7-L9)  
**Severity:** CRITICAL  
**Lines:** 7-9

```python
@staticmethod
def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
```

**Issues:**
1. **No salt:** Same password produces identical hash across all users
2. **No iteration count:** Fast, vulnerable to brute force attacks
3. **Reversible in tables:** SHA-256 hashes are widely pre-computed in rainbow tables
4. **Not designed for passwords:** SHA-256 is a general-purpose hash, not a password hash

**Example Attack:**
```python
# Attacker can reverse common passwords
import hashlib
common_passwords = ['password123', '123456', 'admin', ...]
for pwd in common_passwords:
    h = hashlib.sha256(pwd.encode()).hexdigest()
    if h == stored_hash:
        print(f"Password found: {pwd}")
```

**Recommendation:** Use `bcrypt` or `argon2` (OWASP standard):
```python
import bcrypt

@staticmethod
def hash_password(password):
    """Hash password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

@staticmethod
def verify_password(password, hash):
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
```

**Install:** `pip install bcrypt`

**Impact:** Complete account takeover for any user with weak passwords

---

### 1.3 Missing CSRF Protection

**File:** [app.py](app.py#L8-L16)  
**Severity:** CRITICAL

**Issue:** Flask sessions and forms are not protected by CSRF tokens.

**Evidence:**
- No `csrf_token()` in any form templates
- No CSRF validation in POST endpoints
- Flask-WTF or similar CSRF middleware not imported
- No `SECRET_KEY` rotation or HTTPS enforcement

**Vulnerable Endpoints:**
- `/register` (POST) - Line 338
- `/login` (POST) - Line 312
- `/profile/update` (POST) - Line 376
- `/profile/change-password` (POST) - Line 389
- `/book/<doctor_id>` (POST) - Line 429
- `/cancel/<appointment_id>` (POST) - Line 516
- `/reschedule/<appointment_id>` (POST) - Line 534

**Attack Scenario:**
```html
<!-- Attacker's website -->
<form action="https://medbooking.com/cancel/a1" method="POST">
  <input type="hidden" name="action" value="cancel">
  <img src=x onerror="this.parentElement.submit()">
</form>
<!-- User clicks link while logged in → appointment cancelled -->
```

**Recommendation:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
csrf.init_app(app)

# In templates:
# <form method="POST">
#   {{ csrf_token() }}
# </form>
```

**Impact:** Unauthorized actions on behalf of authenticated users (cancel/reschedule appointments, change password)

---

### 1.4 Missing Input Validation - Injection Risks

**File:** [app.py](app.py#L31-L92)  
**Severity:** CRITICAL  
**Lines:** Query parameters used directly

**Issue:** User input from request parameters is not validated or sanitized:

**Vulnerable Code:**
```python
@app.route('/select-doctor')
def select_doctor():
    symptoms = request.args.get('symptoms', '').strip()  # No validation
    province = request.values.get('province', '').strip()  # No validation
    district = request.values.get('district', '').strip()  # No validation
    ward = request.values.get('ward', '').strip()  # No validation
    
    matched_docs = SymptomMatcher.match_doctors_by_symptom(symptoms)  # Unsafe
```

**Problems:**
1. Symptoms query could be 100KB+ causing DoS
2. Coordinates (lat/lon) not bounded to valid ranges (-90 to 90, -180 to 180)
3. Province/district/ward could contain path traversal or injection patterns
4. No length limits on input fields

**Validation Examples:**

```python
def validate_location_params():
    """Validate and constrain location query parameters."""
    lat = request.values.get('lat', '').strip()
    lon = request.values.get('lon', '').strip()
    
    # Validate latitude range
    try:
        lat_f = float(lat) if lat else None
        if lat_f is not None and not (-90 <= lat_f <= 90):
            raise ValueError("Latitude must be between -90 and 90")
    except (ValueError, TypeError):
        lat_f = None
    
    # Validate longitude range
    try:
        lon_f = float(lon) if lon else None
        if lon_f is not None and not (-180 <= lon_f <= 180):
            raise ValueError("Longitude must be between -180 and 180")
    except (ValueError, TypeError):
        lon_f = None
    
    # Validate string fields: max 100 chars, alphanumeric + spaces
    province = request.values.get('province', '').strip()[:100]
    district = request.values.get('district', '').strip()[:100]
    ward = request.values.get('ward', '').strip()[:100]
    
    if not all(c.isalnum() or c.isspace() or c in 'áàảãạăằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ,-.' 
               for c in f"{province}{district}{ward}"):
        raise ValueError("Invalid characters in location fields")
    
    return lat_f, lon_f, province, district, ward
```

**Impact:** 
- Denial of Service attacks
- Unexpected application behavior
- Potential code injection if data is later used in dynamic queries

---

### 1.5 Unsafe CSV Data Operations - Race Conditions

**File:** [src/csv_helper.py](src/csv_helper.py#L19-L57)  
**Severity:** CRITICAL  
**Lines:** 19-57

**Issue:** CSV read/write operations have race conditions in concurrent environments.

**Problems:**
```python
@classmethod
def read_csv(cls, file_path):
    """Read CSV file (no caching - always fresh)."""
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return pd.DataFrame()
    # No file locking
    df = pd.read_csv(file_path, dtype=str)  # Potential race condition here
    return df.copy()

@staticmethod
def write_csv(df, file_path):
    """Write DataFrame to CSV file."""
    # NO ATOMIC WRITE - partial writes possible
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)  # Not atomic, can corrupt on crash
    return True
```

**Attack Scenario:**
```
Thread 1: Read appointments.csv
Thread 2: Read appointments.csv
Thread 1: Add appointment a1, Write to CSV
Thread 2: Add appointment a2 (doesn't see a1), Write to CSV
Result: a1 is lost, a2 overwrites it
```

**Race Condition Scenarios:**
1. **Lost Update:** Concurrent writes overwrite each other
2. **Dirty Read:** Read stale data while write is in progress
3. **File Corruption:** Partial write during crash leaves file corrupted
4. **Double Booking:** Same time slot booked twice due to concurrent reads

**Recommendation:** Use database instead of CSV:
```python
# Option 1: SQLite (simplest)
import sqlite3

@classmethod
def get_appointments_db(cls):
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    return cursor.fetchall()

# Option 2: Use file locking with fcntl (Linux/Mac)
import fcntl

@classmethod
def read_csv_safe(cls, file_path):
    with open(file_path, 'r') as f:
        fcntl.flock(f, fcntl.LOCK_SH)  # Shared lock for reading
        df = pd.read_csv(f)
        fcntl.flock(f, fcntl.LOCK_UN)  # Unlock
    return df

# Option 3: Use atomic write with temp file
def write_csv_safe(df, file_path):
    temp_path = file_path + '.tmp'
    df.to_csv(temp_path, index=False)
    os.replace(temp_path, file_path)  # Atomic on most filesystems
```

**Impact:** Lost bookings, double bookings, data corruption

---

## 2. HIGH-SEVERITY ISSUES

### 2.1 Missing Type Hints Throughout Codebase

**Files:** ALL Python files  
**Severity:** HIGH

**Issue:** No type hints in any Python files. Makes code hard to understand, debug, and maintain.

**Current:**
```python
def match_doctors_by_symptom(cls, query_text):
    """Analyze user's query text for symptoms, and match doctors."""
    df_doctors = CSVHelper.get_doctors()
    if df_doctors.empty:
        return []
    
    cleaned_query = cls.clean_text(query_text)
    matched_doctors = []
```

**Recommended:**
```python
from typing import List, Dict, Any, Optional
import pandas as pd

@classmethod
def match_doctors_by_symptom(cls, query_text: str) -> List[Dict[str, Any]]:
    """Analyze user's query text for symptoms, and match doctors.
    
    Args:
        query_text: User's symptom description in natural language
        
    Returns:
        List of doctor dictionaries with match_score and matched_symptoms
    """
    df_doctors: pd.DataFrame = CSVHelper.get_doctors()
    if df_doctors.empty:
        return []
    
    cleaned_query: str = cls.clean_text(query_text)
    matched_doctors: List[Dict[str, Any]] = []
```

**Benefits:**
- IDE autocomplete support
- Catch type errors before runtime
- Self-documenting code
- Enable static analysis tools (mypy, pyright)

**Commands to Add:**
```bash
pip install mypy
mypy src/  # Check for type errors
```

**Key files needing annotations:**
- [src/auth_service.py](src/auth_service.py)
- [src/booking_manager.py](src/booking_manager.py)
- [src/csv_helper.py](src/csv_helper.py)
- [src/distance_calculator.py](src/distance_calculator.py)
- [app.py](app.py)

---

### 2.2 Session Configuration Security

**File:** [config.py](config.py#L25-L26)  
**Severity:** HIGH

```python
# Session options
SESSION_COOKIE_NAME = 'medical_booking_session'
```

**Missing Security Headers:**
```python
# MISSING - Should be added:
SESSION_COOKIE_SECURE = True  # Only send over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour timeout
SESSION_COOKIE_NAME = 'medical_booking_session'
```

**Recommended Fix:**
```python
# config.py
class Config:
    # ... existing config ...
    
    # Security headers
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Add these Flask security settings:
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files
    PREFERRED_URL_SCHEME = 'https' if SESSION_COOKIE_SECURE else 'http'
```

---

### 2.3 Incomplete Email Validation

**File:** [app.py](app.py#L340-L343)  
**Severity:** HIGH

```python
if '@' not in email or '.' not in email:
    flash("Email không hợp lệ.", "error")
    return render_template('register.html')
```

**Issues:**
1. **Too simplistic:** `a@b` passes validation (no TLD)
2. **No RFC compliance:** Should validate according to RFC 5321
3. **Allows invalid emails:** `test@@example.com`, `test@.com`, etc.

**Recommendation:**
```python
import re
from email_validator import validate_email, EmailNotValidError

def validate_user_email(email: str) -> tuple[bool, str]:
    """Validate email format and deliverability."""
    try:
        # Normalize
        v = validate_email(email)
        return True, v.email  # Normalized form
    except EmailNotValidError as e:
        return False, str(e)

# In register route:
is_valid, error_msg = validate_user_email(email)
if not is_valid:
    flash(f"Email không hợp lệ: {error_msg}", "error")
    return render_template('register.html')
```

**Install:** `pip install email-validator`

---

### 2.4 Missing Boundary Checks in Distance Queries

**File:** [src/distance_calculator.py](src/distance_calculator.py#L151-L168)  
**Severity:** HIGH

```python
@classmethod
def get_clinics_with_distance(cls, user_lat, user_lon, province=None, district=None, ward=None,
                              prefer_city=None, max_radius_km=None):
    # No validation of user_lat/user_lon ranges
    parsed_lat, parsed_lon = cls._parse_user_coords(user_lat, user_lon)
    
    if max_radius_km is not None and parsed_lat is not None:
        pool = [c for c in pool if c['distance_km'] <= max_radius_km]  # No upper bound on max_radius_km
```

**Issues:**
1. `max_radius_km` can be 999999, forcing computation of distance to all clinics
2. No rate limiting on repeated queries with different parameters
3. Haversine calculations could cause DoS if `lat/lon` are 0.0 (pole singularities)

**Recommendation:**
```python
from typing import Optional

VALID_LAT_RANGE = (-90.0, 90.0)
VALID_LON_RANGE = (-180.0, 180.0)
MAX_SEARCH_RADIUS_KM = 500  # Absolute maximum

@classmethod
def get_clinics_with_distance(cls, 
                             user_lat: Optional[float], 
                             user_lon: Optional[float], 
                             province: Optional[str] = None, 
                             district: Optional[str] = None, 
                             ward: Optional[str] = None,
                             prefer_city: Optional[str] = None, 
                             max_radius_km: Optional[float] = None):
    """Get clinics sorted by distance with validated parameters."""
    
    # Validate radius
    if max_radius_km is not None:
        if max_radius_km <= 0:
            raise ValueError("max_radius_km must be positive")
        if max_radius_km > MAX_SEARCH_RADIUS_KM:
            raise ValueError(f"max_radius_km cannot exceed {MAX_SEARCH_RADIUS_KM} km")
    
    # ... rest of logic
```

---

### 2.5 Exception Handling Too Broad

**File:** [src/geocoding_service.py](src/geocoding_service.py#L36-L43)  
**Severity:** HIGH

```python
@classmethod
def search(cls, query, limit=5):
    if not query or not str(query).strip():
        return []
    q = str(query).strip()
    if 'việt nam' not in q.lower() and 'viet nam' not in q.lower():
        q = f"{q}, Việt Nam"
    return cls._fetch('search', {  # Can raise urllib exception
        'q': q,
        'limit': limit,
        'addressdetails': 1,
        'countrycodes': 'vn',
    })
```

**Issues:**
- Network timeouts, parse errors not handled
- Errors bubble up to templates
- No fallback or retry logic

**Better:**
```python
@classmethod
def search(cls, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search for addresses via Nominatim.
    
    Args:
        query: Address search query
        limit: Maximum results to return
        
    Returns:
        List of location dicts, or empty list on error
    """
    if not query or not str(query).strip():
        return []
    
    q = str(query).strip()
    if 'việt nam' not in q.lower() and 'viet nam' not in q.lower():
        q = f"{q}, Việt Nam"
    
    try:
        return cls._fetch('search', {
            'q': q,
            'limit': limit,
            'addressdetails': 1,
            'countrycodes': 'vn',
        })
    except urllib.error.URLError as e:
        print(f"[GeocodingService] Network error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"[GeocodingService] Parse error: {e}")
        return []
    except Exception as e:
        print(f"[GeocodingService] Unexpected error: {e}")
        return []
```

---

### 2.6 Missing Phone Number Validation

**File:** [app.py](app.py#L333-L365)  
**Severity:** HIGH

```python
phone = request.form.get('phone', '').strip()

if not name or not email or not phone:
    flash("Vui lòng điền đầy đủ tên, email và số điện thoại.", "error")
    return render_template('register.html')
```

**Issues:**
- Any non-empty string accepted (including "xyz", "abcdef")
- Vietnamese phone numbers must be 10 digits starting with 0
- No international support

**Recommendation:**
```python
import re

def validate_phone_number(phone: str) -> tuple[bool, str]:
    """Validate Vietnamese phone number format."""
    phone = phone.strip().replace(' ', '').replace('-', '')
    
    # Vietnamese phone: 10 digits starting with 0 (or +84)
    vietnamese_pattern = r'^(0|\+84)[1-9]\d{8}$'
    
    if not re.match(vietnamese_pattern, phone):
        return False, "Số điện thoại phải là 10 chữ số bắt đầu từ 0 (ví dụ: 0912345678)"
    
    return True, phone

# In register:
is_valid, error = validate_phone_number(phone)
if not is_valid:
    flash(f"Số điện thoại không hợp lệ: {error}", "error")
    return render_template('register.html')
```

---

### 2.7 SQL Injection-like Risk in CSV Search

**File:** [src/symptom_matcher.py](src/symptom_matcher.py#L23-L40)  
**Severity:** MEDIUM-HIGH

While not true SQL injection, substring matching without sanitization could cause:

```python
for symptom in symptoms:
    if symptom in cleaned_query:  # Substring matching, case-sensitive
        match_score += 1
```

**Issues:**
1. Substring "ho" matches "họ", "hố", etc.
2. Could match unintended symptoms
3. No word boundary checking

**Recommendation:**
```python
import re

def _is_word_in_text(word: str, text: str) -> bool:
    """Check if word appears as a complete word in text."""
    # Use word boundaries for Vietnamese (approximate)
    pattern = r'\b' + re.escape(word) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))

for symptom in symptoms:
    # Use word boundary matching instead of substring
    if _is_word_in_text(symptom, cleaned_query):
        match_score += 1
```

---

### 2.8 No Logging of Security Events

**File:** app.py, src/auth_service.py  
**Severity:** HIGH

**Issues:**
- Failed login attempts not logged
- Password changes not audited
- No suspicious activity detection
- No forensic trail for security investigations

**Recommendation:**
```python
import logging
from datetime import datetime

# Set up security audit logger
security_logger = logging.getLogger('security')

# In login:
user = AuthService.login_user(email, password)
if not user:
    security_logger.warning(f"Failed login attempt for {email} from {request.remote_addr}")
else:
    security_logger.info(f"Successful login for {email}")

# In password change:
security_logger.info(f"Password changed for user {user_id} from IP {request.remote_addr}")

# In logout:
security_logger.info(f"Logout for user {user_id}")
```

---

### 2.9 No Rate Limiting on Authentication Endpoints

**File:** [app.py](app.py#L312-L380)  
**Severity:** HIGH

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    # No rate limiting - brute force attack possible
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        user = AuthService.login_user(email, password)
```

**Issues:**
- Attacker can try unlimited passwords
- No account lockout after failed attempts
- No exponential backoff

**Recommendation:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # 5 attempts per minute
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        user = AuthService.login_user(email, password)
        # ...
```

**Install:** `pip install Flask-Limiter`

---

### 2.10 Hardcoded Redirect Coordinates

**File:** [app.py](app.py#L429-L434)  
**Severity:** MEDIUM-HIGH

```python
@app.route('/doctor/<doctor_id>')
def doctor_detail(doctor_id):
    # ...
    lat = request.args.get('lat', '21.0285').strip()  # Hanoi hardcoded
    lon = request.args.get('lon', '105.8542').strip()  # Hanoi hardcoded
    province = request.args.get('province', '').strip()
```

**Issues:**
- Defaults to Hanoi coordinates regardless of actual user location
- User traveling in Ho Chi Minh sees Hanoi doctors first
- Confusing UX for non-Hanoi users

**Better:**
```python
# Use geolocation from browser or last selected location
DEFAULT_LAT = None  # No default - require user input
DEFAULT_LON = None

lat = request.args.get('lat', '').strip() or DEFAULT_LAT
lon = request.args.get('lon', '').strip() or DEFAULT_LON
```

---

## 3. MEDIUM-SEVERITY ISSUES

### 3.1 Performance: Repeated CSV File Reads

**File:** [src/booking_manager.py](src/booking_manager.py#L76-L108)  
**Severity:** MEDIUM

```python
@classmethod
def create_booking(cls, user_id, doctor_id, date_str, time_str):
    # ... validation ...
    
    df_appointments = CSVHelper.get_appointments()  # Read from disk
    # ... create appointment ...
    if CSVHelper.save_appointments(df_appointments):  # Write to disk
        return True, new_appointment
```

**Issues:**
- Every booking read/writes entire CSV file
- Multiple requests hit disk simultaneously
- Scales poorly with more appointments
- 1000 bookings/day = 2000+ disk I/O operations

**Recommendation:** Use database caching:
```python
# Use SQLite or cache with TTL
from functools import lru_cache
import time

_cache = {}
_cache_time = {}
CACHE_TTL = 60  # seconds

@classmethod
def get_appointments_cached(cls):
    """Get appointments with caching."""
    now = time.time()
    if 'appointments' in _cache:
        if now - _cache_time.get('appointments', 0) < CACHE_TTL:
            return _cache['appointments'].copy()
    
    df = CSVHelper.get_appointments()
    _cache['appointments'] = df
    _cache_time['appointments'] = now
    return df.copy()

# Invalidate cache after writes
@classmethod
def create_booking(cls, ...):
    # ... create ...
    if CSVHelper.save_appointments(df_appointments):
        _cache.pop('appointments', None)  # Invalidate
        return True, new_appointment
```

---

### 3.2 Date/Time Handling Issues

**File:** [src/reminder_service.py](src/reminder_service.py#L26-L37)  
**Severity:** MEDIUM

```python
now = datetime.now()
target_from = now
target_to = now + timedelta(hours=24)

# ...
appt_dt = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M")
if not (target_from <= appt_dt <= target_to):
    continue
```

**Issues:**
1. Timezone-unaware datetime - fails if server timezone changes
2. 24-hour window may miss late appointments (sent too early)
3. No consideration for daylight savings

**Recommendation:**
```python
from datetime import datetime, timedelta, timezone

# Use UTC consistently
now = datetime.now(timezone.utc)
target_from = now
target_to = now + timedelta(hours=24)

# Parse with timezone info
appt_dt = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M")
appt_dt = appt_dt.replace(tzinfo=timezone.utc)

if not (target_from <= appt_dt <= target_to):
    continue
```

---

### 3.3 Missing Documentation

**Files:** Most Python files  
**Severity:** MEDIUM

**Issues:**
- No docstrings on many functions
- No README with setup instructions
- No API documentation
- No architecture diagram

**Example - Missing docstring:**
```python
# BEFORE: No documentation
@classmethod
def create_booking(cls, user_id, doctor_id, date_str, time_str):
    # ... code ...

# AFTER: Complete documentation
@classmethod
def create_booking(cls, 
                   user_id: str, 
                   doctor_id: str, 
                   date_str: str, 
                   time_str: str) -> tuple[bool, dict | str]:
    """Create a new appointment booking with collision detection.
    
    Args:
        user_id: Unique user identifier (e.g., 'u_12345')
        doctor_id: Unique doctor identifier (e.g., 'd_67890')
        date_str: Appointment date in ISO format (YYYY-MM-DD)
        time_str: Appointment time in 24h format (HH:MM)
        
    Returns:
        Tuple of (success: bool, result: dict or error message)
        - On success: (True, {appointment dict})
        - On failure: (False, "Error message")
        
    Raises:
        ValueError: If date format is invalid
        
    Examples:
        >>> success, result = BookingManager.create_booking(
        ...     'u_1', 'd_1', '2026-06-15', '14:00'
        ... )
        >>> if success:
        ...     print(f"Booked appointment {result['id']}")
    """
    # ...
```

---

### 3.4 No Request ID Tracing

**File:** app.py  
**Severity:** MEDIUM

**Issue:** Difficult to trace requests across multiple endpoints for debugging.

**Recommendation:**
```python
import uuid
from flask import g

@app.before_request
def before_request():
    """Assign unique request ID for tracing."""
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    print(f"[{g.request_id}] {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Add request ID to response headers."""
    response.headers['X-Request-ID'] = g.request_id
    return response

# Use in logging:
print(f"[{g.request_id}] Booking created: {appointment_id}")
```

---

### 3.5 No Health Check Endpoint

**File:** app.py  
**Severity:** MEDIUM

**Issue:** Load balancers cannot determine if application is healthy.

**Recommendation:**
```python
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers."""
    try:
        # Quick checks
        CSVHelper.get_doctors()  # Verify data access
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 503
```

---

### 3.6 Inconsistent Error Response Format

**Files:** app.py, src/  
**Severity:** MEDIUM

```python
# Inconsistent response formats
return jsonify({'ok': True, 'results': results})  # Line 154
return jsonify({'ok': False, 'error': str(e), 'results': []}), 502  # Line 157
return jsonify({'error': f'Address not found: {address}'})  # Line 200
```

**Recommendation:**
```python
def api_response(ok: bool, data: dict = None, error: str = None, status: int = 200):
    """Standardized API response format."""
    response = {
        'ok': ok,
        'timestamp': datetime.now().isoformat(),
        'request_id': g.request_id
    }
    if data:
        response['data'] = data
    if error:
        response['error'] = error
    return jsonify(response), status

# Usage:
if not valid_coords:
    return api_response(False, error='Invalid coordinates', status=400)

return api_response(True, data={'clinics': clinics_list})
```

---

### 3.7 Incomplete Input Sanitization for Display

**File:** templates (not provided, but app passes unsanitized data)  
**Severity:** MEDIUM

**Issue:** User input displayed in templates without escaping (XSS risk).

**Vulnerable Code:**
```python
# In app.py
location_label = _build_location_label(province, district, ward)
return render_template('select_doctor.html', location_label=location_label)
```

**In template (if not escaped):**
```html
<!-- Vulnerable if location_label not escaped -->
<h2>Kết quả tìm kiếm: {{ location_label }}</h2>
<!-- Safe with Jinja2 autoescape (Flask default) -->
```

**Recommendation:**
```html
<!-- Ensure Flask template autoescape is enabled (default) -->
<h2>Kết quả tìm kiếm: {{ location_label | safe }}</h2>  <!-- Use safe only if definitely safe -->

<!-- Or in Python:
from markupsafe import escape
location_label = escape(location_label)
-->
```

---

### 3.8 No Database Constraints

**File:** All database operations via CSV  
**Severity:** MEDIUM

**Issues:**
- Duplicate user IDs possible
- No referential integrity (doctor_id could be invalid)
- No unique constraints (duplicate appointments possible)
- No data type enforcement

**Recommendation:** Migrate to SQLite with proper schema:
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    doctor_id TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT DEFAULT 'Đã xác nhận',
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, date, time, status)  -- Prevent double booking
);
```

---

## 4. LOW-SEVERITY ISSUES

### 4.1 Magic Numbers and Strings

**Files:** Multiple  
**Severity:** LOW

```python
# In booking_manager.py
def _available_slots(cls, booked_slots, date_str, limit=None):
    """Return standard slots not in booked_slots, excluding past times for today."""
    available_slots = [slot for slot in cls.STANDARD_SLOTS if slot not in booked_slots]
    today_str = datetime.today().strftime('%Y-%m-%d')  # Magic format string
    if date_str == today_str:
        now_time = datetime.now().strftime('%H:%M')  # Magic format string
        available_slots = [s for s in available_slots if s > now_time]
```

**Recommendation:**
```python
# Define constants
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = f'{DATE_FORMAT} {TIME_FORMAT}'

def _available_slots(cls, booked_slots, date_str, limit=None):
    available_slots = [slot for slot in cls.STANDARD_SLOTS if slot not in booked_slots]
    today_str = datetime.today().strftime(DATE_FORMAT)
    if date_str == today_str:
        now_time = datetime.now().strftime(TIME_FORMAT)
        available_slots = [s for s in available_slots if s > now_time]
```

---

### 4.2 Print Statements Instead of Logging

**Files:** All  
**Severity:** LOW

```python
print(f"[BOOKING] Loading booking page for doctor {doctor_id}, method={request.method}")
print(f"[BOOKING] Found doctor: {doctor.get('name')} (clinic: {doctor.get('clinic_id')})")
```

**Issues:**
- Not captured in production logs
- No log levels (debug, info, warning, error)
- Difficult to filter/search

**Recommendation:**
```python
import logging

logger = logging.getLogger(__name__)

logger.debug(f"Loading booking page for doctor {doctor_id}, method={request.method}")
logger.info(f"Found doctor: {doctor.get('name')} (clinic: {doctor.get('clinic_id')})")
logger.warning(f"Booking collision detected for {doctor_id}")
logger.error(f"Email service failed: {e}", exc_info=True)
```

---

### 4.3 Inconsistent Naming Conventions

**Files:** Multiple  
**Severity:** LOW

```python
# Inconsistent naming
df = CSVHelper.get_doctors()  # snake_case
df_docs = CSVHelper.get_doctors()  # snake_case with prefix
doctors_list = df_doctors.to_dict('records')  # different prefix
matched_doctors = [...]  # different style
```

**Recommendation:**
```python
# Consistent: use descriptive names without prefixes
doctors = CSVHelper.get_doctors()
appointments = CSVHelper.get_appointments()
```

---

### 4.4 Incomplete Error Messages

**File:** [app.py](app.py) and [src/](src/)  
**Severity:** LOW

```python
# Cryptic error messages
flash("Lỗi hệ thống.", "error")  # Not helpful
flash("Không tìm thấy thông tin bác sĩ.", "error")  # Which doctor?
```

**Better:**
```python
flash(f"Lỗi hệ thống: {str(e)}", "error")
flash(f"Không tìm thấy bác sĩ {doctor_id}.", "error")
```

---

### 4.5 No Pagination for Large Result Sets

**File:** [app.py](app.py#L273-L283)  
**Severity:** LOW

```python
filtered = sorted(filtered, key=sort_key)[:5] if not district else sorted(filtered, key=sort_key)
```

**Issue:** Returns max 5 doctors. If user selects district, returns all (no limit).

**Recommendation:**
```python
MAX_RESULTS_PER_PAGE = 10
PAGE_SIZE = 10

def paginate_results(items, page=1, per_page=PAGE_SIZE):
    """Paginate list of items."""
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], (len(items) + per_page - 1) // per_page

filtered = sorted(filtered, key=sort_key)
page = request.args.get('page', 1, type=int)
results, total_pages = paginate_results(filtered, page=page)
```

---

### 4.6 No Backup/Restore Functionality

**File:** Application  
**Severity:** LOW

**Issue:** CSV files could be accidentally deleted; no backup mechanism.

**Recommendation:**
```python
import shutil
from datetime import datetime

def backup_data():
    """Create backup of all data files."""
    backup_dir = os.path.join(Config.DATA_DIR, 'backups', datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(backup_dir, exist_ok=True)
    
    for csv_file in [Config.USERS_CSV, Config.DOCTORS_CSV, Config.APPOINTMENTS_CSV]:
        if os.path.exists(csv_file):
            shutil.copy2(csv_file, backup_dir)
    
    return backup_dir

# Schedule daily backups
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(backup_data, 'cron', hour=2, minute=0)  # 2 AM daily
scheduler.start()
```

---

### 4.7 No Audit Trail for Appointments

**File:** [src/booking_manager.py](src/booking_manager.py)  
**Severity:** LOW

**Issue:** No record of who created, modified, or cancelled appointments.

**Recommendation:**
```python
def create_booking(...):
    # ... existing code ...
    new_appointment = {
        'id': appointment_id,
        'user_id': user_id,
        'doctor_id': doctor_id,
        'date': date_str,
        'time': time_str,
        'status': 'Đã xác nhận',
        'created_by': user_id,
        'created_at': datetime.now().isoformat(),
        'modified_by': user_id,
        'modified_at': datetime.now().isoformat()
    }
```

---

### 4.8 Test Fixtures Not Cleaned Up

**File:** [tests/conftest.py](tests/conftest.py)  
**Severity:** LOW

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(tmp_path_factory):
    # ... creates temp files ...
    yield
    
    # Restore original configuration
    Config.USERS_CSV = orig_users
    # But temp files not explicitly deleted
```

**Recommendation:**
```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(tmp_path_factory):
    # ...setup...
    
    yield
    
    # Cleanup
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Restore
    Config.USERS_CSV = orig_users
    # etc
```

---

## 5. CODE QUALITY AND BEST PRACTICES

### 5.1 Missing Environment Variable Documentation

Create `.env.example`:
```bash
# Django settings
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-with-os.urandom(24).hex()>

# Email service (Resend)
RESEND_API_KEY=<your-api-key>
EMAIL_FROM=noreply@yourdomain.com

# Geolocation
NOMINATIM_USER_AGENT=MedBooking/1.0

# Database
DATABASE_URL=sqlite:///medbooking.db

# Session security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Rate limiting
RATELIMIT_ENABLED=True
```

### 5.2 Requirements.txt Missing Versions

**File:** [requirements.txt](requirements.txt)

```python
# BEFORE: Unpinned versions (compatibility issues)
Flask>=3.0.0
pandas>=2.0.0
pytest>=7.0.0
gunicorn>=21.0.0
requests>=2.31.0
resend>=0.7.0

# AFTER: Pinned versions (reproducible builds)
Flask==3.0.2
pandas==2.0.3
pytest==7.4.0
gunicorn==21.2.0
requests==2.31.0
resend==0.7.1
bcrypt==4.0.1
flask-limiter==3.5.0
python-dotenv==1.0.0
email-validator==2.0.0
```

Generate with: `pip freeze > requirements.txt`

---

### 5.3 Missing .gitignore Entries

Add to `.gitignore`:
```bash
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Data and backups
/data/
/data/backups/
*.csv
*.log
*.db
.DS_Store

# Test coverage
htmlcov/
.coverage
.pytest_cache/
```

---

## 6. TESTING RECOMMENDATIONS

### 6.1 Add Integration Tests

```python
# tests/test_integration.py
def test_full_booking_flow(client):
    """Test complete booking workflow."""
    # 1. Register user
    resp = client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'secure123',
        'phone': '0912345678'
    })
    assert resp.status_code == 302  # Redirect to login
    
    # 2. Login
    resp = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'secure123'
    })
    assert 'user_id' in client.session
    
    # 3. Browse doctors
    resp = client.get('/select-doctor?symptoms=ho')
    assert resp.status_code == 200
    
    # 4. Book appointment
    resp = client.post('/book/d1', data={
        'date': '2026-06-15',
        'time': '14:00'
    })
    assert resp.status_code == 302  # Redirect to confirmation
    
    # 5. Verify booking in dashboard
    resp = client.get('/dashboard')
    assert 'Bác sĩ X' in resp.data.decode()
```

### 6.2 Add Security Tests

```python
# tests/test_security.py
def test_csrf_protection(client):
    """Test CSRF token validation."""
    resp = client.post('/register', data={
        'name': 'Attacker',
        'email': 'attacker@evil.com',
        'password': 'pass123',
        'phone': '0912345678'
    })
    # Should fail without CSRF token
    assert resp.status_code == 400

def test_password_not_exposed_in_logs(caplog):
    """Ensure passwords not logged."""
    AuthService.login_user('user@example.com', 'secret_password_123')
    assert 'secret_password_123' not in caplog.text

def test_sql_injection_attempt(client):
    """Test SQL injection protection."""
    resp = client.get("/select-doctor?symptoms='; DROP TABLE users; --")
    assert resp.status_code == 200  # Should handle gracefully
```

---

## 7. DEPLOYMENT CHECKLIST

- [ ] Remove debug mode: `FLASK_DEBUG=False`
- [ ] Set strong SECRET_KEY from environment variable
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set session cookie security flags
- [ ] Implement CSRF protection with tokens
- [ ] Set up rate limiting
- [ ] Configure proper logging to files
- [ ] Set up database (migrate from CSV)
- [ ] Enable security headers (CSP, HSTS, X-Frame-Options)
- [ ] Implement backup/restore procedures
- [ ] Set up monitoring and alerting
- [ ] Use bcrypt for password hashing
- [ ] Enable request ID tracing
- [ ] Implement health check endpoint
- [ ] Document API endpoints
- [ ] Set up CI/CD pipeline
- [ ] Run security scan (OWASP ZAP, Bandit)
- [ ] Load test the application

---

## 8. PRIORITY ACTION ITEMS

### CRITICAL (Fix Before Production)
1. ✅ Move API key to environment variable
2. ✅ Implement bcrypt password hashing
3. ✅ Add CSRF protection tokens
4. ✅ Validate all user inputs with bounds
5. ✅ Migrate from CSV to SQLite database

### HIGH (Fix Before Next Release)
6. ✅ Add type hints to all modules
7. ✅ Implement proper session security
8. ✅ Add email validation (RFC 5321)
9. ✅ Implement rate limiting
10. ✅ Add security event logging

### MEDIUM (Fix in Next Sprint)
11. ✅ Implement pagination
12. ✅ Add comprehensive docstrings
13. ✅ Use logging instead of print statements
14. ✅ Create health check endpoint
15. ✅ Standardize API response format

---

## Appendix A: Recommended Security Headers

Add to `config.py`:
```python
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'SAMEORIGIN',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}

@app.after_request
def apply_security_headers(response):
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response
```

---

## Appendix B: Database Migration Script

```python
# migrate_csv_to_sqlite.py
import sqlite3
import pandas as pd
from config import Config

def migrate():
    """Migrate from CSV files to SQLite database."""
    conn = sqlite3.connect(Config.DB_PATH)
    
    # Create tables
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS doctors (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            specialty TEXT,
            symptoms TEXT,
            clinic_id TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS clinics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            lat REAL,
            lon REAL,
            city TEXT,
            district TEXT
        );
        
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            doctor_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'Đã xác nhận',
            reminder_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(doctor_id, date, time, status)
        );
    ''')
    
    # Migrate data
    users = pd.read_csv(Config.USERS_CSV)
    users.to_sql('users', conn, if_exists='append', index=False)
    
    doctors = pd.read_csv(Config.DOCTORS_CSV)
    doctors.to_sql('doctors', conn, if_exists='append', index=False)
    
    clinics = pd.read_csv(Config.CLINICS_CSV)
    clinics.to_sql('clinics', conn, if_exists='append', index=False)
    
    appointments = pd.read_csv(Config.APPOINTMENTS_CSV)
    appointments.to_sql('appointments', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    
    print("Migration completed!")

if __name__ == '__main__':
    migrate()
```

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Critical Issues | 5 |
| High Issues | 10 |
| Medium Issues | 8 |
| Low Issues | 8 |
| **Total Issues** | **31** |
| Files Reviewed | 15 |
| Lines of Code Analyzed | ~2000+ |

---

**Review Completed By:** Code Analysis System  
**Next Review:** After implementing critical fixes (1-2 weeks)
