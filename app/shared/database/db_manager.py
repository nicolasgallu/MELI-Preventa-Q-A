import json
from sqlalchemy import create_engine, text
from google.cloud.sql.connector import Connector
from app.shared.core.logger import logger
from app.shared.core.settings import INSTANCE_DB, USER_DB, PASSWORD_DB, NAME_DB, SCHEMA_MERCADOLIBRE

# ======================================================
# CONEXIÓN
# ======================================================
def getconn():
    connector = Connector() 
    return connector.connect(
        INSTANCE_DB,
        "pymysql",
        user=USER_DB,
        password=PASSWORD_DB,
        db=NAME_DB,
    )   

engine = create_engine(
        "mysql+pymysql://",
        creator=getconn,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=2,
    )

# ======================================================
# DB MANAGER
# ======================================================

class DBManager:
    """Maneja las operaciones usando SQL Puro (text)"""

    def __init__(self):
        self.engine = engine

    # ////////////////////////////// SAFE SEARCH METHODS ////////////////////////////////////////
    def question_search(self, question_id):
        """Busca si existe la pregunta y devuelve su data."""
        try:
            sql = text(f"""
                SELECT data 
                FROM {SCHEMA_MERCADOLIBRE}.questions 
                WHERE question_id = :question_id 
                LIMIT 1;
            """)
            with self.engine.connect() as conn:
                result = conn.execute(sql, {"question_id": question_id}).fetchone()
                if result:
                    return json.loads(result[0])
                return False
        except Exception as e:
            logger.exception(f"Error buscando pregunta {question_id}: {e}")
            return False

    def items_search(self, question_id):
        """Verifica existencia del item (True/False)."""
        try:
            sql = text(f"""
                SELECT 1 
                FROM {SCHEMA_MERCADOLIBRE}.items 
                WHERE question_id = :question_id 
                LIMIT 1;
            """)
            with self.engine.connect() as conn:
                result = conn.execute(sql, {"question_id": question_id}).fetchone()
                if result:
                    return True   
                else:
                    return False 
        except Exception as e:
            logger.exception(f"Error buscando item {question_id}: {e}")
            return False

    # ////////////////////////////// INSERT METHODS ////////////////////////////////////////
    def insert_questions(self, question_id, data):
        try:
            json_data = json.dumps(data) if isinstance(data, (dict, list)) else data
            sql = text(f"""
                INSERT INTO {SCHEMA_MERCADOLIBRE}.questions (question_id, data) 
                VALUES (:question_id, :data);
            """)
            with self.engine.begin() as conn:
                conn.execute(sql, {"question_id": question_id, "data": json_data})
        except Exception as e:
            logger.exception(f"Error insertando pregunta: {e}")
            raise

    def insert_items(self, question_id, data):
        try:
            json_data = json.dumps(data) if isinstance(data, (dict, list)) else data
            
            sql = text(f"""
                INSERT INTO {SCHEMA_MERCADOLIBRE}.items (question_id, data) 
                VALUES (:question_id, :data);
            """)
            with self.engine.begin() as conn:
                conn.execute(sql, {"question_id": question_id, "data": json_data})
        except Exception as e:
            logger.exception(f"Error insertando item: {e}")
            raise

    def insert_ai_response(self, question_id, stage, response):
        try:
            json_resp = json.dumps(response) if isinstance(response, (dict, list)) else response
            sql = text(f"""
                INSERT INTO {SCHEMA_MERCADOLIBRE}.ai_responses (question_id, stage, response) 
                VALUES (:question_id, :stage, :resp);
            """)
            with self.engine.begin() as conn:
                conn.execute(sql, {"question_id": question_id, "stage": stage, "resp": json_resp})
        except Exception as e:
            logger.exception(f"Error insertando AI response: {e}")
            raise

    # ////////////////////////////// GET METHODS ////////////////////////////////////////
    def get_inventory(self):
        """Trae items Publicados y Activos en Mercadolibre con stock > 0 ordenados por nombre.""" 
        try:
            sql = text(f"""
                SELECT product_name 
                FROM {SCHEMA_MERCADOLIBRE}.product_status 
                WHERE stock > 0 AND meli_id IS NOT NULL AND status = 'active'
            """)
            with self.engine.connect() as conn:
                result = conn.execute(sql)
                return [dict(row) for row in result.mappings()]      
        except Exception as e:
            logger.exception(f"Error obteniendo inventario: {e}")
            return None

    def get_prompt(self, prompt_title):
        """
        Busca el texto de un prompt específico por su título.
        """
        try:
            sql = text(f"""
                SELECT {prompt_title} 
                FROM {SCHEMA_MERCADOLIBRE}.prompts 
                LIMIT 1;
            """)
            with self.engine.connect() as conn:
                result = conn.execute(sql).fetchone()
                if result:
                    return result[0] 
                return None
        except Exception as e:
            logger.exception(f"Error obteniendo prompt '{prompt_title}': {e}")
            return None