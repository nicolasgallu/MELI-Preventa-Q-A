from app.mercadolibre.services.questions_pipeline import pipeline
from app.shared.core.logger import logger
from flask import Blueprint, request, jsonify
import threading

#BLUEPRINT CREATION
preventa_bp = Blueprint("meli_questions", __name__, url_prefix="/webhooks/questions")
@preventa_bp.route("", methods=["POST"], strict_slashes=False)
def main():
    """Get notifications from Meli Customer questions."""
    data = request.json
    topic = data.get("topic")
    if topic == "questions":
        thread = threading.Thread(target=pipeline, args=(data,))
        thread.start()
        
    return jsonify({"status": "accepted", "message": "Task dispatched to background"}), 202