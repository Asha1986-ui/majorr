"""
Prediction Schema v2 — India Diabetes Dataset fields.
PredictionRequest now uses the new feature set.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """
    Request body for POST /api/prediction.
    All fields match the India Diabetes Patient Dataset features.
    Fields are Optional so the pipeline's imputers can handle missing values.
    """
    # Optional reference to existing assessment record
    assessment_id: Optional[int] = Field(None, example=1)

    # Demographic & Lifestyle (India Dataset)
    patient_group: Optional[str] = Field("Urban", example="Urban")
    gender: Optional[str] = Field("Male", example="Male")
    age: Optional[int] = Field(35, ge=1, le=120, example=35)
    monthly_income: Optional[float] = Field(35000.0, ge=0.0, example=45000.0)
    month: Optional[float] = Field(6.0, ge=1.0, le=12.0, example=5.0)

    # Metabolic Biomarkers (India Dataset)
    bmi: Optional[float] = Field(24.5, ge=10.0, le=100.0, example=24.5)
    blood_pressure: Optional[float] = Field(120.0, ge=40.0, le=250.0, example=120.0)
    hba1c: Optional[float] = Field(5.7, ge=3.0, le=20.0, example=5.8)
    fasting_glucose: Optional[float] = Field(None, ge=40.0, le=600.0, example=105.0)

    # Habits & Genetics (India Dataset)
    physical_activity_hours: Optional[float] = Field(2.0, ge=0.0, le=24.0, example=1.5)
    daily_sugar_intake: Optional[float] = Field(30.0, ge=0.0, le=500.0, example=25.0)
    fast_food_frequency: Optional[float] = Field(2.0, ge=0.0, le=30.0, example=1.0)
    sleep_hours: Optional[float] = Field(7.0, ge=1.0, le=24.0, example=7.5)
    family_history: Optional[float] = Field(0.0, ge=0.0, le=1.0, example=0.0)

    # Legacy compatibility fields
    glucose: Optional[float] = Field(None, ge=0.0, le=600.0, example=105.0)
    pregnancies: Optional[int] = Field(0, ge=0, le=20, example=0)
    skin_thickness: Optional[float] = Field(0.0, ge=0.0, le=100.0, example=20.0)
    insulin: Optional[float] = Field(0.0, ge=0.0, le=900.0, example=85.0)
    diabetes_pedigree_function: Optional[float] = Field(0.0, ge=0.0, le=5.0, example=0.45)


class PredictionResponse(BaseModel):
    id: Optional[int] = None
    assessment_id: Optional[int] = None
    prediction: str   # "Higher Risk Pattern" or "Lower Risk Pattern"
    risk_percentage: float
    confidence: float
    recommendation: Optional[str] = (
        "This is a health awareness screening result. "
        "Please consult a qualified healthcare professional for clinical guidance."
    )
    contributing_factors: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    total: int
    predictions: List[PredictionResponse]
