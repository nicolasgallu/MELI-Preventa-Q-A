import json
import re
from app.utils.logger import logger
from app.config.config import COST_PER_1K_TOKENS,FALLBACK_MESSAGE
from app.services.preventa.helpers.item_context import get_item_context
from app.services.preventa.helpers.llm_switch import switch_llm_body
from app.services.preventa.helpers.llm_consumption import load_llm_consumption
from app.services.preventa.helpers.llm_prompts import get_prompt_json



class ProductQuestionBot:
    
    def __init__(self):
        self

    def _calculate_cost(self,response_json,model):
        """Calcula el costo en USD de cada accion del LLM"""
        for i in COST_PER_1K_TOKENS:
            if i == model:
                cost_data = COST_PER_1K_TOKENS.get(model, {"input": 0, "output": 0})
                break
            else: continue
        usage = response_json.get('usage', {})
        input_cost = cost_data["costo"]["input"] / 1000 * usage.get('prompt_tokens', 0)
        output_cost = cost_data["costo"]["output"] / 1000 * usage.get('completion_tokens', 0)
        total_cost = input_cost + output_cost   
        return total_cost

          

    def _classify_question(self, question):
        """Clasifica la pregunta en una de las categorías."""
        logger.info(f"Ejecutando modelo para clasificar la pregunta del cliente")
        prompt = "\n".join(json.loads(get_prompt_json("categories_json"))["categories"]["description"])
        response_json,model = switch_llm_body(prompt, question, 50, 0.2)
        category = response_json['choices'][0]['message']['content'].strip()
        total_cost = self._calculate_cost(response_json,model)
        return category,total_cost
    


    def _answering_customer (self, question, category, item_context, total_cost=0):
        """Responde la pregunta del Customer."""
        logger.info(f"Ejecutando modelo para responder al cliente.")
        clusterfile = json.loads(get_prompt_json("clusters_json"))
        for cluster in clusterfile:
            if cluster == category:
                context_prompt = "\n".join(clusterfile[cluster]["description"])
                break
            else:continue
        prompt = f"{context_prompt} \n ----- \n LA PREGUNTA DEL CLIENTE ES EXCLUSIVAMENTE SOBRE EL SIGUIENTE PRODUCTO: {item_context}"
        response_json,model = switch_llm_body(prompt, question, 1000, 0.55)
        response = response_json['choices'][0]['message']['content'].strip()
        total_cost = self._calculate_cost(response_json,model)
        return response, total_cost, model
        

    def _audit_answer (self, question, item_context, response):
        logger.info(f"Ejecutando modelo para auditar respuesta del bot.")
        prompt = "\n".join(json.loads(get_prompt_json("audit_json"))["audit"]["description"])
        question = f"pregunta_cliente: {question} \n  contexto: {item_context} \n respuesta_llm: {response}"
        response_json,model = switch_llm_body(prompt, question, 1000, 0.45)
        total_cost = self._calculate_cost(response_json,model)  

        output_text = response_json['choices'][0]['message']['content'].strip()
        if output_text.startswith("```") and output_text.endswith("```"):
            output_text = re.sub(r'^```(?:json)?\s*', '', output_text)
            output_text = re.sub(r'\s*```$', '', output_text)
     
        
        try:
            audit_response = json.loads(output_text)
            try:
                if type(audit_response) is not dict:
                    logger.error(f"Error el formato de respuesta del bot auditor no fue un diccionario.")
                    raise ValueError
                if not all(key in audit_response for key in ["respuesta_valida", "razon_rechazo", "correccion_sugerida"]):
                    logger.error(f"Error el formato de respuesta del bot auditor no contiene algunas de las claves necesarias.")
                    raise ValueError
                else:
                    return audit_response,total_cost,model
            except:
                return total_cost
        except:
            logger.error("Audit Bot fallo al procesar el json.loads:")   
            return total_cost

    def _filter_output(self,response):
        logger.info(f"Ejecutando filtro FALLBACK")
        if "humano" in response.lower() or "vendedor" in response.lower():
            logger.info(f"La respuesta del bot cae en el filtro FALLBACK")
            return True
        else:
            logger.info(f"La respuesta del bot paso el filtro FALLBACK")
            return False



    def _execute_bot(self,question,item_context,item_id,item_name):

        total_cost = 0
        category,new_cost = self._classify_question(question)
        total_cost+=new_cost
        bot_answer,new_cost,model = self._answering_customer(question=question, category=category, item_context=item_context,total_cost=total_cost)
        total_cost+=new_cost

        if self._filter_output(bot_answer): 
            load_llm_consumption(item_id, item_name, question, category, bot_answer, bot_answer_sent=False, bot_feedback="", bot_feedback_sent=False, total_cost=total_cost,bot_model=model)
            return FALLBACK_MESSAGE
        
        
        audit_tuple = self._audit_answer(question, item_context, bot_answer)

        try:
            if len(audit_tuple) > 2:
                audit_dict = audit_tuple[0]
                new_cost = audit_tuple[1]
                model = audit_tuple[2]
                audit_answer = audit_dict["respuesta_valida"]
                bot_feedback = audit_dict["correccion_sugerida"]
                bot_feedback_reason = audit_dict["razon_rechazo"]
                total_cost += new_cost

                if audit_answer is True or audit_answer == "True" or audit_answer == "true":
                    logger.info(f"La respuesta paso con exito la auditoria.")
                    load_llm_consumption(item_id, item_name, question, category, bot_answer, bot_answer_sent=True, bot_feedback="", bot_feedback_sent=False, total_cost=total_cost,bot_model=model)
                    return bot_answer

                elif len(bot_feedback) > 10:
                    logger.info(f"La respuesta no paso con exito la auditoria.")
                    if self._filter_output(bot_feedback): 
                        load_llm_consumption(item_id, item_name, question, category, bot_answer, bot_answer_sent=False, 
                                             bot_feedback=bot_feedback, bot_feedback_sent=False, bot_feedback_reason=bot_feedback_reason,
                                             total_cost=total_cost,bot_model=model)
                        return FALLBACK_MESSAGE
                    else:
                        logger.info(f"Se envia la respuesta sugerida por bot auditor")
                        load_llm_consumption(item_id, item_name, question, category, bot_answer, bot_answer_sent=False, 
                                             bot_feedback=bot_feedback, bot_feedback_sent=True, bot_feedback_reason=bot_feedback_reason,
                                             total_cost=total_cost,bot_model=model) 
                        return bot_feedback                
        except:
            new_cost = audit_tuple[0]
            total_cost += new_cost
            load_llm_consumption(item_id, item_name, question, category, bot_answer, bot_answer_sent=False, bot_feedback=bot_feedback, bot_feedback_sent=False, total_cost=total_cost,bot_model=model) 
            return FALLBACK_MESSAGE
                    
    

    def generate_llm_response(self,question,item_id):
        try:
            item_context = get_item_context(item_id)
            if not item_context:
                logger.warning(f"No se pudo obtener contexto para el ítem {item_id} CONTEXTO: {item_context}.")
                return FALLBACK_MESSAGE
            
            item_id = item_context["item_id"]
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
            
            return self._execute_bot(question,item_context,item_id,item_name)
        
        except Exception as e:
            logger.error("Error de respuesta por parte del LLM",e)
            return FALLBACK_MESSAGE

        
