import re
from app.shared.core.logger import logger

def create_payload(message, phone, name, timestamp):
    """
    Recibe un dict tipo 'message' de WhatsApp y extrae los campos estructurados
    del cuerpo del mensaje.
    """
    logger.info("starting extracting")
    if not isinstance(message, str):
        return logger.error(f"No se pudo obtener un cuerpo de texto válido desde el mensaje: {message}")

    # Compilar el patrón para extraer los campos
    patron = re.compile(
        r"\*ID:\*\s*(.+?)\s*\n"
        r"\*URL:\*\s*(.+?)\s*\n"
        r"\*ITEM:\*\s*(.+?)\s*\n"
        r"\*PREGUNTA:\*\s*(.+?)\s*\n"
        r"\*RESPUESTA:\*\s*(.+)",
        re.IGNORECASE | re.DOTALL
    )

    match = patron.search(message)
    if not match:
        return logger.error("No se pudieron extraer todos los campos esperados. Verificá el formato del mensaje.")

    id_str, url, item_name, question_text, raw_response = match.groups()


    try:
        question_id, user_id, item_id = id_str.strip().split("-")
        payload = {
            "source": "wpp",
            "phone": phone,
            "name": name,
            "created_at":timestamp,
            "message": raw_response.strip(),
            "user_id": user_id.strip(),
            "question_id": question_id.strip(),
            "item_id": item_id.strip(),
            "url": url.strip(),
            "item_name": item_name.strip(),
            "question": question_text.strip(),
            }
        return payload
    
    except ValueError as e:
        return logger.error(f"Paylaod failed to being created: {e}")