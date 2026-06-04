import os
import sys
import io

# Force UTF-8 encoding for Windows console to prevent charmap errors
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import datetime as dt
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import Config
from src.auth_service import AuthService
from src.csv_helper import CSVHelper
from src.distance_calculator import DistanceCalculator
from src.symptom_matcher import SymptomMatcher
from src.booking_manager import BookingManager
from src.email_service import EmailService
from src.reminder_service import ReminderService
from src.geocoding_service import GeocodingService
from src.pricing import Pricing
from src.debug_routes import debug_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register debug routes only when explicitly enabled.
if app.debug or Config.ENABLE_DEBUG_ROUTES:
    app.register_blueprint(debug_bp)

# Helper function to check login
def is_logged_in():
    return 'user_id' in session

# BUG FIX #7: Validate that the 'next' redirect target is internal to prevent Open Redirect attacks
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def _parse_location_args():
    """Đọc và chuẩn hóa tham số vị trí từ request. Hỗ trợ debug mode."""
    lat = request.values.get('lat', '').strip()
    lon = request.values.get('lon', '').strip()
    province = request.values.get('province', '').strip()
    district = request.values.get('district', '').strip()
    ward = request.values.get('ward', '').strip()
    location_source = request.values.get('location_source', '').strip()
    debug = request.values.get('debug', '').lower() == 'true'
    
    try:
        user_lat = float(lat)
        user_lon = float(lon)
        valid_coords = True
    except (ValueError, TypeError):
        user_lat = None
        user_lon = None
        valid_coords = False

    # DEBUG MODE: Nếu debug=true, cho phép bypass GPS check
    if debug:
        valid_coords = True
        if not user_lat or not user_lon:
            # Dùng tọa độ quận nếu có
            LOCATION_HIERARCHY = {
                'Hà Nội': {
                    'Quận Ba Đình': { 'lat': 21.0450, 'lon': 105.8350 },
                    'Quận Hoàn Kiếm': { 'lat': 21.0283, 'lon': 105.8542 },
                    'Quận Đống Đa': { 'lat': 21.0200, 'lon': 105.8500 },
                },
                'TP. Hồ Chí Minh': {
                    'Quận 1': { 'lat': 10.7700, 'lon': 106.7000 },
                    'Quận 3': { 'lat': 10.7850, 'lon': 106.6750 },
                }
            }
            if province and district and province in LOCATION_HIERARCHY and district in LOCATION_HIERARCHY[province]:
                coords = LOCATION_HIERARCHY[province][district]
                user_lat = coords['lat']
                user_lon = coords['lon']

    if not valid_coords and (province or district):
        # Fallback: try geocoding administrative address server-side if coordinates were not supplied
        address_query = ', '.join(filter(None, [district, province, 'Việt Nam']))
        try:
            results = GeocodingService.search(address_query, limit=1)
            if results:
                user_lat = float(results[0].get('lat', 0))
                user_lon = float(results[0].get('lon', 0))
                valid_coords = True
        except Exception:
            pass

    return user_lat, user_lon, province, district, ward, valid_coords, location_source


def _clean_clinic_address(address: str) -> str:
    """Remove trailing city names (Hà Nội, TP. Hồ Chí Minh, etc.) from clinic address."""
    import re
    if not address:
        return address
    # Strip trailing commas/spaces then remove trailing city variants
    addr = address.strip().rstrip(',').strip()
    city_patterns = [
        r',?\s*TP\.?\s*Hồ\s*Chí\s*Minh$',
        r',?\s*Thành\s*phố\s*Hồ\s*Chí\s*Minh$',
        r',?\s*Hồ\s*Chí\s*Minh$',
        r',?\s*Hà\s*Nội$',
        r',?\s*TP\.?\s*HCM$',
    ]
    for pattern in city_patterns:
        addr = re.sub(pattern, '', addr, flags=re.IGNORECASE).strip().rstrip(',').strip()
    return addr


def _build_location_label(province, district, ward):
    if ward and district and province:
        return f"{ward}, {district}, {province}"
    if district and province:
        return f"{district}, {province}"
    if province:
        return province
    return ""


