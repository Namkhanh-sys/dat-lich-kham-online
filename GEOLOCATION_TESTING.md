# 🧪 Geolocation Testing Tools

A comprehensive testing suite for accurately detecting user coordinates and calculating distances to clinic locations using graph algorithms and geographic mathematics.

## 📋 Overview

This tool provides multiple ways to test and verify geolocation accuracy:

1. **Command-Line Tool** - Test from terminal with Vietnamese addresses
2. **Debug API Endpoints** - Test via HTTP requests
3. **Python API** - Use directly in your code

---

## 🛠️ Using the Command-Line Tool

### Basic Usage

```bash
# Test a Vietnamese address with 15 km clinic search (default)
python -m src.geolocation_tester "Bệnh viện Việt Đức, Hanoi"

# Specify custom search radius
python -m src.geolocation_tester "12 Nguyễn Huệ, Hanoi" --max-distance 20

# Get output as JSON
python -m src.geolocation_tester "Saigon Square, Ho Chi Minh" --json
```

### Examples

**Test Hanoi location:**
```bash
python -m src.geolocation_tester "Hà Nội"
```

**Output:**
```
============================================================
🧪 GEOLOCATION TEST
============================================================

📍 Locating address: Hà Nội
✅ Found: Hà Nội, Việt Nam
   Coordinates: (21.0285, 105.8542)
   Province: Hà Nội

🏥 Finding clinics within 15 km...
✅ Found 8 clinics nearby:
   1. Bệnh viện Việt Đức - 2.34 km
      📍 193A Tràng Thi, Hà Nội
   2. Bệnh viện Bạch Mai - 4.12 km
      📍 78 Giải Phóng, Hà Nội
   ... and 6 more clinics

============================================================
📊 TEST SUMMARY
============================================================
User Address:      Hà Nội, Việt Nam
User Coordinates:  (21.0285, 105.8542)
Province:          Hà Nội
Clinics Found:     8

🏆 Closest Clinic:
   Name:     Bệnh viện Việt Đức
   Distance: 2.34 km
   Address:  193A Tràng Thi, Hà Nội
```

**Test specific clinic:**
```bash
python -m src.geolocation_tester "Bệnh viện Việt Đức, Hanoi" --max-distance 10
```

**Test Ho Chi Minh area with extended radius:**
```bash
python -m src.geolocation_tester "Ho Chi Minh City" --max-distance 30
```

---

## 🌐 Using the Debug API Endpoints

Make sure Flask is running:
```bash
python app.py
```

### 1. Test Geolocation (`/api/debug/geolocation`)

**GET Request:**
```bash
curl "http://localhost:5000/api/debug/geolocation?address=Hanoi&max_distance=15"
```

**POST Request:**
```bash
curl -X POST http://localhost:5000/api/debug/geolocation \
  -H "Content-Type: application/json" \
  -d '{
    "address": "12 Nguyễn Huệ, Hanoi",
    "max_distance": 20
  }'
```

**Response:**
```json
{
  "ok": true,
  "user_location": {
    "lat": 21.0285,
    "lon": 105.8542,
    "address": "Hà Nội, Việt Nam"
  },
  "clinics_count": 8,
  "max_distance_km": 15,
  "nearest_clinic": {
    "name": "Bệnh viện Việt Đức",
    "address": "193A Tràng Thi, Hà Nội",
    "distance": 2.34,
    "lat": 21.0125,
    "lon": 105.8531
  },
  "all_clinics": [...]
}
```

### 2. Calculate Distance (`/api/debug/distance`)

**GET Request:**
```bash
# From Hanoi to Ho Chi Minh (distance calculation)
curl "http://localhost:5000/api/debug/distance?from_lat=21.0285&from_lon=105.8542&to_lat=10.8231&to_lon=106.6297"
```

**POST Request:**
```bash
curl -X POST http://localhost:5000/api/debug/distance \
  -H "Content-Type: application/json" \
  -d '{
    "from_lat": 21.0285,
    "from_lon": 105.8542,
    "to_lat": 10.8231,
    "to_lon": 106.6297
  }'
```

**Response:**
```json
{
  "ok": true,
  "distance_km": 1203.84,
  "from": {
    "lat": 21.0285,
    "lon": 105.8542
  },
  "to": {
    "lat": 10.8231,
    "lon": 106.6297
  }
}
```

### 3. Find Clinics Near Address (`/api/debug/clinics-near-address`)

**GET Request:**
```bash
curl "http://localhost:5000/api/debug/clinics-near-address?address=Ha%20Noi&max_distance=10&limit=5"
```

**POST Request:**
```bash
curl -X POST http://localhost:5000/api/debug/clinics-near-address \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Hà Nội",
    "max_distance": 10,
    "limit": 5
  }'
```

**Response:**
```json
{
  "ok": true,
  "search_address": "Hà Nội, Việt Nam",
  "user_coordinates": {
    "lat": 21.0285,
    "lon": 105.8542
  },
  "clinics_count": 5,
  "max_distance_km": 10,
  "clinics": [
    {
      "name": "Bệnh viện Việt Đức",
      "address": "193A Tràng Thi, Hà Nội",
      "distance": 2.34,
      "lat": 21.0125,
      "lon": 105.8531
    },
    ...
  ]
}
```

