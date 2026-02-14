import requests
from app.shared.core.settings import TOKEN_WHAPI
from app.shared.core.logger import logger

def enviar_mensaje_whapi(mensaje, phone):
    logger.info(f"Sending WPP Message to: {phone}")
    url = "https://gate.whapi.cloud/messages/text"
    payload = {
        "to": f"{phone}",
        "body": mensaje
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {TOKEN_WHAPI}"
    }
    
    res = requests.post(url, json=payload, headers=headers)
    return res.json()