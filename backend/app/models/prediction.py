from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.config.database import Base


class Prediction(Base):
    """
    SQLAlchemy Prediction Model.
    Table: predictions
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    prediction = Column(String(50), nullable=False)  # 'Diabetic' or 'Non-Diabetic'
    risk_percentage = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    assessment = relationship("Assessment", back_populates="prediction")
    diet_plan = relationship("DietPlan", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
