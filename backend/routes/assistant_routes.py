from flask import Blueprint

from backend.controllers.assistant_controller import AssistantController
from backend.utils.auth import token_required


assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")


@assistant_bp.route("/chat", methods=["POST"])
@token_required
def chat(current_user):
    return AssistantController.chat(current_user)