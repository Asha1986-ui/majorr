"""
SQLAlchemy Assessment Model v2
Migrated from Pima-style features to India Diabetes Dataset features.
Old columns are preserved as nullable for rollback compatibility.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.config.database import Base


class Assessment(Base):
    """
    SQLAlchemy Assessment Model — India Diabetes Dataset schema.
    Table: assessments
    Supports both new Indian Diabetes Patient Dataset fields and legacy Pima fields for zero data loss.
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Demographic & Lifestyle (India Dataset)
    patient_group = Column(String(50), nullable=True, default="Urban")
    gender = Column(String(20), nullable=True, default="Male")
    age = Column(Integer, nullable=False, default=35)
    monthly_income = Column(Float, nullable=True, default=35000.0)
    month = Column(Float, nullable=True, default=6.0)

    # Metabolic Biomarkers (India Dataset)
    bmi = Column(Float, nullable=False, default=24.5)
    blood_pressure = Column(Float, nullable=False, default=120.0)
    hba1c = Column(Float, nullable=True, default=5.7)
    fasting_glucose = Column(Float, nullable=True, default=100.0)

    # Habits & Genetics (India Dataset)
    physical_activity_hours = Column(Float, nullable=True, default=2.0)
    daily_sugar_intake = Column(Float, nullable=True, default=30.0)
    fast_food_frequency = Column(Float, nullable=True, default=2.0)
    sleep_hours = Column(Float, nullable=True, default=7.0)
    family_history = Column(Float, nullable=True, default=0.0)

    # Legacy Pima Fields (Retained for historical backwards compatibility)
    pregnancies = Column(Integer, default=0, nullable=True)
    glucose = Column(Float, nullable=True, default=100.0)
    skin_thickness = Column(Float, default=0.0, nullable=True)
    insulin = Column(Float, default=0.0, nullable=True)
    diabetes_pedigree_function = Column(Float, default=0.0, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="assessments")
    prediction = relationship(
        "Prediction", back_populates="assessment",
        uselist=False, cascade="all, delete-orphan"
    )
