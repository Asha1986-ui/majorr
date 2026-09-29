"""
Production Inference Module — DiaSense AI v2
Uses india_diabetes_patient_dataset.csv trained pipeline.

IMPORTANT: Output is a SCREENING risk score, not a clinical diagnosis.
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional

from app.utils.logger import logger

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_V2_PATH = os.path.join(CURRENT_DIR, "diabetes_pipeline_v2.pkl")
METADATA_V2_PATH = os.path.join(CURRENT_DIR, "model_metadata_v2.json")
COMPAT_METRICS_PATH = os.path.join(CURRENT_DIR, "model_metrics.json")

_pipeline_bundle = None
_metrics_instance = None


def load_pipeline_bundle() -> dict:
    """Singleton loader for the v2 pipeline bundle."""
    global _pipeline_bundle
    if _pipeline_bundle is None:
        if not os.path.exists(PIPELINE_V2_PATH):
            logger.warning(
                "diabetes_pipeline_v2.pkl not found — triggering training..."
            )
            from app.ml.train_model_v2 import train_and_save_pipeline
            train_and_save_pipeline()

        with open(PIPELINE_V2_PATH, "rb") as f:
            _pipeline_bundle = pickle.load(f)

        threshold = _pipeline_bundle.get("decision_threshold", 0.5)
        logger.info("=" * 52)
        logger.info(" DiaSense AI v2 — India Diabetes Pipeline Loaded")
        logger.info(f" Decision Threshold : {threshold}")
        logger.info("=" * 52)
    return _pipeline_bundle


def get_model_metrics() -> Dict[str, Any]:
    """Returns the compat metrics JSON for the API /metrics endpoint."""
    global _metrics_instance
    if _metrics_instance is None:
        if os.path.exists(COMPAT_METRICS_PATH):
            with open(COMPAT_METRICS_PATH, "r") as f:
                _metrics_instance = json.load(f)
        else:
            # Trigger training
            load_pipeline_bundle()
            if os.path.exists(COMPAT_METRICS_PATH):
                with open(COMPAT_METRICS_PATH, "r") as f:
                    _metrics_instance = json.load(f)
    return _metrics_instance or {}


def _build_input_dataframe(assessment_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Map the incoming API payload (snake_case) to the DataFrame the pipeline expects.
    All fields are optional at this layer — missing values are handled by the
    pipeline's median/mode imputers (fitted on training data only).
    """
    from app.ml.train_model_v2 import add_engineered_features

    row = {
        "Patient_Group":           assessment_data.get("patient_group", None),
        "Age":                     assessment_data.get("age", None),
        "Gender":                  assessment_data.get("gender", None),
        "BMI":                     assessment_data.get("bmi", None),
        "Physical_Activity_Hours": assessment_data.get("physical_activity_hours", None),
        "Daily_Sugar_Intake":      assessment_data.get("daily_sugar_intake", None),
        "Fast_Food_Frequency":     assessment_data.get("fast_food_frequency", None),
        "Sleep_Hours":             assessment_data.get("sleep_hours", None),
        "Family_History":          assessment_data.get("family_history", None),
        "Blood_Pressure":          assessment_data.get("blood_pressure", None),
        "HbA1c":                   assessment_data.get("hba1c", None),
        "Fasting_Glucose":         assessment_data.get("fasting_glucose", None),
        "Monthly_Income":          assessment_data.get("monthly_income", None),
        "Month":                   assessment_data.get("month", None),
    }

    df = pd.DataFrame([row])

    # Apply the same feature engineering used during training
    df = add_engineered_features(df)

    # Drop target column if accidentally included
    if "Diabetes" in df.columns:
        df = df.drop(columns=["Diabetes"])

    return df


