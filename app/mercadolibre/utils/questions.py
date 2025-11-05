import requests
from datetime import datetime
from app.shared.core.logger import logger
from app.shared.database.db_manager import DBManager

class QuestionsAPI():
    
    BASE_URL = "https://api.mercadolibre.com/questions"
    ANSWERS_URL = "https://api.mercadolibre.com/answers"
    ITEMS_URL = "https://api.mercadolibre.com/items"

    def __init__(self, user_id, question_id, access_token, item_id=None):
        self.user_id = user_id
        self.question_id = question_id
        self.token = access_token  
        self.headers = {"Authorization": f"Bearer {self.token}"}
        # Varibale
        self.item_id = item_id        
        # DB Manager
        self.dbmanager = DBManager()


    def get_question_data(self):
        """Obtiene datos de la pregunta recibida y realiza check de si ya esta procesada"""
        try:
            url = f"{self.BASE_URL}/{self.question_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                question_data = response.json()
                self.item_id = question_data.get("item_id")
                status = question_data.get("status")
                logger.info("CHECKING IF ANSWERED")
                if status == "ANSWERED":
                    return "already_answered"
                if self.dbmanager.question_search(self.question_id) != False:
                    return "already_registered"
                else:
                    payload = {
                        "status":status,
                        "text":question_data.get("text"),
                        "item_id":self.item_id,
                        "user_id": self.user_id,
                        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                        } 
                    # Inserting data
                    self.dbmanager.insert_questions(self.question_id, payload)
                    return payload
            logger.error(f"Error fetching question {self.question_id}: {response.json()}")
        except Exception as e:
            logger.exception(f"Exception fetching question {self.question_id}")
        return False


    def get_item_data(self):
        """Obtiene los datos básicos del item desde la API."""
        try:
            # Fields Definition
            url_a = f"""
                {self.ITEMS_URL}/{self.item_id}?
                attributes=id,
                seller_id,
                permalink,
                price,
                category_id,
                title,
                available_quantity,
                condition,
                warranty,
                shipping.free_shipping,
                seller_address.comment,
                seller_address.address_line"""
            # Endpoint General
            response_a = requests.get(url_a, headers=self.headers)
            if response_a.status_code != 200:
                logger.error(f"Error fetching item data {self.item_id}: {response_a.json()}")
                return False        
            data = response_a.json()
            # Endpoint Description
            url_b = f"{self.ITEMS_URL}/{self.item_id}/description"
            response_b = requests.get(url_b, headers=self.headers)
            if response_b.status_code == 200:
                data["description"] = response_b.json().get("plain_text", "")
            else:
                data["description"] = ""
            # Complete Output
            payload = {
                "item_id": self.item_id,
                "title": data.get("title"),
                "price": data.get("price"),
                "available_quantity": data.get("available_quantity", 0.0),
                "description": data.get("description"),
                "condition": data.get("condition"),
                "warranty": data.get("warranty"),
                "boolean_free_shipping": data.get("shipping", {}).get("free_shipping", False),
                "local_address": (
                    (data.get("seller_address", {}).get("comment") or "") + " " +
                    (data.get("seller_address", {}).get("address_line") or "")
                ).strip(),
                "permalink": data.get("permalink")
            }
            # Validating that item related to question dont exits
            item = self.dbmanager.items_search(self.question_id)
            # Inserting data
            if item  == False:
                self.dbmanager.insert_items(self.question_id, payload)
            else:
                None            
            return payload
        except Exception as e:
            logger.exception(f"Exception fetching item data {self.item_id}")
            return False


    def post_response(self, answer):
        payload = {
            "question_id": self.question_id, 
            "text": answer}
        try:
            response = requests.post(self.ANSWERS_URL, headers=self.headers, json=payload)
            if response.status_code == 200:
                logger.info(f"Successfull Response to Question:{self.question_id}")
                return True
            logger.error(f"Error to Response Question:{self.question_id} - {response.json()}")
        except Exception as e:
             logger.exception(f"Exception to Response Question:{self.question_id} - {e}")
        return False
