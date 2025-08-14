import openai
import requests
from app.utils.logger import logger
from app.config.config import OPENAI_API_KEY, GPT_MODEL, DS_API_KEY, DS_MODEL


def _call_deepseek(
    prompt: str,
    question: str,
    max_tokens: int,
    temperature: float,
    api_key: str = DS_API_KEY,
    model: str = DS_MODEL):

    """Send Request to Deepseek Model.
    Args:
        prompt:
        question:
        max_tokens:
        temperature:
        api_key:
        model:
    Returns: data (dict) , model (str)
    """


    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system",  "content": prompt},
            {"role": "user",    "content": question}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    logger.info(f"[Deepseek] Modelo utilizado: {model}")
    return data, model


def _call_openai(
    prompt: str,
    question: str,
    max_tokens: int,
    temperature: float,
    api_key: str = OPENAI_API_KEY,
    model: str = GPT_MODEL):

    """Send Request to GPT Model.
    Args:
        prompt:
        question:
        max_tokens:
        temperature:
        api_key:
        model:
    Returns: data (dict) , model (str)
    """

    openai.api_key = api_key
    data = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": question}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    logger.info(f"[OpenAI] Modelo utilizado: {model}")
    return data, model


def switch_llm_body(
    prompt: str,
    question: str,
    max_tokens: int,
    temperature: float):
    """Primero intenta Deepseek; si hay cualquier fallo HTTP o de red,cae en OpenAI como fallback.
        Returns: data (dict) , model (str)
    """
    try:
        return _call_deepseek(prompt, question, max_tokens, temperature)
    except requests.RequestException as e:
        logger.warning("Deepseek falló, usando OpenAI como fallback", exc_info=e)
        return _call_openai(prompt, question, max_tokens, temperature)
    except Exception as e:
        # Captura otros errores imprevistos de Deepseek
        logger.error("Error inesperado en Deepseek, fallback a OpenAI", exc_info=e)
        return _call_openai(prompt, question, max_tokens, temperature)
