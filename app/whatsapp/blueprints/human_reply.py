from flask import Blueprint, request, request, jsonify
from app.whatsapp.services.wpp_pipeline import pipeline
from app.shared.core.logger import logger
import threading
import json

wpp_bp = Blueprint("wpp_improve_answers", __name__, url_prefix="/wpp/webhook/messages")
@wpp_bp.route('', methods=['POST'])
def handle_webhook(): 
    payload = request.json
    try:
        payload = json.loads(payload)
        thread = threading.Thread(target=pipeline, args=([payload]))
        thread.start()
        return jsonify({"status": "accepted", "message": "Task dispatched to background"}), 202
    except:
        return jsonify({"status": "accepted", "message": "Messsage dont correspond to this service"}), 500