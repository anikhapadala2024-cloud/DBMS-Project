from flask import request
from backend.services.farmer_service import FarmerService
from backend.utils.validators import success_response, error_response

class FarmerController:
    @staticmethod
    def get_all(current_user):
        search = request.args.get("search")
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        farmer_user_id = current_user.id if current_user.role == "farmer" else None
        result = FarmerService.get_all(
            search=search,
            page=page,
            limit=limit,
            farmer_user_id=farmer_user_id
        )
        return success_response(data=result, message="Farmers retrieved successfully")

    @staticmethod
    def get_by_id(current_user, farmer_id):
        farmer = FarmerService.get_by_id(farmer_id)
        if not farmer:
            return error_response("Farmer not found", status_code=404)
        if current_user.role == "farmer" and farmer_id != getattr(current_user.farmer_profile, "farmer_id", None):
            return error_response("Farmer not found", status_code=404)
        return success_response(data=farmer, message="Farmer retrieved successfully")

    @staticmethod
    def create(current_user):
        data = request.get_json() or {}
        farmer, err = FarmerService.create(data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=farmer, message="Farmer added successfully", status_code=201)

    @staticmethod
    def update(current_user, farmer_id):
        data = request.get_json() or {}
        farmer, err = FarmerService.update(farmer_id, data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=farmer, message="Farmer updated successfully")

    @staticmethod
    def delete(current_user, farmer_id):
        success, err = FarmerService.delete(farmer_id)
        if not success:
            return error_response(err or "Failed to delete farmer", status_code=400)
        return success_response(message="Farmer deleted successfully")
