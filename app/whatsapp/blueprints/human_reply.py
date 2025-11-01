from flask import Blueprint, request
from app.shared.core.logger import logger
from app.whatsapp.utils.webhook_init import wh_activation
from app.whatsapp.services.wpp_pipeline import pipeline

wpp_bp = Blueprint("wpp", __name__, url_prefix="/wpp")
@wpp_bp.route('', methods=['GET', 'POST'])

def handle_webhook():
    if request.method =='GET':
        logger.info("Processing GET Request from WPP")
        return wh_activation(request)
    if request.method =='POST' and request.get_json():
        logger.info("Processing POST Request from WPP")
        return pipeline(request)