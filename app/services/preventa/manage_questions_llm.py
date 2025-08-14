import json
import re
from json.decoder import JSONDecodeError
from app.utils.logger import logger
from app.config.config import COST_PER_1K_TOKENS,FALLBACK_MESSAGE
from app.services.preventa.database.gbq_item_context import get_item_context
from app.services.preventa.helpers.llm_switch import switch_llm_body
from app.services.preventa.helpers.llm_recomendation import suggest_response
from app.services.preventa.database.gbq_llm_consume import load_llm_consumption
from app.services.preventa.database.gbq_llm_prompts import get_prompt_json


REQUIRED_KEYS = {"respuesta_valida", "razon_rechazo", "correccion_sugerida"}

class ProductQuestionBot:

    def _calculate_cost(self, response_json, model):
        """Calculate the cost in USD of the model.
        Args:
            response_json: llm response metadata.
            model: model used.
        Returns: Cost in USD (float)
        """
        try:
            logger.info(f"Running Model Usage Cost..")
            cost_data = COST_PER_1K_TOKENS.get(model, {"costo": {"input": 0.0, "output": 0.0}})
            usage = response_json.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            input_cost  = cost_data["costo"]["input"]  * prompt_tokens / 1000
            output_cost = cost_data["costo"]["output"] * completion_tokens / 1000
            return input_cost + output_cost
        except Exception as e:
            logger.error("Unexpected Error while calculating LLM cost", exc_info=e)
            return 0


    def _classify_question(self, question):
        """Clasify the customer question within a category.
        Args:
            question: User Question.
        Returns: Category (str) and total_cost (float)
        """
        try:
            logger.info(f"Running Question Category Model..")
            prompt = get_prompt_json("categories_json")
            response_json,model = switch_llm_body(prompt, question, 200, 0.2)
            category = response_json['choices'][0]['message']['content'].strip()
            total_cost = self._calculate_cost(response_json,model)
            return category,total_cost
        except Exception as e:
            logger.error("Unexpected Error while Running Category Model", exc_info=e)
    

    def _answering_customer (self, question, category, item_context, total_cost=0):
        """LLM Call to responde to Customer Question.
        Args:
            question: User Question.
            category: Question Category.
            item_context: Item Metadata.
            total_cost: Cost of the Model Use.
        Returns: response (str) , total_cost (float), model (str)
        """
        try:
            logger.info(f"Running Model to Reply Customer Question..")
            categ_prompt = get_prompt_json(category)
            prompt = f"{categ_prompt} \n ----- \n la pregunta del cliente es sobre el siguiente producto: {item_context}"
            response_json,model = switch_llm_body(prompt, question, 3000, 0.55)
            response = response_json['choices'][0]['message']['content'].strip()
            total_cost = self._calculate_cost(response_json,model)
            return response, total_cost, model
        except Exception as e:
            logger.error("Unexpected Error while Running Customer Reply Model", exc_info=e)
        

    #――――――――――――AUDIT AUXILIARS AND MAIN AUDIT FUNCTIOṆ̣̣̣――――――――――――

    def _strip_code_fences(self, text: str):
        """Elimina ```json … ``` si el modelo lo incluye."""
        if text.startswith("```") and text.endswith("```"):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
        return text.strip()

    def _parse_and_validate_audit(self, output_text: str):
        """
        Intenta parsear output_text como JSON y verificar keys obligatorias.
        Devuelve el dict si todo está OK, o None en caso contrario.
        """
        try:
            payload = json.loads(output_text)
        except JSONDecodeError as e:
            logger.error("JSON inválido en auditoría: %s", output_text, exc_info=e)
            return None

        if not isinstance(payload, dict):
            logger.error("Respuesta de auditoría no es un dict: %r", payload)
            return None

        faltantes = REQUIRED_KEYS - payload.keys()
        if faltantes:
            logger.error("Faltan claves en auditoría: %s", faltantes)
            return None

        return payload

    def _audit_answer(self, question, item_context, response):
        logger.info("Running Audit Bot…")
        prompt = get_prompt_json("audit_json")
        full_input = (
            f"pregunta_cliente: {question}\n"
            f"contexto: {item_context}\n"
            f"respuesta_llm: {response}"
        )

        response_json, model = switch_llm_body(prompt, full_input, 3000, 0.45)
        total_cost = self._calculate_cost(response_json, model)
        raw = response_json['choices'][0]['message']['content']
        cleaned = self._strip_code_fences(raw)

        audit_payload = self._parse_and_validate_audit(cleaned)
        if audit_payload:
            return audit_payload, total_cost, model
        # Si llegamos acá, la auditoría falló: devolvemos solo el coste >>validar como levantar el error.
        return total_cost


