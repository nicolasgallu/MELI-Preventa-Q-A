import os 
import time  # <--- NUEVO: Necesario para los retrasos
from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    String, JSON, insert
)
# Asumo que esta importación es correcta para tu proyecto
from app.shared.core.logger import logger 
from sqlalchemy.exc import OperationalError, ProgrammingError

# --- CONFIGURACIÓN E INICIALIZACIÓN GLOBAL (Singleton) ---
# Estas líneas se ejecutan UNA SOLA VEZ cuando el worker de Gunicorn arranca.

DB_HOST = "127.0.0.1" 
DB_PORT = "5432"
# Asegúrate de que estos valores sean EXACTAMENTE los correctos para tu DB
DB_NAME = "test_meli"
DB_USER = "nicolas"
DB_PASS = "Pinguin0!"
        
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 1. Crear el Engine y Metadata UNA VEZ
ENGINE = create_engine(DATABASE_URL)
METADATA = MetaData()

# 2. Definición de Tablas
questions_table = Table(
    "questions",
    METADATA,
    Column("question_id", String, primary_key=True),
    Column("data", JSON),
)

items_table = Table(
    "items",
    METADATA,
    Column("question_id", String, primary_key=True),
    Column("data", JSON),
)

ai_responses_table = Table(
    "ai_responses",
    METADATA,
    Column("question_id", String, primary_key=True),
    Column("stage", String),
    Column("response", JSON),
)

# 3. Intento de Creación de Tablas con Retraso y Reintento
# Esto resuelve la "carrera de condición" donde el Proxy no ha terminado de arrancar en 5432
MAX_RETRIES = 10  # Número máximo de intentos
RETRY_DELAY = 10  # Retraso en segundos entre cada intento

for attempt in range(MAX_RETRIES):
    try:
        if attempt > 0:
            # Esperamos ANTES de intentar la conexión, dándole tiempo al Proxy
            print(f"DEBUG: Conexión al Proxy fallida. Esperando {RETRY_DELAY}s... (Intento {attempt + 1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY) 

        # Esto intenta la conexión y la creación de tablas
        METADATA.create_all(ENGINE)
        print("DEBUG: Tablas verificadas/creadas exitosamente al inicio del worker.")
        break  # Si tiene éxito, salimos del bucle
    except (OperationalError, ProgrammingError) as e:
        if attempt == MAX_RETRIES - 1:
            # Si fallamos en el último intento, registramos el error crítico
            print("ERROR CRÍTICO EN SETUP: Falló la conexión inicial a 127.0.0.1 (Proxy) después de varios intentos.")
            logger.exception(f"ERROR CRÍTICO EN SETUP: {e}")
            # No re-lanzamos la excepción aquí, permitiendo que el worker se inicie.
            # Las inserciones posteriores seguirán fallando hasta que se arregle la causa raíz.
    except Exception as e:
        logger.exception(f"ERROR INESPERADO en setup de DB: {e}")
        break


# --- CLASE DE INSERCIÓN (Para uso en runtime) ---
class DBInsertManager:
    """
    Clase que maneja las operaciones de la DB.
    Usa el motor (ENGINE) creado globalmente.
    """
    def __init__(self):
        # La inicialización es instantánea, ya que solo se referencia al motor existente.
        self.engine = ENGINE
        self.questions = questions_table
        self.items = items_table
        self.ai_responses = ai_responses_table

    def insert_questions(self, question_id, data):
        """Insert Questions Received and Metadata"""
        try:
            stmt = insert(self.questions).values(
                question_id=question_id,
                data=data
            )
            # La conexión de red real se establece aquí, bajo el timeout de la solicitud.
            with self.engine.begin() as conn:
                conn.execute(stmt)
        except Exception as e:
            logger.exception(f"ERROR INSERTING QUESTIONS: {e}")
            raise # Re-lanza la excepción

    def insert_items(self, question_id, data):
        """Insert Item Data related to question"""
        try:
            stmt = insert(self.items).values(
                question_id=question_id,
                data=data,
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
        except Exception as e:
            logger.exception(f"ERROR INSERTING ITEMS: {e}")
            raise

    def insert_ai_response(self, question_id, stage, response):
        """Insert AI responses"""
        try:
            stmt = insert(self.ai_responses).values(
                question_id=question_id,
                stage=stage,
                response=response,
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
        except Exception as e:
            logger.exception(f"ERROR INSERTING AI RESPONSE: {e}")
            raise