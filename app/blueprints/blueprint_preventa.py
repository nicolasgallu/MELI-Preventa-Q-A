from flask import Blueprint, request, jsonify
from app.utils.logger import logger
from app.config.config import FALLBACK_MESSAGE
from app.utils.helpers.respond_utils import build_response
from app.services.preventa.database.gbq_filter_questions import register_question_in_db
from app.services.preventa.database.gbq_item_context import get_item_context
from app.services.preventa.manage_questions_init import fetch_question_text,send_response,is_answered,fetch_item_id
from app.services.preventa.manage_questions_llm import ProductQuestionBot
from app.services.preventa.notifications import notify_human_wpp,notify_errors_intern
from app.utils.helpers.token_reader import return_token

def handle_questions(data=None):
    try:
        question_id = data.get("resource").split("/")[-1]
        user_id = data.get("user_id")
        access_token = return_token (user_id)
        logger.debug("Procesando pregunta con ID: %s", question_id)

        #1) CHECK: ¿PREGUNTA PREVIAMENTE RESPONDIDA?
        if is_answered(question_id, access_token):
            logger.warning("La pregunta %s ya ha sido respondida anteriormente.", question_id)
            return build_response("status", message="question__previously_responded", http_code=200)
        #2) CHECK: OBTENER TEXTO DE LA PREGUNTA
        question = fetch_question_text(question_id, access_token)
        if not question:
            logger.error("No se pudo obtener el texto de la pregunta con ID: %s", question_id)
            return build_response("error", message="question__unable_to_get_text", http_code=400)
        #3) CHECK: OBTENER ITEM ASOCIADO A LA PREGUNTA
        item_id = fetch_item_id(question_id, access_token)
        if not item_id:
            logger.error("No se pudo obtener el item_id para la pregunta con ID: %s", question_id)
            return build_response("error", message="question__unable_to_get_item", http_code=400)
        #4) CHECK: ¿PREGUNTA PREEVIAMENT EN DB? --> caso contrario se almacena en DB
        db_status = register_question_in_db(question_id, question, item_id)
        if db_status == "already_registered":
            logger.info("La pregunta %s ya está registrada en la base de datos.", question_id)
            return build_response("status", message="question_previously_registered", http_code=200)
        
        if db_status == "error":
            logger.error("Error al manejar la base de datos para la pregunta %s.", question_id)
            return build_response("error", message="database error", http_code=500)
        

        #5) Bot Response Creation.
        bot =  ProductQuestionBot()
        response_text = bot.generate_llm_response(user_id, question, item_id)
        item_context = get_item_context(item_id)
        item_link = item_context["permalink"] 
        item_name = item_context["title"] 
        
        #6) Bot Response Filter, Delivering and Notification.
        if FALLBACK_MESSAGE not in response_text.lower():
            try:
                send_response(question_id, response_text, access_token)
                return build_response("status", message="question_answered", http_code=200)
            except Exception as e:
                notify_errors_intern("Preventa-MeliReply-Error",e)
                notify_human_wpp(question, question_id, item_id, user_id, item_link, item_name)
                return build_response("error", e, http_code=200)

        #7) Bot If Failed to pass Filter.
        else:
            logger.info(f"Question deliver directly to Employee: {question}")
            try:
                notify_human_wpp(question, question_id, item_id, user_id, item_link, item_name)
                return build_response("status", message="question_unanswered", http_code=200)
            except Exception as e:
                notify_errors_intern("Preventa-NotifyWpp-Error",e)
                return build_response("error", e, http_code=200)
            
    except Exception as e:
        notify_errors_intern("Preventa-General-Error",e)
        return build_response("error", e, http_code=200)




# CREAR BLUEPRINT
preventa_bp = Blueprint("webhook", __name__, url_prefix="/webhook")
@preventa_bp.route("", methods=["POST"], strict_slashes=False)

def handle_webhook():
    """
    Maneja todas las notificaciones (questions) de Mercado Libre en el endpoint /webhook.
    """
    data = request.json
    topic = data.get("topic", "unknown")
    resource = data.get("resource", "unknown")

    if not topic:
        logger.warning("Datos inválidos o falta de tema en la notificación.")
        return jsonify({"error": "No data or topic"}), 400

    try:
        if topic == "questions":
            logger.info(f"Webhook received - Topic: {topic}, Resource: {resource}")
            handle_questions(data)
            return jsonify({"status": "processed", "topic": "questions"}), 200

        return jsonify({"status": "unhandled by LLM Q&A", "topic": topic}), 200

    except Exception as e:
        logger.error(f"Error al procesar el webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500