from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.services.diet_service import DietService
from app.utils.response import success_response

router = APIRouter(prefix="/api/diet", tags=["Diet Plan"])


@router.get("/latest", status_code=status.HTTP_200_OK)
def get_latest_diet_plan(
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en", alias="Accept-Language"),
    db: Session = Depends(get_db),
):
    """
    Retrieve latest personalized diet and exercise plan for authenticated user in requested language.
    """
    service = DietService(db)
    result = service.get_latest_diet_plan(current_user, lang=accept_language)
    return success_response(
        data=result,
        message="Latest diet plan retrieved successfully",
    )


@router.get("/{prediction_id}", status_code=status.HTTP_200_OK)
def get_diet_plan_by_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en", alias="Accept-Language"),
    db: Session = Depends(get_db),
):
    """
    Retrieve personalized diet plan for a specific prediction ID in requested language.
    """
    service = DietService(db)
    result = service.get_diet_plan_by_prediction_id(current_user, prediction_id, lang=accept_language)
    return success_response(
        data=result,
        message="Diet plan retrieved successfully",
    )
