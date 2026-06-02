import math
import re
from src.csv_helper import CSVHelper

# Vùng địa lý (bounding box) để suy ra thành phố từ GPS khi không chọn tỉnh
CITY_BOUNDS = {
    'Hà Nội': {'lat_min': 20.85, 'lat_max': 21.25, 'lon_min': 105.65, 'lon_max': 106.05},
    'TP. Hồ Chí Minh': {'lat_min': 10.55, 'lat_max': 11.05, 'lon_min': 106.35, 'lon_max': 106.95},
    'Đà Nẵng': {'lat_min': 15.95, 'lat_max': 16.20, 'lon_min': 108.10, 'lon_max': 108.35},
    'Cần Thơ': {'lat_min': 9.90, 'lat_max': 10.20, 'lon_min': 105.60, 'lon_max': 105.90},
}

# Chuẩn hóa tên tỉnh/thành từ dropdown hoặc Nominatim → city trong clinics.csv
PROVINCE_ALIASES = {
    'ha noi': 'Hà Nội',
    'thanh pho ha noi': 'Hà Nội',
    'hanoi': 'Hà Nội',
    'tp ho chi minh': 'TP. Hồ Chí Minh',
    'thanh pho ho chi minh': 'TP. Hồ Chí Minh',
    'ho chi minh': 'TP. Hồ Chí Minh',
    'hcm': 'TP. Hồ Chí Minh',
    'sai gon': 'TP. Hồ Chí Minh',
    'da nang': 'Đà Nẵng',
    'can tho': 'Cần Thơ',
}


