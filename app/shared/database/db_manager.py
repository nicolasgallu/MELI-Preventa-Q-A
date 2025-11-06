from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, insert, select
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.shared.core.logger import logger
import os

# ======================================================
# CONFIGURACIÓN DE CONEXIÓN A CLOUD SQL
# ======================================================

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_SOCKET_DIR = os.getenv("DB_SOCKET_DIR")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/"
    f"{DB_NAME}?host={DB_SOCKET_DIR}/{INSTANCE_CONNECTION_NAME}"
)

logger.info(f"DATABASE URL: {DATABASE_URL}")

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
        Column("question_id", String, primary_key=False),
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


    def question_search(self, question_id):
        """
        """
        try:
            stmt = select(self.questions.c.data).where(
                self.questions.c.question_id == question_id
            )
            with self.engine.connect() as conn:
                result = conn.execute(stmt).fetchone()
                if result:
                    # 'result' es un objeto Row. Accedemos al valor de la columna 'data'
                    question_data = result[0] # o result['data'] si el driver lo soporta mejor
                    logger.info(f"Question ID {question_id} found.")
                    return question_data
                else: 
                    return False
        except Exception as e:
            logger.exception(f"Error verificando existencia de pregunta {question_id}: {e}")
            return False


    def items_search(self, question_id):
        """
        """
        try:
            stmt = select(self.items.c.data).where(
                self.items.c.question_id == question_id
            )
            with self.engine.connect() as conn:
                result = conn.execute(stmt).fetchone()
                if result:
                    return True
                else: 
                    return False
        except Exception as e:
            logger.exception(f"Error verificando existencia de item {question_id}: {e}")
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
