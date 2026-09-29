from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.assessment import Assessment


class AssessmentRepository:
    """
    Data Access Layer for Assessment Entity.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, assessment: Assessment) -> Assessment:
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get_by_id(self, assessment_id: int) -> Optional[Assessment]:
        return self.db.query(Assessment).filter(Assessment.id == assessment_id).first()

    def get_by_user_id(self, user_id: int) -> List[Assessment]:
        return (
            self.db.query(Assessment)
            .filter(Assessment.user_id == user_id)
            .order_by(Assessment.created_at.desc())
            .all()
        )

    def delete(self, assessment: Assessment) -> None:
        self.db.delete(assessment)
        self.db.commit()
