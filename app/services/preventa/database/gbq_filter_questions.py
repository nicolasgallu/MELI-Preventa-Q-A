from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import NotFound
from app.config.config import GOOGLE_APPLICATION_CREDENTIALS,DATASET_ID,TABLE_QA_INIT
from app.utils.logger import logger

# Inicializar las credenciales y cliente de BigQuery
credentials = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

TABLE_ID = f"{client.project}.{DATASET_ID}.{TABLE_QA_INIT}"  # ID completo de la tabla

def ensure_table_exists():
    try:
        dataset_ref = client.dataset(DATASET_ID)
        table_ref = dataset_ref.table(TABLE_QA_INIT)

        # Verificar si la tabla ya existe
        client.get_table(table_ref)  # Esto lanza una excepción si la tabla no existe
        logger.info(f"La tabla '{TABLE_QA_INIT}' ya existe en el dataset '{DATASET_ID}'.")
    except NotFound:
        logger.warning(f"La tabla '{TABLE_QA_INIT}' no existe. Se procederá a crearla.")
        schema = [
            bigquery.SchemaField("question_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("question_text", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("item_id", "STRING", mode="NULLABLE"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        logger.info(f"Tabla '{TABLE_QA_INIT}' creada exitosamente en el dataset '{DATASET_ID}'.")
    except Exception as e:
        logger.error(f"Error inesperado al verificar/crear la tabla '{TABLE_QA_INIT}': {e}")


def register_question_in_db(question_id, question_text=None, item_id=None):
    if not question_id:
        logger.error("El question_id es requerido.")
        return "error"

    try:
        # Asegurarse de que la tabla exista antes de continuar
        ensure_table_exists()

        # Verificar si la pregunta ya está registrada
        query = f"""
        SELECT 1 FROM `{TABLE_ID}`
        WHERE question_id = @question_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("question_id", "STRING", question_id)
            ]
        )
        query_job = client.query(query, job_config=job_config)
        if query_job.result().total_rows > 0:
            logger.info(f"La pregunta {question_id} ya está registrada en la tabla -> {TABLE_QA_INIT}.")
            return "already_registered"

        # Insertar nueva pregunta si hay datos suficientes
        if question_text and item_id:
            rows_to_insert = [
                {
                    "question_id": question_id,
                    "question_text": question_text,
                    "item_id": item_id,
                }
            ]
            errors = client.insert_rows_json(TABLE_ID, rows_to_insert)
            if errors:
                logger.error(f"Error al insertar la pregunta en BigQuery -> {TABLE_QA_INIT}: {errors}")
                return "error"
            logger.info(f"Pregunta {question_id} registrada exitosamente en BigQuery -> {TABLE_QA_INIT}.")
            return "registered"

        logger.warning(f"Falta información para registrar la pregunta {question_id} en BigQuery -> {TABLE_QA_INIT}.")
        return "error"

    except Exception as e:
        logger.error(f"Error al manejar BigQuery -> {TABLE_QA_INIT}: {e}")
        return "error"
