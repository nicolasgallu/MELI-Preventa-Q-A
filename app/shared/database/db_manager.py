import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, insert, select
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.shared.core.logger import logger

# ======================================================
# CONFIGURACIÓN DE CONEXIÓN A CLOUD SQL
# ======================================================

DB_USER = os.getenv("DB_USER", "nicolas")
DB_PASS = os.getenv("DB_PASS", "Pinguin0!")
DB_NAME = os.getenv("DB_NAME", "test_meli")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
DB_SOCKET_DIR = os.getenv("DB_SOCKET_DIR", "/cloudsql")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/"
    f"{DB_NAME}?host={DB_SOCKET_DIR}/{INSTANCE_CONNECTION_NAME}"
)

try:
    ENGINE = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    METADATA = MetaData()

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

    METADATA.create_all(ENGINE)
    logger.info("DEBUG: Tablas verificadas/creadas exitosamente.")

except (OperationalError, ProgrammingError) as e:
    logger.exception(f"Error crítico conectando a Cloud SQL: {e}")
except Exception as e:
    logger.exception(f"Error inesperado en setup de DB: {e}")


# ======================================================
# CLASS DEFINTION
# ======================================================

class DBManager:
    """Maneja las operaciones de inserción en la base de datos."""

    def __init__(self):
        self.engine = ENGINE
        self.questions = questions_table
        self.items = items_table
        self.ai_responses = ai_responses_table


    def question_exists(self, question_id):
        """
        """
        try:
            stmt = select(self.questions.c.question_id).where(
                self.questions.c.question_id == question_id
            )
            with self.engine.connect() as conn:
                result = conn.execute(stmt).fetchone()
                logger.info(f"The question ID was matched as:{result}")
            return True if result else False
        except Exception as e:
            logger.exception(f"Error verificando existencia de pregunta {question_id}: {e}")
            return False

    def insert_questions(self, question_id, data):
        try:
            stmt = insert(self.questions).values(question_id=question_id, data=data)
            with self.engine.begin() as conn:
                conn.execute(stmt)
        except Exception as e:
            logger.exception(f"Error insertando pregunta: {e}")
            raise

    def insert_items(self, question_id, data):
        try:
            stmt = insert(self.items).values(question_id=question_id, data=data)
            with self.engine.begin() as conn:
                conn.execute(stmt)
        except Exception as e:
            logger.exception(f"Error insertando item: {e}")
            raise

    def insert_ai_response(self, question_id, stage, response):
        try:
            stmt = insert(self.ai_responses).values(
                question_id=question_id,
                stage=stage,
                response=response,
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
        except Exception as e:
            logger.exception(f"Error insertando respuesta AI: {e}")
            raise
