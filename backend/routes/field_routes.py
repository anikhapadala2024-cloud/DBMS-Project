from flask import Blueprint
from backend.controllers.field_controller import FieldController
from backend.utils.auth import token_required, admin_required

field_bp = Blueprint("fields", __name__, url_prefix="/api/fields")

@field_bp.route("", methods=["GET"])
@token_required
def get_all(current_user):
    return FieldController.get_all(current_user)

@field_bp.route("/<int:field_id>", methods=["GET"])
@token_required
def get_by_id(current_user, field_id):
    return FieldController.get_by_id(current_user, field_id)

@field_bp.route("", methods=["POST"])
@admin_required
def create(current_user):
    return FieldController.create(current_user)

@field_bp.route("/<int:field_id>", methods=["PUT"])
@admin_required
def update(current_user, field_id):
    return FieldController.update(current_user, field_id)

@field_bp.route("/<int:field_id>", methods=["DELETE"])
@admin_required
def delete(current_user, field_id):
    return FieldController.delete(current_user, field_id)
