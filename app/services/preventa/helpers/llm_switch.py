import openai
import requests
from app.utils.logger import logger
from app.config.config import OPENAI_API_KEY, GPT_MODEL, DS_API_KEY, DS_MODEL


def switch_llm_body(prompt, question, max_tokens, temperature, deepseek_api_key=DS_API_KEY, deepseek_model=DS_MODEL, gpt_api_key=OPENAI_API_KEY, gpt_model=GPT_MODEL):
    try:
        deepseek_url = "https://api.deepseek.com/v1/chat/completions" 
        headers = {"Authorization": f"Bearer {deepseek_api_key}","Content-Type": "application/json"}
        data = {
            "model": deepseek_model,
            "messages": [{"role": "system", "content": prompt},{"role": "user", "content": question}],
            "max_tokens": max_tokens,
            "temperature": temperature}
        response = requests.post(deepseek_url, headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP
        response_json = response.json()
        model = deepseek_model
        logger.info(f"Modelo utilizado: {model}")
        return response_json,model


    except Exception as e:
        openai.api_key = gpt_api_key
        response_json = openai.ChatCompletion.create(model=gpt_model,
            messages=[{"role": "system", "content": prompt},{"role": "user", "content": question}],
            max_tokens=max_tokens,
            temperature=temperature)
        model = gpt_model
        logger.info(f"Modelo utilizado: {model}")   
        return response_json,model