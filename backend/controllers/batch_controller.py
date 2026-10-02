from flask import request
from backend.models.batch import CropBatch
from backend.services.batch_service import BatchService
from backend.utils.validators import success_response, error_response

class BatchController:
    @staticmethod
    def get_all(current_user):
        crop_id = request.args.get("crop_id", type=int)
        farmer_id = request.args.get("farmer_id", type=int)
        field_id = request.args.get("field_id", type=int)
        status = request.args.get("status")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        search = request.args.get("search")

        # If user is a farmer, only show their assigned batches
        if current_user.role == "farmer" and current_user.farmer_profile:
            farmer_id = current_user.farmer_profile.farmer_id
        elif current_user.role == "farmer":
            farmer_id = -1

        batches = BatchService.get_all(
            crop_id=crop_id,
            farmer_id=farmer_id,
            field_id=field_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            search=search
        )
        return success_response(data=batches, message="Batches retrieved successfully")

    @staticmethod
    def get_by_id(current_user, batch_id):
        batch_record = CropBatch.query.get(batch_id)
        if current_user.role == "farmer" and (
            not batch_record or
            batch_record.field.farmer_id != getattr(current_user.farmer_profile, "farmer_id", None)
        ):
            return error_response("Crop batch not found", status_code=404)
        batch = BatchService.get_by_id(batch_id)
        if not batch:
            return error_response("Crop batch not found", status_code=404)
        return success_response(data=batch, message="Batch retrieved successfully")

    @staticmethod
    def generate_code(current_user):
        crop_id = request.args.get("crop_id", type=int)
        code = BatchService.generate_code(crop_id)
        return success_response(data={"batch_code": code}, message="Batch code generated")

    @staticmethod
    def create(current_user):
        data = request.get_json() or {}
        batch, err = BatchService.create(data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=batch, message="Crop batch created successfully", status_code=201)

    @staticmethod
    def update(current_user, batch_id):
        data = request.get_json() or {}
        batch_record = CropBatch.query.get(batch_id)
        if current_user.role == "farmer":
            farmer_id = getattr(current_user.farmer_profile, "farmer_id", None)
            if not batch_record or batch_record.field.farmer_id != farmer_id:
                return error_response("Crop batch not found", status_code=404)
            if "field_id" in data:
                from backend.models.field import Field
                target_field = Field.query.get(data["field_id"])
                if not target_field or target_field.farmer_id != farmer_id:
                    return error_response("Field not found", status_code=404)
        batch, err = BatchService.update(batch_id, data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=batch, message="Crop batch updated successfully")

    @staticmethod
    def update_status(current_user, batch_id):
        data = request.get_json() or {}
        if current_user.role == "farmer":
            batch_record = CropBatch.query.get(batch_id)
            farmer_id = getattr(current_user.farmer_profile, "farmer_id", None)
            if not batch_record or batch_record.field.farmer_id != farmer_id:
                return error_response("Crop batch not found", status_code=404)
        new_status = data.get("status")
        yield_val = data.get("yield")
        actual_harvest_date = data.get("actual_harvest_date")

        if not new_status:
            return error_response("Status is required", status_code=400)

        batch, err = BatchService.update_status(
            batch_id=batch_id,
            new_status=new_status,
            yield_amount=yield_val,
            actual_harvest_date_str=actual_harvest_date
        )
        if err:
            return error_response(err, status_code=400)
        return success_response(data=batch, message=f"Batch status transitioned to {new_status}")

    @staticmethod
    def delete(current_user, batch_id):
        success, err = BatchService.delete(batch_id)
        if not success:
            return error_response(err or "Failed to delete batch", status_code=400)
        return success_response(message="Crop batch deleted successfully")