def analyze_contributing_factors(assessment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Produce a human-readable list of contributing risk factors
    based on the NEW dataset's features and clinical thresholds.
    """
    factors = []

    # ── Fasting Glucose ──────────────────────────────────────────────────────
    glucose = assessment_data.get("fasting_glucose")
    if glucose is not None:
        g = float(glucose)
        if g >= 126:
            factors.append({
                "factor": "Fasting Glucose",
                "value": f"{g:.0f} mg/dL",
                "impact": "High Risk",
                "description": (
                    "Fasting glucose >= 126 mg/dL meets the ADA clinical threshold "
                    "for elevated diabetes risk. A confirmatory test is strongly recommended."
                ),
            })
        elif g >= 100:
            factors.append({
                "factor": "Fasting Glucose",
                "value": f"{g:.0f} mg/dL",
                "impact": "Moderate Risk",
                "description": (
                    "Fasting glucose 100-125 mg/dL (impaired fasting glucose / pre-diabetic range). "
                    "Lifestyle changes and regular monitoring are advised."
                ),
            })
        else:
            factors.append({
                "factor": "Fasting Glucose",
                "value": f"{g:.0f} mg/dL",
                "impact": "Good",
                "description": "Fasting glucose within the healthy normal range (< 100 mg/dL).",
            })

    # ── HbA1c ───────────────────────────────────────────────────────────────
    hba1c = assessment_data.get("hba1c")
    if hba1c is not None:
        h = float(hba1c)
        if h >= 6.5:
            factors.append({
                "factor": "HbA1c",
                "value": f"{h:.1f}%",
                "impact": "High Risk",
                "description": (
                    "HbA1c >= 6.5% is consistent with elevated long-term blood sugar levels. "
                    "This warrants prompt medical consultation."
                ),
            })
        elif h >= 5.7:
            factors.append({
                "factor": "HbA1c",
                "value": f"{h:.1f}%",
                "impact": "Moderate Risk",
                "description": (
                    "HbA1c 5.7-6.4% falls in the pre-diabetic range. "
                    "Dietary adjustments and physical activity can help."
                ),
            })
        else:
            factors.append({
                "factor": "HbA1c",
                "value": f"{h:.1f}%",
                "impact": "Good",
                "description": "HbA1c below 5.7% indicates good long-term glycemic control.",
            })

    # ── BMI ─────────────────────────────────────────────────────────────────
    bmi = assessment_data.get("bmi")
    if bmi is not None:
        b = float(bmi)
        if b >= 30:
            factors.append({
                "factor": "BMI (Body Mass Index)",
                "value": f"{b:.1f}",
                "impact": "High Risk",
                "description": (
                    "BMI >= 30 is classified as obesity. Excess weight significantly "
                    "increases insulin resistance and diabetes risk."
                ),
            })
        elif b >= 25:
            factors.append({
                "factor": "BMI (Body Mass Index)",
                "value": f"{b:.1f}",
                "impact": "Moderate Risk",
                "description": "BMI 25-29.9 (overweight range). Weight management is recommended.",
            })
        else:
            factors.append({
                "factor": "BMI (Body Mass Index)",
                "value": f"{b:.1f}",
                "impact": "Good",
                "description": "BMI within healthy range (18.5-24.9).",
            })

    # ── Daily Sugar Intake ───────────────────────────────────────────────────
    sugar = assessment_data.get("daily_sugar_intake")
    if sugar is not None:
        s = float(sugar)
        if s > 75:
            factors.append({
                "factor": "Daily Sugar Intake",
                "value": f"{s:.0f} g/day",
                "impact": "High Risk",
                "description": (
                    "High daily sugar intake is the strongest predictor of diabetes risk "
                    "in this dataset. Reducing sugar and processed food consumption is critical."
                ),
            })
        elif s > 45:
            factors.append({
                "factor": "Daily Sugar Intake",
                "value": f"{s:.0f} g/day",
                "impact": "Moderate Risk",
                "description": (
                    "Sugar intake above WHO recommended levels (< 25-50 g/day). "
                    "Consider reducing sugary drinks and snacks."
                ),
            })
        else:
            factors.append({
                "factor": "Daily Sugar Intake",
                "value": f"{s:.0f} g/day",
                "impact": "Good",
                "description": "Daily sugar intake within reasonable bounds.",
            })

    # ── Physical Activity ────────────────────────────────────────────────────
    activity = assessment_data.get("physical_activity_hours")
    if activity is not None:
        a = float(activity)
        if a < 2:
            factors.append({
                "factor": "Physical Activity",
                "value": f"{a:.1f} hrs/day",
                "impact": "High Risk",
                "description": (
                    "Very low physical activity level. Regular exercise (>= 150 min/week) "
                    "substantially reduces diabetes risk."
                ),
            })
        elif a < 4:
            factors.append({
                "factor": "Physical Activity",
                "value": f"{a:.1f} hrs/day",
                "impact": "Moderate Risk",
                "description": (
                    "Moderate activity level. Aim for at least 30 minutes of "
                    "brisk walking or exercise daily."
                ),
            })
        else:
            factors.append({
                "factor": "Physical Activity",
                "value": f"{a:.1f} hrs/day",
                "impact": "Good",
                "description": "Good physical activity level. Keep it up!",
            })

    # ── Family History ───────────────────────────────────────────────────────
    fam = assessment_data.get("family_history")
    if fam is not None and float(fam) == 1:
        factors.append({
            "factor": "Family History of Diabetes",
            "value": "Yes",
            "impact": "Moderate Risk",
            "description": (
                "Having a first-degree family member with diabetes increases "
                "your genetic predisposition. Regular screening is recommended."
            ),
        })

    # ── Blood Pressure ───────────────────────────────────────────────────────
    bp = assessment_data.get("blood_pressure")
    if bp is not None:
        p = float(bp)
        if p >= 140:
            factors.append({
                "factor": "Blood Pressure",
                "value": f"{p:.0f} mmHg",
                "impact": "Moderate Risk",
                "description": (
                    "Elevated systolic blood pressure. Hypertension frequently "
                    "co-occurs with diabetes and increases cardiovascular risk."
                ),
            })

    return factors


def predict_diabetes_risk(
    assessment_data: Dict[str, Any],
    lang: str = "en"
) -> Tuple[str, float, float, str, List[Dict[str, Any]]]:
    """
    Main inference function.
    Returns:
        prediction_label  : 'Higher Risk Pattern' or 'Lower Risk Pattern'
        risk_percentage   : model-estimated probability × 100
        confidence        : max(P(positive), P(negative)) × 100
        recommendation    : plain-language guidance text
        contributing_factors
    """
    bundle = load_pipeline_bundle()
    pipeline = bundle["pipeline"]
    threshold = bundle.get("decision_threshold", 0.5)

    # Build input DataFrame (with feature engineering)
    X_input = _build_input_dataframe(assessment_data)

    # Inference
    probabilities = pipeline.predict_proba(X_input)[0]
    risk_prob = float(probabilities[1])
    non_risk_prob = float(probabilities[0])

    risk_percentage = round(risk_prob * 100.0, 1)
    confidence = round(max(risk_prob, non_risk_prob) * 100.0, 1)

    # Apply the stored threshold (not hardcoded 0.5)
    is_higher_risk = risk_prob >= threshold

    # Use safe, non-diagnostic labels
    prediction_label = "Higher Risk Pattern" if is_higher_risk else "Lower Risk Pattern"

    # Recommendation
    if is_higher_risk:
        recommendation = (
            "Based on the information you provided, your responses indicate an elevated risk pattern "
            "that warrants attention. We strongly recommend consulting a healthcare professional "
            "for a formal evaluation, including fasting blood glucose and HbA1c tests. "
            "Focus on reducing daily sugar intake, increasing physical activity, "
            "and maintaining a balanced diet."
        )
    else:
        recommendation = (
            "Your responses suggest a lower risk pattern at this time. "
            "Maintaining healthy habits — regular exercise, balanced nutrition with "
            "reduced sugar intake, adequate sleep, and routine health checkups — "
            "will help you stay on track. Rescreen annually or if symptoms appear."
        )

    contributing_factors = analyze_contributing_factors(assessment_data)

    logger.info(
        f"Prediction: {prediction_label} | Risk: {risk_percentage}% "
        f"| Threshold: {threshold} | Confidence: {confidence}%"
    )

    return prediction_label, risk_percentage, confidence, recommendation, contributing_factors