class DistanceCalculator:
    @staticmethod
    def _parse_user_coords(user_lat, user_lon):
        """Return (lat, lon) floats or (None, None) when coordinates are missing/invalid."""
        if user_lat is None or user_lon is None:
            return None, None
        if isinstance(user_lat, str) and not user_lat.strip():
            return None, None
        if isinstance(user_lon, str) and not user_lon.strip():
            return None, None
        try:
            return float(user_lat), float(user_lon)
        except (ValueError, TypeError):
            return None, None

    @classmethod
    def _normalize_text(cls, text):
        if not text:
            return ''
        text = text.lower().strip()
        text = re.sub(r'[đĐ]', 'd', text)
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    @classmethod
    def resolve_user_city(cls, user_lat, user_lon, province=None):
        """Xác định thành phố/khu vực của người dùng từ tỉnh chọn hoặc tọa độ GPS."""
        if province:
            key = cls._normalize_text(province)
            for alias, city in PROVINCE_ALIASES.items():
                if alias in key or key in alias:
                    return city
            for city in CITY_BOUNDS:
                if cls._normalize_text(city) in key or key in cls._normalize_text(city):
                    return city

        parsed_lat, parsed_lon = cls._parse_user_coords(user_lat, user_lon)
        if parsed_lat is None:
            return None

        for city, bounds in CITY_BOUNDS.items():
            if (bounds['lat_min'] <= parsed_lat <= bounds['lat_max'] and
                    bounds['lon_min'] <= parsed_lon <= bounds['lon_max']):
                return city
        return None

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """Khoảng cách đường chim bay (km) giữa hai điểm GPS."""
        try:
            lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        except (ValueError, TypeError):
            return 9999.0

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return round(c * 6371.0, 2)

    @classmethod
    def _enrich_clinic(cls, clinic, parsed_lat, parsed_lon):
        """Gắn khoảng cách thật từ tọa độ người dùng đến phòng khám (tọa độ CSV)."""
        clinic = dict(clinic)
        clinic['lat'] = float(clinic.get('lat', 0))
        clinic['lon'] = float(clinic.get('lon', 0))
        clinic['city'] = clinic.get('city', '').strip() or cls._city_from_address(clinic.get('address', ''))

        if parsed_lat is not None and parsed_lon is not None:
            clinic['distance_km'] = cls.haversine(
                parsed_lat, parsed_lon, clinic['lat'], clinic['lon']
            )
        else:
            clinic['distance_km'] = 9999.0
        return clinic

    @classmethod
    def _city_from_address(cls, address):
        """Suy ra thành phố từ địa chỉ phòng khám nếu thiếu cột city."""
        addr = cls._normalize_text(address)
        if 'ha noi' in addr or 'hanoi' in addr:
            return 'Hà Nội'
        if 'ho chi minh' in addr or 'hcm' in addr or 'tp hcm' in addr:
            return 'TP. Hồ Chí Minh'
        if 'da nang' in addr:
            return 'Đà Nẵng'
        if 'can tho' in addr:
            return 'Cần Thơ'
        return ''

    @classmethod
    def get_clinics_with_distance(cls, user_lat, user_lon, province=None, district=None, ward=None,
                                  prefer_city=None, max_radius_km=None):
        """
        Trả về danh sách phòng khám với địa chỉ/tọa độ THẬT từ CSV và khoảng cách Haversine thật.
        district/ward giữ để tương thích API; không ghi đè địa chỉ phòng khám.
        """
        df_clinics = CSVHelper.get_clinics()
        if df_clinics.empty:
            return []

        parsed_lat, parsed_lon = cls._parse_user_coords(user_lat, user_lon)
        user_city = prefer_city or cls.resolve_user_city(user_lat, user_lon, province)

        clinics_list = []
        for row in df_clinics.to_dict('records'):
            clinic = cls._enrich_clinic(row, parsed_lat, parsed_lon)
            clinic['in_user_city'] = bool(user_city and clinic.get('city') == user_city)
            clinics_list.append(clinic)

        if user_city:
            in_city = [c for c in clinics_list if c['in_user_city']]
            pool = in_city if in_city else clinics_list
        else:
            pool = clinics_list

        if max_radius_km is not None and parsed_lat is not None:
            pool = [c for c in pool if c['distance_km'] <= max_radius_km]

        return sorted(pool, key=lambda x: x['distance_km'])

    @classmethod
    def get_clinic_details(cls, clinic_id, user_lat=None, user_lon=None, province=None, district=None, ward=None):
        """Chi tiết một phòng khám — địa chỉ và tọa độ thật, khoảng cách tính từ vị trí người dùng."""
        df_clinics = CSVHelper.get_clinics()
        cid_str = str(clinic_id).strip()
        clinic_row = df_clinics[df_clinics['id'].str.strip() == cid_str]
        if clinic_row.empty:
            return {
                "id": clinic_id,
                "name": "Phòng khám chưa xác định",
                "address": "Chưa có địa chỉ",
                "lat": 0.0,
                "lon": 0.0,
                "city": "",
                "distance_km": 9999.0,
            }

        parsed_lat, parsed_lon = cls._parse_user_coords(user_lat, user_lon)
        return cls._enrich_clinic(clinic_row.iloc[0].to_dict(), parsed_lat, parsed_lon)

    @classmethod
    def filter_doctors_by_region(cls, doctors, clinics_dict, user_lat, user_lon, province=None,
                               max_distance_km=150):
        """
        Ưu tiên bác sĩ thuộc phòng khám cùng thành phố hoặc trong bán kính hợp lý.
        Trả về (doctors_filtered, user_city, region_note).
        """
        user_city = cls.resolve_user_city(user_lat, user_lon, province)
        note = None

        def attach_and_check(doc):
            cid = str(doc.get('clinic_id', '')).strip()
            clinic = clinics_dict.get(cid, {})
            doc = dict(doc)
            doc['clinic_name'] = clinic.get('name', 'Phòng khám chưa xác định')
            doc['clinic_address'] = clinic.get('address', 'Chưa có địa chỉ')
            doc['distance_km'] = clinic.get('distance_km', 9999.0)
            doc['clinic_city'] = clinic.get('city', '')
            return doc

        enriched = [attach_and_check(d) for d in doctors]

        if user_city:
            same_city = [d for d in enriched if d.get('clinic_city') == user_city and d.get('distance_km', 9999) <= max_distance_km]
            if same_city:
                return same_city, user_city, None
            note = (
                f"Không có phòng khám tại {user_city} trong vòng {max_distance_km} km. "
                f"Hiển thị phòng khám gần nhất theo khoảng cách thực tế."
            )

        nearby = [d for d in enriched if d.get('distance_km', 9999) <= max_distance_km]
        if nearby:
            return nearby, user_city, note

        return [], user_city, note or f"Không có phòng khám trong vòng {max_distance_km} km từ vị trí của bạn."
