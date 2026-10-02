from flask import request, Response
from backend.services.analytics_service import AnalyticsService
from backend.services.export_service import ExportService
from backend.utils.validators import success_response

class AnalyticsController:
    @staticmethod
    def get_dashboard(current_user):
        farmer_id = None
        if current_user.role == "farmer":
            farmer_id = getattr(current_user.farmer_profile, "farmer_id", -1)

        summary = AnalyticsService.get_dashboard_summary(farmer_id=farmer_id)
        return success_response(data=summary, message="Dashboard analytics retrieved")

    @staticmethod
    def get_reports(current_user):
        crop_id = request.args.get("crop_id", type=int)
        farmer_id = request.args.get("farmer_id", type=int)
        field_id = request.args.get("field_id", type=int)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")

        if current_user.role == "farmer":
            farmer_id = getattr(current_user.farmer_profile, "farmer_id", -1)

        reports = AnalyticsService.get_detailed_reports(
            crop_id=crop_id,
            farmer_id=farmer_id,
            field_id=field_id,
            date_from=date_from,
            date_to=date_to
        )
        return success_response(data=reports, message="Detailed reports calculated")

    @staticmethod
    def export_batches(current_user):
        crop_id = request.args.get("crop_id", type=int)
        farmer_id = request.args.get("farmer_id", type=int)
        status = request.args.get("status")

        if current_user.role == "farmer":
            farmer_id = getattr(current_user.farmer_profile, "farmer_id", -1)

        csv_content = ExportService.export_batches_csv(
            crop_id=crop_id,
            farmer_id=farmer_id,
            status=status
        )

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=crop_batches_export.csv"}
        )

    @staticmethod
    def export_activities(current_user):
        batch_id = request.args.get("batch_id", type=int)
        activity_type = request.args.get("activity_type")

        farmer_id = None
        if current_user.role == "farmer":
            farmer_id = getattr(current_user.farmer_profile, "farmer_id", -1)

        csv_content = ExportService.export_activities_csv(
            batch_id=batch_id,
            activity_type=activity_type,
            farmer_id=farmer_id
        )

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=cultivation_activities_export.csv"}
        )
