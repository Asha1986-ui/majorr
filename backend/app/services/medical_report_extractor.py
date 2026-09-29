"""
Medical Report Extractor Service — DiaSense AI
Extracts diabetes-relevant health data from PDF and image medical reports.
"""
import io
import re
import os
import sys
import zlib
import logging
from typing import Optional, Dict, Any

# Automatically include backend/.venv site-packages if present so PDF/OCR libraries
# are always discoverable even when launched via system Python.
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _venv_sp in (
    os.path.join(_BACKEND_DIR, ".venv", "Lib", "site-packages"),
    os.path.join(_BACKEND_DIR, "venv", "Lib", "site-packages"),
):
    if os.path.isdir(_venv_sp) and _venv_sp not in sys.path:
        sys.path.insert(0, _venv_sp)

logger = logging.getLogger(__name__)

# ── Field validation ranges (matching prediction_schema.py) ──────────────────
FIELD_RANGES = {
    "age":                    (1.0,   110.0),
    "height":                 (100.0, 230.0),
    "weight":                 (20.0,  250.0),
    "bmi":                    (10.0,  70.0),
    "blood_pressure":         (50.0,  240.0),
    "physical_activity_hours":(0.0,   20.0),
    "daily_sugar_intake":     (0.0,   200.0),
    "fast_food_frequency":    (0.0,   21.0),
    "sleep_hours":            (2.0,   16.0),
    "hba1c":                  (3.0,   20.0),
    "fasting_glucose":        (50.0,  450.0),
    "family_history":         (0.0,   1.0),
    "monthly_income":         (0.0,   2000000.0),
}

GENDER_MAP = {"male": "Male", "female": "Female", "m": "Male", "f": "Female"}
PATIENT_GROUP_MAP = {
    "urban": "Urban",
    "rural": "Rural",
    "semi-urban": "Semi-Urban",
    "semiurban": "Semi-Urban",
}
FAMILY_HISTORY_YES = {"yes", "positive", "present", "1", "true", "यस", "हाँ"}
FAMILY_HISTORY_NO  = {"no", "negative", "absent", "0", "false", "none", "नहीं", "नहि"}


