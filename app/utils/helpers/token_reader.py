from app.utils.logger import logger
from app.config.config import CLIENT_ID,GOOGLE_APPLICATION_CREDENTIALS,DATASET_ID,TABLE_CREDENTIALS
from google.cloud import bigquery
from google.oauth2.service_account import Credentials

#la extracccion del token, debe ser segun el ultimo dato y ademas coincidir con el dato de app_id
def return_token():
    credentials = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
    CLIENT = bigquery.Client(credentials=credentials, project=credentials.project_id)
    TABLE_ID = f"{CLIENT.project}.{DATASET_ID}.{TABLE_CREDENTIALS}"

    QUERY = (
        'SELECT *'
        f'FROM `{TABLE_ID}` '
        f'WHERE id = {CLIENT_ID} '  
        'QUALIFY ROW_NUMBER() OVER(PARTITION BY id ORDER BY token_created_at desc)=1')
    query_job = CLIENT.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    access_token = [row.access_token for row in rows][0] 
    logger.info("token obtenido exitosamente")
    return access_token









