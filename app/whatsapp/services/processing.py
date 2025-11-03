from app.whatsapp.utils.extraction import create_payload 
from app.shared.core.logger import logger
from datetime import datetime

def message_processing(request):
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
            return False       
    except Exception as e:
        logger.error(f"Error Extracting webhook payload: {e}")
        return False