def _prepare_doctors_with_real_distance(
    matched_docs, user_lat, user_lon, province, district, ward,
    max_distance_km=150, strict_region=False
):
    """Gắn phòng khám thật, khoảng cách Haversine thật, lọc theo khu vực, ưu tiên quận."""
    user_city = DistanceCalculator.resolve_user_city(user_lat, user_lon, province)
    clinics_list = DistanceCalculator.get_clinics_with_distance(
        user_lat, user_lon, province=province, district=district, prefer_city=user_city
    )

    if strict_region:
        if district:
            clinics_list = [c for c in clinics_list if c.get('district', '') == district]
        elif user_city:
            clinics_list = [c for c in clinics_list if c.get('city', '') == user_city]

    clinics_dict = {str(c['id']).strip(): c for c in clinics_list}
    if strict_region and clinics_dict:
        allowed_clinic_ids = set(clinics_dict.keys())
        matched_docs = [
            doc for doc in matched_docs
            if str(doc.get('clinic_id', '')).strip() in allowed_clinic_ids
        ]

    filtered, _, region_note = DistanceCalculator.filter_doctors_by_region(
        matched_docs, clinics_dict, user_lat, user_lon, province, max_distance_km=max_distance_km
    )

    all_info = CSVHelper.get_doctors_info()
    for doc in filtered:
        if doc['id'] in all_info:
            doc_info = all_info[doc['id']]
        else:
            doc_info = get_dynamic_doc_info(doc['id'], doc.get('name', ''), doc.get('specialty', ''), all_info.get('default', {}))
        doc['avatar'] = doc_info.get('avatar', '')
        doc['short_bio'] = doc_info.get('short_bio', '')
        doc['consultation_fee'] = Pricing.consultation_fee(doc['id'])
        doc['consultation_fee_display'] = Pricing.format_vnd(doc['consultation_fee'])
        # Clean up clinic address: remove trailing city name
        if 'clinic_address' in doc:
            doc['clinic_address'] = _clean_clinic_address(doc['clinic_address'])

    # If district is selected, filter doctors to only those from clinics in that district
    if district:
        district_clinics = [c for c in clinics_list if c.get('district', '') == district]
        district_clinic_ids = {str(c['id']).strip() for c in district_clinics}
        filtered = [doc for doc in filtered if str(doc.get('clinic_id', '')).strip() in district_clinic_ids]

    # Sort by: match_score desc, distance asc
    def sort_key(doc):
        score = -doc['match_score']  # Negative for descending
        distance = doc['distance_km']
        return (score, distance)
    
    filtered = sorted(filtered, key=sort_key)[:5] if not district else sorted(filtered, key=sort_key)
    return filtered, region_note


@app.route('/')
def index():
    diseases = CSVHelper.get_diseases()
    return render_template('index.html', diseases=diseases)


@app.route('/api/geocode/search')
def api_geocode_search():
    q = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 5)), 10)
    try:
        results = GeocodingService.search(q, limit=limit)
        return jsonify({'ok': True, 'results': results})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'results': []}), 502


@app.route('/api/geocode/reverse')
def api_geocode_reverse():
    lat = request.args.get('lat', '')
    lon = request.args.get('lon', '')
    try:
        data = GeocodingService.reverse(lat, lon)
        return jsonify({'ok': True, 'result': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'result': None}), 502


