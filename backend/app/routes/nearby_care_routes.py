from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.services.nearby_care_service import NearbyCareService
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/api/nearby-care", tags=["Nearby Healthcare Facilities"])
care_service = NearbyCareService()


@router.get("", status_code=status.HTTP_200_OK)
def get_nearby_care_facilities(
    latitude: Optional[float] = Query(None, description="User GPS latitude coordinate"),
    longitude: Optional[float] = Query(None, description="User GPS longitude coordinate"),
    type: str = Query("hospital", description="Facility type: 'hospital' or 'laboratory'"),
    radius: int = Query(5000, description="Search radius in meters (500 to 50000)"),
    query: Optional[str] = Query(None, description="Optional manual location query (City, Locality, PIN)"),
    current_user: User = Depends(get_current_user),
):
    """
    Find real nearby hospitals, clinics, or diabetes diagnostic laboratories
    based on coordinates or a geocoded location query. Accessible only to authenticated users.
    """
    resolved_lat = latitude
    resolved_lon = longitude
    location_name = None

    # If manual location search query is provided, geocode it
    if query and query.strip():
        geocode_res = care_service.geocode_location(query.strip())
        if not geocode_res:
            return error_response(
                message=f"Unable to locate '{query.strip()}'. Please verify the city or area name.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        resolved_lat = geocode_res.latitude
        resolved_lon = geocode_res.longitude
        location_name = geocode_res.display_name

    if resolved_lat is None or resolved_lon is None:
        return error_response(
            message="Location coordinates (latitude and longitude) or a valid location query must be provided.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Validate coordinate ranges
    if not (-90.0 <= resolved_lat <= 90.0) or not (-180.0 <= resolved_lon <= 180.0):
        return error_response(
            message="Invalid geographical coordinates provided.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    clean_type = "laboratory" if "lab" in type.lower() else "hospital"
    clean_radius = max(500, min(radius, 50000))

    result = care_service.get_nearby_facilities(
        latitude=resolved_lat,
        longitude=resolved_lon,
        facility_type=clean_type,
        radius_meters=clean_radius,
        location_name=location_name,
    )

    return success_response(
        data=result.model_dump(),
        message=f"Found {result.total_count} real nearby {result.facility_type} facilities.",
    )


@router.get("/geocode", status_code=status.HTTP_200_OK)
def geocode_manual_location(
    query: str = Query(..., min_length=2, description="City, Area, or PIN code to geocode"),
    current_user: User = Depends(get_current_user),
):
    """
    Geocode manual location text to latitude and longitude coordinates.
    """
    res = care_service.geocode_location(query.strip())
    if not res:
        return error_response(
            message=f"Could not find coordinates for '{query.strip()}'. Please try a nearby city or area.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return success_response(
        data=res.model_dump(),
        message="Location successfully geocoded.",
    )
