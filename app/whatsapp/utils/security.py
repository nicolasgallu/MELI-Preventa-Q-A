from app.shared.core.settings import VERIFY_WHOOK,META_APP_SECRET
from app.shared.core.logger import logger
from flask import make_response
import hashlib
import hmac

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