from backend.database import db
from backend.models.user import User
from backend.models.farmer import Farmer
from backend.utils.auth import generate_token
from backend.utils.validators import is_valid_email

class AuthService:
    VALID_ROLES = {"farmer", "admin"}

    @staticmethod
    def login(email: str, password: str):
        if not email or not password:
            return None, "Email and password are required."

        email_clean = email.strip().lower()
        user = User.query.filter_by(email=email_clean).first()
        if not user or not user.check_password(password):
            return None, "Invalid email or password."

        token = generate_token(user)
        user_data = user.to_dict()
        return {
            "token": token,
            "user": user_data
        }, None

    @staticmethod
    def register(name: str, email: str, password: str, role: str = "farmer"):
        if not name or not name.strip():
            return None, "Name is required."
        if not is_valid_email(email):
            return None, "A valid email address is required."
        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters long."

        role_name = (role or "farmer").strip().lower()
        if role_name not in AuthService.VALID_ROLES:
            return None, "Role must be either farmer or admin."

        email_clean = email.strip().lower()

        if User.query.filter_by(email=email_clean).first():
            return None, "An account with this email address already exists."

        user = User(name=name.strip(), email=email_clean, role=role_name)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        if user.role == "farmer":
            farmer = Farmer(
                user_id=user.id,
                name=user.name,
                phone="",
                address="",
                village="",
                land_size_acres=None,
                soil_type="",
                preferred_crop="",
                profile_photo_url="",
                farm_notes=""
            )
            db.session.add(farmer)
            db.session.commit()

        token = generate_token(user)
        return {
            "token": token,
            "user": user.to_dict()
        }, None

    @staticmethod
    def get_profile(user: User):
        data = user.to_dict()
        if user.farmer_profile:
            data["farmer_details"] = user.farmer_profile.to_dict()
        return data

    @staticmethod
    def update_profile(user: User, data: dict):
        name = data.get("name")
        if name and name.strip():
            user.name = name.strip()
            if user.farmer_profile:
                user.farmer_profile.name = user.name

        password = data.get("password")
        if password and len(password) >= 6:
            user.set_password(password)

        if user.role == "farmer" and user.farmer_profile:
            if "phone" in data:
                user.farmer_profile.phone = data["phone"].strip()
            if "address" in data:
                user.farmer_profile.address = data["address"].strip()
            if "village" in data:
                user.farmer_profile.village = data["village"].strip()
            if "land_size_acres" in data:
                try:
                    user.farmer_profile.land_size_acres = float(data["land_size_acres"])
                except (TypeError, ValueError):
                    return None, "Land size must be a valid number."
            if "soil_type" in data and data["soil_type"] is not None:
                user.farmer_profile.soil_type = str(data["soil_type"]).strip()
            if "preferred_crop" in data and data["preferred_crop"] is not None:
                user.farmer_profile.preferred_crop = str(data["preferred_crop"]).strip()
            if "profile_photo_url" in data and data["profile_photo_url"] is not None:
                user.farmer_profile.profile_photo_url = str(data["profile_photo_url"]).strip()
            if "farm_notes" in data and data["farm_notes"] is not None:
                user.farmer_profile.farm_notes = str(data["farm_notes"]).strip()

        db.session.commit()
        return user.to_dict(), None
