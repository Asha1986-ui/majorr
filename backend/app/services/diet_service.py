from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.diet_repository import DietRepository
from app.utils.i18n import localize_diet_plan, normalize_lang


class DietService:
    """
    Business Logic Layer for Personalized Nutrition & Diet Plan Retrieval with multilingual support.
    """
    def __init__(self, db: Session):
        self.db = db
        self.prediction_repo = PredictionRepository(db)
        self.diet_repo = DietRepository(db)

    def get_latest_diet_plan(self, user: User, lang: str = "en") -> Dict[str, Any]:
        latest_pred = self.prediction_repo.get_latest_by_user_id(user.id)
        if not latest_pred:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No prediction records found for user to generate diet plan",
            )
        
        diet_obj = self.diet_repo.get_by_prediction_id(latest_pred.id)
        if not diet_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diet plan not found for latest prediction",
            )

        localized_plan = localize_diet_plan(latest_pred.prediction, lang)

        return {
            "id": diet_obj.id,
            "prediction_id": diet_obj.prediction_id,
            "prediction_label": latest_pred.prediction,
            "risk_percentage": latest_pred.risk_percentage,
            "breakfast": localized_plan["breakfast"],
            "lunch": localized_plan["lunch"],
            "dinner": localized_plan["dinner"],
            "snacks": localized_plan["snacks"],
            "exercise": localized_plan["exercise"],
            "tips": localized_plan["tips"],
        }

    def get_diet_plan_by_prediction_id(self, user: User, prediction_id: int, lang: str = "en") -> Dict[str, Any]:
        prediction = self.prediction_repo.get_by_id(prediction_id)
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction record not found",
            )

        diet_obj = self.diet_repo.get_by_prediction_id(prediction_id)
        if not diet_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diet plan not found for requested prediction",
            )

        localized_plan = localize_diet_plan(prediction.prediction, lang)

        return {
            "id": diet_obj.id,
            "prediction_id": diet_obj.prediction_id,
            "prediction_label": prediction.prediction,
            "risk_percentage": prediction.risk_percentage,
            "breakfast": localized_plan["breakfast"],
            "lunch": localized_plan["lunch"],
            "dinner": localized_plan["dinner"],
            "snacks": localized_plan["snacks"],
            "exercise": localized_plan["exercise"],
            "tips": localized_plan["tips"],
        }
