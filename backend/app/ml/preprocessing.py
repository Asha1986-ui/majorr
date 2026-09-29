import pandas as pd
import numpy as np
from typing import Dict, Any


def preprocess_assessment_data(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Transforms client assessment input dictionary into a normalized DataFrame
    matching the Indian Diabetes Patient Dataset pipeline.
    """
    # 1. Categorical fields
    patient_group = str(data.get("patient_group") or data.get("Patient_Group") or "Urban").strip()
    if patient_group.lower() in ("urban", "city"):
        patient_group = "Urban"
    elif patient_group.lower() in ("semi-urban", "semiurban", "town"):
        patient_group = "Semi-Urban"
    elif patient_group.lower() in ("rural", "village"):
        patient_group = "Rural"
    else:
        patient_group = "Urban"

    gender = str(data.get("gender") or data.get("Gender") or "Male").strip()
    if gender.lower().startswith("f"):
        gender = "Female"
    else:
        gender = "Male"

    # Family history: handle boolean, int, or string
    raw_fh = data.get("family_history") if data.get("family_history") is not None else data.get("Family_History")
    if isinstance(raw_fh, bool):
        family_history = 1.0 if raw_fh else 0.0
    elif isinstance(raw_fh, (int, float)):
        family_history = float(raw_fh)
    elif isinstance(raw_fh, str):
        family_history = 1.0 if raw_fh.lower() in ("yes", "true", "1", "positive") else 0.0
    else:
        family_history = 0.0

    # 2. Numerical fields (with biological fallback clamps)
    age = float(data.get("age") or data.get("Age") or 35.0)
    bmi = float(data.get("bmi") or data.get("BMI") or 24.5)
    physical_activity = float(data.get("physical_activity_hours") or data.get("Physical_Activity_Hours") or 2.0)
    daily_sugar = float(data.get("daily_sugar_intake") or data.get("Daily_Sugar_Intake") or 30.0)
    fast_food = float(data.get("fast_food_frequency") or data.get("Fast_Food_Frequency") or 2.0)
    sleep_hours = float(data.get("sleep_hours") or data.get("Sleep_Hours") or 7.0)
    blood_pressure = float(data.get("blood_pressure") or data.get("Blood_Pressure") or 120.0)
    hba1c = float(data.get("hba1c") or data.get("HbA1c") or 5.7)

    # Fasting glucose fallback to legacy 'glucose' if missing
    fasting_glucose = float(
        data.get("fasting_glucose") or data.get("Fasting_Glucose") or data.get("glucose") or data.get("Glucose") or 100.0
    )

    monthly_income = float(data.get("monthly_income") or data.get("Monthly_Income") or 35000.0)
    month = float(data.get("month") or data.get("Month") or 6.0)

    # 3. Engineered features
    hba1c_glucose = hba1c * fasting_glucose
    glucose_bmi = fasting_glucose * bmi
    age_bmi = age * bmi
    high_hba1c = 1.0 if hba1c >= 6.5 else 0.0
    high_glucose = 1.0 if fasting_glucose >= 126.0 else 0.0
    lifestyle_index = (daily_sugar + fast_food * 5.0) / (physical_activity + 1.0)

    row = {
        "Patient_Group": patient_group,
        "Gender": gender,
        "Age": age,
        "BMI": bmi,
        "Physical_Activity_Hours": physical_activity,
        "Daily_Sugar_Intake": daily_sugar,
        "Fast_Food_Frequency": fast_food,
        "Sleep_Hours": sleep_hours,
        "Family_History": family_history,
        "Blood_Pressure": blood_pressure,
        "HbA1c": hba1c,
        "Fasting_Glucose": fasting_glucose,
        "Monthly_Income": monthly_income,
        "Month": month,
        "HbA1c_FastingGlucose": hba1c_glucose,
        "Glucose_BMI": glucose_bmi,
        "Age_BMI": age_bmi,
        "High_HbA1c": high_hba1c,
        "High_Glucose": high_glucose,
        "Lifestyle_Index": lifestyle_index,
    }

    return pd.DataFrame([row])
