import json
from app.shared.core.logger import logger
from app.shared.core.settings import FALLBACK_MESSAGE
from app.shared.database.db_manager import DBManager
from app.mercadolibre.utils.ai_switch import AiSwitch


class AiPreOrder:

    def __init__(self, user_id, question_id, question_text, item_data):
        self.user_id = user_id
        self.question_id = question_id
        self.question = question_text
        self.item_data = item_data
        # variables
        self.category = None
        self.ai_payload = None
        self.db_manager = DBManager()
    
    # ////////////////////////////// STAGE OF QUESTION CATEGORIZATION ////////////////////////////////////////
    def classify_question(self):
        """
        Returns the 'category' that matchs the question.

        ----
        DB Notes
        ----
        1. call the switch function, with the categories prompt.
        2. insert_ai_response saves the payload of the complete response.
        3. save_data saves the payload (json) inside the JSON_CATEGORY path.
        """
        try:
            logger.info("Running Model - Classify Question..")
            # Prompting
            sys_prompt = self.db_manager.get_prompt("ai_category")
            # Instancing & API Call
            ai_instance = AiSwitch(sys_prompt, self.question, max_tokens=200, temperature=0.2)
            self.ai_payload = ai_instance.switch()
            self.category = self.ai_payload["response"]
            # Inserting data
            self.db_manager.insert_ai_response(self.question_id, "category", self.ai_payload)
            return self.category
        except Exception as e:
            logger.error("Unexpected Error while Running - Classify Question - ", exc_info=e)

    # ////////////////////////////// STAGE OF ANSWER BY AI ////////////////////////////////////////
    def _answer_question(self):
        """
        """
        try:
            logger.info("Running Model - Answering Question..")
            # Prompting
            sys_prompt = f"""{self.db_manager.get_prompt(self.category)}\n
                        Estas son tus reglas a cumplir: {self.db_manager.get_prompt('rules')}
                """
            user_prompt = f"""
                Pregunta del cliente: {self.question}\n
                Producto en el cual se realiza la pregunta: {self.item_data}
            """
            # Instancing & API Call
            ai_instance = AiSwitch(sys_prompt, user_prompt, max_tokens=3000, temperature=0.55)
            self.ai_payload = ai_instance.switch()
            # Inserting data
            self.db_manager.insert_ai_response(self.question_id, "answer", self.ai_payload)
        except Exception as e:
            logger.error("Unexpected Error while Running - Answering Question - ", exc_info=e)

    # ////////////////////////////// STAGE OF AUDITORY ////////////////////////////////////////
    def audit_answer(self):
        """
        """
        self._answer_question()
        logger.info("Running Model - Audit Answer..")
        # Prompting
        answer = self.ai_payload["response"] #answer from the AI.
        sys_prompt = self.db_manager.get_prompt("ai_auditor")
        user_prompt = f"""
            Pregunta del cliente: {self.question}\n
            Producto en el cual se realiza la pregunta: {self.item_data}\n 
            Respuesta del bot: {answer}
        """
        # Instancing & API Call
        ai_instance = AiSwitch(sys_prompt, user_prompt, max_tokens=3000, temperature=0.45)
        self.ai_payload = ai_instance.switch()
        # Inserting data
        self.db_manager.insert_ai_response(self.question_id, "audit", self.ai_payload)
        
        # Variables
        data = json.loads(self.ai_payload.get("response"))
        status = data.get("valid")
        # Status Condition
        if status == False:
            logger.info("Audit Question - Failed & Corrected.")
            new_answer = data.get("corrected_answer")
            return new_answer
        else:
            logger.info("Audit Question - Not Correction Needed.")
            return answer

    # ////////////////////////////// STAGE OF STOCK SEARCH BY AI (DEPENDING ON CATEGORY) ////////////////////////////////////////
    def _stock_search(self):
        """LLM read inventory table and returns items realated to question item.
            Returns: A list with max. 5 items by partition.
        """
        try:
            logger.info("Running Model Stock Search..")
            # Inventory Set-Up
            inventory_raw = self.db_manager.get_inventory()
            inventory =  [i.get('product_name') for i in inventory_raw]
            total_items = len(inventory)
            chunk_size = 400
            partitions = [inventory[i:i + chunk_size] for i in range(0, total_items, chunk_size)]
            # Sys Prompting
            sys_prompt = self.db_manager.get_prompt("ai_inventory_search")
            responses = []
            for i in range(len(partitions)):
                items = partitions[i]
                # User Prompting
                user_prompt = f"""
                    Pregunta del cliente: {self.question}\n
                    Producto en el cual se realiza la pregunta: {self.item_data.get("title")}\n 
                    El inventario disponible es el seguiente:\n 
                    {items}
                """
                # Instancing & API Call
                ai_instance = AiSwitch(sys_prompt, user_prompt, 5000, 0.2)
                self.ai_payload = ai_instance.switch()
                # Populing Responses
                response = self.ai_payload.get("response")
                responses.append(response)
                # Inserting data
                self.db_manager.insert_ai_response(self.question_id, "stock_search", self.ai_payload)
            return responses
        
        except Exception as e:
                logger.error("Unexpected Error while running Model Stock Search", exc_info=e)

    # ////////////////////////////// STAGE OF PRODUCTS RELATED RECOMMENDATION (DEPENDING ON CATEGORY) ////////////////////////////////////////
    def recommendation_answer(self):
        """
        """
        responses = self._stock_search()
        try:
            logger.info("Running Bot Recomendation Response..")
            # Prompting
            sys_prompt = f"""
                Rol 
                Vas actuar como un vendedor experto en una plataforma de ecommerce con la tarea de sugerirle al cliente cualquiera de los productos 
                que te vamos a dar de nuestro inventario, el objetivo es lograr darle las mejores recomendaciones y ser lo mas amigable y profesional posible.\n
                Estas son tus reglas a cumplir: {self.db_manager.get_prompt('rules')}
            """
            user_prompt = f"""
                    Pregunta del cliente: {self.question}\n
                    Producto en el cual se realiza la pregunta: {self.item_data.get("title")}\n 
                    El inventario disponible es el seguiente:\n 
                    {responses}
                """
            # Instancing & API Call
            ai_instance = AiSwitch(sys_prompt, user_prompt, 5000, 0.2)
            self.ai_payload = ai_instance.switch()
            response = self.ai_payload.get("response")
            # Inserting data
            self.db_manager.insert_ai_response(self.question_id, "stock_recommendation", self.ai_payload)
            return response
        except Exception as e:
            logger.error("Unexpected Error while Running Bot Recomendation Response", exc_info=e)
            return FALLBACK_MESSAGE
    
    # ////////////////////////////// STAGE OF IMPROVING HUMAN REPLY (DEPENDING ON WPP EVENT) ////////////////////////////////////////
    def improve_human_answer(self, employee_reply):
        """
        """
        try:
            logger.info("Running model to improve the human response")
            # Prompting
            category_prompt = self.db_manager.get_prompt("ai_improving_human_reply")
            full_prompt = f"""
                {category_prompt} \n
                La pregunta del cliente fue: {self.question}\n
                El producto es: {self.item_data["title"]}
            """
            user_input = f"La respuesta del empleado que tenes que mejorar es la siguiente: {employee_reply}"
            # Instancing & API Call
            ai_instance = AiSwitch(full_prompt, user_input, 2500, 0.55)
            self.ai_payload = ai_instance.switch()
            response = self.ai_payload.get("response")
            # Inserting data
            self.db_manager.insert_ai_response(self.question_id, "improve_human_answer", self.ai_payload)
            return response
        except Exception as e:
            logger.error("Unexpected Error while Running Customer Improve Reply Model", exc_info=e)
            return FALLBACK_MESSAGE
