"""
Debug endpoints for testing geolocation, distance calculations, and email.
Only available in development mode.
"""

from flask import Blueprint, request, jsonify
from src.geocoding_service import GeocodingService
from src.distance_calculator import DistanceCalculator
from src.email_service import EmailService

debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')

geocoder = GeocodingService()
distance_calc = DistanceCalculator()


@debug_bp.route('/geolocation', methods=['GET', 'POST'])
def test_geolocation():
    """
    Test geolocation with a Vietnamese address.
    
    Query params or JSON:
      - address: Vietnamese address to locate
      - max_distance: Max distance to clinics (default: 15 km)
      
    Example:
      GET /api/debug/geolocation?address=Bệnh viện Việt Đức, Hanoi&max_distance=10
    """
    try:
        # Get parameters
        if request.method == 'POST':
            data = request.get_json() or {}
            address = data.get('address')
            max_distance = float(data.get('max_distance', 15))
        else:
            address = request.args.get('address')
            max_distance = float(request.args.get('max_distance', 15))
        
        if not address:
            return jsonify({
                'ok': False,
                'error': 'Missing parameter: address'
            }), 400
        
        # Step 1: Search for address
        results = geocoder.search(address)
        if not results:
            return jsonify({
                'ok': False,
                'error': f'Address not found: {address}',
                'search_query': address
            }), 404
        
        result = results[0]
        user_lat = float(result.get('lat'))
        user_lon = float(result.get('lon'))
        user_address = result.get('display_name', address)
        
        # Step 2: Get nearby clinics
        clinics_with_distance = distance_calc.get_clinics_with_distance(
            user_lat=user_lat,
            user_lon=user_lon,
            max_radius_km=max_distance
        )
        
        # Sort by distance
        clinics_with_distance.sort(key=lambda x: float(x.get('distance', float('inf'))))
        
        return jsonify({
            'ok': True,
            'user_location': {
                'lat': user_lat,
                'lon': user_lon,
                'address': user_address
            },
            'clinics_count': len(clinics_with_distance),
            'max_distance_km': max_distance,
            'nearest_clinic': clinics_with_distance[0] if clinics_with_distance else None,
            'all_clinics': clinics_with_distance[:20]  # Top 20
        })
        
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@debug_bp.route('/distance', methods=['GET', 'POST'])
def test_distance():
    """
    Test distance calculation between two coordinates.
    
    Query params or JSON:
      - from_lat, from_lon: User coordinates
      - to_lat, to_lon: Target coordinates
      
    Example:
      GET /api/debug/distance?from_lat=21.0285&from_lon=105.8542&to_lat=10.8231&to_lon=106.6297
    """
    try:
        # Get parameters
        if request.method == 'POST':
            data = request.get_json() or {}
            from_lat = float(data.get('from_lat'))
            from_lon = float(data.get('from_lon'))
            to_lat = float(data.get('to_lat'))
            to_lon = float(data.get('to_lon'))
        else:
            from_lat = float(request.args.get('from_lat'))
            from_lon = float(request.args.get('from_lon'))
            to_lat = float(request.args.get('to_lat'))
            to_lon = float(request.args.get('to_lon'))
        
        # Calculate distance
        distance_km = distance_calc.haversine(from_lat, from_lon, to_lat, to_lon)
        
        return jsonify({
            'ok': True,
            'distance_km': round(distance_km, 2),
            'from': {
                'lat': from_lat,
                'lon': from_lon
            },
            'to': {
                'lat': to_lat,
                'lon': to_lon
            }
        })
        
    except ValueError as e:
        return jsonify({
            'ok': False,
            'error': f'Invalid coordinates: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@debug_bp.route('/clinics-near-address', methods=['GET', 'POST'])
def clinics_near_address():
    """
    Find clinics near a specific Vietnamese address.
    
    Query params or JSON:
      - address: Vietnamese address
      - max_distance: Max distance in km (default: 15)
      - limit: Max clinics to return (default: 20)
      
    Example:
      GET /api/debug/clinics-near-address?address=Hà Nội&max_distance=10&limit=10
    """
    try:
        # Get parameters
        if request.method == 'POST':
            data = request.get_json() or {}
            address = data.get('address')
            max_distance = float(data.get('max_distance', 15))
            limit = int(data.get('limit', 20))
        else:
            address = request.args.get('address')
            max_distance = float(request.args.get('max_distance', 15))
            limit = int(request.args.get('limit', 20))
        
        if not address:
            return jsonify({
                'ok': False,
                'error': 'Missing parameter: address'
            }), 400
        
        # Search for address
        results = geocoder.search(address)
        if not results:
            return jsonify({
                'ok': False,
                'error': f'Address not found: {address}'
            }), 404
        
        result = results[0]
        user_lat = float(result.get('lat'))
        user_lon = float(result.get('lon'))
        user_address = result.get('display_name', address)
        
        # Find nearby clinics
        clinics_with_distance = distance_calc.get_clinics_with_distance(
            user_lat=user_lat,
            user_lon=user_lon,
            max_radius_km=max_distance
        )
        
        # Sort and limit
        clinics_with_distance.sort(key=lambda x: float(x.get('distance', float('inf'))))
        clinics_with_distance = clinics_with_distance[:limit]
        
        return jsonify({
            'ok': True,
            'search_address': user_address,
            'user_coordinates': {
                'lat': user_lat,
                'lon': user_lon
            },
            'clinics_count': len(clinics_with_distance),
            'max_distance_km': max_distance,
            'clinics': clinics_with_distance
        })
        
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@debug_bp.route('/send-test-email', methods=['POST'])
def send_test_email():
    """
    Test email sending via EmailJS.
    
    JSON payload:
      - to_email: Recipient email (required)
      - user_name: User name (default: "Test User")
      - doctor_name: Doctor name (default: "Dr. John Doe")
      - date_str: Appointment date (default: "2026-06-15")
      - time_str: Appointment time (default: "14:00")
      - clinic_name: Clinic name (default: "Clinic 1")
      - address: Clinic address (default: "123 Main St")
      
    Example:
      POST /api/debug/send-test-email
      {
        "to_email": "test@example.com",
        "user_name": "John",
        "doctor_name": "Dr. Smith"
      }
    """
    try:
        data = request.get_json() or {}
        
        to_email = data.get('to_email')
        if not to_email:
            return jsonify({
                'ok': False,
                'error': 'Missing required field: to_email'
            }), 400
        
        user_name = data.get('user_name', 'Test User')
        doctor_name = data.get('doctor_name', 'Dr. John Doe')
        date_str = data.get('date_str', '2026-06-15')
        time_str = data.get('time_str', '14:00')
        clinic_name = data.get('clinic_name', 'Clinic 1')
        address = data.get('address', '123 Main St')
        
        # Send email
        success, message = EmailService.send_booking_confirmation(
            user_email=to_email,
            user_name=user_name,
            doctor_name=doctor_name,
            date_str=date_str,
            time_str=time_str,
            clinic_name=clinic_name,
            address=address
        )
        
        return jsonify({
            'ok': success,
            'message': message,
            'to_email': to_email,
            'user_name': user_name,
            'doctor_name': doctor_name,
            'date_str': date_str,
            'time_str': time_str,
            'clinic_name': clinic_name,
            'address': address
        }), 200 if success else 400
        
    except Exception as e:
        import traceback
        return jsonify({
            'ok': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
