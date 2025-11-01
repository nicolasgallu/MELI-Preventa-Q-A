from app.shared.core.logger import logger
from app.shared.core.http_response import http_response
from app.mercadolibre.utils.token_meli import token_meli
from app.mercadolibre.utils.questions import QuestionsAPI
from app.mercadolibre.utils.notifications import notify_errors_intern
from app.mercadolibre.utils.notifications import notify_human_wpp_answered
from app.whatsapp.services.processing import message_processing
from app.mercadolibre.services.bot import AiPreOrder


def pipeline(request):

    payload = message_processing(request) 

    source = payload["source"]
    phone = payload["phone"]
    employee_name = payload["name"]
    created_at = payload["created_at"]
    employee_reply = payload["message"]
    question_id = payload["question_id"] 
    item_id = payload["item_id"] 
    item_name = payload["item_name"]
    question_text = payload["question"] 
    user_id = payload["user_id"] 
    
    # Start 
    logger.info(f"Processing Question - {question_id}")
    access_token = token_meli(user_id)
    
    # Instancing Question Object
    question = QuestionsAPI(user_id, question_id, access_token)
    question_data = question.get_question_data()
    
    # Filter if Answered
    if question_data == "already_answered":
        logger.info("Question Already Answered - Nothing to Do.")
        return http_response("status", message="question_responded", http_code=200)
    
    #Variables
    item_data = question.get_item_data()

    # Instancing Bot Object
    bot = AiPreOrder(user_id, question_id, question_text, item_data)
    bot_answer = bot.improve_human_answer(employee_reply)
    try:
        question.post_response(bot_answer)
        notify_human_wpp_answered(question_id, item_id, user_id, bot_answer)
        return http_response("status", message="question-answered", http_code=200)
    
    except Exception as e:
        notify_errors_intern("failed-meli-wpp-service",e)
        return http_response("status", message="failed to post message meli-wpp-service", http_code=400)
