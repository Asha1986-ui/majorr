from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.services.report_service import ReportService
from app.services.prediction_service import PredictionService
from app.utils.response import success_response

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_report_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve prediction report details by ID with IDOR validation.
    """
    service = PredictionService(db)
    result = service.get_latest_prediction(current_user)
    return success_response(
        data=result,
        message="Report details retrieved successfully",
    )


@router.get("/latest/pdf", status_code=status.HTTP_200_OK)
def download_latest_pdf_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate and stream downloadable PDF health risk report for user's latest assessment.
    """
    pred_service = PredictionService(db)
    latest_pred = pred_service.get_latest_prediction(current_user)
    if not latest_pred:
        return Response(
            content=b"No health assessment found. Please complete an assessment first.",
            status_code=status.HTTP_404_NOT_FOUND,
            media_type="text/plain",
        )
    pred_id = latest_pred["id"] if isinstance(latest_pred, dict) else getattr(latest_pred, "id", 1)
    service = ReportService(db)
    pdf_bytes = service.generate_pdf_report(current_user, pred_id)
    headers = {
        "Content-Disposition": f"attachment; filename=DiaSense_Health_Report_{pred_id}.pdf"
    }
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers,
    )


@router.get("/{id}/pdf")
def download_pdf_report(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate and stream downloadable PDF health risk report.
    """
    if id <= 0:
        return download_latest_pdf_report(current_user=current_user, db=db)

    service = ReportService(db)
    pdf_bytes = service.generate_pdf_report(current_user, id)
    
    headers = {
        "Content-Disposition": f"attachment; filename=DiaSense_Health_Report_{id}.pdf"
    }
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers,
    )