@app.route('/api/geolocation/by-ip')
def api_geolocation_by_ip():
    """Lấy vị trí từ địa chỉ IP của người dùng."""
    try:
        client_ip = request.remote_addr
        
        # Nếu là localhost (local testing), thử lấy IP từ header hoặc báo lỗi để frontend dùng Browser Geolocation API
        if client_ip.startswith('127.') or client_ip == 'localhost':
            x_forwarded = request.headers.get('X-Forwarded-For', '')
            if x_forwarded:
                client_ip = x_forwarded.split(',')[0].strip()
            else:
                # Không hardcode HCM - để frontend dùng Browser Geolocation API hoặc chọn thủ công
                return jsonify({
                    'ok': False,
                    'error': 'Developing locally. Please use browser geolocation or select location manually.',
                    'result': None
                }), 400
        
        import urllib.request
        import json as json_module
        
        # Sử dụng freegeoip.app - không giới hạn rate trên free tier
        url = f"https://freegeoip.app/json/{client_ip}"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'MedBooking/1.0'},
        )
        
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json_module.loads(resp.read().decode('utf-8'))
        
        if data.get('latitude') and data.get('longitude'):
            return jsonify({
                'ok': True,
                'result': {
                    'lat': float(data['latitude']),
                    'lon': float(data['longitude']),
                    'city': data.get('city', ''),
                    'region': data.get('region_name', ''),
                    'country': data.get('country_name', ''),
                }
            })
        else:
            return jsonify({'ok': False, 'error': 'Không lấy được tọa độ từ IP'}), 502
            
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'result': None}), 502


@app.route('/api/clinics/nearby')
def api_clinics_nearby():
    user_lat, user_lon, province, district, ward, valid, location_source = _parse_location_args()
    if not valid:
        return jsonify({'ok': False, 'error': 'Thiếu tọa độ hợp lệ', 'clinics': []}), 400
    max_km = request.args.get('max_km')
    max_radius = float(max_km) if max_km else None
    user_city = DistanceCalculator.resolve_user_city(user_lat, user_lon, province)
    clinics = DistanceCalculator.get_clinics_with_distance(
        user_lat, user_lon, province=province, district=district,
        prefer_city=user_city, max_radius_km=max_radius
    )
    return jsonify({'ok': True, 'clinics': clinics, 'user_city': user_city})


@app.route('/select-doctor')
def select_doctor():
    symptoms = request.args.get('symptoms', '').strip()
    user_lat, user_lon, province, district, ward, valid_coords, location_source = _parse_location_args()

    if not symptoms:
        flash("Vui lòng nhập triệu chứng để tìm kiếm bác sĩ phù hợp.", "warning")
        return redirect(url_for('index'))

    if not valid_coords:
        flash("Vui lòng xác định vị trí của bạn (GPS, tìm địa chỉ hoặc chọn trên bản đồ) trước khi tìm bác sĩ.", "warning")
        return redirect(url_for('index', symptoms=symptoms))

    matched_docs = SymptomMatcher.match_doctors_by_symptom(symptoms)
    strict_region = location_source in ('gps', 'ip', 'debug') and bool(province or district)
    matched_docs, region_note = _prepare_doctors_with_real_distance(
        matched_docs, user_lat, user_lon, province, district, ward,
        strict_region=strict_region
    )

    if region_note:
        flash(region_note, "warning")

    location_label = _build_location_label(province, district, ward)

    return render_template(
        'select_doctor.html',
        doctors=matched_docs,
        symptoms_query=symptoms,
        user_lat=user_lat,
        user_lon=user_lon,
        province=province,
        district=district,
        ward=ward,
        location_source=location_source,
        location_label=location_label
    )

