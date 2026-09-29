"""
Assessment Schema v2 — India Diabetes Patient Dataset fields.
Replaces old Pima-style schema (pregnancies / insulin / skin_thickness / dpf).
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AssessmentCreateRequest(BaseModel):
    # Demographics
    patient_group: Optional[str] = Field("Urban", example="Urban")
    gender: Optional[str] = Field("Male", example="Male")
    age: int = Field(..., ge=1, le=120, example=35)
    monthly_income: Optional[float] = Field(35000.0, ge=0.0, example=50000.0)
    month: Optional[float] = Field(6.0, ge=1.0, le=12.0, example=5.0)

    # Clinical & Metabolic Biomarkers
    bmi: float = Field(..., ge=10.0, le=100.0, example=24.5)
    blood_pressure: float = Field(..., ge=40.0, le=250.0, example=120.0)
    hba1c: Optional[float] = Field(5.7, ge=3.0, le=20.0, example=5.8)
    fasting_glucose: Optional[float] = Field(None, ge=40.0, le=600.0, example=105.0)

    # Lifestyle & Genetics
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


class AssessmentResponse(BaseModel):
    id: int
    user_id: int
    patient_group: Optional[str] = "Urban"
    gender: Optional[str] = "Male"
    age: int
    bmi: float
    blood_pressure: float
    hba1c: Optional[float] = 5.7
    fasting_glucose: Optional[float] = 100.0
    physical_activity_hours: Optional[float] = 2.0
    daily_sugar_intake: Optional[float] = 30.0
    fast_food_frequency: Optional[float] = 2.0
    sleep_hours: Optional[float] = 7.0
    family_history: Optional[float] = 0.0
    monthly_income: Optional[float] = 35000.0
    month: Optional[float] = 6.0

    # Legacy fields
    glucose: Optional[float] = None
    pregnancies: Optional[int] = None
    skin_thickness: Optional[float] = None
    insulin: Optional[float] = None
    diabetes_pedigree_function: Optional[float] = None

    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentListResponse(BaseModel):
    total: int
    assessments: List[AssessmentResponse]
