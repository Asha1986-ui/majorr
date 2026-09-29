import pytest
from app.ml.prediction import predict_diabetes_risk, get_model_metrics


def test_ml_model_metrics():
    metrics = get_model_metrics()
    assert "accuracy" in metrics
    assert "accuracy_percentage" in metrics
    assert float(metrics["accuracy"]) > 0.60  # Pima dataset accuracy threshold


def test_ml_prediction_inference():
    high_risk_data = {
        "pregnancies": 5,
        "glucose": 175.0,
        "blood_pressure": 95.0,
        "skin_thickness": 35.0,
        "insulin": 200.0,
        "bmi": 36.2,
        "diabetes_pedigree_function": 0.85,
        "age": 52
    }

    pred_label, risk_pct, confidence, recommendation, factors = predict_diabetes_risk(high_risk_data)
    
    assert pred_label in ["Higher Risk Pattern", "Lower Risk Pattern", "Diabetic", "Non-Diabetic"]
    assert 0.0 <= risk_pct <= 100.0
    assert 0.0 <= confidence <= 100.0
    assert len(recommendation) > 10
    assert isinstance(factors, list)
    assert len(factors) > 0


def test_ml_low_risk_inference():
    low_risk_data = {
        "pregnancies": 0,
        "glucose": 85.0,
        "blood_pressure": 65.0,
        "skin_thickness": 18.0,
        "insulin": 70.0,
        "bmi": 21.5,
        "diabetes_pedigree_function": 0.15,
        "age": 23
    }

    pred_label, risk_pct, confidence, recommendation, factors = predict_diabetes_risk(low_risk_data)
    assert risk_pct < 50.0
    assert pred_label in ["Lower Risk Pattern", "Non-Diabetic"]
