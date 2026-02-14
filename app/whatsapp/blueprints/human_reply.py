from flask import Blueprint, request, request, jsonify
from app.whatsapp.services.wpp_pipeline import pipeline
from app.shared.core.settings import USER_ID

wpp_bp = Blueprint("wpp_improve_answers", __name__, url_prefix="/webhook/messages")
@wpp_bp.route('', methods=['GET', 'POST'])
def handle_webhook(): 
    payload = request.json
    mensaje = payload['messages'][0]['text']['body']
    if "bot no pudo responder" in mensaje and "<su respuesta aquí>" not in mensaje:
        
        lines = mensaje.split('\n')
        for line in lines:
             if "*ID:*" in line:
                 line= line.split('*ID:*')[1].split('-')
                 user_id=line[0].replace(' ','')
                 question_id=line[1].replace(' ','')
             if "*RESPUESTA:*" in line:
                 employee_reply=(line.split('*RESPUESTA:*')[1]).replace(' ','')
        
        if user_id == USER_ID:
            pipeline(question_id, employee_reply)
        else:
            None
    
    else:
        None
    return jsonify({"status": "accepted", "message": "Task dispatched to background"}), 202
