"""
Feature definitions for DiaSense AI v2
India Diabetes Patient Dataset (25,500 records)
"""

# ── Raw API-level feature names (snake_case, matching Pydantic schema) ────────
FEATURE_NAMES_V2 = [
    "patient_group",
    "age",
    "gender",
    "bmi",
    "physical_activity_hours",
    "daily_sugar_intake",
    "fast_food_frequency",
    "sleep_hours",
    "family_history",
    "blood_pressure",
    "hba1c",
    "fasting_glucose",
    "monthly_income",
    "month",
]

# ── Categorical features (require OrdinalEncoding) ────────────────────────────
CATEGORICAL_FEATURES = ["patient_group", "gender"]

# ── Binary features (0/1, use mode imputation) ────────────────────────────────
BINARY_FEATURES = ["family_history"]

# ── Continuous numerical features (use median imputation + StandardScaler) ────
NUMERICAL_FEATURES = [
    "age", "bmi", "physical_activity_hours", "daily_sugar_intake",
    "fast_food_frequency", "sleep_hours", "blood_pressure",
    "hba1c", "fasting_glucose", "monthly_income", "month",
]

# ── Engineered features added during training and inference ───────────────────
ENGINEERED_FEATURES = [
    "BMI_Category",        # categorical bins (Underweight/Normal/Overweight/Obese)
    "HbA1c_Category",      # categorical bins (Normal/Prediabetic/Diabetic)
    "Glucose_Category",    # categorical bins (Normal/Impaired/Diabetic)
    "Activity_Category",   # categorical bins (Sedentary/Moderate/Active)
    "Sugar_x_Activity",    # interaction term
    "Age_x_BMI",           # interaction term
    "FamilyHistory_x_Age", # interaction term
]

# ── Legacy v1 Pima features (DEPRECATED — no longer used in inference) ─────────
LEGACY_PIMA_FEATURES = [
    "pregnancies",
    "glucose",          # replaced by fasting_glucose
    "blood_pressure",   # renamed
    "skin_thickness",   # not in new dataset
    "insulin",          # not in new dataset
    "bmi",              # still present in v2
    "diabetes_pedigree_function",  # replaced by family_history
    "age",              # still present in v2
]

# Default fallback values for optional fields
DEFAULT_FEATURE_VALUES_V2 = {
    "patient_group": "Urban",
    "age": 45.0,
    "gender": "Male",
    "bmi": 27.0,
    "physical_activity_hours": 3.0,
    "daily_sugar_intake": 50.0,
    "fast_food_frequency": 2.0,
    "sleep_hours": 7.0,
    "family_history": 0.0,
    "blood_pressure": 128.0,
    "hba1c": 5.9,
    "fasting_glucose": 110.0,
    "monthly_income": 40000.0,
    "month": 6.0,
}
