from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.utils.response import success_response

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", status_code=status.HTTP_200_OK)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve comprehensive user dashboard metrics, profile, latest prediction, assessment history, health summary, and diet plan.
    """
    service = DashboardService(db)
    data = service.get_dashboard_data(current_user)
    return success_response(
        data=data,
        message="Dashboard data retrieved successfully",
    )
