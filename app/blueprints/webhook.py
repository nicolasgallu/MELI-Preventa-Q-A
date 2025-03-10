from flask import Blueprint, request, jsonify
from app.utils.logger import logger
from app.blueprints.blueprint_preventa import handle_questions 

# Crear el blueprint
webhook_blueprint = Blueprint("webhook", __name__, url_prefix="/webhook")

@webhook_blueprint.route("", methods=["POST"], strict_slashes=False)
def handle_webhook():
    """
    Maneja todas las notificaciones de Mercado Libre en el endpoint /webhook.
    """
    data = request.json
    topic = data.get("topic", "unknown")
    resource = data.get("resource", "unknown")
    logger.info(f"Webhook received - Topic: {topic}, Resource: {resource}")

    if not topic:
        logger.warning("Datos inválidos o falta de tema en la notificación.")
        return jsonify({"error": "No data or topic"}), 400

    try:
        if topic == "questions":
            handle_questions(data)
            return jsonify({"status": "processed", "topic": "questions"}), 200

        return jsonify({"status": "unhandled by LLM Q&A", "topic": topic}), 200

    except Exception as e:
        logger.error(f"Error al procesar el webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500