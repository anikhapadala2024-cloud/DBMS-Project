from flask import Blueprint
from backend.controllers.crop_controller import CropController
from backend.utils.auth import token_required, admin_required

crop_bp = Blueprint("crops", __name__, url_prefix="/api/crops")

@crop_bp.route("", methods=["GET"])
@token_required
def get_all(current_user):
    return CropController.get_all(current_user)

@crop_bp.route("/<int:crop_id>", methods=["GET"])
@token_required
def get_by_id(current_user, crop_id):
    return CropController.get_by_id(current_user, crop_id)

@crop_bp.route("", methods=["POST"])
@admin_required
def create(current_user):
    return CropController.create(current_user)

@crop_bp.route("/<int:crop_id>", methods=["PUT"])
@admin_required
def update(current_user, crop_id):
    return CropController.update(current_user, crop_id)

@crop_bp.route("/<int:crop_id>", methods=["DELETE"])
@admin_required
def delete(current_user, crop_id):
    return CropController.delete(current_user, crop_id)