@app.route('/disease/<disease_id>')
def disease_detail(disease_id):
    diseases = CSVHelper.get_diseases()
    disease = next((d for d in diseases if d['id'] == disease_id), None)
    if not disease:
        flash("Không tìm thấy thông tin bệnh lý.", "error")
        return redirect(url_for('index'))

    user_lat, user_lon, province, district, ward, valid_coords, location_source = _parse_location_args()

    if not valid_coords:
        flash("Vui lòng xác định vị trí của bạn trên trang chủ trước khi xem bác sĩ.", "warning")
        return redirect(url_for('index'))

    matched_docs = SymptomMatcher.match_doctors_by_symptom(disease['keywords'])
    strict_region = location_source in ('gps', 'ip', 'debug') and bool(province or district)
    matched_docs, region_note = _prepare_doctors_with_real_distance(
        matched_docs, user_lat, user_lon, province, district, ward,
        max_distance_km=20, strict_region=strict_region
    )

    if region_note:
        flash(region_note, "warning")

    location_label = _build_location_label(province, district, ward)
    
    # Get available districts from actual clinics in clinics.csv (not from hardcoded LOCATION_HIERARCHY)
    clinics = CSVHelper.get_clinics()
    available_districts = []
    if province:
        available_districts = sorted(list(set(
            clinics[(clinics['city'] == province)]['district'].tolist()
        )))
    available_districts = [d for d in available_districts if d.strip()]  # Remove empty/whitespace

    # Determine if location is from GPS/IP (accurate) vs manual selection
    is_gps_location = location_source in ('gps', 'ip', 'debug')

    return render_template(
        'disease_detail.html',
        disease=disease,
        doctors=matched_docs,
        user_lat=user_lat,
        user_lon=user_lon,
        province=province,
        district=district,
        ward=ward,
        location_source=location_source,
        location_label=location_label,
        available_districts=available_districts,
        current_district=district or '',
        debug_mode=request.values.get('debug', '').lower() == 'true',
        is_gps_location=is_gps_location
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        user = AuthService.login_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f"Đăng nhập thành công! Chào mừng {user['name']}.", "success")
            
            # Redirect to next page if specified — validate to prevent Open Redirect
            next_url = request.args.get('next')
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            flash("Email hoặc mật khẩu không chính xác.", "error")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        
        if not name or not email or not phone:
            flash("Vui lòng điền đầy đủ tên, email và số điện thoại.", "error")
            return render_template('register.html')
        if '@' not in email or '.' not in email:
            flash("Email không hợp lệ.", "error")
            return render_template('register.html')
        if len(password) < 6:
            flash("Mật khẩu phải dài tối thiểu 6 ký tự.", "error")
            return render_template('register.html')
            
        success, message = AuthService.register_user(name, email, password, phone)
        if success:
            flash(message + " Vui lòng đăng nhập.", "success")
            return redirect(url_for('login'))
        else:
            flash(message, "error")
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Bạn đã đăng xuất khỏi hệ thống thành công.", "success")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        flash("Vui lòng đăng nhập để xem lịch cá nhân.", "warning")
        return redirect(url_for('login', next=request.url))
        
    all_appointments = BookingManager.get_user_appointments(session['user_id'])
    # Only show active appointments (exclude cancelled ones)
    appointments = [a for a in all_appointments if a.get('status', '').strip() != 'Đã hủy']
    today_str = dt.date.today().strftime('%Y-%m-%d')
    return render_template('dashboard.html', appointments=appointments, today_str=today_str)

@app.route('/profile')
def profile():
    if not is_logged_in():
        flash("Vui lòng đăng nhập để xem thông tin hồ sơ.", "warning")
        return redirect(url_for('login', next=request.url))
        
    users = CSVHelper.get_users()
    user_row = users[users['id'] == session['user_id']]
    if user_row.empty:
        session.clear()
        flash("Người dùng không tồn tại.", "error")
        return redirect(url_for('login'))
        
    user = user_row.iloc[0].to_dict()
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
def profile_update():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()

    if not name or not phone:
        flash("Vui lòng nhập đầy đủ tên và số điện thoại.", "error")
        return redirect(url_for('profile'))
    
    success, message = AuthService.update_profile(session['user_id'], name, phone)
    if success:
        session['user_name'] = name
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
def change_password():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    old_password = request.form.get('old_password', '').strip()
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not old_password or not new_password or not confirm_password:
        flash("Vui lòng điền đầy đủ thông tin đổi mật khẩu.", "error")
        return redirect(url_for('profile'))

    if new_password != confirm_password:
        flash("Mật khẩu mới và mật khẩu xác nhận không khớp.", "error")
        return redirect(url_for('profile'))
        
    if len(new_password) < 6:
        flash("Mật khẩu mới phải dài tối thiểu 6 ký tự.", "error")
        return redirect(url_for('profile'))
        
    success, message = AuthService.change_password(session['user_id'], old_password, new_password)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('profile'))

