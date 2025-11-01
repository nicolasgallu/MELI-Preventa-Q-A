from app.whatsapp.utils.extraction import create_payload 
from flask import make_response
from app.shared.core.logger import logger
from app.shared.core.settings import *
from datetime import datetime
import hashlib
import hmac

def wh_activation(request):
    """
    Returns to Meta the corresponded validation to activate the webhook.\n
    Requires: a **VERYFY_TOKEN** value that is seted in **.env** file and it needs
    to be the same in "Identificador de verificación" inside **Meta Webhook config**. 
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_WHOOK:
        logger.info("Webhook verified successfully.")
        return make_response(challenge, 200)
    else:
        logger.warning("Webhook verification failed.")
        return make_response('Forbidden', 403)

def sign_validation(request):
    """
    Validates the authenticity of incoming webhook POST requests from Meta.
    This function checks the **X-Hub-Signature** header sent by Meta against a hash
    computed using the raw request body and the **META_APP_SECRET**. If the signature 
    matches, the request is considered valid.
    Returns:
        - 403 Forbidden if the signature is missing or invalid.
        - None if the signature is valid (so the request can continue being processed).
    """
    # Signature verification
    signature = request.headers.get('X-Hub-Signature')
    if not signature:
        logger.warning("No signature in request.")
        return False
    body = request.get_data()
    expected_signature = 'sha1=' + hmac.new(META_APP_SECRET.encode(), body, hashlib.sha1).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        logger.warning("Invalid signature.")
        return False

def message_processing(request):
    if request.method =='GET':
        return wh_activation(request)
    if request.method =='POST' and request.get_json():
        if sign_validation(request) == False:
            return make_response('Forbidden', 403)
        else:
            try:
                data = request.get_json()
                value = data["entry"][0]["changes"][0]["value"]
                contact = value.get("contacts", [{}])[0]
                message = (value.get("messages", [{}])[0]).get("text", {}).get("body")
                name = contact.get("profile", {}).get("name")
                phone = contact.get("wa_id")
                msg_obj = value.get("messages", [{}])[0]
                timestamp = str(datetime.fromtimestamp(int(msg_obj.get("timestamp"))))
                logger.info(f"New message from {name}")
                if "el bot no pudo responder" in str(message).lower():
                    payload = create_payload(message, phone, name, timestamp)
                    return payload
                else:
                    logger.warning("Message dont correspond to zamplin-Service.")
                    return make_response('', 200)         
            except Exception as e:
                logger.error(f"Error Extracting webhook payload: {e}")
                return make_response('', 400)