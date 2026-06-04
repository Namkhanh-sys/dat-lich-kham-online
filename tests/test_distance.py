import pytest
from src.distance_calculator import DistanceCalculator

def test_haversine_formula():
    # Distance between Hoan Kiem (21.0285, 105.8542) and Hoan Kiem clinic (21.0278, 105.8523)
    dist = DistanceCalculator.haversine(21.0285, 105.8542, 21.0278, 105.8523)
    # Around ~0.21 kilometers
    assert dist > 0.0
    assert dist < 1.0
    
    # Distance to itself should be 0
    assert DistanceCalculator.haversine(21.0, 105.0, 21.0, 105.0) == 0.0

    # Handling of bad input types
    assert DistanceCalculator.haversine("bad", "input", 21.0, 105.0) == 9999.0

def test_get_clinics_with_distance():
    # Retrieve clinics sorted by distance from Hoan Kiem lake (Hà Nội)
    clinics = DistanceCalculator.get_clinics_with_distance(21.0285, 105.8542, province='Hà Nội')
    assert len(clinics) >= 2

    # Real addresses from CSV — not fake generated street names
    assert 'Nguyễn Trãi' not in clinics[0]['address']
    assert clinics[0]['distance_km'] < 5.0

    # Check that they are sorted by distance
    assert clinics[0]['distance_km'] <= clinics[1]['distance_km']
    assert 'distance_km' in clinics[0]

def test_resolve_user_city_and_region_filter():
    city = DistanceCalculator.resolve_user_city(21.0285, 105.8542, 'Hà Nội')
    assert city == 'Hà Nội'

    clinics = DistanceCalculator.get_clinics_with_distance(
        21.0285, 105.8542, province='Hà Nội', prefer_city='Hà Nội'
    )
    assert all(c.get('city') == 'Hà Nội' for c in clinics)

def test_get_clinics_with_distance_filters_by_district():
    clinics = DistanceCalculator.get_clinics_with_distance(
        21.0285, 105.8542, province='HÃ  Ná»™i', district='Quáº­n HoÃ n Kiáº¿m'
    )

    assert len(clinics) == 1
    assert clinics[0]['id'] == 'c1'

def test_zero_coordinates_not_treated_as_missing():
    """Bug Fix #4: latitude/longitude of 0.0 should be valid coordinates,
    not falsy/missing — distance should be computed, not defaulted to 9999."""
    clinics = DistanceCalculator.get_clinics_with_distance(0.0, 0.0)
    assert len(clinics) >= 1
    for c in clinics:
        assert c['distance_km'] != 9999.0, (
            f"Clinic {c.get('id')} got distance_km=9999 — zero-coord was treated as None!"
        )

def test_invalid_coords_do_not_crash():
    """Empty or invalid coordinate strings should not raise ValueError."""
    clinic = DistanceCalculator.get_clinic_details('c1', '', '')
    assert clinic['distance_km'] == 9999.0

    clinic2 = DistanceCalculator.get_clinic_details('c1', 'not-a-number', 'also-bad')
    assert clinic2['distance_km'] == 9999.0
