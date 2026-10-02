from flask import Blueprint
from backend.controllers.user_controller import UserController
from backend.utils.auth import admin_required

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

@user_bp.route("", methods=["GET"])
@admin_required
def get_all(current_user):
    return UserController.get_all(current_user)

@user_bp.route("", methods=["POST"])
@admin_required
def create(current_user):
    return UserController.create(current_user)

@user_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update(current_user, user_id):
    return UserController.update(current_user, user_id)

@user_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete(current_user, user_id):
    return UserController.delete(current_user, user_id)
