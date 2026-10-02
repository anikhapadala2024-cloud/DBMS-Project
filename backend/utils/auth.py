import jwt
from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import request
from backend.config import Config
from backend.models.user import User
from backend.utils.validators import error_response

def generate_token(user: User) -> str:
    """Generate a JWT token valid for the configured duration."""
    payload = {
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "farmer_id": user.farmer_profile.farmer_id if user.farmer_profile else None,
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def decode_token(token: str):
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_header() -> str:
    """Extract Bearer token from Authorization header or query parameter."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1].strip()
    
    # Fallback to query parameter for direct browser downloads (e.g. CSV export)
    query_token = request.args.get("token")
    if query_token:
        return query_token.strip()

    return None

def token_required(f):
    """Decorator to require a valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return error_response("Authentication token is missing. Please log in.", status_code=401)

        payload = decode_token(token)
        if not payload:
            return error_response("Token has expired or is invalid. Please log in again.", status_code=401)

        current_user = User.query.get(payload.get("user_id"))
        if not current_user:
            return error_response("User associated with this token no longer exists.", status_code=401)

        return f(current_user, *args, **kwargs)
    return decorated

def role_required(allowed_roles):
    """Decorator to require specific roles (e.g., ['admin'], ['farmer', 'admin'])."""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in allowed_roles:
                return error_response(
                    f"Access forbidden: Requires one of the following roles: {', '.join(allowed_roles)}",
                    status_code=403
                )
            return f(current_user, *args, **kwargs)
        return token_required(decorated_function)
    return decorator

def admin_required(f):
    """Shortcut decorator for admin-only endpoints."""
    return role_required(["admin"])(f)
