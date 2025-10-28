from app.shared.core.logger import logger
from app.shared.core.settings import FALLBACK_MESSAGE
from app.mercadolibre.utils.token_meli import token_meli
from app.shared.core.http_response import http_response
from app.mercadolibre.utils.questions import QuestionsAPI
from app.mercadolibre.utils.notifications import notify_human_wpp,notify_errors_intern
from app.mercadolibre.services.bot import AiPreOrder

def pipeline(user_id, question_id):
        
    logger.info(f"Processing Question - {question_id}")
    access_token = token_meli(user_id)

    # Instancing Question Object
    question = QuestionsAPI(user_id, question_id, access_token)
    # Calling QuestionsAPI
    question_data = question.get_question_data()

    # Filter if Answered
    if question_data == False:
        logger.info("Question Already Answered - Nothing to Do.")
        return http_response("status", message="question_responded", http_code=200)
    
    # Calling ItemsAPI
    item_data = question.get_item_data()

    # Variables
    question_text = question_data.get("text")
    item_id = question_data.get("item_id") 
    item_link = item_data.get("permalink")
    item_name = item_data.get("title") 

    # Instancing Bot Object
    bot = AiPreOrder(user_id, question_id, question_text, item_data)
    
    # Executing AI Pipeline
    category = bot.classify_question()
    if category == "busqueda_inventario":
        bot_answer = bot.recommendation_answer()
    else:
        bot_answer = bot.audit_answer()

    # Filer & Posting answer
    if FALLBACK_MESSAGE != bot_answer and "humano" not in bot_answer:
        try:
            question.post_response(bot_answer)
            return http_response("status", message="question_answered", http_code=200)
        except Exception as e:
            notify_errors_intern("Preventa-MeliReply-Error", e)
            notify_human_wpp(question_text, question_id, item_id, user_id, item_link, item_name)
            return http_response("error", e, http_code=200)
        
    else:
        logger.info(f"Question deliver directly to Employee: {question_text}")
        try:
            notify_human_wpp(question_text, question_id, item_id, user_id, item_link, item_name)
            return http_response("status", message="question_unanswered", http_code=200)
        except Exception as e:
            notify_errors_intern("Preventa-NotifyWpp-Error",e)
            return http_response("error", e, http_code=200)