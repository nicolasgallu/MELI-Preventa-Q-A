from datetime import datetime
from app.shared.core.secrets import meli_secrets
from app.shared.core.notifications import enviar_mensaje_whapi
from app.mercadolibre.utils.mercadolibre_api import QuestionsAPI
from app.mercadolibre.utils.bot import AiPreOrder
from app.shared.database.db_manager import DBManager
from app.shared.core.logger import logger
from app.shared.core.settings import FALLBACK_MESSAGE, PHONE_INTERNAL, PHONE_CLIENT


#//////////MERCADOLIBRE QUESTIONS PIPELINE//////////###
def pipeline(data):

    user_id = data.get("user_id")
    question_id = data.get("resource").split("/")[-1]
    logger.info(f"Processing Question: {question_id}")

    #Access to meli token
    access_token = meli_secrets()

    #Instancing Question Object
    question = QuestionsAPI(user_id, question_id, access_token)
    
    #Calling QuestionsAPI
    question_data = question.get_question_data()

    #Filter if Answered
    if question_data == "already_answered" or question_data == "already_registered":
        logger.info(f"Question ID: {question_id} already resolved.")
        return
    
    #Calling ItemsAPI
    item_data = question.get_item_data()

    #Variables
    question_text = question_data.get("text")
    item_name = item_data.get("title") 

    #AUXILIAR MENSAJE PARA DUEÑO (en caso de no responderse la pregunta utilizaremos este mensaje)
    external_message = (
        "⚠️ *El bot no pudo responder al cliente en MercadoLibre.*\n"
        "Por favor, respondé solo reemplazando el campo *'su respuesta aquí'*.\n"
        "*No modifiques el resto del mensaje*, así el sistema puede procesarlo correctamente.\n\n"
        f"*ID:* {user_id}-{question_id}\n"
        f"*ITEM:* {item_name}\n"
        f"*PREGUNTA:* {question_text}\n\n"
        "*RESPUESTA:* <su respuesta aquí>"
    )


    #Instancing Bot Object
    bot = AiPreOrder(user_id, question_id, question_text, item_data)
    
    #Executing AI Pipeline
    category = bot.classify_question()
    if category == "ai_inventory_search":
        bot_answer = bot.recommendation_answer()
    else:
        bot_answer = bot.audit_answer()

    #Auxiliar Creating values for valid/invalid answer.
    dbmanager = DBManager()
    response = {
            "reason":f"Final response not contains: {FALLBACK_MESSAGE}",
            "bool_invalid": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
  
    #Filer & Posting answer
    logger.info(f"Validating fallback filter for question: {question_id}")
    if FALLBACK_MESSAGE != bot_answer and "humano" not in bot_answer: #SUCCES ANSWER
        logger.info("Answer passed the fallback filter.")
        dbmanager.insert_ai_response(question_id, stage="fallback", response=response)
        response = question.post_response(bot_answer)
        if response == True:
            return
        else:
            enviar_mensaje_whapi(response, PHONE_INTERNAL)
            enviar_mensaje_whapi(external_message, PHONE_CLIENT)
            return
        
    else: #FAILED ANSWER
        logger.info("Answer failed to pass the fallback filter.")
        response["bool_invalid"]=1
        response["reason"]=f"Final response contains: {FALLBACK_MESSAGE}"
        dbmanager.insert_ai_response(question_id, stage="fallback", response=response)
        enviar_mensaje_whapi(external_message, PHONE_CLIENT)
        return