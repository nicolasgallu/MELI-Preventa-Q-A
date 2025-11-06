from app.mercadolibre.services.questions_pipeline import pipeline
from app.shared.core.http_response import http_response
from app.shared.core.logger import logger
from flask import Blueprint, request

# BLUEPRINT CREATION
preventa_bp = Blueprint("wh_questions", __name__, url_prefix="/questions")
@preventa_bp.route("", methods=["POST"], strict_slashes=False)

def handle_webhook():
    """
    Get notifications from Meli Customer questions.
    """
    data = request.json
    
    # Variables
    topic = data.get("topic")
    resource = data.get("resource")
    user_id = data.get("user_id")
    question_id = resource.split("/")[-1]
    logger.info(f"Webhook Q&A received - Topic: {topic}, Resource: {resource}")

    # Filter by Topic
    if topic == "questions":
        return pipeline(user_id, question_id)
    else:
        return http_response("status", message="unhandled by webhook Q&A", http_code=200)
