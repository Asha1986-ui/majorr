import re


def is_valid_email(email: str) -> bool:
    """
    Validates email format using regex pattern.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))


def is_strong_password(password: str) -> bool:
    """
    Checks if password meets minimum length requirements (6+ characters).
    """
    return len(password) >= 6
