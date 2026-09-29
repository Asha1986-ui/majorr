"""
Smart Assessment Routes — DiaSense AI
POST /api/smart-assessment/extract-report
"""
import os
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.medical_report_extractor import extract_from_report
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/api/smart-assessment", tags=["Smart Assessment"])

ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB


@router.post("/extract-report", status_code=status.HTTP_200_OK)
async def extract_medical_report(file: UploadFile = File(...)):
    """
    Accept a PDF or image medical report and extract diabetes-relevant health data.
    - Validates file type and size
    - Extracts text via pdfplumber / PyMuPDF
    - Falls back to OCR (pytesseract) for scanned PDFs and images
    - Returns extracted field values with confidence scores
    - Files are processed in-memory only and NOT stored permanently
    """
    # ── 1. File type validation ──────────────────────────────────────────────
    filename = file.filename or ""
    ext = os.path.splitext(filename.lower())[1]
    content_type = file.content_type or ""

    if ext not in ALLOWED_EXTENSIONS and content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Please upload a PDF, JPG, or PNG file.",
        )

    # ── 2. File size validation ──────────────────────────────────────────────
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum allowed size is 10 MB.",
        )

    if len(file_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File appears to be empty or corrupt. Please try a different file.",
        )

    # ── 3. Extract medical data ──────────────────────────────────────────────
    result = extract_from_report(file_bytes, filename, content_type)

    if not result["success"]:
        return success_response(
            data={
                "success": False,
                "extracted_fields": {},
                "source_type": result.get("source_type", "unknown"),
                "fields_found": 0,
            },
            message=result.get("error", "Could not extract information from this document."),
        )

    fields = result["extracted_fields"]
    return success_response(
        data={
            "success": True,
            "extracted_fields": fields,
            "source_type": result["source_type"],
            "fields_found": len(fields),
            "raw_text_preview": result.get("raw_text_preview", "")[:300],
        },
        message=f"Successfully extracted {len(fields)} health fields from your report.",
    )
