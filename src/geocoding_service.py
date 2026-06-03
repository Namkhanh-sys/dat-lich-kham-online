import json
import urllib.parse
import urllib.request
from config import Config


class GeocodingService:
    """Proxy Nominatim (OpenStreetMap) với User-Agent hợp lệ — ổn định hơn gọi trực tiếp từ trình duyệt."""

    BASE_URL = 'https://nominatim.openstreetmap.org'
    _cache = {}

    @classmethod
    def _fetch(cls, path, params):
        params = dict(params)
        params.setdefault('format', 'json')
        params.setdefault('accept-language', 'vi')
        cache_key = (path, tuple(sorted(params.items())))
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        url = f"{cls.BASE_URL}/{path}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': Config.NOMINATIM_USER_AGENT},
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            cls._cache[cache_key] = data
            return data

    @classmethod
    def search(cls, query, limit=5):
        if not query or not str(query).strip():
            return []
        q = str(query).strip()
        if 'việt nam' not in q.lower() and 'viet nam' not in q.lower():
            q = f"{q}, Việt Nam"
        return cls._fetch('search', {
            'q': q,
            'limit': limit,
            'addressdetails': 1,
            'countrycodes': 'vn',
        })

    @classmethod
    def reverse(cls, lat, lon):
        try:
            lat_f, lon_f = float(lat), float(lon)
        except (ValueError, TypeError):
            return None
        return cls._fetch('reverse', {
            'lat': lat_f,
            'lon': lon_f,
            'addressdetails': 1,
            'zoom': 18,
        })