#――――――――――――FILTER ANSWER――――――――――――

    def _filter_output(self,response):
        if "humano" in response.lower():
            logger.info(f"Falls in Direct Fallback Filter. ❌")
            return True
        else:
            logger.info(f"Passed the Direct Fallback Filter. ✅")
            return False

#――――――――――――MAIN FUNCTION――――――――――――

    def _execute_bot(self, user_id=str, question=str, item_context=str, item_id=str, item_name=str):
        total_cost = 0
        feedback = ""
        reason = ""

        #0) Classify the question & calculating acumulated cost.
        category, new_cost = self._classify_question(question)
        total_cost += new_cost

        #1) Running LLM recomendation System.
        if category == "busqueda_inventario":
            answer = suggest_response(user_id,question)
            if self._filter_output(answer):
                return FALLBACK_MESSAGE
            else:
                return answer

        #2) Generate Bot Reply & calculating acumulated cost.
        answer, new_cost, model = self._answering_customer(question, category, item_context,total_cost)
        total_cost += new_cost
        
        #3) Direct Filters & Auditing Bot Reply.
            #a. direct fallback filter
        if self._filter_output(answer): 
            load_llm_consumption(item_id, item_name, question, category, answer, False, feedback, False, reason, total_cost, model)
            return FALLBACK_MESSAGE
        
            #b. auditing bot reply
        try:
            audit_payload, new_cost, model = self._audit_answer(question, item_context, answer)
            bool_valid = audit_payload["respuesta_valida"]
            feedback = audit_payload["correccion_sugerida"]
            reason = audit_payload["razon_rechazo"]
            total_cost += new_cost

            #c. bot reply passed audit control.
            if bool_valid is True or str(bool_valid).lower() == "true":
                logger.info(f"Bot Reply passed the Audit Control. ✅")
                load_llm_consumption(item_id, item_name, question, category, answer, True, feedback, False, reason ,total_cost, model)
                return answer
            
            #d. bot reply did not passed audit control.
            elif len(feedback) > 10:
                logger.info(f"Bot Audit returned a Feedback.")
                if self._filter_output(feedback): 
                    load_llm_consumption(item_id, item_name, question, category, answer, False, feedback, False, reason, total_cost, model)
                    return FALLBACK_MESSAGE
                else:
                    logger.info(f"Bot Audit Feedback is good to use. ✅")
                    load_llm_consumption(item_id, item_name, question, category, answer, False, feedback, True, reason, total_cost, model)
                    return feedback         
                       
        except Exception as e:
            logger.error("Unexpected Error while Running Audit Model, returning FallBack Reply.. ", exc_info=e)
            total_cost += new_cost
            load_llm_consumption(item_id, item_name, question, category, answer, False, feedback, False, reason, total_cost, model)
            return FALLBACK_MESSAGE
            



    def generate_llm_response(self, user_id, question, item_id):
        try:
            item_context = get_item_context(item_id)
            if not item_context:
                logger.error(f"There is not context for the following item: {item_id}, runngin FallBack Reply")
                return FALLBACK_MESSAGE

            item_name = item_context["title"]
            item_context =  { 
                "product_name" : item_context["title"], 
                "description" : item_context["description"], 
                "available_quantity" : item_context["available_quantity"], 
                "price" : item_context["price"], 
                "condition" : item_context["condition"], 
                "warranty" : item_context["warranty"], 
                "boolean_free_shipping" : item_context["boolean_free_shipping"], 
                "direccion_local" : item_context["direccion_local"]}
            return self._execute_bot(user_id, question, item_context, item_id, item_name)
        
        except Exception as e:
            logger.error("Unexpected Error while starting running Bot Model, Running Fallback Reply Instead.",exc_info=e)
            return FALLBACK_MESSAGE

        
