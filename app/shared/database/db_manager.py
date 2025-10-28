from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    String, JSON, insert
)
from app.shared.core.logger import logger


class DBInsertManager:
    def __init__(self):
        # Configuración de conexión
        DB_HOST = "127.0.0.1"
        DB_PORT = "5432"
        DB_NAME = "test_meli"
        DB_USER = "nicolas"
        DB_PASS = "Pinguin0!"
        
        database_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        self.engine = create_engine(database_url)
        self.metadata = MetaData()

        self.questions = Table(
            "questions",
            self.metadata,
            Column("question_id", String, primary_key=True),
            Column("data", JSON),
        )

        self.items = Table(
            "items",
            self.metadata,
            Column("question_id", String, primary_key=True),
            Column("data", JSON),
        )

        self.ai_responses = Table(
            "ai_responses",
            self.metadata,
            Column("question_id", String, primary_key=True),
            Column("stage", String),
            Column("response", JSON),
        )

        # Crea las tablas si no existen
        self.metadata.create_all(self.engine)

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
            logger.exception(f"ERROR INSERTING {e}")


    def insert_items(self, question_id, data):
        """Insert Item Data related to question"""
        stmt = insert(self.items).values(
            question_id=question_id,
            data=data,
        )
        with self.engine.begin() as conn:
            conn.execute(stmt)

    def insert_ai_response(self, question_id, stage, response):
        """Insert AI responses"""
        stmt = insert(self.ai_responses).values(
            question_id=question_id,
            stage=stage,
            response=response,
        )
        with self.engine.begin() as conn:
            conn.execute(stmt)
