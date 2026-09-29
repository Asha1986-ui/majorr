from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.assessment import Assessment
from app.repositories.assessment_repository import AssessmentRepository
from app.schemas.assessment_schema import AssessmentCreateRequest, AssessmentResponse, AssessmentListResponse


class AssessmentService:
    """
    Business Logic Layer for Assessment Operations.
    Supports 14 Indian Diabetes clinical and lifestyle predictors with full backward compatibility.
    """
    def __init__(self, db: Session):
        self.db = db
        self.assessment_repo = AssessmentRepository(db)

    def create_assessment(self, user: User, request: AssessmentCreateRequest) -> AssessmentResponse:
        glu_val = request.fasting_glucose or request.glucose or 100.0

        assessment = Assessment(
            user_id=user.id,
            patient_group=request.patient_group or "Urban",
            gender=request.gender or user.gender or "Male",
            age=request.age or user.age or 35,
            bmi=request.bmi,
            blood_pressure=request.blood_pressure,
            hba1c=request.hba1c or 5.7,
            fasting_glucose=glu_val,
            physical_activity_hours=request.physical_activity_hours or 2.0,
            daily_sugar_intake=request.daily_sugar_intake or 30.0,
            fast_food_frequency=request.fast_food_frequency or 2.0,
            sleep_hours=request.sleep_hours or 7.0,
            family_history=request.family_history or 0.0,
            monthly_income=request.monthly_income or 35000.0,
            month=request.month or 6.0,
            # Legacy mapping
            glucose=glu_val,
            pregnancies=request.pregnancies or 0,
            skin_thickness=request.skin_thickness or 20.0,
            insulin=request.insulin or 80.0,
            diabetes_pedigree_function=request.diabetes_pedigree_function or 0.45,
        )
        saved = self.assessment_repo.create(assessment)

        # Auto-update User Profile Age and Gender if changed or not set
        try:
            user.age = request.age
            if request.gender:
                user.gender = request.gender
            elif request.pregnancies and request.pregnancies > 0:
                user.gender = "Female"
            self.db.add(user)
            self.db.commit()
        except Exception:
            pass

        return AssessmentResponse.model_validate(saved)

    def get_assessment_history(self, user: User) -> AssessmentListResponse:
        assessments = self.assessment_repo.get_by_user_id(user.id)
        items = []
        for a in assessments:
            # Ensure fallback if legacy record has glucose instead of fasting_glucose
            resp_item = AssessmentResponse.model_validate(a)
            if resp_item.fasting_glucose is None and a.glucose is not None:
                resp_item.fasting_glucose = a.glucose
            items.append(resp_item)
        return AssessmentListResponse(total=len(items), assessments=items)

    def get_assessment_by_id(self, user: User, assessment_id: int) -> AssessmentResponse:
        assessment = self.assessment_repo.get_by_id(assessment_id)
        if not assessment or assessment.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment record not found or access denied",
            )
        return AssessmentResponse.model_validate(assessment)

    def delete_assessment(self, user: User, assessment_id: int) -> None:
        assessment = self.assessment_repo.get_by_id(assessment_id)
        if not assessment or assessment.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment record not found or access denied",
            )
        self.assessment_repo.delete(assessment)
