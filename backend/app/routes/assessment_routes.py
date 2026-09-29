from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.schemas.assessment_schema import AssessmentCreateRequest
from app.services.assessment_service import AssessmentService
from app.utils.response import success_response

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_assessment(
    request: AssessmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new health assessment record.
    """
    service = AssessmentService(db)
    result = service.create_assessment(current_user, request)
    return success_response(
        data=result,
        message="Assessment recorded successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/history", status_code=status.HTTP_200_OK)
def get_assessment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve all previous assessment records for authenticated user.
    """
    service = AssessmentService(db)
    result = service.get_assessment_history(current_user)
    return success_response(
        data=result,
        message="Assessment history retrieved successfully",
    )


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_assessment_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve specific assessment record by ID.
    """
    service = AssessmentService(db)
    result = service.get_assessment_by_id(current_user, id)
    return success_response(
        data=result,
        message="Assessment details retrieved successfully",
    )


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_assessment(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete specific assessment record by ID.
    """
    service = AssessmentService(db)
    service.delete_assessment(current_user, id)
    return success_response(
        data={"id": id},
        message="Assessment record deleted successfully",
    )
