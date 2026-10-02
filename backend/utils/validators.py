import re
from datetime import datetime
from flask import jsonify

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def is_valid_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))

def parse_date(date_str: str | None):
    """Parse YYYY-MM-DD string into datetime.date object or return None."""
    if not date_str:
        return None
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def success_response(data=None, message="Operation successful", status_code=200):
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message="An error occurred", status_code=400, errors=None):
    response = {
        "success": False,
        "message": message,
        "errors": errors or []
    }
    return jsonify(response), status_code
