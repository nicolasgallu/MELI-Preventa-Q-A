from app.shared.core.logger import logger
from app.shared.core.http_response import http_response
from app.mercadolibre.utils.token_meli import token_meli
from app.mercadolibre.utils.notifications import notify_errors_intern,notify_human_wpp_answered
from app.whatsapp.services.processing import message_processing
from app.mercadolibre.utils.questions import QuestionsAPI
from app.mercadolibre.services.bot import AiPreOrder
from app.shared.database.db_manager import DBManager


def pipeline(request):

    payload = message_processing(request) 
    if payload == False:
        logger.warning("No valid payload returned from message_processing()")
        return http_response("status", message="ignored_message", http_code=200)
    
    # PREPARING DATA
    # Data > wpp payload
    question_id = payload["question_id"] 
    phone = payload["phone"]
    employee_name = payload["name"]
    employee_reply = payload["message"]
    created_at = payload["created_at"]
    # Instancing DBManager
    dbmanager = DBManager()
    question_data = dbmanager.question_search(question_id)
    # Data > question db
    user_id = question_data["user_id"]
    item_id = question_data["item_id"]
    question_text = question_data["text"]
    
    # START 
    logger.info(f"Processing Question - {question_id}")
    access_token = token_meli(user_id)
    
    # Instancing Question Object
    question_api = QuestionsAPI(user_id, question_id, access_token)
    question_data = question_api.get_question_data()

    # Filter if Answered
    if question_data == "already_answered":
        logger.info("Question Already Answered - Nothing to Do.")
        return http_response("status", message="question_responded", http_code=200)
    
    #Variables
    item_data = question_api.get_item_data()

    # Instancing Bot Object
    bot = AiPreOrder(user_id, question_id, question_text, item_data)
    bot_answer = bot.improve_human_answer(employee_reply)
    try:
        question_api.post_response(bot_answer)
        notify_human_wpp_answered(question_id, item_id, user_id, bot_answer)
        return http_response("status", message="question-answered", http_code=200)
    
    except Exception as e:
        notify_errors_intern("failed-meli-wpp-service",e)
        return http_response("status", message="failed to post message meli-wpp-service", http_code=400)
