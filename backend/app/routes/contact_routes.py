from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.contact import ContactMessage
from app.schemas.contact_schema import ContactMessageRequest, ContactMessageResponse
from app.services.email_service import EmailService
from app.utils.response import success_response

router = APIRouter(prefix="/api/contact", tags=["Contact"])


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_contact_message(
    request: ContactMessageRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a user inquiry / contact form message and trigger admin email notification
    to gagankamati643@gmail.com.
    """
    message_obj = ContactMessage(
        name=request.name,
        email=request.email.lower().strip(),
        subject=request.subject,
        message=request.message,
    )
    db.add(message_obj)
    db.commit()
    db.refresh(message_obj)

    # Trigger admin email notification to gagankamati643@gmail.com
    email_service = EmailService()
    email_service.send_contact_notification(
        name=request.name,
        email=request.email,
        subject=request.subject,
        message=request.message,
    )

    response_data = ContactMessageResponse.model_validate(message_obj).model_dump()
    return success_response(
        data=response_data,
        message="Thank you for your message. Your inquiry has been sent to gagankamati643@gmail.com and recorded!",
        status_code=status.HTTP_201_CREATED,
    )
