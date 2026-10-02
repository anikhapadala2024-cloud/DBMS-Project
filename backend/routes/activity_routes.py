from flask import Blueprint
from backend.controllers.activity_controller import ActivityController
from backend.utils.auth import token_required

activity_bp = Blueprint("activities", __name__, url_prefix="/api/activities")

@activity_bp.route("", methods=["GET"])
@token_required
def get_all(current_user):
    return ActivityController.get_all(current_user)

@activity_bp.route("/<int:activity_id>", methods=["GET"])
@token_required
def get_by_id(current_user, activity_id):
    return ActivityController.get_by_id(current_user, activity_id)

@activity_bp.route("", methods=["POST"])
@token_required
def create(current_user):
    return ActivityController.create(current_user)

@activity_bp.route("/<int:activity_id>", methods=["PUT"])
@token_required
def update(current_user, activity_id):
    return ActivityController.update(current_user, activity_id)

@activity_bp.route("/<int:activity_id>", methods=["DELETE"])
@token_required
def delete(current_user, activity_id):
    return ActivityController.delete(current_user, activity_id)
