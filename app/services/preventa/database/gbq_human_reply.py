from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import NotFound
from app.config.config import GOOGLE_APPLICATION_CREDENTIALS,DATASET_ID,TABLE_HUM_REPLY
from app.utils.logger import logger

# Inicializar las credenciales y cliente de BigQuery
credentials = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

TABLE_ID = f"{client.project}.{DATASET_ID}.{TABLE_HUM_REPLY}"  # ID completo de la tabla

def ensure_table_exists():
    try:
        dataset_ref = client.dataset(DATASET_ID)
        table_ref = dataset_ref.table(TABLE_HUM_REPLY)

        # Verificar si la tabla ya existe
        client.get_table(table_ref)  # Esto lanza una excepción si la tabla no existe
        logger.info(f"La tabla '{TABLE_HUM_REPLY}' ya existe en el dataset '{DATASET_ID}'.")

    except NotFound:
        logger.warning(f"La tabla '{TABLE_HUM_REPLY}' no existe. Se procederá a crearla.")
        schema = [
            bigquery.SchemaField("created_at", "DATETIME", mode="NULLABLE"),
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("question_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("phone", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("employee_name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("response", "STRING", mode="NULLABLE"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        logger.info(f"Tabla '{TABLE_HUM_REPLY}' creada exitosamente en el dataset '{DATASET_ID}'.")

    except Exception as e:
        logger.error(f"Error inesperado al verificar/crear la tabla '{TABLE_HUM_REPLY}': {e}")




def db_write_reply(created_at, user_id, question_id, source, phone, employee_name, response,):
    try:
        ensure_table_exists()
        rows_to_insert = [{
            "created_at" : created_at,
            "user_id" : user_id,
            "question_id" : question_id,
            "source" : source,
            "phone" : phone,
            "employee_name" : employee_name,
            "response" : response,
            }]
        errors = client.insert_rows_json(TABLE_ID, rows_to_insert)
        
        if errors:
            return logger.error(f"Error al escribir human reply GBQ -> {TABLE_HUM_REPLY}: {errors}")
        return logger.info(f"Respuesta {response} registrada exitosamente en BigQuery -> {TABLE_HUM_REPLY}.")
         
    
    except Exception as e:
        return logger.error(f"Error al manejar BigQuery -> {TABLE_HUM_REPLY}: {e}")
