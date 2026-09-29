from typing import Optional
from sqlalchemy.orm import Session
from app.models.diet_plan import DietPlan


class DietRepository:
    """
    Data Access Layer for DietPlan Entity.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, diet_plan: DietPlan) -> DietPlan:
        self.db.add(diet_plan)
        self.db.commit()
        self.db.refresh(diet_plan)
        return diet_plan

    def get_by_prediction_id(self, prediction_id: int) -> Optional[DietPlan]:
        return self.db.query(DietPlan).filter(DietPlan.prediction_id == prediction_id).first()
