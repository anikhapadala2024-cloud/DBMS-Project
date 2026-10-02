from flask import request
from backend.services.auth_service import AuthService
from backend.utils.validators import success_response, error_response

class AuthController:
    @staticmethod
    def login():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        result, err = AuthService.login(email, password)
        if err:
            return error_response(err, status_code=401)
        return success_response(data=result, message="Login successful")

    @staticmethod
    def register():
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "farmer")

        result, err = AuthService.register(name, email, password, role)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=result, message="Account registered successfully", status_code=201)

    @staticmethod
    def me(current_user):
        profile = AuthService.get_profile(current_user)
        return success_response(data=profile, message="Profile retrieved")

    @staticmethod
    def update_profile(current_user):
        data = request.get_json() or {}
        profile, err = AuthService.update_profile(current_user, data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=profile, message="Profile updated successfully")
