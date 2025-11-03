import json
from app.shared.core.logger import logger
from app.shared.core.settings import FALLBACK_MESSAGE
from app.shared.database.gbq_inventory import get_inventory
from app.shared.database.gbq_llm_prompts import get_prompt_json
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
        self.insert = DBManager()

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
            prompt = get_prompt_json("categories_json")
            # Instancing & API Call
            ai_instance = AiSwitch(prompt, self.question, max_tokens=200, temperature=0.2)
            self.ai_payload = ai_instance.switch()
            self.category = self.ai_payload["response"]
            # Inserting data
            self.insert.insert_ai_response(self.question_id, "category", self.ai_payload)
            logger.info("Finish running Model - Classify Question.")
        except Exception as e:
            logger.error("Unexpected Error while Running - Classify Question - ", exc_info=e)
    
    def _answer_question(self):
        """
        """
        try:
            logger.info("Running Model - Answering Question..")
            # Prompting
            category_prompt = get_prompt_json(self.category)
            prompt = f"""
                {category_prompt}\n
                Esta es la informacion interna sobre el producto:\n
                {self.item_data}
            """
            # Instancing & API Call
            ai_instance = AiSwitch(prompt, self.question, max_tokens=3000, temperature=0.55)
            self.ai_payload = ai_instance.switch()
            # Inserting data
            self.insert.insert_ai_response(self.question_id, "answer", self.ai_payload)
            logger.info("Finish running Model - Answering Question.")
        except Exception as e:
            logger.error("Unexpected Error while Running - Answering Question - ", exc_info=e)

    def audit_answer(self):
        """
        """
        self._answer_question()
        logger.info("Running Model - Audit Answer..")
        # Prompting
        category_prompt = get_prompt_json("audit_json")
        answer = self.ai_payload["response"] #original answer
        full_input = f"""
            customer_question: {self.question}\n
            item_data: {self.item_data}\n"
            ai_answer: {answer}
        """        
        # Instancing & API Call
        ai_instance = AiSwitch(category_prompt, full_input, max_tokens=3000, temperature=0.45)
        self.ai_payload = ai_instance.switch()
        # Inserting data
        self.insert.insert_ai_response(self.question_id, "audit", self.ai_payload)
        logger.info("Finish running Model - Audit Question.")
        
        # Variables
        data = json.loads(self.ai_payload.get("response"))
        status = data.get("valid")
        # Status Condition
        if status == False:
            logger.info("Audit Question - Failed & Corrected.")
            new_answer = data.get("corrected_answer")
            return new_answer
        else:
            logger.info("Audit Question - Successfull.")
            return answer

    def _stock_search(self):
        """LLM read inventory table and returns items realated to question item.
            Returns: A list with max. 5 items by partition.
        """
        try:
            logger.info(f"Running Model Stock Search..")
            # Inventory Set-Up
            inventory = get_inventory(self.user_id)
            rows = len(inventory)
            chunk_size = 400
            partitions = [inventory[i:i + chunk_size].values.tolist() for i in range(0, rows, chunk_size)]
            # Prompting
            category_prompt = get_prompt_json("busqueda_inventario")
            responses = []
            for i in range(len(partitions)):
                items = partitions[i]
                full_prompt = f"""
                    {category_prompt}\n
                    La base con la que vas a trabajar es la siguiente:\n 
                    {items}
                """
                # Instancing & API Call
                ai_instance = AiSwitch(full_prompt, self.question, 5000, 0.2)
                self.ai_payload = ai_instance.switch()
                # Populing Responses
                response = self.ai_payload.get("response")
                responses.append(response)
                # Inserting data
                self.insert.insert_ai_response(self.question_id, "stock_research", self.ai_payload)
            return responses
        
        except Exception as e:
                logger.error("Unexpected Error while running Model Stock Search", exc_info=e)
    
    def recommendation_answer(self):
        """
        """
        responses = self._stock_search()
        try:
            logger.info(f"Running Bot Recomendation Response..")
            # Prompting
            category_prompt = get_prompt_json("respuesta_recomendacion")
            full_prompt = f"""
                {category_prompt}\n  
                La base con la que vas a trabajar es la siguiente:\n 
                {responses}
            """
            # Instancing & API Call
            ai_instance = AiSwitch(full_prompt, self.question, 5000, 0.2)
            self.ai_payload = ai_instance.switch()
            response = self.ai_payload.get("response")
            # Inserting data
            self.insert.insert_ai_response(self.question_id, "stock_recommendation", self.ai_payload)
            return response
        except Exception as e:
            logger.error("Unexpected Error while Running Bot Recomendation Response", exc_info=e)
            return FALLBACK_MESSAGE
    
    def improve_human_answer(self, employee_reply):
        """
        """
        try:
            logger.info(f"Running model to improve the human response")
            # Prompting
            category_prompt = get_prompt_json("improve_human_reply")
            full_prompt = f"""
                {category_prompt} \n
                La pregunta del cliente fue: {self.question}\n
                El producto es: {self.item_data["title"]}
            """
            user_input = f"La respuesta del empleado que tenes que mejorar es la siguiente: {employee_reply}"
            # Instancing & API Call
            logger.info(f"ESTE ES EL INPUT A USAR PARA LA MEJORA{user_input}")
            ai_instance = AiSwitch(full_prompt, user_input, 2500, 0.55)
            self.ai_payload = ai_instance.switch()
            response = self.ai_payload.get("response")
            # Inserting data
            self.insert.insert_ai_response(self.question_id, "improve_human_answer", self.ai_payload)
            return response
        except Exception as e:
            logger.error("Unexpected Error while Running Customer Improve Reply Model", exc_info=e)
            return FALLBACK_MESSAGE
