from flask import Blueprint, request, make_response
from app.shared.core.logger import logger
from app.whatsapp.utils.security import wh_activation,sign_validation
from app.whatsapp.services.wpp_pipeline import pipeline

wpp_bp = Blueprint("wpp", __name__, url_prefix="/wpp")
@wpp_bp.route('', methods=['GET', 'POST'])

def handle_webhook():
    if request.method =='GET':
        logger.info("Processing GET Request from WPP")
        return wh_activation(request)
    
    if request.method =='POST' and request.get_json():
        if sign_validation(request) == False:
            return make_response('Forbidden', 403)
        else:
            logger.info("Processing POST Request from WPP")
            return pipeline(request)