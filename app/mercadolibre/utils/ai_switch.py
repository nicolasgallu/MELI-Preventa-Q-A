import openai
import requests
from datetime import datetime
from app.shared.core.logger import logger
from app.shared.core.settings import OPENAI_API_KEY, GPT_MODEL, DS_API_KEY, DS_MODEL

class AiSwitch():
    
    DS_URL = "https://api.deepseek.com/v1/chat/completions"

    def __init__(self, prompt, question, max_tokens, temperature):
        self.prompt = prompt
        self.question = question
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.response = {
            "model": None, 
            "response": None, 
            "tokens_used": 0,
            "timestamp": None
        }


    def _call_deepseek(self):  
        headers = {
            "Authorization": f"Bearer {DS_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": DS_MODEL,
            "messages": [
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.question}
                ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }   
        resp = requests.post(url=self.DS_URL, headers=headers, json=payload)
        resp_json = resp.json()
        self.response["model"] = DS_MODEL
        self.response["response"] = resp_json['choices'][0]['message']['content'].strip()
        self.response["tokens_used"]= resp_json.get("usage", {}).get("total_tokens", 0)
        self.response["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return self.response
 

    def _call_openai(self):
        openai.api_key = OPENAI_API_KEY
        resp_json = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": self.question}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        self.response["model"] = GPT_MODEL
        self.response["response"] = resp_json['choices'][0]['message']['content'].strip().lower()
        self.response["tokens_used"] = resp_json.get('usage', {}).get('total_tokens', 0)
        self.response["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        return self.response


    def switch(self):
        """
        Return a dictionary with the model name, response text, and tokens used.
        
        Format:
        {
            "model": str,
            "response": str,
            "tokens_used": int
        }
        """
        try:
            logger.info("Trying to Run Deepseek Model..")
            data = self._call_deepseek()
            logger.info("Deepseek AI Success Run.")
            return data
        except Exception as e:
            logger.warning("Deepseek Failed, trying to use OpenAI Model", exc_info=e)
            return self._call_openai()
