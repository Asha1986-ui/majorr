from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[str] = Field(None)


class UserPasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


class UserProfileStatsResponse(BaseModel):
    user: UserProfileResponse
    total_assessments: int = 0
    latest_prediction: Optional[str] = None
    latest_risk_score: Optional[float] = None
    latest_confidence: Optional[float] = None
    latest_assessment_date: Optional[datetime] = None
