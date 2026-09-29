from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator


class ContactMessageRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: EmailStr = Field(..., example="jane.smith@example.com")
    subject: str = Field(..., min_length=2, max_length=200, example="Inquiry about AI model accuracy")
    message: str = Field(..., min_length=3, max_length=2000, example="Hello, I would like to know more about the dataset used.")

    @model_validator(mode="after")
    def validate_name_presence(self):
        resolved_name = self.name or self.full_name
        if not resolved_name or len(resolved_name.strip()) < 2:
            raise ValueError("Please provide a valid full name.")
        self.name = resolved_name.strip()
        return self


class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
