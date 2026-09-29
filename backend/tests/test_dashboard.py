def test_dashboard_endpoint(client):
    # 1. Register user
    reg_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Dashboard Tester",
            "email": "dashboard@example.com",
            "password": "Password123!",
        },
    )
    token = reg_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Dashboard Data
    dash_response = client.get("/api/dashboard", headers=headers)
    assert dash_response.status_code == 200
    dash_data = dash_response.json()["data"]
    assert "user_profile" in dash_data
    assert "health_summary" in dash_data
    assert "risk_level" in dash_data
