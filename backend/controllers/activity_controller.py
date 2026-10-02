from flask import request
from backend.models.activity import CultivationActivity
from backend.models.batch import CropBatch
from backend.services.activity_service import ActivityService
from backend.utils.validators import success_response, error_response

class ActivityController:
    @staticmethod
    def get_all(current_user):
        batch_id = request.args.get("batch_id", type=int)
        activity_type = request.args.get("activity_type")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        farmer_id: int | None = None
        if current_user.role == "farmer":
            farmer_id = getattr(current_user.farmer_profile, "farmer_id", -1)

        activities = ActivityService.get_all(
            batch_id=batch_id,
            activity_type=activity_type,
            date_from=date_from,
            date_to=date_to,
            farmer_id=farmer_id
        )
        return success_response(data=activities, message="Cultivation activities retrieved")

    @staticmethod
    def get_by_id(current_user, activity_id):
        activity = ActivityService.get_by_id(activity_id)
        if not activity:
            return error_response("Activity not found", status_code=404)
        if current_user.role == "farmer":
            record = CultivationActivity.query.get(activity_id)
            if not record or record.batch.field.farmer_id != getattr(current_user.farmer_profile, "farmer_id", None):
                return error_response("Activity not found", status_code=404)
        return success_response(data=activity, message="Activity retrieved")

    @staticmethod
    def create(current_user):
        data = request.get_json() or {}
        if current_user.role == "farmer" and data.get("batch_id"):
            batch = CropBatch.query.get(data.get("batch_id"))
            if not batch or batch.field.farmer_id != getattr(current_user.farmer_profile, "farmer_id", None):
                return error_response("Crop batch not found", status_code=404)
        activity, err = ActivityService.create(data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=activity, message="Cultivation activity recorded successfully", status_code=201)

    @staticmethod
    def update(current_user, activity_id):
        data = request.get_json() or {}
        if current_user.role == "farmer":
            record = CultivationActivity.query.get(activity_id)
            if not record or (record.batch is not None and record.batch.field.farmer_id != getattr(current_user.farmer_profile, "farmer_id", None)):
                return error_response("Activity not found", status_code=404)
        activity, err = ActivityService.update(activity_id, data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=activity, message="Activity updated successfully")

    @staticmethod
    def delete(current_user, activity_id):
        if current_user.role == "farmer":
            record = CultivationActivity.query.get(activity_id)
            if not record or (record.batch is not None and record.batch.field.farmer_id != getattr(current_user.farmer_profile, "farmer_id", None)):
                return error_response("Activity not found", status_code=404)
        success, err = ActivityService.delete(activity_id)
        if not success:
            return error_response(err or "Failed to delete activity", status_code=400)
        return success_response(message="Cultivation activity deleted successfully")
