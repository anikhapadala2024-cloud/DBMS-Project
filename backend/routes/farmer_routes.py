from flask import Blueprint
from backend.controllers.farmer_controller import FarmerController
from backend.utils.auth import token_required, admin_required

farmer_bp = Blueprint("farmers", __name__, url_prefix="/api/farmers")

@farmer_bp.route("", methods=["GET"])
@token_required
def get_all(current_user):
    return FarmerController.get_all(current_user)

@farmer_bp.route("/<int:farmer_id>", methods=["GET"])
@token_required
def get_by_id(current_user, farmer_id):
    return FarmerController.get_by_id(current_user, farmer_id)

@farmer_bp.route("", methods=["POST"])
@admin_required
def create(current_user):
    return FarmerController.create(current_user)

@farmer_bp.route("/<int:farmer_id>", methods=["PUT"])
@admin_required
def update(current_user, farmer_id):
    return FarmerController.update(current_user, farmer_id)

@farmer_bp.route("/<int:farmer_id>", methods=["DELETE"])
@admin_required
def delete(current_user, farmer_id):
    return FarmerController.delete(current_user, farmer_id)
