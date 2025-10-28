from flask import Blueprint, request
from app.whatsapp.services.wpp_pipeline import pipeline

wpp_bp = Blueprint("wpp", __name__, url_prefix="/wpp")
@wpp_bp.route('', methods=['GET', 'POST'])

def handle_webhook():
    pipeline(request)