from flask import Blueprint, request
from app.utils.logger import logger
from app.services.preventa.improve_human_reply import ImproveHumanReply
from app.services.preventa.database.gbq_human_reply import db_write_reply
from app.services.preventa.manage_questions_init import is_answered,send_response
from app.utils.helpers.respond_utils import build_response
from app.utils.helpers.token_reader import return_token
from app.services.preventa.notifications import notify_errors_intern
from app.services.preventa.notifications import notify_human_wpp_answered


wpp_bp = Blueprint("wpp", __name__, url_prefix="/wpp")
@wpp_bp.route("", methods=["POST"])

def read_wpp():
    try:
        logger.info(f"mensaje desde wpp-service recibido exitosamente")

        #1) Extracting Data
        data = request.json
        source = data["source"]
        phone = data["phone"]
        employee_name = data["name"]
        created_at = data["created_at"]
        response = data["message"]
        question_id = data["question_id"] 
        item_id = data["item_id"] 
        item_name = data["item_name"]
        question = data["question"] 
        user_id = data["user_id"] 
    
        #2) Getting Token.
        access_token = return_token (user_id)
    
        #3) CHECK: ¿PREGUNTA PREVIAMENTE RESPONDIDA?
        if is_answered(question_id,access_token):
            logger.warning("La pregunta %s ya ha sido respondida anteriormente.", question_id)
            return build_response("status", message="question__previously_responded", http_code=200)
    
    
        else:
            #4) Writting Human Reply.
            db_write_reply(created_at, user_id, question_id, source, phone, employee_name, response)

            #5) Improving reply and writting the LLM Consume.
            bot =  ImproveHumanReply()
            response_text = bot._execute_bot(question, item_id, item_name, response)
    
            #6) Sending Response to Customer
            send_response(question_id, response_text, access_token)
    
            #7) Notify trough Intern Email and to Employee WPP. 
            notify_human_wpp_answered(question_id, item_id, user_id, response_text)
            return build_response("status", message="question_answered", http_code=200)
        
    except Exception as e:
        notify_errors_intern("failed-meli-wpp-service",e)
        return build_response("status", message="failed-meli-wpp-service", http_code=400)

 

    
