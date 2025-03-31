from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import NotFound
from datetime import datetime
import time
from app.utils.logger import logger
from app.config.config import GOOGLE_APPLICATION_CREDENTIALS,DATASET_ID,TABLE_QA_LLM

# Inicializar las credenciales y cliente de BigQuery
credentials = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

TABLE_ID = f"{client.project}.{DATASET_ID}.{TABLE_QA_LLM}"


def ensure_table_schema():
    """Verifica si la tabla de BigQuery tiene todos los campos definidos.  Si la tabla no existe, la crea.Si la tabla existe pero le faltan campos, la actualiza."""
    try:
        table_ref = client.dataset(DATASET_ID).table(TABLE_QA_LLM)
        try:
            table = client.get_table(table_ref)  # Intenta obtener la tabla
            existing_fields = {field.name: field for field in table.schema}  # Esquema actual
            expected_schema = [
                bigquery.SchemaField("item_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("item_name", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "DATETIME", mode="REQUIRED"),
                bigquery.SchemaField("question", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("question_category", "STRING", mode="NULLABLE"),  
                bigquery.SchemaField("bot_answer", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("bot_answer_sent", "BOOLEAN", mode="NULLABLE"),
                bigquery.SchemaField("bot_feedback", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("bot_feedback_sent", "BOOLEAN", mode="NULLABLE"),
                bigquery.SchemaField("bot_feedback_reason", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("bot_model", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("total_cost", "FLOAT", mode="NULLABLE")
                ]

            missing_fields = [field for field in expected_schema if field.name not in existing_fields]

            if missing_fields:
                logger.info(f"Agregando nuevos campos a la tabla '{TABLE_QA_LLM}': {[field.name for field in missing_fields]}")
                updated_schema = table.schema + missing_fields
                table.schema = updated_schema
                client.update_table(table, ["schema"])
                logger.info(f"Esquema de la tabla '{TABLE_QA_LLM}' actualizado correctamente.")
                time.sleep(3)
            else:
                logger.info("El esquema de la tabla ya está actualizado.")
        except NotFound:
            logger.warning(f"La tabla '{TABLE_QA_LLM}' no existe. Creándola ahora.")
            create_table()
    except Exception as e:
        logger.error(f"Error al verificar/actualizar el esquema de la tabla: {e}")


def create_table():
    """
    Crea la tabla de BigQuery con el esquema definido.
    """
    dataset_ref = client.dataset(DATASET_ID)
    table_ref = dataset_ref.table(TABLE_QA_LLM)
    schema = [
    bigquery.SchemaField("item_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("item_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "DATETIME", mode="REQUIRED"),
    bigquery.SchemaField("question", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("question_category", "STRING", mode="NULLABLE"),  
    bigquery.SchemaField("bot_answer", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("bot_answer_sent", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("bot_feedback", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("bot_feedback_sent", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("bot_feedback_reason", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("bot_model", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("total_cost", "FLOAT", mode="NULLABLE")
    ]
    
    table = bigquery.Table(table_ref, schema=schema)
    client.create_table(table)
    logger.info(f"Tabla '{TABLE_QA_LLM}' creada exitosamente en el dataset '{DATASET_ID}'.")



def load_llm_consumption (item_id, item_name, question, category, bot_answer, 
                          bot_answer_sent=False, bot_feedback="", bot_feedback_sent=False, bot_feedback_reason="",
                          total_cost=0,bot_model=None):
    logger.info(f"guardando datos de consumo en llm_consumption")
    try:
        ensure_table_schema() 
        rows_to_insert = [{
            "item_id": item_id,
            "item_name": item_name,
            "created_at": datetime.now().isoformat(),
            "question": question,
            "question_category": category,
            "bot_answer": bot_answer,
            "bot_answer_sent": bot_answer_sent,
            "bot_feedback": bot_feedback,
            "bot_feedback_sent": bot_feedback_sent,
            "bot_feedback_reason": bot_feedback_reason,
            "bot_model": bot_model,
            "total_cost": total_cost
            }]

        errors = client.insert_rows_json(TABLE_ID, rows_to_insert)
        if errors:
            logger.error(f"Error al insertar el consumo del LLM en BigQuery -> {TABLE_QA_LLM} : {errors}")
        else:
            logger.info(f"Consumo de LLM registrado exitosamente en BigQuery -> {TABLE_QA_LLM}.")
    except Exception as e:
        logger.error(f"Error inesperado al registrar el consumo de LLM en BigQuery -> {TABLE_QA_LLM}: {e}")
