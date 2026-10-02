from backend.routes.auth_routes import auth_bp
from backend.routes.farmer_routes import farmer_bp
from backend.routes.field_routes import field_bp
from backend.routes.crop_routes import crop_bp
from backend.routes.batch_routes import batch_bp
from backend.routes.activity_routes import activity_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.user_routes import user_bp
from backend.routes.assistant_routes import assistant_bp

__all__ = [
    "auth_bp",
    "farmer_bp",
    "field_bp",
    "crop_bp",
    "batch_bp",
    "activity_bp",
    "analytics_bp",
    "user_bp",
    "assistant_bp"
]
