from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from google.oauth2.service_account import Credentials
from app.utils.logger import logger
from app.config.config import GOOGLE_APPLICATION_CREDENTIALS,DATASET_ID,TABLE_INVENTORY

# Inicializar las credenciales y cliente de BigQuery
credentials = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)



TABLE_ID = f"{client.project}.{DATASET_ID}.{TABLE_INVENTORY}"

def get_item_context(item_id):
    """Busca información del ítem asociado desde la tabla de BigQuery."""
    try:
        QUERY = (
            'SELECT *'
            f'FROM `{TABLE_ID}` '
            f'WHERE item_id = "{item_id}" '  
            'QUALIFY ROW_NUMBER() OVER(PARTITION BY item_id ORDER BY item_id desc)=1')
        query_job = client.query(QUERY)  # API request
        rows = query_job.to_dataframe()  # Waits for query to finish
        
        item_id = rows["item_id"][0]
        title = rows["title"][0]
        price = rows["price"][0]
        available_quantity = rows["available_quantity"][0]
        description = rows["description"][0]
        condition = rows["condition"][0]
        warranty = rows["warranty"][0]
        boolean_free_shipping = rows["boolean_free_shipping"][0]
        direccion_local = rows["direccion_local"][0]

        # Construir el contexto del ítem
        context = {
            "item_id": item_id,
            "title": title,
            "price": price,
            "available_quantity": available_quantity,
            "description": description,
            "condition":condition ,
            "warranty":warranty ,
            "boolean_free_shipping":boolean_free_shipping ,
            "direccion_local":direccion_local 
            }
        return context

    except NotFound as nf_error:
        logger.info(f"Tabla no encontrada: {nf_error}")
        return None
    except Exception as e:
        logger.info(f"Error inesperado al buscar contexto de ítem {item_id}: {e}")
        return None
