"""
Geolocation Testing Tool for Clinic Location Accuracy
Allows testing user location detection and distance calculations with real Vietnamese addresses.
"""

import sys
import json
import os
from typing import Dict, List, Tuple, Optional
from src.geocoding_service import GeocodingService
from src.distance_calculator import DistanceCalculator
from src.csv_helper import CSVHelper


class GeolocationTester:
    """Tool for testing geolocation and calculating distances to clinics."""
    
    def __init__(self):
        self.geocoder = GeocodingService()
        self.distance_calc = DistanceCalculator()
        self.csv_helper = CSVHelper()
        
    def locate_address(self, address: str) -> Optional[Dict]:
        """
        Locate a Vietnamese address and return coordinates.
        
        Args:
            address: Vietnamese address string (e.g., "12 Nguyễn Huệ, Hanoi")
            
        Returns:
            Dict with keys: lat, lon, formatted_address, province
        """
        print(f"\n📍 Locating address: {address}")
        
        try:
            results = self.geocoder.search(address)
            
            if not results:
                print("❌ Address not found")
                return None
            
            result = results[0]
            lat = float(result.get('lat'))
            lon = float(result.get('lon'))
            formatted = result.get('display_name', address)
            
            # Try to extract province
            province = self._extract_province(result)
            
            location = {
                'lat': lat,
                'lon': lon,
                'address': formatted,
                'province': province
            }
            
            print(f"✅ Found: {formatted}")
            print(f"   Coordinates: ({lat:.4f}, {lon:.4f})")
            if province:
                print(f"   Province: {province}")
            
            return location
            
        except Exception as e:
            print(f"❌ Error locating address: {str(e)}")
            return None
    
    def find_nearby_clinics(self, user_location: Dict, 
                           max_distance_km: float = 15) -> List[Dict]:
        """
        Find clinics near a user location with distances.
        
        Args:
            user_location: Dict with 'lat' and 'lon' keys
            max_distance_km: Maximum distance to search
            
        Returns:
            List of clinics with calculated distances
        """
        print(f"\n🏥 Finding clinics within {max_distance_km} km...")
        
        try:
            # Get clinics with distances
            clinics_with_distance = self.distance_calc.get_clinics_with_distance(
                user_lat=user_location['lat'],
                user_lon=user_location['lon'],
                max_radius_km=max_distance_km
            )
            
            # Sort by distance
            clinics_with_distance.sort(key=lambda x: x.get('distance', float('inf')))
            
            print(f"✅ Found {len(clinics_with_distance)} clinics nearby:")
            
            for i, clinic in enumerate(clinics_with_distance[:10], 1):  # Show top 10
                try:
                    distance = float(clinic.get('distance', 0))
                except (ValueError, TypeError):
                    distance = 0
                name = clinic.get('name', 'Unknown')
                address = clinic.get('address', 'N/A')
                print(f"   {i}. {name} - {distance:.2f} km")
                print(f"      📍 {address}")
            
            if len(clinics_with_distance) > 10:
                print(f"   ... and {len(clinics_with_distance) - 10} more clinics")
            
            return clinics_with_distance
            
        except Exception as e:
            print(f"❌ Error finding clinics: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def test_distance_calculation(self, lat1: float, lon1: float, 
                                  lat2: float, lon2: float) -> Dict:
        """
        Test distance calculation between two points.
        
        Args:
            lat1, lon1: User coordinates
            lat2, lon2: Clinic coordinates
            
        Returns:
            Dict with distance info
        """
        print(f"\n📏 Calculating distance...")
        print(f"   From: ({lat1:.4f}, {lon1:.4f})")
        print(f"   To:   ({lat2:.4f}, {lon2:.4f})")
        
        try:
            distance = self.distance_calc.haversine(lat1, lon1, lat2, lon2)
            print(f"   ✅ Distance: {distance:.2f} km")
            
            return {
                'distance_km': distance,
                'from': {'lat': lat1, 'lon': lon1},
                'to': {'lat': lat2, 'lon': lon2}
            }
        except Exception as e:
            print(f"❌ Error calculating distance: {str(e)}")
            return None
    
    def test_user_to_clinics(self, address: str, max_distance_km: float = 15) -> Dict:
        """
        Complete test: locate user address → find nearby clinics → show distances.
        
        Args:
            address: Vietnamese address to test
            max_distance_km: Maximum search distance
            
        Returns:
            Test results summary
        """
        print("\n" + "="*60)
        print("🧪 GEOLOCATION TEST")
        print("="*60)
        
        # Step 1: Locate the address
        user_location = self.locate_address(address)
        if not user_location:
            return {'success': False, 'error': 'Could not locate address'}
        
        # Step 2: Find nearby clinics
        nearby_clinics = self.find_nearby_clinics(user_location, max_distance_km)
        
        # Step 3: Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"User Address:      {user_location['address']}")
        print(f"User Coordinates:  ({user_location['lat']:.4f}, {user_location['lon']:.4f})")
        print(f"Province:          {user_location.get('province', 'Unknown')}")
        print(f"Clinics Found:     {len(nearby_clinics)}")
        
        if nearby_clinics:
            closest = nearby_clinics[0]
            try:
                distance = float(closest.get('distance', 0))
            except (ValueError, TypeError):
                distance = 0
            print(f"\n🏆 Closest Clinic:")
            print(f"   Name:     {closest.get('name', 'N/A')}")
            print(f"   Distance: {distance:.2f} km")
            print(f"   Address:  {closest.get('address', 'N/A')}")
        
        return {
            'success': True,
            'user_location': user_location,
            'clinics_found': len(nearby_clinics),
            'nearest_clinic': nearby_clinics[0] if nearby_clinics else None,
            'all_clinics': nearby_clinics
        }
    
    def _extract_province(self, geocode_result: Dict) -> Optional[str]:
        """Extract Vietnamese province name from geocoding result."""
        try:
            # Try to get province from address components
            address_parts = geocode_result.get('address', {})
            
            # Check common province keys
            for key in ['province', 'state', 'county']:
                if key in address_parts:
                    return address_parts[key]
            
            # Try parsing from display_name
            display_name = geocode_result.get('display_name', '')
            parts = display_name.split(',')
            if len(parts) >= 2:
                return parts[-2].strip()
            
            return None
        except:
            return None


def main():
    """Command-line interface for geolocation testing."""
    tester = GeolocationTester()
    
    if len(sys.argv) < 2:
        print("🧪 Geolocation Tester - Test address location and clinic distances\n")
        print("Usage:")
        print("  python -m src.geolocation_tester 'Address in Vietnam'")
        print("  python -m src.geolocation_tester 'Address' --max-distance 20")
        print("\nExamples:")
        print("  python -m src.geolocation_tester 'Bệnh viện Việt Đức, Hanoi'")
        print("  python -m src.geolocation_tester '12 Nguyễn Huệ, Hanoi' --max-distance 10")
        print("  python -m src.geolocation_tester 'Saigon Square, Ho Chi Minh'")
        return
    
    address = sys.argv[1]
    max_distance = 15
    
    # Parse optional max-distance argument
    if '--max-distance' in sys.argv:
        try:
            idx = sys.argv.index('--max-distance')
            max_distance = float(sys.argv[idx + 1])
        except:
            pass
    
    # Run test
    result = tester.test_user_to_clinics(address, max_distance)
    
    # Output JSON for programmatic use
    if '--json' in sys.argv:
        print("\n📦 JSON Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
