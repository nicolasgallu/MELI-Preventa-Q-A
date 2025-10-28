from app.shared.core.logger import logger
from app.shared.core.settings import GOOGLE_APPLICATION_CREDENTIALS, DATASET_ID, TABLE_PROMPTS
from google.oauth2.service_account import Credentials
from google.cloud import bigquery, bigquery_storage


credentials = Credentials.from_service_account_info(GOOGLE_APPLICATION_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

TABLE_PROMPTS = f"{client.project}.{DATASET_ID}.{TABLE_PROMPTS}"

def get_prompt_json(campo):
    """devuelve el campo seleccionado de la tabla 'prompts_json' en GBQ."""
    logger.info("Running Get Prompts..")
    storage_client = bigquery_storage.BigQueryReadClient(credentials=credentials)
    query = f"""
        SELECT {campo} 
        FROM `{TABLE_PROMPTS}`"""
    query_job = client.query(query)
    data = query_job.to_dataframe(bqstorage_client=storage_client)
    logger.info("Prompts Base Runned Successfully")
    return str(data.iloc[0, 0])
