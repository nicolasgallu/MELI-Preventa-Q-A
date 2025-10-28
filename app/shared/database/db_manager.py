import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, insert
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.shared.core.logger import logger  # Módulo de logging centralizado

# ======================================================
# CONFIGURACIÓN GLOBAL (una sola vez por worker)
# ======================================================

# Variables de entorno requeridas
DB_USER = os.getenv("DB_USER", "nicolas")
DB_PASS = os.getenv("DB_PASS", "Pinguin0!")
DB_NAME = os.getenv("DB_NAME", "test_meli")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")  # p.ej. "project:region:instance"
DB_SOCKET_DIR = os.getenv("DB_SOCKET_DIR", "/cloudsql")

# Validación de entorno
required_env_vars = ["DB_USER", "DB_PASS", "DB_NAME", "INSTANCE_CONNECTION_NAME"]
missing = [v for v in required_env_vars if not os.getenv(v)]
if missing:
    logger.error(f"❌ Variables de entorno faltantes: {missing}")
else:
    logger.info("✅ Todas las variables de entorno necesarias están definidas.")

# Log de configuración (sin exponer credenciales)
logger.info("==== CONFIG CLOUD SQL CONNECTION ====")
logger.info(f"DB_USER: {DB_USER}")
logger.info(f"DB_NAME: {DB_NAME}")
logger.info(f"INSTANCE_CONNECTION_NAME: {INSTANCE_CONNECTION_NAME}")
logger.info(f"DB_SOCKET_DIR exists: {os.path.exists(DB_SOCKET_DIR)}")
logger.info(f"Full expected socket path: {os.path.join(DB_SOCKET_DIR, INSTANCE_CONNECTION_NAME)}")
logger.info(
    f"DATABASE_URL (sanitized): "
    f"postgresql+psycopg2://{DB_USER}:***@/{DB_NAME}?host={DB_SOCKET_DIR}/{INSTANCE_CONNECTION_NAME}"
)
logger.info("=====================================")

# ======================================================
# CONEXIÓN SEGURA A CLOUD SQL
# ======================================================

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

    # Función auxiliar: test de conexión inicial
    def test_db_connection(engine):
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT NOW()")
                logger.info(f"✅ Conexión a DB exitosa. Hora actual: {list(result)[0][0]}")
        except Exception as e:
            logger.exception("❌ Error conectando a la DB")

    test_db_connection(ENGINE)

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

    # ⚠️ OPCIONAL: crear tablas si no existen (solo para entorno dev)
    METADATA.create_all(ENGINE)
    logger.info("✅ Tablas verificadas o creadas exitosamente al inicio del worker.")

except (OperationalError, ProgrammingError) as e:
    logger.exception("❌ ERROR CRÍTICO EN SETUP: No se pudo conectar o inicializar la base de datos.")
except Exception as e:
    logger.exception("❌ ERROR INESPERADO en setup de DB.")


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
            logger.debug(f"📝 Inserting into 'questions': question_id={question_id}")
            stmt = insert(self.questions).values(
                question_id=question_id,
                data=data
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
            logger.info(f"✅ Inserted question {question_id}")
        except Exception as e:
            logger.exception(f"❌ ERROR INSERTING QUESTIONS: {e}")
            raise

    def insert_items(self, question_id, data):
        """Insert Item Data related to question"""
        try:
            logger.debug(f"📝 Inserting into 'items': question_id={question_id}")
            stmt = insert(self.items).values(
                question_id=question_id,
                data=data,
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
            logger.info(f"✅ Inserted item {question_id}")
        except Exception as e:
            logger.exception(f"❌ ERROR INSERTING ITEMS: {e}")
            raise

    def insert_ai_response(self, question_id, stage, response):
        """Insert AI responses"""
        try:
            logger.debug(f"📝 Inserting into 'ai_responses': question_id={question_id}, stage={stage}")
            stmt = insert(self.ai_responses).values(
                question_id=question_id,
                stage=stage,
                response=response,
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
            logger.info(f"✅ Inserted AI response for {question_id} at stage {stage}")
        except Exception as e:
            logger.exception(f"❌ ERROR INSERTING AI RESPONSE: {e}")
            raise
