import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.utils.logger import logger
from app.config.config import SENDER_EMAIL,SENDER_PASSWORD,RECIPIENT_EMAIL



def notify_human(subject, question_text):
    """Envía un correo con los detalles de la pregunta en formato estructurado."""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Formatear el diccionario en líneas legibles
    if isinstance(question_text, dict):
        question_text = "\n".join([f"{key}: {value}" for key, value in question_text.items()])

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(question_text, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Iniciar conexión segura
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            logger.info("Correo enviado exitosamente.")
    except Exception as e:
        logger.error(f"Error al enviar el correo: {e}")