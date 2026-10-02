from flask import request
from backend.models.field import Field
from backend.services.field_service import FieldService
from backend.utils.validators import success_response, error_response

class FieldController:
    @staticmethod
    def get_all(current_user):
        farmer_id = request.args.get("farmer_id", type=int)
        search = request.args.get("search")

        # If logged in user is a farmer, only show their fields if farmer_id not explicitly given
        if current_user.role == "farmer" and current_user.farmer_profile:
            farmer_id = current_user.farmer_profile.farmer_id
        elif current_user.role == "farmer":
            farmer_id = -1

        fields = FieldService.get_all(farmer_id=farmer_id, search=search)
        return success_response(data=fields, message="Fields retrieved successfully")

    @staticmethod
    def get_by_id(current_user, field_id):
        field = Field.query.get(field_id)
        if not field:
            return error_response("Field not found", status_code=404)
        if current_user.role == "farmer" and field.farmer_id != getattr(current_user.farmer_profile, "farmer_id", None):
            return error_response("Field not found", status_code=404)
        return success_response(data=FieldService.get_by_id(field_id), message="Field retrieved successfully")

    @staticmethod
    def create(current_user):
        data = request.get_json() or {}
        # If farmer role, auto-assign farmer_id
        if current_user.role == "farmer" and current_user.farmer_profile:
            data["farmer_id"] = current_user.farmer_profile.farmer_id

        field, err = FieldService.create(data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=field, message="Field added successfully", status_code=201)

    @staticmethod
    def update(current_user, field_id):
        data = request.get_json() or {}
        field, err = FieldService.update(field_id, data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=field, message="Field updated successfully")

    @staticmethod
    def delete(current_user, field_id):
        success, err = FieldService.delete(field_id)
        if not success:
            return error_response(err or "Failed to delete field", status_code=400)
        return success_response(message="Field deleted successfully")
