from app.shared.core.secrets import meli_secrets
from app.shared.core.notifications import enviar_mensaje_whapi
from app.mercadolibre.utils.mercadolibre_api import QuestionsAPI
from app.mercadolibre.utils.bot import AiPreOrder
from app.shared.database.db_manager import DBManager
from app.shared.core.logger import logger
from app.shared.core.settings import PHONE_INTERNAL, PHONE_CLIENT

#//////////WHATSAPP PIPELINE//////////###

def pipeline(question_id, employee_reply):
    logger.info("Receveid User message from whatsapp")

    # Instancing DBManager
    dbmanager = DBManager()
    question_data = dbmanager.question_search(question_id)
    # Data > question db
    user_id = question_data["user_id"]
    item_id = question_data["item_id"]
    question_text = question_data["text"]
    
    # START 
    logger.info(f"Processing Question - {question_id}")
    access_token = meli_secrets()
    
    # Instancing Question Object
    question_api = QuestionsAPI(user_id, question_id, access_token, item_id)
    question_data = question_api.get_question_data()

    # Filter if Answered
    if question_data == "already_answered":
        logger.info("Question Already Answered - Nothing to Do.")
        return
    
    #Variables
    item_data = question_api.get_item_data()

    # Instancing Bot Object
    bot = AiPreOrder(user_id, question_id, question_text, item_data)
    bot_answer = bot.improve_human_answer(employee_reply)

    try:
        question_api.post_response(bot_answer)
        external_message = (
            "*✅ Respuesta enviada correctamente al cliente.*\n\n"
            f"*ID:* {question_id}\n"
            f"*RESPUESTA MEJORADA:* {bot_answer}"
        )
        enviar_mensaje_whapi(external_message, PHONE_CLIENT)
        return
    
    except Exception as e:
        message = f"Error al intentar enviar respuesta al Cliente: {e}"
        enviar_mensaje_whapi(message, PHONE_INTERNAL)
        enviar_mensaje_whapi("failed-meli-wpp-service",e)
        return 