def get_dynamic_doc_info(doctor_id, doctor_name, specialty, default_profile):
    import random
    import hashlib
    import copy
    
    # Deterministic random seed based on doctor_id so it stays the same on refresh
    seed = int(hashlib.md5(doctor_id.encode('utf-8')).hexdigest(), 16)
    random.seed(seed)
    
    info = copy.deepcopy(default_profile)
    
    # Dynamic avatar color (Vibrant professional palette)
    colors = ["2563eb", "059669", "dc2626", "d97706", "7c3aed", "db2777", "0284c7", "4f46e5"]
    color = random.choice(colors)
    
    # Extract the last word (first name) from the doctor's full name
    name_parts = doctor_name.strip().split()
    first_name = name_parts[-1] if name_parts else "BS"
    
    import urllib.parse
    enc_name = urllib.parse.quote(first_name)
    info['avatar'] = f"https://ui-avatars.com/api/?name={enc_name}&background={color}&color=fff&size=200&length=1"
    
    titles = [
        f"Chuyên gia y tế cấp cao - Tu nghiệp tại Singapore",
        f"Bác sĩ chuyên khoa {specialty} uy tín",
        f"Bác sĩ chuyên sâu về {specialty} - Từng tu nghiệp tại Pháp",
        f"Chuyên gia hàng đầu trong lĩnh vực {specialty}",
        f"Bác sĩ CKII với hơn 15 năm kinh nghiệm lâm sàng",
    ]
    info['short_bio'] = random.choice(titles) + "\n" + random.choice([
        "Hơn 20 năm kinh nghiệm khám chữa bệnh chuyên sâu",
        "Tận tâm chăm sóc sức khỏe cộng đồng",
        "Liên tục cập nhật phác đồ điều trị mới nhất",
        "Thường xuyên tham gia hội chẩn các ca bệnh khó"
    ])
    
    intros = [
        f"là một trong những bác sĩ hàng đầu về {specialty} với bề dày kinh nghiệm trong chẩn đoán và điều trị bệnh lý phức tạp. Bác sĩ luôn đặt y đức lên hàng đầu, liên tục cập nhật phác đồ điều trị tiên tiến.",
        f"là bác sĩ có chuyên môn sâu rộng trong khoa {specialty}. Với phương châm 'Lương y như từ mẫu', bác sĩ đã điều trị thành công cho hàng nghìn bệnh nhân và nhận được sự tin tưởng tuyệt đối từ cộng đồng.",
        f"hiện đang là chuyên gia y tế chuyên sâu về {specialty}. Bác sĩ luôn nỗ lực nghiên cứu và mang lại những giải pháp điều trị hiệu quả, an toàn nhất cho người bệnh.",
        f"là bác sĩ giàu kinh nghiệm điều trị các bệnh lý {specialty}. Bác sĩ luôn tận tình, lắng nghe và chia sẻ cùng bệnh nhân trong suốt quá trình thăm khám."
    ]
    info['intro'] = random.choice(intros)
    
    # Pick a subset to vary the lengths and items
    edus = default_profile.get('education', [])
    if len(edus) >= 3:
        info['education'] = random.sample(edus, k=random.randint(2, len(edus)))
        
    exps = default_profile.get('experience', [])
    if len(exps) >= 3:
        info['experience'] = random.sample(exps, k=random.randint(3, len(exps)))
        
    expsrt = default_profile.get('expertise', [])
    if len(expsrt) >= 3:
        info['expertise'] = random.sample(expsrt, k=random.randint(3, len(expsrt)))
        
    return info

