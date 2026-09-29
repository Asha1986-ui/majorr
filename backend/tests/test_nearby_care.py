import sys
import os

# Add parent directory to sys.path so app modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.nearby_care_service import NearbyCareService, calculate_haversine_distance
from app.config.database import SessionLocal, init_db
from app.models.user import User
from app.config.security import create_access_token, hash_password
from fastapi.testclient import TestClient
from app.main import app

def test_haversine():
    print("--> Testing Haversine Distance Formula...")
    # Bangalore (12.9716, 77.5946) to Whitefield (12.9698, 77.7500) ~ 16.8 km
    dist = calculate_haversine_distance(12.9716, 77.5946, 12.9698, 77.7500)
    print(f"    Calculated distance: {dist} km")
    assert 14.0 <= dist <= 19.0, f"Distance out of expected range: {dist}"
    print("    [PASS] Haversine calculation verified.")

def test_geocoding():
    print("--> Testing Nominatim Geocoding...")
    service = NearbyCareService()
    res = service.geocode_location("Bangalore")
    assert res is not None, "Geocoding returned None"
    print(f"    Resolved Bangalore: lat={res.latitude}, lon={res.longitude}, name={res.display_name}")
    assert 12.0 <= res.latitude <= 14.0, f"Unexpected latitude: {res.latitude}"
    assert 76.5 <= res.longitude <= 78.5, f"Unexpected longitude: {res.longitude}"
    print("    [PASS] Geocoding verified.")

def test_nearby_hospitals():
    print("--> Testing Nearby Hospitals Query (Real OSM Overpass)...")
    service = NearbyCareService()
    # Bangalore coordinates: 12.9716, 77.5946, radius 5km
    res = service.get_nearby_facilities(12.9716, 77.5946, facility_type="hospital", radius_meters=5000)
    print(f"    Found {res.total_count} hospitals/clinics.")
    assert res.total_count > 0, "No hospitals returned from real place query"
    first = res.facilities[0]
    print(f"    Top nearest hospital: {first.name} ({first.distance} km away)")
    print(f"    Address: {first.address}")
    print(f"    Maps URL: {first.maps_url}")
    assert first.latitude is not None and first.longitude is not None
    assert first.distance >= 0
    assert "https://www.google.com/maps/dir/" in first.maps_url
    print("    [PASS] Nearby hospitals query verified.")

def test_nearby_laboratories():
    print("--> Testing Nearby Diagnostic Laboratories Query (Real OSM Overpass)...")
    service = NearbyCareService()
    # Bangalore coordinates: 12.9716, 77.5946, radius 6km
    res = service.get_nearby_facilities(12.9716, 77.5946, facility_type="laboratory", radius_meters=6000)
    print(f"    Found {res.total_count} diagnostic labs.")
    assert res.total_count > 0, "No diagnostic labs returned from real place query"
    first = res.facilities[0]
    print(f"    Top nearest lab: {first.name} ({first.distance} km away)")
    print(f"    Type: {first.type}")
    print(f"    Address: {first.address}")
    assert first.latitude is not None and first.longitude is not None
    print("    [PASS] Nearby diagnostic labs query verified.")

def test_api_endpoints():
    print("--> Testing FastAPI Endpoints for Protected Auth...")
    init_db()
    db = SessionLocal()

    # Create test user if not exists
    test_email = "care_test_user@diasense.ai"
    user = db.query(User).filter(User.email == test_email).first()
    if not user:
        user = User(
            full_name="Care Test User",
            email=test_email,
            password=hash_password("CareTest@1234"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.email})
    client = TestClient(app)

    # 1. Unauthenticated request should fail with 401
    unauth_res = client.get("/api/nearby-care?latitude=12.9716&longitude=77.5946")
    print(f"    Unauthenticated status: {unauth_res.status_code}")
    assert unauth_res.status_code == 401, f"Expected 401 but got {unauth_res.status_code}"
    print("    [PASS] Unauthenticated access blocked.")

    # 2. Authenticated request
    auth_headers = {"Authorization": f"Bearer {token}"}
    auth_res = client.get(
        "/api/nearby-care?latitude=12.9716&longitude=77.5946&type=hospital&radius=5000",
        headers=auth_headers,
    )
    print(f"    Authenticated status: {auth_res.status_code}")
    assert auth_res.status_code == 200, f"Expected 200 but got {auth_res.status_code}"
    data = auth_res.json()
    assert data["success"] is True
    assert "facilities" in data["data"]
    print(f"    API returned {len(data['data']['facilities'])} facilities.")
    print("    [PASS] Authenticated endpoint verified.")

    # 3. Geocode endpoint
    geo_res = client.get("/api/nearby-care/geocode?query=Bangalore", headers=auth_headers)
    assert geo_res.status_code == 200
    geo_data = geo_res.json()
    assert geo_data["success"] is True
    print(f"    Geocoded via API: {geo_data['data']['display_name']}")
    print("    [PASS] Geocode endpoint verified.")

    db.close()

if __name__ == "__main__":
    print("==================================================")
    print(" Running DiaSense AI Nearby Care Verification Suite")
    print("==================================================")
    test_haversine()
    test_geocoding()
    test_nearby_hospitals()
    test_nearby_laboratories()
    test_api_endpoints()
    print("==================================================")
    print(" ALL VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")