# ─────────────────────────────────────────────────────────────────────────────
# TEXT EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def _pure_python_pdf_text(file_bytes: bytes) -> str:
    """Fallback pure-Python PDF stream text extractor using zlib."""
    chunks = []
    try:
        for match in re.finditer(rb"stream[\r\n]+(.*?)[\r\n]+endstream", file_bytes, re.DOTALL):
            stream_data = match.group(1)
            try:
                decompressed = zlib.decompress(stream_data)
            except Exception:
                try:
                    decompressed = zlib.decompress(stream_data.strip(b"\r\n"))
                except Exception:
                    continue
            decoded = decompressed.decode("latin-1", errors="ignore")
            # Extract parenthesized strings (...) in BT/ET blocks
            for txt_match in re.finditer(r"\(([^()\\]*(?:\\.[^()\\]*)*)\)", decoded):
                s = txt_match.group(1)
                s = s.replace(r"\(", "(").replace(r"\)", ")").replace(r"\\", "\\")
                if s.strip():
                    chunks.append(s)
    except Exception as exc:
        logger.warning("Pure-Python PDF parser failed: %s", exc)
    return " ".join(chunks)


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Try PyMuPDF (fitz), pdfplumber, pypdf, and pure-Python fallback."""
    text = ""

    # 1. PyMuPDF (pymupdf) — fast and preserves reading order well
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        if text.strip():
            logger.info("PDF text extracted via PyMuPDF (%d chars)", len(text))
            return text
    except Exception as exc:
        logger.warning("PyMuPDF failed: %s", exc)

    # 2. pdfplumber fallback (including table extraction)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                for table in (page.extract_tables() or []):
                    for row in table:
                        if row:
                            text += " ".join(str(cell or "").strip() for cell in row) + "\n"
        if text.strip():
            logger.info("PDF text extracted via pdfplumber (%d chars)", len(text))
            return text
    except Exception as exc:
        logger.warning("pdfplumber failed: %s", exc)

    # 3. pypdf fallback
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            logger.info("PDF text extracted via pypdf (%d chars)", len(text))
            return text
    except Exception as exc:
        logger.warning("pypdf failed: %s", exc)

    # 4. Pure-Python zlib stream fallback
    text = _pure_python_pdf_text(file_bytes)
    if text.strip():
        logger.info("PDF text extracted via pure-Python parser (%d chars)", len(text))
    return text


def _ocr_image_bytes(img_bytes: bytes) -> str:
    """OCR image bytes using RapidOCR (no external binary required) or pytesseract."""
    # 1. RapidOCR (self-contained ONNX runtime OCR)
    try:
        from rapidocr_onnxruntime import RapidOCR
        ocr_engine = RapidOCR()
        result, _ = ocr_engine(img_bytes)
        if result:
            lines = [item[1] for item in result if len(item) >= 2 and item[1]]
            text = "\n".join(lines)
            if text.strip():
                logger.info("Image OCR completed via RapidOCR (%d chars)", len(text))
                return text
    except Exception as exc:
        logger.warning("RapidOCR failed: %s", exc)

    # 2. pytesseract fallback
    try:
        import pytesseract
        from PIL import Image
        for tesseract_path in (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ):
            if os.path.isfile(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                break
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img, lang="eng")
        if text.strip():
            logger.info("Image OCR completed via pytesseract (%d chars)", len(text))
            return text
    except Exception as exc:
        logger.warning("pytesseract OCR failed: %s", exc)

    return ""


def _extract_text_from_image_bytes(file_bytes: bytes, content_type: str) -> str:
    """OCR an image using RapidOCR or pytesseract."""
    return _ocr_image_bytes(file_bytes)


def _pdf_needs_ocr(text: str) -> bool:
    """Returns True if extracted text looks like a scanned/empty PDF."""
    return len(text.strip()) < 40


def _ocr_pdf_pages(file_bytes: bytes) -> str:
    """Rasterise PDF pages and OCR them."""
    text = ""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            png_bytes = pix.tobytes("png")
            text += _ocr_image_bytes(png_bytes) + "\n"
        doc.close()
        logger.info("PDF OCR completed (%d chars)", len(text))
    except Exception as exc:
        logger.warning("PDF OCR failed: %s", exc)
    return text


# ─────────────────────────────────────────────────────────────────────────────
# MEDICAL FIELD EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def _parse_float(s: str) -> Optional[float]:
    try:
        return float(re.sub(r"[^\d.]", "", s))
    except (ValueError, TypeError):
        return None


def _confidence(value: Optional[float], field: str) -> str:
    if value is None:
        return "LOW"
    lo, hi = FIELD_RANGES.get(field, (None, None))
    if lo is None:
        return "HIGH"
    if lo <= value <= hi:
        return "HIGH"
    # Allow ±15% outside range → MEDIUM
    if (lo * 0.85) <= value <= (hi * 1.15):
        return "MEDIUM"
    return "LOW"


# Pattern registry: each entry → (field_key, regex, transform)
# Handles standard clinical lab formats, tabular layouts, and DiaSense AI reports.
_PATTERNS = [
    # Fasting Glucose
    ("fasting_glucose", r"fasting\s*(?:blood\s*)?(?:glucose|sugar)(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:mg[/\s]?dl)?", None),
    ("fasting_glucose", r"\b(?:fbg|fbs)\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:mg[/\s]?dl)?", None),
    ("fasting_glucose", r"blood\s*glucose(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:mg[/\s]?dl)?", None),
    ("fasting_glucose", r"\bglucose\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:mg[/\s]?dl)?", None),

    # HbA1c
    ("hba1c", r"hba1c(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*%?", None),
    ("hba1c", r"glycated\s+h(?:ae|e)moglobin(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*%?", None),
    ("hba1c", r"glycosylated\s+h(?:ae|e)moglobin(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*%?", None),
    ("hba1c", r"\ba1c\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*%?", None),

    # Blood Pressure (systolic from 120/80, or single recorded value like 120 mmHg / 74.0 mmHg)
    ("blood_pressure", r"blood\s*pressure(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*/\s*\d+(?:\.\d+)?\s*(?:mmhg)?", None),
    ("blood_pressure", r"\bbp\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*/\s*\d+(?:\.\d+)?\s*(?:mmhg)?", None),
    ("blood_pressure", r"systolic(?:\s*bp|\s*blood\s*pressure)?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:mmhg)?", None),
    ("blood_pressure", r"blood\s*pressure(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*mmhg", None),
    ("blood_pressure", r"\bbp\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*mmhg", None),

    # BMI
    ("bmi", r"\bbmi\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:kg[/\s]?m[\u00b2²2]?)?", None),
    ("bmi", r"body\s+mass\s+index\s*\)?[:\s\-]+(\d+(?:\.\d+)?)", None),

    # Height & Weight
    ("height", r"\bheight\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:cm|centimeters?)?", None),
    ("weight", r"\bweight\b(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)?", None),

    # Age (supports "Age: 34", "Age / Gender: 34 yrs / Male", "Age/Sex: 34/M")
    ("age", r"\bage\s*(?:/\s*(?:gender|sex))?\s*[:\-]\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)?", None),
    ("age", r"\bage\b[:\s\-]+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)?", None),
    ("age", r"(\d{1,3})\s*(?:years?|yrs?)\s*/\s*(?:male|female|m|f)\b", None),

    # Sleep
    ("sleep_hours", r"sleep(?:\s+duration)?(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)?", None),

    # Physical Activity
    ("physical_activity_hours", r"physical\s*activity(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)(?:\s*/\s*day)?", None),
    ("physical_activity_hours", r"exercise(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)(?:\s*/\s*day)?", None),

    # Sugar intake
    ("daily_sugar_intake", r"(?:daily\s+)?sugar\s*intake(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:g(?:rams?)?(?:/day)?)?", None),

    # Fast food frequency
    ("fast_food_frequency", r"fast\s*food(?:\s+frequency)?(?:\s*\([^)]*\))?[:\s\-]+(\d+(?:\.\d+)?)\s*(?:times?|meals?)?", None),

    # Monthly Income
    ("monthly_income", r"monthly\s*(?:household\s*)?income[:\s\-]+(?:rs\.?|inr\.?|₹)?\s*(\d+(?:\.\d+)?)", None),
    ("monthly_income", r"\bincome\b[:\s\-]+(?:rs\.?|inr\.?|₹)?\s*(\d+(?:\.\d+)?)", None),
]

_NAME_PATTERN = re.compile(
    r"patient\s*name\s*[:\-]\s*([A-Za-z][A-Za-z\s.]{1,40}?)(?=\s+(?:report\s*id|email|age|gender|sex|date|patient|id)\b|\r|\n|$)",
    re.IGNORECASE,
)
_GENDER_PATTERNS = [
    re.compile(r"\bage\s*/\s*(?:gender|sex)\s*[:\-]\s*\d+\s*(?:years?|yrs?)?\s*/\s*(male|female|m|f)\b", re.IGNORECASE),
    re.compile(r"\b(?:gender|sex)\s*[:\-]\s*(male|female|m|f)\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*(?:years?|yrs?)\s*/\s*(male|female)\b", re.IGNORECASE),
]
_FH_PATTERN = re.compile(
    r"family\s*history(?:\s*of\s*diabetes)?[:\s\-]+([^\r\n]+)",
    re.IGNORECASE,
)
_PEDIGREE_PATTERN = re.compile(
    r"diabetes\s*pedigree\s*(?:score|function)?[:\s\-]+(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)
_PG_PATTERN = re.compile(r"\b(semi-urban|semiurban|urban|rural)\b", re.IGNORECASE)


def _extract_fields(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns dict of { field_name: { value, confidence, raw } }
    Only fields actually found in the text are returned.
    """
    # Normalize whitespace while preserving newlines for line-anchored patterns
    normalized = re.sub(r"[ \t]+", " ", text)
    lower = normalized.lower()
    results: Dict[str, Dict[str, Any]] = {}

    # 1. Patient Full Name
    nm = _NAME_PATTERN.search(normalized)
    if nm:
        full_name = nm.group(1).strip()
        if len(full_name) >= 2:
            results["full_name"] = {"value": full_name, "confidence": "HIGH", "raw": nm.group(0).strip()}

    # 2. Numeric Clinical & Lifestyle Fields
    for field, pattern, transform in _PATTERNS:
        if field in results:          # already captured with higher-priority pattern
            continue
        m = re.search(pattern, lower, re.IGNORECASE)
        if m:
            raw = m.group(1)
            value = _parse_float(raw) if transform is None else transform(raw)
            if value is not None:
                conf = _confidence(value, field)
                if conf != "LOW":
                    # Format integer-like values cleanly if appropriate
                    if field in ("age", "fast_food_frequency") and float(value).is_integer():
                        value = int(value)
                    results[field] = {"value": value, "confidence": conf, "raw": m.group(0).strip()}

    # 3. Gender
    for pat in _GENDER_PATTERNS:
        gm = pat.search(normalized)
        if gm:
            gval = GENDER_MAP.get(gm.group(1).strip().lower())
            if gval:
                results["gender"] = {"value": gval, "confidence": "HIGH", "raw": gm.group(0).strip()}
                break

    # 4. Family History (explicit Yes/No/Positive/Negative OR Diabetes Pedigree Score)
    fhm = _FH_PATTERN.search(normalized)
    if fhm:
        answer = fhm.group(1).strip().lower()
        if any(re.search(rf"\b{re.escape(k)}\b", answer) for k in FAMILY_HISTORY_YES):
            results["family_history"] = {"value": 1, "confidence": "HIGH", "raw": fhm.group(0).strip()}
        elif any(re.search(rf"\b{re.escape(k)}\b", answer) for k in FAMILY_HISTORY_NO):
            results["family_history"] = {"value": 0, "confidence": "HIGH", "raw": fhm.group(0).strip()}

    if "family_history" not in results:
        pm = _PEDIGREE_PATTERN.search(normalized)
        if pm:
            ped_val = _parse_float(pm.group(1))
            if ped_val is not None:
                fh_val = 1 if ped_val >= 0.5 else 0
                results["family_history"] = {"value": fh_val, "confidence": "MEDIUM", "raw": pm.group(0).strip()}

    # 5. Patient Group / Region
    pgm = _PG_PATTERN.search(normalized)
    if pgm:
        pgval = PATIENT_GROUP_MAP.get(pgm.group(1).strip().lower(), "Urban")
        results["patient_group"] = {"value": pgval, "confidence": "HIGH", "raw": pgm.group(0).strip()}

    return results


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def extract_from_report(file_bytes: bytes, filename: str, content_type: str) -> Dict[str, Any]:
    """
    Main entry point. Returns:
    {
        "success": bool,
        "source_type": "pdf_text" | "pdf_ocr" | "image_ocr",
        "raw_text_preview": str,          # first 500 chars of extracted text
        "extracted_fields": {
            field_name: { "value": ..., "confidence": "HIGH"|"MEDIUM", "raw": "..." }
        },
        "error": str | None
    }
    """
    fn_lower = filename.lower()
    ct_lower = (content_type or "").lower()

    try:
        if fn_lower.endswith(".pdf") or "pdf" in ct_lower:
            text = _extract_text_from_pdf(file_bytes)
            source_type = "pdf_text"
            if _pdf_needs_ocr(text):
                ocr_text = _ocr_pdf_pages(file_bytes)
                if ocr_text.strip():
                    text = ocr_text
                    source_type = "pdf_ocr"
        else:
            # image
            text = _extract_text_from_image_bytes(file_bytes, content_type)
            source_type = "image_ocr"

        if not text.strip():
            return {
                "success": False,
                "source_type": source_type,
                "raw_text_preview": "",
                "extracted_fields": {},
                "error": "Could not read any text from this document. Please enter values manually.",
            }

        fields = _extract_fields(text)
        return {
            "success": True,
            "source_type": source_type,
            "raw_text_preview": text[:500],
            "extracted_fields": fields,
            "error": None,
        }

    except Exception as exc:
        logger.error("Report extraction error: %s", exc, exc_info=True)
        return {
            "success": False,
            "source_type": "unknown",
            "raw_text_preview": "",
            "extracted_fields": {},
            "error": "An unexpected error occurred while processing your report. Please try again.",
        }

