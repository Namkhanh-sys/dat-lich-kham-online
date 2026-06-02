import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.csv_helper import CSVHelper
from src.distance_calculator import DistanceCalculator

# Test reading clinics
clinics = CSVHelper.get_clinics()
print("=== CLINICS ===")
for _, row in clinics.iterrows():
    print(f"  id='{row['id']}' lat={row['lat']} lon={row['lon']}")

# Test reading doctors
docs = CSVHelper.get_doctors()
print()
print("=== DOCTORS (id, clinic_id) ===")
for _, row in docs.iterrows():
    print(f"  id='{row['id']}' clinic_id='{row['clinic_id']}'")

# Test distance calculation
user_lat, user_lon = 21.0115, 105.8505
clinics_list = DistanceCalculator.get_clinics_with_distance(user_lat, user_lon)
clinics_dict = {str(c['id']).strip(): c for c in clinics_list}
print()
print("=== CLINICS DICT KEYS ===")
print(list(clinics_dict.keys()))

# Test matching per doctor
print()
print("=== MATCHING RESULT ===")
for doc in docs.to_dict('records'):
    cid = str(doc.get('clinic_id', '')).strip()
    found = cid in clinics_dict
    dist = clinics_dict[cid]['distance_km'] if found else 9999.0
    print(f"{doc['id']} cid='{cid}' found={found} dist={dist}")
