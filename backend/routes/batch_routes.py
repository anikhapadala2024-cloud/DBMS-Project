from flask import Blueprint
from backend.controllers.batch_controller import BatchController
from backend.utils.auth import token_required, admin_required

batch_bp = Blueprint("batches", __name__, url_prefix="/api/batches")

@batch_bp.route("", methods=["GET"])
@token_required
def get_all(current_user):
    return BatchController.get_all(current_user)

@batch_bp.route("/<int:batch_id>", methods=["GET"])
@token_required
def get_by_id(current_user, batch_id):
    return BatchController.get_by_id(current_user, batch_id)

@batch_bp.route("/generate-code", methods=["GET"])
@token_required
def generate_code(current_user):
    return BatchController.generate_code(current_user)

@batch_bp.route("", methods=["POST"])
@admin_required
def create(current_user):
    return BatchController.create(current_user)

@batch_bp.route("/<int:batch_id>", methods=["PUT"])
@token_required
def update(current_user, batch_id):
    return BatchController.update(current_user, batch_id)

@batch_bp.route("/<int:batch_id>/status", methods=["PATCH"])
@token_required
def update_status(current_user, batch_id):
    return BatchController.update_status(current_user, batch_id)

@batch_bp.route("/<int:batch_id>", methods=["DELETE"])
@admin_required
def delete(current_user, batch_id):
    return BatchController.delete(current_user, batch_id)
