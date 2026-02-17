import os
from dotenv import load_dotenv
load_dotenv()

FALLBACK_MESSAGE = "consultar con humano"

# SERVICES > LLM MODULE
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DS_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# WHAPI CREDS
TOKEN_WHAPI = os.getenv("TOKEN_WHAPI")
PHONE_INTERNAL = os.getenv("PHONE_INTERNAL") #para notificaciones internas al area de GUIAS.
PHONE_CLIENT = os.getenv("PHONE_CLIENT") #para notificaciones externas, ej cliente.

#CLOUD SQL (MYSQL)
INSTANCE_DB = os.getenv("INSTANCE_DB")
USER_DB = os.getenv("USER_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
NAME_DB = os.getenv("NAME_DB")

#SECRET MANAGER
PROJECT_ID=os.getenv("PROJECT_ID")
SECRET_ID=os.getenv("SECRET_ID")

#MERCADOLIBRE USERID
USER_ID=os.getenv("USER_ID")

SCHEMA_MERCADOLIBRE = os.getenv("SCHEMA_MERCADOLIBRE")