from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Operation successful",
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    Unified Success Response Wrapper with automatic JSON-safe encoding.
    """
    payload = {
        "success": True,
        "message": message,
        "data": jsonable_encoder(data),
    }
    return JSONResponse(status_code=status_code, content=payload)


def error_response(
    message: str = "An error occurred",
    errors: Optional[Any] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    """
    Unified Error Response Wrapper with automatic JSON-safe encoding.
    """
    payload = {
        "success": False,
        "message": message,
        "errors": jsonable_encoder(errors),
    }
    return JSONResponse(status_code=status_code, content=payload)
