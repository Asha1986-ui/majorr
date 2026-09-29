from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class DietPlan(Base):
    """
    SQLAlchemy Diet Plan Model.
    Table: diet_plans
    """
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False)
    breakfast = Column(Text, nullable=False)
    lunch = Column(Text, nullable=False)
    dinner = Column(Text, nullable=False)
    snacks = Column(Text, nullable=False)
    exercise = Column(Text, nullable=False)
    tips = Column(Text, nullable=False)

    # Relationships
    prediction = relationship("Prediction", back_populates="diet_plan")
