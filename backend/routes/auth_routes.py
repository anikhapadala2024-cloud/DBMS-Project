from flask import Blueprint
from backend.controllers.auth_controller import AuthController
from backend.utils.auth import token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    return AuthController.login()

@auth_bp.route("/register", methods=["POST"])
def register():
    return AuthController.register()

@auth_bp.route("/me", methods=["GET"])
@token_required
def me(current_user):
    return AuthController.me(current_user)

@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    return AuthController.update_profile(current_user)
