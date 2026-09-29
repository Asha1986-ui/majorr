from datetime import datetime


def get_current_utc_timestamp() -> str:
    """
    Returns ISO 8601 formatted UTC timestamp.
    """
    return datetime.utcnow().isoformat()


def sanitize_string(value: str) -> str:
    """
    Strips leading and trailing whitespace from string input.
    """
    if isinstance(value, str):
        return value.strip()
    return value
