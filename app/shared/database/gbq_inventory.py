from app.shared.core.settings import GOOGLE_APPLICATION_CREDENTIALS,DATASET_ID,TABLE_INVENTORY
from app.shared.core.logger import logger
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from google.oauth2.service_account import Credentials

# Inicializar las credenciales y cliente de BigQuery
credentials = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

TABLE_ID = f"{client.project}.{DATASET_ID}.{TABLE_INVENTORY}"

def get_inventory(user_id):
    """Get all the items with available stock from a user"""
    try:
        QUERY = (
            'SELECT title '
            f'FROM `{TABLE_ID}` '
            f'WHERE user_id = "{user_id}" AND available_quantity > 0 '  
            'group by title '
            'order by 1 ')
        query_job = client.query(QUERY)  # API request
        inventory = query_job.to_dataframe()  # Waits for query to finish

        return inventory

    except NotFound as nf_error:
        logger.info(f"Tabla no encontrada: {nf_error}")
        return None
    except Exception as e:
        logger.info(f"Error inesperado al buscar items del user: {user_id}: {e}")
        return None