@app.route('/doctor/<doctor_id>')
def doctor_detail(doctor_id):
    # Get basic info
    df_docs = CSVHelper.get_doctors()
    doc_row = df_docs[df_docs['id'] == doctor_id]
    if doc_row.empty:
        flash("Không tìm thấy thông tin bác sĩ.", "error")
        return redirect(url_for('index'))
        
    doctor = doc_row.iloc[0].to_dict()
    
    # Pass location params along
    lat = request.args.get('lat', '21.0285').strip()
    lon = request.args.get('lon', '105.8542').strip()
    province = request.args.get('province', '').strip()
    district = request.args.get('district', '').strip()
    ward = request.args.get('ward', '').strip()

    try:
        user_lat = float(lat)
        user_lon = float(lon)
    except ValueError:
        user_lat = 21.0285
        user_lon = 105.8542

    # Get clinic info
    clinic_id = str(doctor.get('clinic_id', '')).strip()
    clinic = DistanceCalculator.get_clinic_details(clinic_id, user_lat, user_lon, province, district, ward)
    doctor['clinic_name'] = clinic['name']
    doctor['clinic_address'] = _clean_clinic_address(clinic['address'])
    doctor['distance_km'] = clinic['distance_km'] if clinic['distance_km'] != 9999.0 else None

    # Get detailed info
    all_info = CSVHelper.get_doctors_info()
    if doctor_id in all_info:
        doc_info = all_info[doctor_id]
    else:
        doc_info = get_dynamic_doc_info(doctor_id, doctor['name'], doctor['specialty'], all_info.get('default', {}))
        
    doctor.update(doc_info)
    doctor['consultation_fee'] = Pricing.consultation_fee(doctor_id)
    doctor['consultation_fee_display'] = Pricing.format_vnd(doctor['consultation_fee'])

    return render_template(
        'doctor_detail.html',
        doctor=doctor,
        lat=user_lat,
        lon=user_lon,
        province=province,
        district=district,
        ward=ward
    )

