from flask import request
from backend.services.crop_service import CropService
from backend.utils.validators import success_response, error_response

class CropController:
    @staticmethod
    def get_all(current_user):
        search = request.args.get("search")
        crops = CropService.get_all(search=search)
        return success_response(data=crops, message="Crops retrieved successfully")

    @staticmethod
    def get_by_id(current_user, crop_id):
        crop = CropService.get_by_id(crop_id)
        if not crop:
            return error_response("Crop not found", status_code=404)
        return success_response(data=crop, message="Crop retrieved successfully")

    @staticmethod
    def create(current_user):
        data = request.get_json() or {}
        crop, err = CropService.create(data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=crop, message="Crop added successfully", status_code=201)

    @staticmethod
    def update(current_user, crop_id):
        data = request.get_json() or {}
        crop, err = CropService.update(crop_id, data)
        if err:
            return error_response(err, status_code=400)
        return success_response(data=crop, message="Crop updated successfully")

    @staticmethod
    def delete(current_user, crop_id):
        success, err = CropService.delete(crop_id)
        if not success:
            return error_response(err or "Failed to delete crop", status_code=400)
        return success_response(message="Crop deleted successfully")
