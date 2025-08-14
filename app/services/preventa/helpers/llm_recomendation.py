from app.services.preventa.database.gbq_llm_prompts import get_prompt_json
from app.services.preventa.helpers.llm_switch import switch_llm_body
from app.services.preventa.database.gbq_inventory import get_inventory
from app.config.config import FALLBACK_MESSAGE
from app.utils.logger import logger


def inventory_search(user_id, question):
    """LLM read inventory table and returns items realated to question item.
        Args:
            user_id: id from the user account
            question: question text made by the user
            item: item text related to the question
        Returns: A list with max. 5 items by partition.
    """
    try:
        logger.info(f"Running Model Inventory Search..")
        inventory = get_inventory(user_id)
        rows = len(inventory)
        chunk_size = 400
        partitions = [inventory[i:i + chunk_size].values.tolist() for i in range(0, rows, chunk_size)]
        prompt = get_prompt_json("busqueda_inventario")
        responses = []
        for i in range(len(partitions)):
            items = partitions[i]
            prompt = f"{prompt} \n ----- \n la base con la que vas a trabajar es la siguiente: {items}"
            response_json,model = switch_llm_body(prompt, question, 5000, 0.2)
            rta = response_json['choices'][0]['message']['content'].strip()
            responses.append(rta)
        return responses
    
    except Exception as e:
            logger.error("Unexpected Error while running Model Inventory Search", exc_info=e)
            return FALLBACK_MESSAGE


def suggest_response(user_id, question):
    """LLM read selected items to create message.
        Args:
            user_id:
            question: question text made by the user
        Returns: Response to Customer
    """
    responses = inventory_search(user_id, question)
    try:
        logger.info(f"Running Bot Recomendation Response..")
        prompt = get_prompt_json("respuesta_recomendacion")
        prompt = f"{prompt} \n ----- \n la base con la que vas a trabajar es la siguiente: {responses}"
        response_json,model = switch_llm_body(prompt, question, 5000, 0.2)
        reply = response_json['choices'][0]['message']['content'].strip()
        return reply
    except Exception as e:
        logger.error("Unexpected Error while Running Bot Recomendation Response", exc_info=e)
        return FALLBACK_MESSAGE