---

## 🐍 Using the Python API

```python
from src.geolocation_tester import GeolocationTester

tester = GeolocationTester()

# Test 1: Locate an address
location = tester.locate_address("Bệnh viện Việt Đức, Hanoi")
print(f"Address: {location['address']}")
print(f"Coordinates: ({location['lat']}, {location['lon']})")

# Test 2: Find nearby clinics
clinics = tester.find_nearby_clinics(location, max_distance_km=15)
for clinic in clinics:
    print(f"{clinic['name']}: {clinic['distance']:.2f} km away")

# Test 3: Calculate distance
result = tester.test_distance_calculation(
    lat1=21.0285, lon1=105.8542,  # Hanoi
    lat2=10.8231, lon2=106.6297   # Ho Chi Minh
)
print(f"Distance: {result['distance_km']:.2f} km")

# Test 4: Complete test (address → clinics)
test_result = tester.test_user_to_clinics("Ha Noi", max_distance_km=20)
print(f"Clinics found: {test_result['clinics_found']}")
```

---

## 🎯 Distance Calculation Algorithm

The tool uses the **Haversine formula** to calculate great-circle distances between two geographic points:

$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

Where:
- $R$ = Earth's radius (6,371 km)
- $\phi$ = latitude
- $\lambda$ = longitude
- $\Delta\phi$, $\Delta\lambda$ = differences in coordinates

This formula provides accurate distance calculations for geographic coordinates.

---

## 📊 How it Works

### 1. **Address Geocoding**
   - Takes Vietnamese address as input
   - Uses Nominatim (OpenStreetMap) API to find coordinates
   - Validates result is in Vietnam (country_code check)
   - Returns: latitude, longitude, formatted address, province

### 2. **Clinic Finding**
   - Loads all clinics from CSV with their stored coordinates
   - Calculates distance from user to each clinic using Haversine formula
   - Filters clinics within specified radius
   - Sorts by distance (closest first)
   - Returns: clinic name, address, distance, coordinates

### 3. **Graph & Mathematical Processing**
   - **Graph Structure**: Clinics form nodes in geographic space
   - **Distance Calculation**: Uses spherical geometry (Haversine)
   - **Filtering**: Spatial filtering to find clinics within radius
   - **Sorting**: Graph traversal ordered by distance

---

## 🧪 Testing Scenarios

### Scenario 1: Verify Hanoi Geolocation
```bash
python -m src.geolocation_tester "Hà Nội"
```
✅ Should show coordinates: (21.0285, 105.8542)
✅ Should find clinics in Hanoi area
❌ Should NOT show Ho Chi Minh City location

### Scenario 2: Test Specific Clinic
```bash
python -m src.geolocation_tester "Bệnh viện Việt Đức, Hanoi" --max-distance 5
```
✅ Should show clinic location
✅ Should show nearby clinics

### Scenario 3: Test Distance Calculation
```bash
curl "http://localhost:5000/api/debug/distance?from_lat=21.0285&from_lon=105.8542&to_lat=21.0125&to_lon=105.8531"
```
✅ Should show distance ~2-3 km (nearby clinics)

### Scenario 4: Multi-City Test
```bash
python -m src.geolocation_tester "Ho Chi Minh" --max-distance 30
python -m src.geolocation_tester "Da Nang" --max-distance 20
python -m src.geolocation_tester "Can Tho" --max-distance 15
```
✅ Each should show correct city coordinates and nearby clinics

---

## 📝 CLI Options Reference

```
Usage:
  python -m src.geolocation_tester 'Vietnamese Address' [OPTIONS]

Options:
  --max-distance NUM  Maximum search distance in km (default: 15)
  --json             Output results as JSON (for programmatic use)

Examples:
  python -m src.geolocation_tester 'Hanoi'
  python -m src.geolocation_tester 'Bệnh viện Việt Đức' --max-distance 20
  python -m src.geolocation_tester 'Ho Chi Minh' --json
```

---

## 🔍 Debugging Tips

If address not found:
- Ensure address is in Vietnamese
- Try including province/city name
- Check spelling (Vietnamese has diacritics)
- Example: "Hanoi" → "Hà Nội"

If distance seems wrong:
- Verify coordinates are in decimal format
- Check that coordinates are within Vietnam
- Latitude range: 8° to 24°N
- Longitude range: 102° to 109°E

If no clinics found:
- Check max_distance is sufficient
- Verify clinic data in `data/clinics.csv`
- Ensure clinics have valid latitude/longitude
- Try increasing radius: `--max-distance 30`

---

## 📦 Dependencies

Required packages (should already be installed):
- `requests` - HTTP requests for Nominatim API
- `pandas` - CSV data handling
- `geopy` - Geographic calculations

---

## ⚠️ Development Only

Debug endpoints are only available when:
- Flask is running in debug mode (`app.debug = True`)
- OR `FLASK_ENV=development` environment variable is set

These endpoints will NOT be available in production.

---

## 🎓 Use Cases

1. **Local Development**: Test your clinic data and distance calculations
2. **QA Testing**: Verify geolocation works for different Vietnamese cities
3. **Data Analysis**: Batch test multiple addresses
4. **Integration Testing**: Use CLI or API in automated tests
5. **Debugging**: Identify why specific addresses aren't being found correctly

