import pytest
from fastapi import status


def test_user_registration_and_login(client):
    # 1. Register User A
    register_payload = {
        "full_name": "Alice Security",
        "email": "alice@security.com",
        "password": "SecretPassword123!"
    }
    response = client.post("/api/auth/register", json=register_payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

    # 2. Login User A
    login_payload = {
        "email": "alice@security.com",
        "password": "SecretPassword123!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == status.HTTP_200_OK
    login_data = response.json()
    assert login_data["data"]["email"] == "alice@security.com"
    token = login_data["data"]["access_token"]

    # 3. Access Profile
    headers = {"Authorization": f"Bearer {token}"}
    profile_res = client.get("/api/auth/profile", headers=headers)
    assert profile_res.status_code == status.HTTP_200_OK
    assert profile_res.json()["data"]["full_name"] == "Alice Security"


def test_idor_protection(client):
    # Register & Login User A
    reg_a = client.post("/api/auth/register", json={"full_name": "User A", "email": "usera@test.com", "password": "Password123!"})
    token_a = reg_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register & Login User B
    reg_b = client.post("/api/auth/register", json={"full_name": "User B", "email": "userb@test.com", "password": "Password123!"})
    token_b = reg_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates an assessment
    assess_payload = {
        "glucose": 135.0,
        "blood_pressure": 82.0,
        "bmi": 29.5,
        "age": 42
    }
    res_a = client.post("/api/assessment", json=assess_payload, headers=headers_a)
    assert res_a.status_code == status.HTTP_201_CREATED
    assessment_id_a = res_a.json()["data"]["id"]

    # User B attempts to access User A's assessment by ID (IDOR Attempt)
    idor_res = client.get(f"/api/assessment/{assessment_id_a}", headers=headers_b)
    # Must return 404/403 Access Denied
    assert idor_res.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
