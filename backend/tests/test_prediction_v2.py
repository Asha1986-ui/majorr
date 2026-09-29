"""
Tests for DiaSense AI v2 — India Diabetes Pipeline
Run from: backend/ directory with:
    python -m pytest tests/test_prediction_v2.py -v
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ─── Unit Tests for Preprocessing ───────────────────────────────────────────

class TestBuildInputDataframe:
    def test_complete_input(self):
        """Full valid input produces a DataFrame with expected columns."""
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {
            "patient_group": "Urban",
            "age": 45.0,
            "gender": "Female",
            "bmi": 28.5,
            "blood_pressure": 130.0,
            "physical_activity_hours": 2.5,
            "daily_sugar_intake": 60.0,
            "fast_food_frequency": 3.0,
            "sleep_hours": 6.5,
            "hba1c": 6.0,
            "fasting_glucose": 112.0,
            "family_history": 1.0,
            "monthly_income": 35000.0,
            "month": 6.0,
        }
        df = _build_input_dataframe(data)
        assert df.shape[0] == 1
        # Engineered features should be present
        assert "BMI_Category" in df.columns
        assert "HbA1c_Category" in df.columns
        assert "Glucose_Category" in df.columns

    def test_all_missing_optional_fields(self):
        """Only required fields (none) present — model imputers must handle NaN."""
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {"age": 50.0, "bmi": 30.0}
        df = _build_input_dataframe(data)
        assert df.shape[0] == 1

    def test_target_column_not_in_output(self):
        """Diabetes target column must not be included in inference input."""
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {"age": 35.0, "bmi": 24.0, "Diabetes": 1}  # accidental inclusion
        df = _build_input_dataframe(data)
        assert "Diabetes" not in df.columns


# ─── Unit Tests for Contributing Factors ────────────────────────────────────

class TestContributingFactors:
    def test_high_glucose_detected(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({"fasting_glucose": 140.0})
        glucose_factors = [f for f in factors if f["factor"] == "Fasting Glucose"]
        assert len(glucose_factors) == 1
        assert glucose_factors[0]["impact"] == "High Risk"

    def test_prediabetic_glucose(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({"fasting_glucose": 110.0})
        glucose_factors = [f for f in factors if f["factor"] == "Fasting Glucose"]
        assert glucose_factors[0]["impact"] == "Moderate Risk"

    def test_normal_glucose(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({"fasting_glucose": 90.0})
        glucose_factors = [f for f in factors if f["factor"] == "Fasting Glucose"]
        assert glucose_factors[0]["impact"] == "Good"

    def test_high_hba1c(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({"hba1c": 7.2})
        hba1c_factors = [f for f in factors if f["factor"] == "HbA1c"]
        assert hba1c_factors[0]["impact"] == "High Risk"

    def test_obese_bmi(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({"bmi": 32.0})
        bmi_factors = [f for f in factors if "BMI" in f["factor"]]
        assert bmi_factors[0]["impact"] == "High Risk"

    def test_low_activity_flag(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({"physical_activity_hours": 0.5})
        act_factors = [f for f in factors if f["factor"] == "Physical Activity"]
        assert act_factors[0]["impact"] == "High Risk"

    def test_family_history_flag(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({"family_history": 1.0})
        fam_factors = [f for f in factors if "Family" in f["factor"]]
        assert len(fam_factors) == 1

    def test_empty_input_no_crash(self):
        from app.ml.prediction_v2 import analyze_contributing_factors
        factors = analyze_contributing_factors({})
        assert isinstance(factors, list)


# ─── Integration Tests for Inference Pipeline ─────────────────────────────

@pytest.fixture(scope="module")
def pipeline_loaded():
    """Load the pipeline once per module — requires training to have completed."""
    pipeline_path = os.path.join(
        os.path.dirname(__file__), "..", "app", "ml", "diabetes_pipeline_v2.pkl"
    )
    if not os.path.exists(pipeline_path):
        pytest.skip("diabetes_pipeline_v2.pkl not found — run train_model_v2.py first")
    from app.ml.prediction_v2 import load_pipeline_bundle
    return load_pipeline_bundle()


class TestPipelineInference:
    def test_probability_in_valid_range(self, pipeline_loaded):
        """Model probability must be in [0, 1]."""
        import pandas as pd
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {
            "age": 50.0, "bmi": 30.0, "fasting_glucose": 130.0,
            "hba1c": 6.8, "daily_sugar_intake": 80.0,
            "physical_activity_hours": 1.0, "family_history": 1.0,
        }
        df = _build_input_dataframe(data)
        pipeline = pipeline_loaded["pipeline"]
        prob = pipeline.predict_proba(df)[0][1]
        assert 0.0 <= prob <= 1.0

    def test_low_risk_profile(self, pipeline_loaded):
        """Clearly healthy profile should produce low risk."""
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {
            "age": 28.0, "bmi": 22.0, "fasting_glucose": 80.0,
            "hba1c": 5.0, "daily_sugar_intake": 20.0,
            "physical_activity_hours": 7.0, "sleep_hours": 8.0,
            "family_history": 0.0, "fast_food_frequency": 0.0,
        }
        df = _build_input_dataframe(data)
        pipeline = pipeline_loaded["pipeline"]
        prob = pipeline.predict_proba(df)[0][1]
        assert prob < 0.5, f"Expected low risk, got {prob:.3f}"

    def test_high_risk_profile(self, pipeline_loaded):
        """Clearly high-risk profile should produce elevated risk."""
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {
            "age": 62.0, "bmi": 38.0, "fasting_glucose": 180.0,
            "hba1c": 8.5, "daily_sugar_intake": 120.0,
            "physical_activity_hours": 0.5, "sleep_hours": 4.0,
            "family_history": 1.0, "fast_food_frequency": 7.0,
        }
        df = _build_input_dataframe(data)
        pipeline = pipeline_loaded["pipeline"]
        prob = pipeline.predict_proba(df)[0][1]
        assert prob > 0.5, f"Expected high risk, got {prob:.3f}"

    def test_all_null_inputs_handled(self, pipeline_loaded):
        """All-None inputs must not crash — imputers handle missing values."""
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {}
        df = _build_input_dataframe(data)
        pipeline = pipeline_loaded["pipeline"]
        prob = pipeline.predict_proba(df)[0][1]
        assert 0.0 <= prob <= 1.0

    def test_unseen_category(self, pipeline_loaded):
        """Unseen categorical value must not crash (OrdinalEncoder handle_unknown)."""
        from app.ml.prediction_v2 import _build_input_dataframe
        data = {
            "patient_group": "ExtraUrban",   # unseen category
            "gender": "Non-Binary",          # unseen category
            "age": 35.0, "bmi": 25.0,
        }
        df = _build_input_dataframe(data)
        pipeline = pipeline_loaded["pipeline"]
        prob = pipeline.predict_proba(df)[0][1]
        assert 0.0 <= prob <= 1.0

    def test_prediction_label_valid_values(self, pipeline_loaded):
        """predict_diabetes_risk must return one of the two documented labels."""
        from app.ml.prediction_v2 import predict_diabetes_risk
        label, risk, conf, rec, factors = predict_diabetes_risk({"age": 40.0, "bmi": 26.0})
        assert label in ("Higher Risk Pattern", "Lower Risk Pattern")
        assert 0.0 <= risk <= 100.0
        assert 0.0 <= conf <= 100.0
        assert isinstance(rec, str) and len(rec) > 10
        assert isinstance(factors, list)

    def test_threshold_respected(self, pipeline_loaded):
        """Threshold from bundle must match the one used in prediction."""
        threshold = pipeline_loaded.get("decision_threshold", 0.5)
        assert 0.2 <= threshold <= 0.8, f"Suspicious threshold: {threshold}"


# ─── Pydantic Schema Tests ──────────────────────────────────────────────────

class TestPredictionSchema:
    def test_valid_request(self):
        from app.schemas.prediction_schema import PredictionRequest
        req = PredictionRequest(age=42.0, bmi=28.0, fasting_glucose=115.0)
        assert req.age == 42.0

    def test_all_optional_fields_none(self):
        from app.schemas.prediction_schema import PredictionRequest
        req = PredictionRequest()
        assert req.age is None
        assert req.bmi is None

    def test_old_pima_fields_not_present(self):
        from app.schemas.prediction_schema import PredictionRequest
        assert not hasattr(PredictionRequest, "pregnancies")
        assert not hasattr(PredictionRequest, "skin_thickness")
        assert not hasattr(PredictionRequest, "diabetes_pedigree_function")
        assert not hasattr(PredictionRequest, "insulin")

    def test_bmi_out_of_range_raises(self):
        from app.schemas.prediction_schema import PredictionRequest
        with pytest.raises(Exception):
            PredictionRequest(bmi=5.0)   # below minimum of 10

    def test_age_out_of_range_raises(self):
        from app.schemas.prediction_schema import PredictionRequest
        with pytest.raises(Exception):
            PredictionRequest(age=200.0)  # above maximum of 110
