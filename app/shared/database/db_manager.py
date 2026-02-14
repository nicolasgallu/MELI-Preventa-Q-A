import json
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, Integer, TEXT, TIMESTAMP, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from google.cloud.sql.connector import Connector
from app.shared.core.logger import logger
from app.shared.core.settings import INSTANCE_DB, USER_DB, PASSWORD_DB, NAME_DB


# ======================================================
# CONEXIÓN
# ======================================================
def getconn():
    connector = Connector()
    conn = connector.connect(
        INSTANCE_DB,
        "pymysql",
        user=USER_DB,
        password=PASSWORD_DB,
        db=NAME_DB,
    )
    return conn

try:
    logger.info(f"Iniciando conexión a Cloud SQL Instancia: {INSTANCE_DB}")
    ENGINE = create_engine(
        "mysql+pymysql://",
        creator=getconn,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=2
    )

    METADATA = MetaData()


    questions_table = Table(
        "questions", METADATA,
        Column("question_id", String(255), primary_key=True),
        Column("data", JSON),
        schema="mercadolibre"
    )

    items_table = Table(
        "items", METADATA,
        Column("question_id", String(255), primary_key=True),
        Column("data", JSON),
        schema="mercadolibre"
    )

    ai_responses_table = Table(
        "ai_responses", METADATA,
        Column("id", Integer, primary_key=True),
        Column("question_id", String(255), index=True),
        Column("stage", String(100)),
        Column("response", JSON),
        schema="mercadolibre"
    )


    catalog = Table(
        "product_catalog_sync", METADATA,
        Column("meli_id", String(255), primary_key=True),
        Column("product_name_meli", String(100)),
        Column("stock", Integer),
        schema="app_import"
    )

    prompts = Table(
        "prompts",
        METADATA,
        Column("id", Integer, primary_key=True), 
        Column("ai_auditor", TEXT), 
        Column("ai_category",TEXT), 
        Column("ai_general", TEXT), 
        Column("ai_inventory_search", TEXT), 
        Column("ai_recommendation", TEXT), 
        Column("ai_improving_human_reply", TEXT), 
        schema="mercadolibre"
    )

    METADATA.create_all(ENGINE)
    logger.info("Tablas verificadas.")

except (OperationalError, ProgrammingError) as e:
    print(e)
    logger.exception(f"Error conexión DB: {e}")


# ======================================================
# DB MANAGER
# ======================================================

class DBManager:
    """Maneja las operaciones usando SQL Puro (text)"""

    def __init__(self):
        self.engine = ENGINE

    # ////////////////////////////// SAFE SEARCH METHODS ////////////////////////////////////////
    def question_search(self, question_id):
        """Busca si existe la pregunta y devuelve su data."""
        try:
            # Usamos :param para evitar inyección SQL
            sql = text("""
                SELECT data 
                FROM mercadolibre.questions 
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
            sql = text("""
                SELECT 1 
                FROM mercadolibre.items 
                WHERE question_id = :question_id 
                LIMIT 1;
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(sql, {"question_id": question_id}).fetchone()
                if result:
                    return True   
                else:
                    False
                
        except Exception as e:
            logger.exception(f"Error buscando item {question_id}: {e}")
            return False

    # ////////////////////////////// INSERT METHODS ////////////////////////////////////////
    def insert_questions(self, question_id, data):
        try:
            # Importante: Aseguramos que 'data' sea un string JSON válido
            json_data = json.dumps(data) if isinstance(data, (dict, list)) else data
            
            sql = text("""
                INSERT INTO mercadolibre.questions (question_id, data) 
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
            
            sql = text("""
                INSERT INTO mercadolibre.items (question_id, data) 
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
            
            sql = text("""
                INSERT INTO mercadolibre.ai_responses (question_id, stage, response) 
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
        
    #ARMAR ESTANDAR, QUE APUNTE A MERCADOLIBRE TABLA DE (INVENTORY) que tenga el mismo formato para futuros clientes porque esta logica esta diseñada para responder solo a Emiliano
        try:
            sql = text("""
                SELECT product_name 
                FROM app_import.product_catalog_sync 
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
        Ejemplo de uso: db.get_prompts('auditor_json')
        """
        try:
            sql = text(f"""
                SELECT {prompt_title} 
                FROM mercadolibre.prompts 
                LIMIT 1;
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(sql).fetchone()
                if result:
                    return result[0] # Retorna el texto del prompt
                return None

        except Exception as e:
            logger.exception(f"Error obteniendo prompt '{prompt_title}': {e}")
            return None