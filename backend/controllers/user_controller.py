from flask import request
from backend.database import db
from backend.models.user import User
from backend.models.farmer import Farmer
from backend.utils.validators import success_response, error_response, is_valid_email
from werkzeug.security import generate_password_hash

class UserController:
    @staticmethod
    def get_all(current_user):
        users = User.query.order_by(User.id.asc()).all()
        return success_response(data=[u.to_dict() for u in users], message="Users retrieved")

    @staticmethod
    def create(current_user):
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "farmer")

        if not name or not name.strip():
            return error_response("Name is required", status_code=400)
        if not is_valid_email(email):
            return error_response("Valid email is required", status_code=400)
        if not password or len(password) < 6:
            return error_response("Password must be at least 6 characters", status_code=400)

        email_clean = email.strip().lower()
        if User.query.filter_by(email=email_clean).first():
            return error_response("User with this email already exists", status_code=400)

        user = User(name=name.strip(), email=email_clean, role=role if role in ("admin", "farmer") else "farmer")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if user.role == "farmer":
            farmer = Farmer(
                user_id=user.id,
                name=user.name,
                phone=data.get("phone", ""),
                address=data.get("address", ""),
                village=data.get("village", "")
            )
            db.session.add(farmer)
            db.session.commit()

        return success_response(data=user.to_dict(), message="User created successfully", status_code=201)

    @staticmethod
    def update(current_user, user_id):
        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", status_code=404)

        data = request.get_json() or {}
        if "name" in data and data["name"].strip():
            user.name = data["name"].strip()
            if user.farmer_profile:
                user.farmer_profile.name = user.name

        if "role" in data and data["role"] in ("admin", "farmer"):
            user.role = data["role"]

        if "password" in data and data["password"]:
            if len(data["password"]) >= 6:
                user.set_password(data["password"])
            else:
                return error_response("Password must be at least 6 characters", status_code=400)

        db.session.commit()
        return success_response(data=user.to_dict(), message="User updated successfully")

    @staticmethod
    def delete(current_user, user_id):
        if current_user.id == user_id:
            return error_response("You cannot delete your own account.", status_code=400)

        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", status_code=404)

        db.session.delete(user)
        db.session.commit()
        return success_response(message="User deleted successfully")
