from flask import Blueprint, request
from app.utils.logger import logger
from app.utils.helpers.respond_utils import build_response
from app.config.config import FALLBACK_MESSAGE
from app.services.preventa.database.filter_questions import register_question_in_db
from app.services.preventa.manage_questions_init import fetch_question_text,send_response,is_answered,fetch_item_id,fetch_question_details
from app.services.preventa.manage_questions_llm import ProductQuestionBot
from app.services.preventa.manage_questions_human import notify_human
from app.services.preventa.manage_questions_intern import notify_intern


questions_blueprint = Blueprint("questions", __name__)
@questions_blueprint.route("/", methods=["POST"])


def handle_questions(data=None):
    try:
        question_id = data.get("resource").split("/")[-1]
        logger.debug("Procesando pregunta con ID: %s", question_id)

        # 1º CHECK: ¿PREGUNTA PREVIAMENTE RESPONDIDA?
        if is_answered(question_id):
            logger.warning("La pregunta %s ya ha sido respondida anteriormente.", question_id)
            return build_response("status", message="question__previously_responded", http_code=200)
        
        # 2º CHECK: OBTENER TEXTO DE LA PREGUNTA
        question_text = fetch_question_text(question_id)
        if not question_text:
            logger.error("No se pudo obtener el texto de la pregunta con ID: %s", question_id)
            return build_response("error", message="question__unable_to_get_text", http_code=400)

        # 3º CHECK: OBTENER ITEM ASOCIADO A LA PREGUNTA
        item_id = fetch_item_id(question_id)
        if not item_id:
            logger.error("No se pudo obtener el item_id para la pregunta con ID: %s", question_id)
            return build_response("error", message="question__unable_to_get_item", http_code=400)

    #    4º CHECK: ¿PREGUNTA PREEVIAMENT EN DB? --> caso contrario se almacena en DB
        db_status = register_question_in_db(question_id, question_text, item_id)
        if db_status == "already_registered":
            logger.info("La pregunta %s ya está registrada en la base de datos.", question_id)
            return build_response("status", message="question_previously_registered", http_code=200)
        
        if db_status == "error":
            logger.error("Error al manejar la base de datos para la pregunta %s.", question_id)
            return build_response("error", message="database error", http_code=500)
        

        # RESPONDER POR BOT
        bot =  ProductQuestionBot()
        response_text = bot.generate_llm_response(question=question_text, item_id=item_id)

        if FALLBACK_MESSAGE not in response_text.lower():
            send_response(question_id, response_text)
            notify_intern("Pregunta respondida por el Bot: ",question_text, response_text)
            return build_response("status", message="question__not_frequent_responded", http_code=200)

        # ESCALAR AL HUMANO SI EL BOT NO PUEDE RESPONDER
        else:
            logger.info(f"Respuesta escalada al Humano: {question_text}")
            question_details = fetch_question_details(question_id)
            notify_human("La siguiente pregunta no logro ser respondida por el Bot: ", question_details)
            notify_intern("La siguiente pregunta no logro ser respondida por el Bot", question_details,"")
            return build_response("status", message="question__escalated_to_human", http_code=200)

    except Exception as e:
        logger.error("Error al procesar la pregunta: %s. Detalles: %s", request.json.get("resource", "desconocido"), str(e))
        notify_intern("Pregunta sin responder debido a error inesperado","","")
        return build_response("error", message="question__internal_Server_error", http_code=200)

