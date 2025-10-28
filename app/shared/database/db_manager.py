import os
from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    String, JSON, insert
)
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.shared.core.logger import logger  # Ajustá según tu estructura de proyecto


# ======================================================
# CONFIGURACIÓN GLOBAL (se ejecuta una sola vez por worker)
# ======================================================

# 🔐 Variables de entorno recomendadas (las seteás al desplegar en Cloud Run)
DB_USER = os.getenv("DB_USER", "nicolas")
DB_PASS = os.getenv("DB_PASS", "Pinguin0!")
DB_NAME = os.getenv("DB_NAME", "test_meli")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")  # p.ej. "project:region:instance"
DB_SOCKET_DIR = os.getenv("DB_SOCKET_DIR", "/cloudsql")

# ======================================================
# CONEXIÓN SEGURA A CLOUD SQL (sin proxy manual)
# ======================================================

# En Cloud Run, GCP monta el socket de conexión dentro de /cloudsql/{INSTANCE_CONNECTION_NAME}
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/"
    f"{DB_NAME}?host={DB_SOCKET_DIR}/{INSTANCE_CONNECTION_NAME}"
)

try:
    ENGINE = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,    # Evita errores por conexiones cerradas
        pool_recycle=300,      # Recicla conexiones cada 5 min
    )
    METADATA = MetaData()

    # ======================================================
    # DEFINICIÓN DE TABLAS
    # ======================================================
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

    # ⚠️ OPCIONAL: crear tablas si no existen
    # En producción, mejor usar migraciones (ej: Alembic)
    METADATA.create_all(ENGINE)
    print("DEBUG: Tablas verificadas/creadas exitosamente al inicio del worker.")

except (OperationalError, ProgrammingError) as e:
    print(f"ERROR CRÍTICO EN SETUP: No se pudo conectar a Cloud SQL.")
    logger.exception(f"ERROR CRÍTICO EN SETUP: {e}")
except Exception as e:
    logger.exception(f"ERROR INESPERADO en setup de DB: {e}")


# ======================================================
# CLASE DE INSERCIÓN A LA DB
# ======================================================

class DBInsertManager:
    """
    Clase que maneja las operaciones de inserción en la DB.
    Usa un engine SQLAlchemy global (ENGINE).
    """

    def __init__(self):
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
            with self.engine.begin() as conn:
                conn.execute(stmt)
        except Exception as e:
            logger.exception(f"ERROR INSERTING QUESTIONS: {e}")
            raise

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
