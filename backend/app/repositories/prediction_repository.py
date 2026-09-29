from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.prediction import Prediction
from app.models.assessment import Assessment


class PredictionRepository:
    """
    Data Access Layer for Prediction Entity.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, prediction: Prediction) -> Prediction:
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction

    def get_by_id(self, prediction_id: int) -> Optional[Prediction]:
        return self.db.query(Prediction).filter(Prediction.id == prediction_id).first()

    def get_latest_by_user_id(self, user_id: int) -> Optional[Prediction]:
        return (
            self.db.query(Prediction)
            .join(Assessment, Prediction.assessment_id == Assessment.id)
            .filter(Assessment.user_id == user_id)
            .order_by(Prediction.created_at.desc())
            .first()
        )

    def get_history_by_user_id(self, user_id: int) -> List[Prediction]:
        return (
            self.db.query(Prediction)
            .join(Assessment, Prediction.assessment_id == Assessment.id)
            .filter(Assessment.user_id == user_id)
            .order_by(Prediction.created_at.desc())
            .all()
        )
