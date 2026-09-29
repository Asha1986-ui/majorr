def test_register_and_login_flow(client):
    # 1. Test Registration
    register_payload = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "Password123!",
        "age": 30,
        "gender": "Male",
    }
    reg_response = client.post("/api/auth/register", json=register_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["success"] is True
    assert "access_token" in reg_data["data"]

    # 2. Test Login
    login_payload = {
        "email": "testuser@example.com",
        "password": "Password123!",
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    assert token is not None

    # 3. Test Profile Retrieval
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/api/auth/profile", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["data"]["email"] == "testuser@example.com"
