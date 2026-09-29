def test_prediction_flow(client):
    # 1. Register & get token
    reg_response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Prediction Test",
            "email": "predict@example.com",
            "password": "Password123!",
        },
    )
    token = reg_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Submit ML Prediction Request
    pred_payload = {
        "pregnancies": 2,
        "glucose": 150.0,
        "blood_pressure": 85.0,
        "skin_thickness": 22.0,
        "insulin": 100.0,
        "bmi": 32.5,
        "diabetes_pedigree_function": 0.65,
        "age": 45,
    }
    pred_response = client.post("/api/prediction", json=pred_payload, headers=headers)
    assert pred_response.status_code == 200
    res_data = pred_response.json()["data"]
    assert "prediction" in res_data
    assert "risk_percentage" in res_data
    assert "confidence" in res_data
    assert "recommendation" in res_data

    # 3. Retrieve Latest Prediction
    latest_response = client.get("/api/prediction/latest", headers=headers)
    assert latest_response.status_code == 200
    assert latest_response.json()["data"]["risk_percentage"] == res_data["risk_percentage"]

    # 4. Check Model Accuracy Endpoint
    accuracy_response = client.get("/api/prediction/accuracy")
    assert accuracy_response.status_code == 200
    acc_data = accuracy_response.json()["data"]
    assert "accuracy" in acc_data
    assert "accuracy_percentage" in acc_data
    assert acc_data["accuracy"] > 0.0

