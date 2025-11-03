from app.shared.core.logger import logger
import re

def create_payload(message, phone, name, timestamp):
    logger.info("Starting Creationg of WPP Payload")
    if not isinstance(message, str):
        return logger.error(f"No se pudo obtener un cuerpo de texto válido desde el mensaje: {message}")

    # Compilar el patrón para extraer solo ID y RESPUESTA
    patron = re.compile(
        # 1. Captura el ID
        r".*\*ID:\*\s*(.+?)\s*\n"
        # 2. Ignora las líneas URL, ITEM y PREGUNTA
        r".*?\n"  # Ignora la línea URL
        r".*?\n"  # Ignora la línea ITEM
        r".*?\n"  # Ignora la línea PREGUNTA
        r"\s*\*RESPUESTA:\*\s*(.+)", # 3. Captura la RESPUESTA
        re.IGNORECASE | re.DOTALL
    )

    match = patron.search(message)
    if not match:
        return logger.error("No se pudieron extraer todos los campos esperados. Verificá el formato del mensaje.")

    # Ajusta la asignación para tomar solo el primer grupo (ID) y el segundo (RESPUESTA)
    question_id, raw_response = match.groups()

    try:
        payload = {
            "phone": phone,
            "name": name,
            "question_id": question_id,
            "message": raw_response.strip(),
            "created_at": timestamp,
            }
        return payload
    
    except ValueError as e:
        return logger.error(f"Paylaod failed to being created: {e}")