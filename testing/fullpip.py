#TESTING PREGUNTAS -- COMPLETE WORKFLOW#

#reemplazar en blueprint_preventa 
#1- handle_questions(data=None) --> handle_questions(user_id, question, item_id)
#2- comentar 2 primeras lineas post funcion y check 4°
#3- comentar todos los send_response de Meli y ademas LLM consumption.

#4- handle_questions(data) dentro de handle_webhook() > handle_questions(user_id, question, item_id)
#agregar variables dentro de handle_webhook:

#topic = data.get("topic")
#user_id = data.get("user_id")
#question = data.get("question")
#item_id = data.get("item_id")


import requests

# URL de tu webhook local (ajusta host/puerto si hace falta)
url = 'http://localhost:5001/webhook'

# Payload con los campos vacíos
payload = {
      "topic": "questions",
      "user_id": "47015668",
      "question_id": "XXXX",
      "question": "QUIERO HABLAR CON UNA PERSONA.",
      "item_id": "MLA753900271"
      }
print("nnnn")
response = requests.post(url, json=payload)
response

print("nnnn")