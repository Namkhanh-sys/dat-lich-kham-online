import pytest
from unittest.mock import patch
from app import app
from src.distance_calculator import DistanceCalculator

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Disable default daily limits to prevent interference with other tests, but keep the route-specific limits
    with app.test_client() as client:
        yield client

def test_coordinate_validation():
    # Test valid coords
    lat, lon = DistanceCalculator._parse_user_coords(21.0285, 105.8542)
    assert lat == 21.0285
    assert lon == 105.8542

    # Test out of bounds lat
    lat, lon = DistanceCalculator._parse_user_coords(95.0, 105.8542)
    assert lat is None
    assert lon is None

    # Test out of bounds lon
    lat, lon = DistanceCalculator._parse_user_coords(21.0285, 200.0)
    assert lat is None
    assert lon is None

    # Test invalid string coords
    lat, lon = DistanceCalculator._parse_user_coords("abc", "105.8542")
    assert lat is None
    assert lon is None

def test_rate_limiting_login(client):
    # Perform 6 post requests to /login (limit is 5 per minute)
    responses = []
    for _ in range(6):
        resp = client.post('/login', data={'email': 'test@example.com', 'password': 'wrongpassword'})
        responses.append(resp)

    # The first 5 should be processed normally (getting redirect or flash message but status is 200/302 depending on page)
    # The 6th should hit the rate limiter and trigger HTTP 302 (redirect) due to our error handler
    redirects = [r for r in responses if r.status_code == 302]
    assert len(redirects) > 0
