from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserProfileUpdateRequest, UserPasswordChangeRequest
from app.utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["User Profile"])


@router.get("/me")
def get_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current logged in user details.
    """
    service = AuthService(db)
    profile = service.get_profile(current_user)
    return success_response(data=profile.model_dump(mode="json"), message="Current user profile retrieved")


@router.get("/profile")
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current user profile with complete screening stats and assessment count.
    """
    service = AuthService(db)
    profile_stats = service.get_profile_with_stats(current_user)
    return success_response(data=profile_stats.model_dump(mode="json"), message="User profile and stats retrieved")


@router.put("/profile")
def update_user_profile(
    request: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile information (full_name, age, gender).
    """
    service = AuthService(db)
    updated_profile = service.update_profile(current_user, request)
    return success_response(data=updated_profile.model_dump(mode="json"), message="Profile updated successfully")


@router.put("/change-password")
def change_user_password(
    request: UserPasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user account password after validating current password.
    """
    service = AuthService(db)
    service.change_password(current_user, request)
    return success_response(message="Password changed successfully")
