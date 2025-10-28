from app.shared.core.settings import GOOGLE_APPLICATION_CREDENTIALS,DATASET_ID,TABLE_CREDENTIALS
from app.shared.core.logger import logger
from google.oauth2.service_account import Credentials
from google.cloud import bigquery

def token_meli(user_id):
    credentials = Credentials.from_service_account_info(GOOGLE_APPLICATION_CREDENTIALS)
    CLIENT = bigquery.Client(credentials=credentials, project=credentials.project_id)
    table_path = f"{CLIENT.project}.{DATASET_ID}.{TABLE_CREDENTIALS}"
    QUERY = (
        'SELECT *'
        f'FROM `{table_path}` '
        f'WHERE user_id = {user_id} '  
        'QUALIFY ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY token_created_at ASC)=1')
    query_job = CLIENT.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    access_token = [row.access_token for row in rows][0] 
    logger.info("Token successfully retrieved for user_id")
    return access_token