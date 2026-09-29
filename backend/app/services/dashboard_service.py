from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.diet_repository import DietRepository
from app.schemas.user_schema import UserProfileResponse
from app.schemas.assessment_schema import AssessmentResponse
from app.schemas.prediction_schema import PredictionResponse
from app.ml.prediction import predict_diabetes_risk


class DashboardService:
    """
    Business Logic Layer for Dashboard Aggregation.
    Provides complete health summary, latest prediction, assessment history, risk analysis, and active diet plan.
    """
    def __init__(self, db: Session):
        self.db = db
        self.assessment_repo = AssessmentRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.diet_repo = DietRepository(db)

    def get_dashboard_data(self, user: User) -> Dict[str, Any]:
        # 1. Profile
        profile_data = UserProfileResponse.model_validate(user).model_dump()

        # 2. Latest Prediction & Diet Plan
        latest_pred = self.prediction_repo.get_latest_by_user_id(user.id)
        latest_pred_data = None
        diet_plan_data = None
        risk_level = "Normal"
        health_score = 90

        if latest_pred:
            # Safely unpack 5-tuple from ML prediction engine
            _, _, _, recommendation, _ = predict_diabetes_risk({})
            pred_res = PredictionResponse.model_validate(latest_pred)
            pred_res.recommendation = recommendation
            latest_pred_data = pred_res.model_dump()

            if latest_pred.prediction == "Diabetic" or latest_pred.risk_percentage >= 50.0:
                risk_level = "High" if latest_pred.risk_percentage >= 75.0 else "Moderate"
                health_score = max(20, int(100 - latest_pred.risk_percentage))
            else:
                risk_level = "Low"
                health_score = min(98, int(100 - (latest_pred.risk_percentage * 0.5)))

            # Fetch active diet plan
            diet_obj = self.diet_repo.get_by_prediction_id(latest_pred.id)
            if diet_obj:
                diet_plan_data = {
                    "id": diet_obj.id,
                    "prediction_id": diet_obj.prediction_id,
                    "breakfast": diet_obj.breakfast,
                    "lunch": diet_obj.lunch,
                    "dinner": diet_obj.dinner,
                    "snacks": diet_obj.snacks,
                    "exercise": diet_obj.exercise,
                    "tips": diet_obj.tips,
                }

        # 3. Assessment History
        assessments = self.assessment_repo.get_by_user_id(user.id)
        history_data = [AssessmentResponse.model_validate(a).model_dump() for a in assessments]

        # 4. Health Summary Overview
        latest_a = assessments[0] if assessments else None
        latest_glu = getattr(latest_a, "fasting_glucose", None) or getattr(latest_a, "glucose", None) if latest_a else None

        health_summary = {
            "health_score": health_score,
            "risk_level": risk_level,
            "total_assessments": len(assessments),
            "latest_bmi": latest_a.bmi if latest_a else None,
            "latest_glucose": latest_glu,
            "latest_blood_pressure": latest_a.blood_pressure if latest_a else None,
            "last_assessed_at": latest_a.created_at.isoformat() if latest_a else None,
        }

        return {
            "user_profile": profile_data,
            "latest_prediction": latest_pred_data,
            "assessment_history": history_data,
            "health_summary": health_summary,
            "risk_level": risk_level,
            "diet_plan": diet_plan_data,
        }
