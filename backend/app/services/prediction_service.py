"""
Prediction Service v2 — India Diabetes Dataset
Uses the new v2 pipeline (diabetes_pipeline_v2.pkl) and new assessment schema.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.assessment import Assessment
from app.models.prediction import Prediction
from app.models.diet_plan import DietPlan
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.diet_repository import DietRepository
from app.schemas.prediction_schema import PredictionRequest, PredictionResponse, PredictionListResponse
from app.ml.prediction_v2 import predict_diabetes_risk
from app.utils.i18n import localize_recommendation, localize_diet_plan, normalize_lang


def _build_assessment_data(request) -> dict:
    """Map PredictionRequest (new schema) to the dict expected by prediction_v2."""
    return {
        "patient_group":            getattr(request, "patient_group", None),
        "age":                      getattr(request, "age", None),
        "gender":                   getattr(request, "gender", None),
        "bmi":                      getattr(request, "bmi", None),
        "blood_pressure":           getattr(request, "blood_pressure", None),
        "physical_activity_hours":  getattr(request, "physical_activity_hours", None),
        "daily_sugar_intake":       getattr(request, "daily_sugar_intake", None),
        "fast_food_frequency":      getattr(request, "fast_food_frequency", None),
        "sleep_hours":              getattr(request, "sleep_hours", None),
        "hba1c":                    getattr(request, "hba1c", None),
        "fasting_glucose":          getattr(request, "fasting_glucose", None),
        "family_history":           getattr(request, "family_history", None),
        "monthly_income":           getattr(request, "monthly_income", None),
        "month":                    getattr(request, "month", None),
    }


def _assessment_obj_to_data(assessment: Assessment) -> dict:
    """Extract assessment ORM object fields into a data dict for inference."""
    return {
        "patient_group":            assessment.patient_group,
        "age":                      assessment.age,
        "gender":                   assessment.gender,
        "bmi":                      assessment.bmi,
        "blood_pressure":           assessment.blood_pressure,
        "physical_activity_hours":  assessment.physical_activity_hours,
        "daily_sugar_intake":       assessment.daily_sugar_intake,
        "fast_food_frequency":      assessment.fast_food_frequency,
        "sleep_hours":              assessment.sleep_hours,
        "hba1c":                    assessment.hba1c,
        "fasting_glucose":          assessment.fasting_glucose,
        "family_history":           assessment.family_history,
        "monthly_income":           assessment.monthly_income,
        "month":                    assessment.month,
    }


class PredictionService:
    """
    Business Logic Layer for Indian Diabetes ML Risk Prediction and Tailored Indian Diet Plan Generation.
    """

    def __init__(self, db: Session):
        self.db = db
        self.assessment_repo = AssessmentRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.diet_repo = DietRepository(db)

    def _extract_assessment_dict(self, obj) -> dict:
        fh = getattr(obj, "family_history", None)
        if fh is None:
            fh_val = 0.0
        elif isinstance(fh, str):
            fh_val = 1.0 if fh.strip().lower() in ("yes", "true", "1", "positive") else 0.0
        else:
            try:
                fh_val = float(fh)
            except (ValueError, TypeError):
                fh_val = 0.0

        def _val(attr_name, default):
            v = getattr(obj, attr_name, None)
            if v is None:
                return default
            try:
                return float(v)
            except (ValueError, TypeError):
                return default

        fasting_glu = getattr(obj, "fasting_glucose", None)
        if fasting_glu is None:
            fasting_glu = getattr(obj, "glucose", None)
        if fasting_glu is None:
            fasting_glu = 100.0
        else:
            try:
                fasting_glu = float(fasting_glu)
            except (ValueError, TypeError):
                fasting_glu = 100.0

        return {
            "patient_group": getattr(obj, "patient_group", None) or "Urban",
            "gender": getattr(obj, "gender", None) or "Male",
            "age": int(_val("age", 35)),
            "bmi": _val("bmi", 24.5),
            "physical_activity_hours": _val("physical_activity_hours", 2.0),
            "daily_sugar_intake": _val("daily_sugar_intake", 30.0),
            "fast_food_frequency": _val("fast_food_frequency", 2.0),
            "sleep_hours": _val("sleep_hours", 7.0),
            "family_history": fh_val,
            "blood_pressure": _val("blood_pressure", 120.0),
            "hba1c": _val("hba1c", 5.7),
            "fasting_glucose": fasting_glu,
            "monthly_income": _val("monthly_income", 35000.0),
            "month": _val("month", 6.0),
        }

    def create_prediction(self, user: Optional[User], request: PredictionRequest, lang: str = "en") -> PredictionResponse:
        assessment_dict = self._extract_assessment_dict(request)

        # Handle Guest (Unauthenticated) Assessment Submissions
        if user is None:
            pred_label, risk_pct, confidence, recommendation, contributing_factors = predict_diabetes_risk(assessment_dict, lang=lang)
            return PredictionResponse(
                id=0,
                assessment_id=0,
                prediction=pred_label,
                risk_percentage=risk_pct,
                confidence=confidence,
                recommendation=recommendation,
                contributing_factors=contributing_factors,
                created_at=datetime.utcnow(),
            )

        # ── Authenticated path ───────────────────────────────────────────────
        # Step 1: Resolve or create Assessment
        assessment = None
        if getattr(request, "assessment_id", None):
            assessment = self.assessment_repo.get_by_id(request.assessment_id)
            if assessment and assessment.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to requested assessment record",
                )

        if not assessment:
            # Auto-create assessment record
            assessment = Assessment(
                user_id=user.id,
                patient_group=assessment_dict["patient_group"],
                gender=assessment_dict["gender"] or user.gender or "Male",
                age=assessment_dict["age"] or user.age or 35,
                bmi=assessment_dict["bmi"],
                blood_pressure=assessment_dict["blood_pressure"],
                hba1c=assessment_dict["hba1c"],
                fasting_glucose=assessment_dict["fasting_glucose"],
                physical_activity_hours=assessment_dict["physical_activity_hours"],
                daily_sugar_intake=assessment_dict["daily_sugar_intake"],
                fast_food_frequency=assessment_dict["fast_food_frequency"],
                sleep_hours=assessment_dict["sleep_hours"],
                family_history=assessment_dict["family_history"],
                monthly_income=assessment_dict["monthly_income"],
                month=assessment_dict["month"],
                # Legacy fields mapping
                glucose=assessment_dict["fasting_glucose"],
                pregnancies=getattr(request, "pregnancies", 0) or 0,
                skin_thickness=getattr(request, "skin_thickness", 20.0) or 20.0,
                insulin=getattr(request, "insulin", 80.0) or 80.0,
                diabetes_pedigree_function=getattr(request, "diabetes_pedigree_function", 0.45) or 0.45,
            )
            assessment = self.assessment_repo.create(assessment)

        # Step 2: Run ML inference
        pred_dict = self._extract_assessment_dict(assessment)
        pred_label, risk_pct, confidence, recommendation, contributing_factors = predict_diabetes_risk(pred_dict, lang=lang)

        # Step 3: Save Prediction entity
        prediction_obj = Prediction(
            assessment_id=assessment.id,
            prediction=pred_label,
            risk_percentage=risk_pct,
            confidence=confidence,
        )
        saved_prediction = self.prediction_repo.create(prediction_obj)

        # Step 4: Automatically generate & store Tailored Indian Diet Plan
        try:
            self._generate_and_save_diet_plan(
                saved_prediction.id,
                pred_label,
                risk_pct,
                assessment_dict["fasting_glucose"],
                assessment_dict["hba1c"],
                assessment_dict["bmi"]
            )
        except Exception:
            pass

        return PredictionResponse(
            id=saved_prediction.id,
            assessment_id=assessment.id,
            prediction=pred_label,
            risk_percentage=risk_pct,
            confidence=confidence,
            recommendation=recommendation,
            contributing_factors=contributing_factors,
            created_at=saved_prediction.created_at,
        )

    def get_latest_prediction(self, user: User, lang: str = "en") -> PredictionResponse:
        latest = self.prediction_repo.get_latest_by_user_id(user.id)
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No prediction records found for user",
            )
        
        assessment_dict = {}
        if latest.assessment:
            assessment_dict = self._extract_assessment_dict(latest.assessment)

        pred_label, risk_pct, confidence, recommendation, contributing_factors = predict_diabetes_risk(assessment_dict, lang=lang)

        return PredictionResponse(
            id=latest.id,
            assessment_id=latest.assessment_id,
            prediction=latest.prediction,
            risk_percentage=latest.risk_percentage,
            confidence=latest.confidence,
            recommendation=recommendation,
            contributing_factors=contributing_factors,
            created_at=latest.created_at,
        )

    def get_prediction_history(self, user: User, lang: str = "en") -> PredictionListResponse:
        predictions = self.prediction_repo.get_history_by_user_id(user.id)
        items = []
        for p in predictions:
            item = PredictionResponse.model_validate(p)
            item.recommendation = "Follow medical lifestyle recommendations provided."
            items.append(item)
        return PredictionListResponse(total=len(items), predictions=items)

    def _generate_and_save_diet_plan(self, prediction_id: int, label: str, risk_pct: float, glucose: float, hba1c: float, bmi: float) -> DietPlan:
        if label == "Diabetic" or label == "Higher Risk Pattern" or risk_pct >= 45.0 or glucose >= 126.0 or hba1c >= 6.5:
            breakfast = "Oats & Ragi Dosa (2 pcs) with Mint Chutney, 1 Boiled Egg / Paneer Bhurji (Low-GI Indian Breakfast)."
            lunch = "Moong Dal & Spinach Khichdi with 1 cup Cucumber Raita and Sprouted Chana Salad."
            dinner = "Palak Paneer with 2 Bajra/Multigrain Rotis and Steamed Lauki/Turai Subzi."
            snacks = "1 cup Roasted Makhana (Fox Nuts) with Green Tea or Sprouted Moong Salad."
            exercise = "30-45 mins Brisk Walking, 15 mins Surya Namaskar & Light Resistance Training 5 days/week."
            tips = "Limit polished white rice, replace with Brown Rice/Ragi/Bajra. Drink 3L water daily and eliminate sugary chai."
        else:
            breakfast = "Methi Paratha (1 pc with curd) or Vegetable Oats Upma with 1 Boiled Egg."
            lunch = "Brown Rice Bowl with Rajma/Chole, Mixed Green Salad, and Cucumber Raita."
            dinner = "Tandoori Chicken / Paneer Tikka with Grilled Vegetables and 1 Whole Wheat Roti."
            snacks = "Roasted Chana, Apple Slices with Peanut Butter, or Handful of Almonds & Walnuts."
            exercise = "150 minutes of moderate-intensity activity (Brisk Walk, Jogging, Yoga) per week."
            tips = "Maintain consistent sleep schedule, practice stress management through Pranayama, and maintain balanced portion control."

        diet_plan = DietPlan(
            prediction_id=prediction_id,
            breakfast=breakfast,
            lunch=lunch,
            dinner=dinner,
            snacks=snacks,
            exercise=exercise,
            tips=tips,
        )
        return self.diet_repo.create(diet_plan)