@app.route('/book/<doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    try:
        if not is_logged_in():
            flash("Vui lòng đăng nhập trước khi thực hiện đặt lịch khám.", "warning")
            return redirect(url_for('login', next=request.url))

        print(f"[BOOKING] Loading booking page for doctor {doctor_id}, method={request.method}")
        
        # Load doctor details
        df_docs = CSVHelper.get_doctors()
        doc_row = df_docs[df_docs['id'] == doctor_id]
        if doc_row.empty:
            print(f"[BOOKING] Doctor {doctor_id} not found")
            flash("Không tìm thấy thông tin bác sĩ.", "error")
            return redirect(url_for('index'))
            
        doctor = doc_row.iloc[0].to_dict()
        print(f"[BOOKING] Found doctor: {doctor.get('name')} (clinic: {doctor.get('clinic_id')})")

        # Location params
        province = request.values.get('province', '').strip()
        district = request.values.get('district', '').strip()
        ward = request.values.get('ward', '').strip()
        location_label = f"{ward}, {district}, {province}".strip(', ') if (ward or district or province) else ''
        
        # Load clinic details to compute distance
        lat = request.values.get('lat', '21.0285').strip()
        lon = request.values.get('lon', '105.8542').strip()
        try:
            user_lat = float(lat)
            user_lon = float(lon)
        except ValueError:
            user_lat = 21.0285
            user_lon = 105.8542
        
        today_str = dt.date.today().strftime('%Y-%m-%d')
            
        clinic_id = str(doctor.get('clinic_id', '')).strip()
        print(f"[BOOKING] Loading clinic {clinic_id}")
        clinic = DistanceCalculator.get_clinic_details(clinic_id, user_lat, user_lon, province, district, ward)
        print(f"[BOOKING] Clinic loaded: {clinic.get('name')}")
        
        doctor['clinic_name'] = clinic['name']
        doctor['clinic_address'] = clinic['address']
        doctor['distance_km'] = clinic['distance_km']
        doctor['consultation_fee'] = Pricing.consultation_fee(doctor_id)
        doctor['consultation_fee_display'] = Pricing.format_vnd(doctor['consultation_fee'])

        if request.method == 'POST':
            appt_date = request.form.get('date', '').strip()
            appt_time = request.form.get('time', '').strip()
            pay_after_exam = request.form.get('pay_after_exam') == 'yes'
            if not pay_after_exam:
                flash("Vui lòng xác nhận thanh toán sau khi khám.", "error")
                return render_template(
                    'booking.html',
                    doctor=doctor,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    province=province,
                    district=district,
                    ward=ward,
                    location_label=location_label,
                    today_str=today_str,
                    selected_date=appt_date,
                    selected_time=appt_time,
                    collision_error=None,
                    alternatives=None
                )
            
            print(f"[BOOKING] POST request: user={session['user_id']}, doctor={doctor_id}, date={appt_date}, time={appt_time}")
            
            # Check collision and create booking
            success, result = BookingManager.create_booking(session['user_id'], doctor_id, appt_date, appt_time)
            print(f"[BOOKING] create_booking returned: success={success}, result={result}")
            
            if success:
                try:
                    # Send booking confirmation email
                    print(f"[BOOKING] Sending email to {session.get('user_email', 'unknown')}")
                    EmailService.send_booking_confirmation(
                        user_email=session['user_email'],
                        user_name=session['user_name'],
                        doctor_name=doctor['name'],
                        date_str=appt_date,
                        time_str=appt_time,
                        clinic_name=doctor['clinic_name'],
                        address=doctor['clinic_address'],
                        consultation_fee=doctor['consultation_fee_display'],
                        payment_note="Thanh toán sau khi khám"
                    )
                    print(f"[BOOKING] Email confirmation logged")
                except Exception as email_err:
                    print(f"[BOOKING] Notification error (non-blocking): {email_err}")
                
                flash("✓ Đặt lịch thành công! Chi tiết lịch hẹn đã được lưu.", "success")
                return redirect(url_for('confirmation', appointment_id=result['id']))
            else:
                collision_error = result
                alternatives = None
                if "bác sĩ đã có lịch hẹn" in result.lower():
                    alternatives = BookingManager.suggest_alternative_slots(doctor_id, appt_date)
                return render_template(
                    'booking.html',
                    doctor=doctor,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    province=province,
                    district=district,
                    ward=ward,
                    location_label=location_label,
                    today_str=today_str,
                    selected_date=appt_date,
                    selected_time=appt_time,
                    collision_error=collision_error,
                    alternatives=alternatives
                )
        
        # GET request - render booking form
        print(f"[BOOKING] Rendering GET page for doctor {doctor_id}")
        return render_template(
            'booking.html',
            doctor=doctor,
            user_lat=user_lat,
            user_lon=user_lon,
            province=province,
            district=district,
            ward=ward,
            location_label=location_label,
            today_str=today_str,
            selected_date=None,
            selected_time=None,
            collision_error=None,
            alternatives=None
        )
    
    except Exception as e:
        import traceback
        error_msg = f"[BOOKING_ERROR] {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        flash(f"Lỗi hệ thống: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/confirmation/<appointment_id>')
def confirmation(appointment_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    df_app = CSVHelper.get_appointments()
    app_row = df_app[(df_app['id'] == appointment_id) & (df_app['user_id'] == session['user_id'])]
    if app_row.empty:
        flash("Không tìm thấy thông tin lịch khám hoặc bạn không có quyền truy cập.", "error")
        return redirect(url_for('dashboard'))
        
    appointment = app_row.iloc[0].to_dict()
    
    # Load doctor details
    df_docs = CSVHelper.get_doctors()
    doc_row = df_docs[df_docs['id'] == appointment['doctor_id']]
    if doc_row.empty:
        flash("Không tìm thấy thông tin bác sĩ liên quan.", "error")
        return redirect(url_for('dashboard'))
        
    doctor = doc_row.iloc[0].to_dict()
    
    # Load clinic details
    clinics = CSVHelper.get_clinics()
    clinic_id = str(doctor.get('clinic_id', '')).strip()
    clinic_row = clinics[clinics['id'].str.strip() == clinic_id]
    if not clinic_row.empty:
        clinic = clinic_row.iloc[0].to_dict()
        doctor['clinic_name'] = clinic['name']
        doctor['clinic_address'] = clinic['address']
    else:
        doctor['clinic_name'] = "Phòng khám chưa xác định"
        doctor['clinic_address'] = "Chưa có địa chỉ"

    appointment['consultation_fee'] = Pricing.format_vnd(Pricing.consultation_fee(appointment['doctor_id']))
    appointment['payment_note'] = "Thanh toán sau khi khám"

    return render_template('confirmation.html', appointment=appointment, doctor=doctor)

@app.route('/cancel/<appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    print(f"[CANCEL] Request received for appointment_id={appointment_id}")
    if not is_logged_in():
        print(f"[CANCEL] User not logged in, redirecting")
        return redirect(url_for('login'))
        
    print(f"[CANCEL] User={session['user_id']}, cancelling appointment={appointment_id}")
    # Get doctor name and date/time before cancellation for notification
    df_app = CSVHelper.get_appointments()
    app_row = df_app[(df_app['id'] == appointment_id) & (df_app['user_id'] == session['user_id'])]
    if app_row.empty:
        print(f"[CANCEL] Appointment not found! Checking all appointments:")
        print(df_app[['id','user_id','status']].to_string())
        flash("Không tìm thấy thông tin lịch khám.", "error")
        return redirect(url_for('dashboard'))
        
    app_data = app_row.iloc[0].to_dict()
    df_docs = CSVHelper.get_doctors()
    doc_row = df_docs[df_docs['id'] == app_data['doctor_id']]
    doc_name = doc_row.iloc[0]['name'] if not doc_row.empty else "Bac si"
        
    success, message = BookingManager.cancel_booking(appointment_id, session['user_id'])
    print(f"[CANCEL] cancel_booking result: success={success}, message={message}")
    if success:
        try:
            EmailService.send_booking_cancellation(
                user_email=session['user_email'],
                user_name=session['user_name'],
                doctor_name=doc_name,
                date_str=app_data['date'],
                time_str=app_data['time']
            )
        except Exception as email_err:
            print(f"[CANCEL] Email error (non-blocking): {email_err}")
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('dashboard'))

@app.route('/confirm_payment/<appointment_id>', methods=['POST'])
def confirm_payment(appointment_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    success, message = BookingManager.confirm_payment(appointment_id, session['user_id'])
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('dashboard'))

@app.route('/reschedule/<appointment_id>', methods=['POST'])
def reschedule_appointment(appointment_id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    date = request.form.get('date', '').strip()
    time = request.form.get('time', '').strip()
    
    # Retrieve details for notification before rescheduling
    df_app = CSVHelper.get_appointments()
    app_row = df_app[(df_app['id'] == appointment_id) & (df_app['user_id'] == session['user_id'])]
    if app_row.empty:
        flash("Không tìm thấy thông tin lịch khám.", "error")
        return redirect(url_for('dashboard'))
        
    app_data = app_row.iloc[0].to_dict()
    
    success, message = BookingManager.update_booking_time(appointment_id, session['user_id'], date, time)
    if success:
        # Load doctor and clinic details for email
        df_docs = CSVHelper.get_doctors()
        doc_row = df_docs[df_docs['id'] == app_data['doctor_id']]
        doc = doc_row.iloc[0].to_dict() if not doc_row.empty else {}
        doc_name = doc.get('name', 'Bác sĩ')
        
        clinics = CSVHelper.get_clinics()
        clinic_id = str(doc.get('clinic_id', '')).strip()
        clinic_row = clinics[clinics['id'].str.strip() == clinic_id]
        clinic = clinic_row.iloc[0].to_dict() if not clinic_row.empty else {}
        clinic_name = clinic.get('name', 'Phòng khám')
        clinic_address = clinic.get('address', 'Địa chỉ')
        
        # Send update email notification
        EmailService.send_booking_update(
            user_email=session['user_email'],
            user_name=session['user_name'],
            doctor_name=doc_name,
            date_str=date,
            time_str=time,
            clinic_name=clinic_name,
            address=clinic_address
        )
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Ensure data files directory exists
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    # Start background service for appointment reminders (Requirement 6)
    ReminderService.start_background_task()
    
    # Run on 0.0.0.0 to allow access from other devices on the network
    # Use debug=False in production
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
