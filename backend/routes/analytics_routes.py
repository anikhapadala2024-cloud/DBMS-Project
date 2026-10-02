from flask import Blueprint
from backend.controllers.analytics_controller import AnalyticsController
from backend.utils.auth import token_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/dashboard", methods=["GET"])
@token_required
def get_dashboard(current_user):
    return AnalyticsController.get_dashboard(current_user)

@analytics_bp.route("/reports", methods=["GET"])
@token_required
def get_reports(current_user):
    return AnalyticsController.get_reports(current_user)

@analytics_bp.route("/export-batches", methods=["GET"])
@token_required
def export_batches(current_user):
    return AnalyticsController.export_batches(current_user)

@analytics_bp.route("/export-activities", methods=["GET"])
@token_required
def export_activities(current_user):
    return AnalyticsController.export_activities(current_user)
