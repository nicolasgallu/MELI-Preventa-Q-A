from app.shared.core.settings import VERIFY_WHOOK
from app.shared.core.logger import logger
from flask import make_response

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