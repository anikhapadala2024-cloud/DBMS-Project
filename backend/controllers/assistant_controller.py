from flask import request

from backend.services.assistant_service import AssistantService
from backend.utils.validators import error_response, success_response


class AssistantController:
    @staticmethod
    def chat(current_user):
        data = request.get_json(silent=True) or {}
        answer, error, status_code = AssistantService.answer(
            current_user,
            data.get("question"),
            data.get("history")
        )
        if error:
            return error_response(error, status_code=status_code)
        return success_response(data=answer, message="Assistant response generated")