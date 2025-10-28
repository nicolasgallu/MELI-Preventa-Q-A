import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

#directorio base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Subir un nivel desde "core"

# SERVICES > LLM MODULE
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DS_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GPT_MODEL = "gpt-4"
DS_MODEL = "deepseek-chat"
FALLBACK_MESSAGE = "consultar con humano"

##NOTIFICATIONS EMAIL INTERN
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

##GBQ ACCESS
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, "core", "bigquery-service-account.json")

##TABLAS
DATASET_ID = os.getenv("DATASET_ID")
TABLE_CREDENTIALS = os.getenv("TABLE_CREDENTIALS")
TABLE_INVENTORY = os.getenv("TABLE_INVENTORY")
TABLE_QA_INIT = os.getenv("TABLE_QA_INIT")
TABLE_QA_LLM = os.getenv("TABLE_QA_LLM")
TABLE_PROMPTS = os.getenv("TABLE_PROMPTS")
TABLE_HUM_REPLY = os.getenv("TABLE_HUM_REPLY")

### CONTACTS ###
PHONE_LIST_RAW = os.getenv("PHONE_LIST")
PHONE_LIST = [p.strip() for p in PHONE_LIST_RAW.split(",") if p.strip()]

### FLASK ###
FLASK_PORT = os.getenv("FLASK_PORT")


# WPP PIPELINE #
### WPP ###
WPP_TOKEN = os.getenv("WPP_TOKEN")
WPP_ID = os.getenv("WPP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")
VERIFY_WHOOK =  os.getenv("VERIFY_WHOOK")

#INTERN CODE
SECRET_CODE = os.getenv("SECRET_CODE")