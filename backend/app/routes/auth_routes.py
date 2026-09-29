from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.schemas.auth_schema import UserRegisterRequest, UserLoginRequest
from app.schemas.user_schema import UserProfileUpdateRequest
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account and issue JWT tokens.
    """
    service = AuthService(db)
    result = service.register(request)
    return success_response(
        data=result.model_dump(mode="json"),
        message="User registered successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/login", status_code=status.HTTP_200_OK)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user credentials and issue JWT tokens.
    """
    service = AuthService(db)
    result = service.login(request)
    return success_response(
        data=result.model_dump(mode="json"),
        message="Login successful",
    )


@router.get("/profile", status_code=status.HTTP_200_OK)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieve authenticated user's profile details.
    """
    service = AuthService(db)
    profile = service.get_profile(current_user)
    return success_response(
        data=profile.model_dump(mode="json"),
        message="User profile retrieved successfully",
    )


@router.put("/profile", status_code=status.HTTP_200_OK)
def update_profile(
    request: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update authenticated user's profile information.
    """
    service = AuthService(db)
    updated_profile = service.update_profile(current_user, request)
    return success_response(
        data=updated_profile.model_dump(mode="json"),
        message="User profile updated successfully",
    )
