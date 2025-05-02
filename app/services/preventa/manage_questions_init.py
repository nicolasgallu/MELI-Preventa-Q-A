import requests
from app.utils.logger import logger

"""FUNCION VERIFICAR PREGUNTAS RESPONDIDAS"""
def is_answered(question_id, access_token):
    url = f"https://api.mercadolibre.com/questions/{question_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            question_data = response.json()
            return question_data.get("status", "") == "ANSWERED"
        logger.error("Error al verificar el estado de la pregunta %s: %s", question_id, response.json())
    except Exception as e:
        logger.exception("Excepción al verificar el estado de la pregunta %s.", question_id)
    return False

"""FUNCION OBTENER TEXTO DE LA PREGUNTA"""
def fetch_question_text(question_id, access_token):
    url = f"https://api.mercadolibre.com/questions/{question_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            question_text = response.json().get("text", "")
            logger.info("Texto de la pregunta %s obtenido exitosamente.", question_id)
            return question_text
        logger.error("Error al obtener la pregunta %s: %s", question_id, response.json())
    except Exception as e:
        logger.exception("Excepción al obtener la pregunta %s.", question_id)
    return None

"""FUNCION OBTENER ITEM SEGUN ID DE LA PREGUNTA"""
def fetch_item_id(question_id, access_token):
    url = f"https://api.mercadolibre.com/questions/{question_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("item_id")
        else:
            print(f"Error al obtener el item_id para question_id {question_id}: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Excepción al obtener el item_id para question_id {question_id}: {e}")
        return None

"""FUNCION ENVIAR RESPUESTA"""
def send_response(question_id, text, access_token):
    url = "https://api.mercadolibre.com/answers"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"question_id": question_id, "text": text}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logger.info("Respuesta enviada exitosamente para la pregunta %s.", question_id)
            return True
        logger.error("Error al responder la pregunta %s: %s", question_id, response.json())
    except Exception as e:
        logger.exception("Excepción al responder la pregunta %s.", question_id)
    return False


def fetch_question_details(question_id, access_token):
    """Obtiene los detalles de una pregunta en MercadoLibre, incluyendo nombre del cliente, pregunta, producto y link del producto."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        # Obtener datos de la pregunta
        question_url = f"https://api.mercadolibre.com/questions/{question_id}"
        question_response = requests.get(question_url, headers=headers)
        if question_response.status_code != 200:
            logger.error("Error al obtener la pregunta %s: %s", question_id, question_response.json())
            return None

        question_data = question_response.json()
        item_id = question_data.get("item_id")
        user_id = question_data.get("from", {}).get("id")
        question_text = question_data.get("text", "")

        # Obtener datos del producto
        item_url = f"https://api.mercadolibre.com/items/{item_id}"
        item_response = requests.get(item_url, headers=headers)
        if item_response.status_code != 200:
            logger.error("Error al obtener el producto %s: %s", item_id, item_response.json())
            return None

        item_data = item_response.json()
        product_name = item_data.get("title", "")
        product_link = item_data.get("permalink", "")

        # Obtener datos del usuario
        user_url = f"https://api.mercadolibre.com/users/{user_id}"
        user_response = requests.get(user_url, headers=headers)
        if user_response.status_code != 200:
            logger.error("Error al obtener el usuario %s: %s", user_id, user_response.json())
            return None

        user_data = user_response.json()
        user_name = user_data.get("nickname", "Usuario desconocido")

        # Estructurar la respuesta
        result = {
            "Nombre del Cliente": user_name,
            "Pregunta": question_text,
            "Nombre del Producto": product_name,
            "Link del Producto": product_link
        }

        logger.info("Detalles de la pregunta %s obtenidos con éxito.", question_id)
        return result

    except Exception as e:
        logger.exception("Excepción al obtener los detalles de la pregunta %s.", question_id)
        return None

