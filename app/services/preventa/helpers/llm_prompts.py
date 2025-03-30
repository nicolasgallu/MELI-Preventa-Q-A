from google.cloud import bigquery, bigquery_storage
from google.oauth2.service_account import Credentials
from app.utils.logger import logger
from app.config.config import GOOGLE_APPLICATION_CREDENTIALS, DATASET_ID, TABLE_PROMPTS


credentials = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

TABLE_PROMPTS = f"{client.project}.{DATASET_ID}.{TABLE_PROMPTS}"


def get_prompt_json(campo):
    """devuelve el campo seleccionado de la tabla 'prompts_json' en GBQ."""
    storage_client = bigquery_storage.BigQueryReadClient(credentials=credentials)
    query = f"""
    SELECT {campo} 
    FROM `{TABLE_PROMPTS}`
    """
    query_job = client.query(query)
    data = query_job.to_dataframe(bqstorage_client=storage_client)
    logger.info(f"Get prompt: {campo} ejecutado con éxito")
    return str(data.iloc[0, 0])



