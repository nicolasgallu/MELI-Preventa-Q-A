from app.utils.logger import logger
from app.config.config import COST_PER_1K_TOKENS,FALLBACK_MESSAGE
from app.services.preventa.helpers.llm_switch import switch_llm_body
from app.services.preventa.database.gbq_llm_consume import load_llm_consumption
from app.services.preventa.database.gbq_llm_prompts import get_prompt_json



class ImproveHumanReply:
    
    def __init__(self):
        self

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


    def _call_llm (self, question, item, employee_reply, category):
        """Mejora la respuesta del Humano utilizando el LLM"""
        try:
            logger.info(f"Ejecutando modelo para mejorar respuesta del Humano")
            categ_prompt = get_prompt_json(category)
            prompt = f"{categ_prompt} \n ----- \n La pregunta del cliente fue: {question} \n ----- \n  El producto es: {item}"
            impr_msg = f"La respuesta del empleado que tenes que mejorar es la siguiente: {employee_reply}"
            response_json,model = switch_llm_body(prompt, impr_msg, 2500, 0.55)
            response = response_json['choices'][0]['message']['content'].strip()
            total_cost = self._calculate_cost(response_json,model)
            return response, total_cost, model
        except Exception as e:
            logger.error("Unexpected Error while Running Customer Improve Reply Model", exc_info=e)
        


    def _execute_bot(self, question, item_id, item_name, employee_reply):
        category="improve_human_reply"
        reason =""
        feedback=""
        answer, total_cost, model = self._call_llm (question, item_name, employee_reply, category)
        load_llm_consumption(item_id, item_name, question, category, answer, True, feedback, False, reason, total_cost, model)

        return answer
        