import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

#directorio base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Subir un nivel desde "services"



##UTILS > REFRESH TOKEN
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

#-----VARIABLES CONSTANTES - PREVENTA-----#

## SERVICES > LLM MODULE
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-4"
DS_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DS_MODEL = "deepseek-chat"
COST_PER_1K_TOKENS = {
    "gpt-4": {
        "costo": {
            "input": 0.03,
            "output": 0.06
        }
    },
    "deepseek-chat": {
        "costo": {
            "input": 0.01,
            "output": 0.03
        }
    }
}


FALLBACK_MESSAGE = "consultar con humano"


##SERVICES > HUMAN NOTIFICATION
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

##GBQ ACCESS
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, "config", "bigquery-service-account.json")
##TABLA INVENTARIO
DATASET_ID = os.getenv("DATASET_ID")
TABLE_CREDENTIALS = os.getenv("TABLE_CREDENTIALS")
TABLE_INVENTORY = os.getenv("TABLE_INVENTORY")
TABLE_QA_INIT = os.getenv("TABLE_QA_INIT")
TABLE_QA_LLM = os.getenv("TABLE_QA_LLM")
TABLE_PROMPTS = os.getenv("TABLE_PROMPTS")

#CLUSTER DEFINITION
CLUSTER_PROMPTS = os.path.join(BASE_DIR, "config", "clusters copy.json")
CATEGORIES_PROMPT = os.path.join(BASE_DIR, "config", "categories.json")
AUDIT_PROMPT = os.path.join(BASE_DIR, "config", "audit.json")
