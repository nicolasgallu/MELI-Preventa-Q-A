import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.utils.logger import logger
from app.config.config import SENDER_EMAIL,SENDER_PASSWORD,WPP_TOKEN,WPP_ID,PHONE_LIST


def notify_errors_intern(subject,message):
    """Send critical/unexpected errors directly to Guias Inboox"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Iniciar conexión segura
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            logger.info("Correo enviado exitosamente.")
    except Exception as e:
        logger.error(f"Error al enviar el correo: {e}")



def notify_human_wpp(question_text, question_id, item_id, user_id, item_link, item_name):
    """Envía un mensaje con plantilla a cada número definido en PHONE_LIST."""

    template = (
        "⚠️ *El bot no pudo responder esta consulta.*\n\n"
        "Por favor, respondé solo reemplazando el campo *'su respuesta aquí'*. El Bot la mejorará automáticamente, por lo que no hace falta extenderse.\n"
        "*No modifiques el resto del mensaje*, así el sistema puede procesarlo correctamente.\n\n"
        f"*ID:* {question_id}-{user_id}-{item_id}\n"
        f"*URL:* {item_link} \n"
        f"*ITEM:* {item_name} \n"
        f"*PREGUNTA:* {question_text}\n\n"
        "*RESPUESTA:* <su respuesta aquí>"
    )

    url = f"https://graph.facebook.com/v22.0/{WPP_ID}/messages"
    header = {
        "Authorization": f"Bearer {WPP_TOKEN}",
        "Content-Type": "application/json"
    }

    for destino in PHONE_LIST:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": destino,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": template
            }
        }

        try:
            response = requests.post(url, headers=header, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Mensaje enviado a: {destino}")
        except requests.RequestException as e:
            logger.error(f"Error al enviar a {destino}: {e}")

             


def notify_human_wpp_answered(question_id, item_id, user_id, response):
    """Envía un mensaje confirmando el deliver de la respuesta al cliente, 
    a todos los teléfonos configurados.
    """

    template = (
        "*✅ Respuesta enviada correctamente al cliente.*\n\n"
        f"*ID:* {question_id}-{user_id}-{item_id}\n"
        f"*RESPUESTA MEJORADA:* {response}"
    )

    url = f"https://graph.facebook.com/v22.0/{WPP_ID}/messages"
    header = {
        "Authorization": f"Bearer {WPP_TOKEN}",
        "Content-Type": "application/json"
    }

    for destino in PHONE_LIST:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": destino,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": template
            }
        }

        try:
            response = requests.post(url, headers=header, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Confirmación enviada a: {destino}")
        except requests.RequestException as e:
            logger.error(f"Error al enviar confirmación a {destino}: {e}")
